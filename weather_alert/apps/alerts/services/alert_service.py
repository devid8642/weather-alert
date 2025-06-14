from datetime import datetime

import httpx
from django.conf import settings

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

    try:
        response = httpx.post(
            settings.N8N_WEBHOOK_URL,
            json={
                'alert_id': alert.id,
                'location': location.name,
                'temperature': temperature,
                'threshold': alert_config.temperature_threshold,
                'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            },
            headers={'N8N_WEBHOOK_KEY': settings.N8N_WEBHOOK_HEADER_KEY},
        )
        response.raise_for_status()
    except httpx.HTTPStatusError:
        print('Erro ao fazer requisição para o N8N')
        print(response.status_code)
        print(response.text)

    return alert
