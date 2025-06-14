import pytest
from ninja.testing import TestAsyncClient

from weather_alert.apps.alerts.models import AlertConfig


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_create_alert_config(
    api_client: TestAsyncClient, mocker, create_location
):
    mock_service = mocker.patch(
        'weather_alert.apps.alerts.views.AlertConfigService.create_alert_config_and_schedule_task'
    )
    mock_service.return_value = AlertConfig(
        id=1,
        location=create_location,
        temperature_threshold=30.5,
        check_interval_minutes=15,
    )

    payload = {
        'location': create_location.id,
        'temperature_threshold': 30.5,
        'check_interval_minutes': 15,
    }

    response = await api_client.post('/alert-configs/', json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['temperature_threshold'] == 30.5

    mock_service.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_create_alert_config_location_not_found(
    api_client: TestAsyncClient,
):
    payload = {
        'location': 99999,
        'temperature_threshold': 30.5,
        'check_interval_minutes': 15,
    }

    response = await api_client.post('/alert-configs/', json=payload)
    assert response.status_code == 404
    assert response.json()['message'] == 'Localidade não encontrada'


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_list_alert_configs(
    api_client: TestAsyncClient, create_alert_config
):
    response = await api_client.get('/alert-configs/')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(
        config['location'] == create_alert_config.location.id
        for config in data
    )


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_get_alert_config(
    api_client: TestAsyncClient, create_alert_config
):
    response = await api_client.get(
        f'/alert-configs/{create_alert_config.id}/'
    )
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == create_alert_config.id

    response_not_found = await api_client.get('/alert-configs/99999/')
    assert response_not_found.status_code == 404
    assert (
        response_not_found.json()['message']
        == 'Configuração de alerta não encontrada'
    )


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_update_alert_config(
    api_client: TestAsyncClient, mocker, create_alert_config
):
    mock_service = mocker.patch(
        'weather_alert.apps.alerts.views.AlertConfigService.update_alert_config_and_schedule_task'
    )
    mock_service.return_value = create_alert_config

    payload = {'temperature_threshold': 29.0}
    response = await api_client.put(
        f'/alert-configs/{create_alert_config.id}/', json=payload
    )

    assert response.status_code == 200
    mock_service.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_delete_alert_config_mocked(
    api_client: TestAsyncClient, mocker, create_alert_config
):
    mock_service = mocker.patch(
        'weather_alert.apps.alerts.views.AlertConfigService.delete_alert_config_and_schedule_task'
    )
    response = await api_client.delete(
        f'/alert-configs/{create_alert_config.id}/'
    )

    assert response.status_code == 204
    mock_service.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_list_alerts(api_client: TestAsyncClient, create_alert):
    response = await api_client.get('/alerts/')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(alert['id'] == create_alert.id for alert in data)


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_list_alerts_filtered(api_client: TestAsyncClient, create_alert):
    response = await api_client.get(
        f'/alerts/?location_id={create_alert.location.id}'
    )
    assert response.status_code == 200
    data = response.json()
    assert all(alert['location'] == create_alert.location.id for alert in data)


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_get_alert(api_client: TestAsyncClient, create_alert):
    response = await api_client.get(f'/alerts/{create_alert.id}/')
    assert response.status_code == 200
    data = response.json()
    assert data['temperature'] == create_alert.temperature

    response_not_found = await api_client.get('/alerts/99999/')
    assert response_not_found.status_code == 404
    assert response_not_found.json()['message'] == 'Alerta não encontrado'
