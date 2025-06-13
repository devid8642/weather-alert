from django.db import models

from apps.location.models import Location


class AlertConfig(models.Model):
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name='alert_config'
    )
    temperature_threshold = models.FloatField()
    check_interval_minutes = models.IntegerField(default=30)

    def __str__(self):
        return f'Config for {self.location.name}'


class Alert(models.Model):
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name='alerts'
    )
    temperature = models.FloatField()
    threshold = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    def __str__(self):
        return f'ALERT: {self.location.name} - {self.temperature}°C'
