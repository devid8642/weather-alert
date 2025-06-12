from django.db import models


class Location(models.Model):
    """
    Modelo que representa uma localização geográfica.

    Attributes:
        name (str): Nome descritivo da localização.
        latitude (float): Latitude da localização em coordenadas decimais.
        longitude (float): Longitude da localização em coordenadas decimais.
    """

    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name
