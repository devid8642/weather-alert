import json

from django_celery_beat.models import IntervalSchedule, PeriodicTask

from weather_alert.apps.alerts.models import AlertConfig
from weather_alert.apps.location.models import Location


class AlertConfigService:
    @staticmethod
    async def create_alert_config_and_schedule_task(
        location: Location,
        temperature_threshold: float,
        check_interval_minutes: int = 30,
    ) -> AlertConfig:
        """
        Cria um AlertConfig e agenda sua task periódica no Celery Beat.

        Args:
            location (Location): Localização associada ao AlertConfig.
            temperature_threshold (float): Limite de temperatura para o alerta.
            check_interval_minutes (int): Intervalo em minutos para verificar a temperatura.

        Returns:
            AlertConfig: A nova configuração de alerta criada e agendada.
        """
        alert_config = await AlertConfig.objects.acreate(
            location=location,
            temperature_threshold=temperature_threshold,
            check_interval_minutes=check_interval_minutes,
        )

        schedule, _ = await IntervalSchedule.objects.aget_or_create(
            every=alert_config.check_interval_minutes,
            period=IntervalSchedule.MINUTES,
        )

        await PeriodicTask.objects.acreate(
            interval=schedule,
            name=f'Check Temperature for Config {alert_config.id}',
            task='weather_alert.apps.alerts.tasks.check_temperature',
            args=json.dumps([alert_config.id]),
        )

        return alert_config

    @staticmethod
    async def update_alert_config_and_schedule_task(
        alert_config: AlertConfig,
        temperature_threshold: float = None,
        check_interval_minutes: int = None,
    ) -> AlertConfig:
        """
        Atualiza o AlertConfig e seu respectivo PeriodicTask.

        Args:
            alert_config (AlertConfig): A configuração de alerta a ser atualizada.
            temperature_threshold (float, optional): Novo limite de temperatura para o alerta.
            check_interval_minutes (int, optional): Novo intervalo em minutos para verificar a temperatura.

        Returns:
            AlertConfig: A configuração de alerta atualizada.
        """
        updated = False

        if temperature_threshold is not None:
            alert_config.temperature_threshold = temperature_threshold
            updated = True

        if (
            check_interval_minutes is not None
            and check_interval_minutes != alert_config.check_interval_minutes
        ):
            alert_config.check_interval_minutes = check_interval_minutes
            updated = True

        if updated:
            await alert_config.asave()

            schedule, _ = await IntervalSchedule.objects.aget_or_create(
                every=alert_config.check_interval_minutes,
                period=IntervalSchedule.MINUTES,
            )

            periodic_task = await PeriodicTask.objects.select_related(
                'interval'
            ).aget(name=f'Check Temperature for Config {alert_config.id}')
            periodic_task.interval = schedule
            periodic_task.args = json.dumps([alert_config.id])
            await periodic_task.asave()

        return alert_config

    @staticmethod
    async def delete_alert_config_and_schedule_task(alert_config: AlertConfig):
        """
        Remove o AlertConfig e seu PeriodicTask associado.

        Args:
            alert_config (AlertConfig): A configuração de alerta a ser removida.

        Raises:
            AlertConfig.DoesNotExist: Se a configuração de alerta não existir.
        """
        try:
            periodic_task = await PeriodicTask.objects.aget(
                name=f'Check Temperature for Config {alert_config.id}'
            )
            await periodic_task.adelete()
        except PeriodicTask.DoesNotExist:
            pass

        await alert_config.adelete()
