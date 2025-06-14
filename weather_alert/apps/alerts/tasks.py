from celery import shared_task

from weather_alert.apps.alerts.models import Alert, AlertConfig
from weather_alert.apps.alerts.services.alert_service import (
    create_alert_and_notify,
)
from weather_alert.apps.temperature.models import TemperatureLog
from weather_alert.integrations.openmeteo import get_current_temperature


@shared_task
def check_temperature(alert_config_id: int):
    """
    Verifica a temperatura atual e cria um alerta se necessário.

    Args:
        alert_config_id (int): ID da configuração de alerta a ser verificada.

    Raises:
        Exception: Se a configuração de alerta com o ID fornecido não for encontrada.
    """
    try:
        alert_config = AlertConfig.objects.get(id=alert_config_id)
    except AlertConfig.DoesNotExist:
        raise Exception(
            f'Não foi encontrado nenhum alerta com id {alert_config_id}'
        )

    location = alert_config.location

    temperature = get_current_temperature(
        location.latitude, location.longitude
    )

    TemperatureLog.objects.create(location=location, temperature=temperature)

    if temperature > alert_config.temperature_threshold:
        create_alert_and_notify(
            location=location,
            temperature=temperature,
            alert_config=alert_config,
        )
