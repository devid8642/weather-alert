from datetime import datetime

import httpx
from django.conf import settings
from loguru import logger

from weather_alert.apps.alerts.models import Alert, AlertConfig
from weather_alert.apps.location.models import Location


def create_alert_and_notify(
    location: Location, temperature: float, alert_config: AlertConfig
):
    """
    Cria um alerta e notifica via webhook do N8N.

    Args:
        location (Location): Localização associada ao alerta.
        temperature (float): Temperatura registrada.
        alert_config (AlertConfig): Configuração de alerta associada.

    Returns:
        Alert: O alerta criado e notificado.
    """
    alert = Alert.objects.create(
        location=location,
        temperature=temperature,
        threshold=alert_config.temperature_threshold,
    )

    payload = {
        'alert_id': alert.id,
        'location': location.name,
        'temperature': temperature,
        'threshold': alert_config.temperature_threshold,
        'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
    }

    logger.info(
        f'Enviando notificação para N8N webhook (alert_id={alert.id})...'
    )

    if settings.FAKE_WEBHOOK:
        logger.warning(
            f'Modo FAKE_WEBHOOK ativo. Simulando notificação para alerta ID {alert.id}'
        )
        alert.notified = True
        alert.save(update_fields=['notified'])
        return alert

    try:
        response = httpx.post(
            settings.N8N_WEBHOOK_URL,
            json=payload,
            headers={'N8N_WEBHOOK_KEY': settings.N8N_WEBHOOK_HEADER_KEY},
        )
        response.raise_for_status()
        logger.success(
            f'Notificação enviada com sucesso para N8N (alert_id={alert.id})'
        )
    except httpx.HTTPStatusError:
        logger.error(
            f'Falha ao notificar N8N para alerta ID {alert.id} - status: {response.status_code} - resposta: {response.text}'
        )

    logger.success(
        f"Alerta criado e notificação enviada para localidade '{location}' (ID: {location.id})"
    )
    return alert
