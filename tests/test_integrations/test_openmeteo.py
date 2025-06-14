import pytest
import respx
from httpx import HTTPStatusError, Request, Response

from weather_alert.integrations.openmeteo import get_current_temperature


@respx.mock
def test_get_current_temperature_success():
    latitude = -8.0628
    longitude = -34.8711
    expected_temperature = 28.5

    route = respx.get('https://api.open-meteo.com/v1/forecast').mock(
        return_value=Response(
            200,
            json={'current_weather': {'temperature': expected_temperature}},
        )
    )

    temperature = get_current_temperature(latitude, longitude)
    assert temperature == expected_temperature
    assert route.called


@respx.mock
def test_get_current_temperature_http_error():
    latitude = -8.0628
    longitude = -34.8711

    respx.get('https://api.open-meteo.com/v1/forecast').mock(
        return_value=Response(
            500,
            request=Request('GET', 'https://api.open-meteo.com/v1/forecast'),
        )
    )

    with pytest.raises(HTTPStatusError):
        get_current_temperature(latitude, longitude)
