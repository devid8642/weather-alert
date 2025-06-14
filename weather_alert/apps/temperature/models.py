from django.db import models

from weather_alert.apps.location.models import Location


class TemperatureLog(models.Model):
    """
    Modelo para registrar logs de temperatura associados a uma localização.

    Attributes:
        location (ForeignKey): Referência à localização associada ao log de temperatura.
        temperature (FloatField): Temperatura registrada.
        timestamp (DateTimeField): Data e hora em que a temperatura foi registrada.
    """

    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name='temperature_logs'
    )
    temperature = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f'{self.location.name} - {self.temperature}°C at {self.timestamp}'
        )
