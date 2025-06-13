import pytest
from ninja.testing import TestAsyncClient


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_list_temperature_logs(
    api_client: TestAsyncClient, create_temperature_log
):
    response = await api_client.get('temperature-logs/')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(log['temperature'] == 28.5 for log in data)


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_list_temperature_logs_filtered(
    api_client: TestAsyncClient, create_temperature_log
):
    location_id = create_temperature_log.location.id
    response = await api_client.get(
        f'temperature-logs/?location_id={location_id}'
    )
    assert response.status_code == 200
    data = response.json()
    assert all(log['location'] == location_id for log in data)


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_get_temperature_log(
    api_client: TestAsyncClient, create_temperature_log
):
    log_id = create_temperature_log.id
    response = await api_client.get(f'temperature-logs/{log_id}/')
    assert response.status_code == 200
    data = response.json()
    assert data['temperature'] == create_temperature_log.temperature

    response_not_found = await api_client.get('temperature-logs/99999/')
    assert response_not_found.status_code == 404
    assert (
        response_not_found.json()['message']
        == 'Registro de temperatura não encontrado'
    )
