import pytest

from weather_alert.apps.alerts.models import Alert, AlertConfig
from weather_alert.apps.temperature.models import TemperatureLog
from weather_alert.apps.alerts.tasks import check_temperature


@pytest.mark.django_db
def test_check_temperature_creates_alert(mocker, create_alert_config):
    mock_get_temp = mocker.patch(
        'weather_alert.apps.alerts.tasks.get_current_temperature',
        return_value=35.0
    )

    check_temperature(create_alert_config.id)

    mock_get_temp.assert_called_once_with(
        create_alert_config.location.latitude,
        create_alert_config.location.longitude
    )

    assert TemperatureLog.objects.filter(location=create_alert_config.location).exists()
    assert Alert.objects.filter(location=create_alert_config.location).exists()


@pytest.mark.django_db
def test_check_temperature_below_threshold(mocker, create_alert_config):
    mock_get_temp = mocker.patch(
        'weather_alert.apps.alerts.tasks.get_current_temperature',
        return_value=25.0
    )

    check_temperature(create_alert_config.id)

    mock_get_temp.assert_called_once()

    assert TemperatureLog.objects.filter(location=create_alert_config.location).exists()
    assert not Alert.objects.filter(location=create_alert_config.location).exists()


@pytest.mark.django_db
def test_check_temperature_config_not_found():
    with pytest.raises(Exception) as exc_info:
        check_temperature(99999)

    assert 'Não foi encontrado nenhum alerta com id' in str(exc_info.value)
