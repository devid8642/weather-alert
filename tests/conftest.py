import os

import pytest
import pytest_asyncio
from ninja.testing import TestAsyncClient
from apps.location.models import Location
from apps.alerts.models import Alert, AlertConfig

from apps.api.app import api


def pytest_generate_tests(metafunc):
    os.environ['NINJA_SKIP_REGISTRY'] = 'yes'


@pytest.fixture
def api_client():
    api.urls_namespace = 'test'
    return TestAsyncClient(api)


@pytest_asyncio.fixture
async def create_location():
    location = await Location.objects.acreate(
        name='Recife Antigo',
        latitude=-8.0628,
        longitude=-34.8711
    )
    return location

@pytest_asyncio.fixture
async def create_alert_config(create_location):
    alert_config = await AlertConfig.objects.acreate(
        location=create_location,
        temperature_threshold=30.5,
        check_interval_minutes=15
    )
    return alert_config

@pytest_asyncio.fixture
async def create_alert(create_location):
    alert = await Alert.objects.acreate(
        location=create_location,
        temperature=35.0,
        threshold=30.5,
        notified=False
    )
    return alert
