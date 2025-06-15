from celery import shared_task
from loguru import logger

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
    logger.info(
        f'Iniciando verificação de temperatura para AlertConfig ID {alert_config_id}'
    )

    try:
        alert_config = AlertConfig.objects.get(id=alert_config_id)
    except AlertConfig.DoesNotExist:
        logger.error(f'AlertConfig ID {alert_config_id} não encontrada')
        raise Exception(
            f'Não foi encontrado nenhum alerta com id {alert_config_id}'
        )

    location = alert_config.location
    logger.info(
        f"Obtendo temperatura atual para localidade '{location}' (ID: {location.id})"
    )

    temperature = get_current_temperature(
        location.latitude, location.longitude
    )
    logger.info(
        f"Temperatura atual em '{location}': {temperature}°C (threshold: {alert_config.temperature_threshold}°C)"
    )

    TemperatureLog.objects.create(location=location, temperature=temperature)
    logger.success(
        f"Log de temperatura registrado para localidade '{location}' (ID: {location.id})"
    )

    if temperature > alert_config.temperature_threshold:
        logger.warning(
            f"Temperatura {temperature}°C excedeu o limite de {alert_config.temperature_threshold}°C para localidade '{location}' (ID: {location.id})"
        )
        create_alert_and_notify(
            location=location,
            temperature=temperature,
            alert_config=alert_config,
        )
    else:
        logger.info(
            f"Temperatura dentro do limite para localidade '{location}' (ID: {location.id}) - Nenhum alerta gerado."
        )
