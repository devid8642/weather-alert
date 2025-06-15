import os

import pytest
import pytest_asyncio
import stamina
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from ninja.testing import TestAsyncClient

from weather_alert.api.app import api
from weather_alert.apps.alerts.models import Alert, AlertConfig
from weather_alert.apps.location.models import Location
from weather_alert.apps.temperature.models import TemperatureLog


def pytest_generate_tests(metafunc):
    os.environ['NINJA_SKIP_REGISTRY'] = 'yes'


@pytest.fixture(autouse=True, scope='session')
def deactivate_retries():
    stamina.set_active(False)


@pytest.fixture
def api_client():
    api.urls_namespace = 'test'
    return TestAsyncClient(api)


@pytest_asyncio.fixture
async def create_location():
    location = await Location.objects.acreate(
        name='Recife Antigo', latitude=-8.0628, longitude=-34.8711
    )
    return location


@pytest_asyncio.fixture
async def create_alert_config(create_location):
    alert_config = await AlertConfig.objects.acreate(
        location=create_location,
        temperature_threshold=30.5,
        check_interval_minutes=15,
    )
    return alert_config


@pytest_asyncio.fixture
async def create_alert(create_location):
    alert = await Alert.objects.acreate(
        location=create_location,
        temperature=35.0,
        threshold=30.5,
        notified=False,
    )
    return alert


@pytest_asyncio.fixture
async def create_temperature_log(create_location):
    temperature_log = await TemperatureLog.objects.acreate(
        location=create_location, temperature=28.5
    )
    return temperature_log


@pytest.fixture
def create_temperature_log_data(create_location):
    return {'location': create_location, 'temperature': 28.5}


@pytest_asyncio.fixture
async def create_schedule():
    schedule = await IntervalSchedule.objects.acreate(
        every=15, period=IntervalSchedule.MINUTES
    )
    return schedule


@pytest_asyncio.fixture
async def create_periodic_task(create_alert_config, create_schedule):
    task = await PeriodicTask.objects.acreate(
        interval=create_schedule,
        name=f'Check Temperature for Config {create_alert_config.id}',
        task='weather_alert.apps.alerts.tasks.check_temperature',
        args='[1]',
    )
    return task
