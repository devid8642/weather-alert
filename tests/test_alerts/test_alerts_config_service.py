import json

import pytest
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from weather_alert.apps.alerts.models import AlertConfig
from weather_alert.apps.alerts.services.alert_config_service import (
    AlertConfigService,
)


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_create_alert_config_and_schedule_task(create_location):
    alert_config = (
        await AlertConfigService.create_alert_config_and_schedule_task(
            location=create_location,
            temperature_threshold=30.5,
            check_interval_minutes=20,
        )
    )

    assert alert_config.location == create_location
    assert alert_config.temperature_threshold == 30.5
    assert alert_config.check_interval_minutes == 20

    periodic_task = await PeriodicTask.objects.aget(
        name=f'Check Temperature for Config {alert_config.id}'
    )
    assert periodic_task is not None
    assert json.loads(periodic_task.args) == [alert_config.id]


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_update_alert_config_and_schedule_task(create_alert_config):
    schedule, _ = await IntervalSchedule.objects.aget_or_create(
        every=create_alert_config.check_interval_minutes,
        period=IntervalSchedule.MINUTES,
    )
    await PeriodicTask.objects.acreate(
        interval=schedule,
        name=f'Check Temperature for Config {create_alert_config.id}',
        task='weather_alert.apps.alerts.tasks.check_temperature',
        args=json.dumps([create_alert_config.id]),
    )

    updated_config = (
        await AlertConfigService.update_alert_config_and_schedule_task(
            alert_config=create_alert_config,
            temperature_threshold=29.0,
            check_interval_minutes=10,
        )
    )

    assert updated_config.temperature_threshold == 29.0
    assert updated_config.check_interval_minutes == 10

    periodic_task = await PeriodicTask.objects.select_related('interval').aget(
        name=f'Check Temperature for Config {updated_config.id}'
    )
    assert periodic_task.interval.every == 10
    assert json.loads(periodic_task.args) == [updated_config.id]


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_delete_alert_config_and_schedule_task(create_alert_config):
    schedule, _ = await IntervalSchedule.objects.aget_or_create(
        every=create_alert_config.check_interval_minutes,
        period=IntervalSchedule.MINUTES,
    )
    periodic_task = await PeriodicTask.objects.acreate(
        interval=schedule,
        name=f'Check Temperature for Config {create_alert_config.id}',
        task='weather_alert.apps.alerts.tasks.check_temperature',
        args=json.dumps([create_alert_config.id]),
    )

    await AlertConfigService.delete_alert_config_and_schedule_task(
        create_alert_config
    )

    with pytest.raises(PeriodicTask.DoesNotExist):
        await PeriodicTask.objects.aget(id=periodic_task.id)

    assert not await AlertConfig.objects.filter(
        id=create_alert_config.id
    ).aexists()
