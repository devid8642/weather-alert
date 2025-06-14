import json

import pytest
import respx
from django.conf import settings
from httpx import Response

from weather_alert.apps.alerts.services.alert_service import (
    create_alert_and_notify,
)


@pytest.mark.django_db
@respx.mock
def test_create_alert_and_notify_success(create_location, create_alert_config):
    url = settings.N8N_WEBHOOK_URL

    respx.post(url).mock(return_value=Response(200))

    alert = create_alert_and_notify(
        location=create_location,
        temperature=35.0,
        alert_config=create_alert_config,
    )

    assert alert.location == create_location
    assert alert.temperature == 35.0
    assert alert.threshold == create_alert_config.temperature_threshold
    assert alert.notified is True

    assert respx.calls.call_count == 1
    request = respx.calls[0].request
    assert (
        request.headers['N8N_WEBHOOK_KEY'] == settings.N8N_WEBHOOK_HEADER_KEY
    )
    request_body = json.loads(request.content)
    assert request_body['location'] == create_location.name
    assert request_body['temperature'] == 35.0


@pytest.mark.django_db
@respx.mock
def test_create_alert_and_notify_failure(create_location, create_alert_config):
    url = settings.N8N_WEBHOOK_URL

    respx.post(url).mock(
        return_value=Response(500, json={'error': 'Internal Server Error'})
    )

    alert = create_alert_and_notify(
        location=create_location,
        temperature=35.0,
        alert_config=create_alert_config,
    )

    assert alert.location == create_location
    assert alert.temperature == 35.0
    assert alert.threshold == create_alert_config.temperature_threshold
    assert alert.notified is False

    assert respx.calls.call_count == 1
