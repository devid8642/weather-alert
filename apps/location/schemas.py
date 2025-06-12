from ninja import ModelSchema, Schema

from .models import Location


class LocationSchema(ModelSchema):
    """
    Schema de saída para exibir informações completas de uma localização.

    Attributes:
        id (int): Identificador único da localização.
        name (str): Nome da localização.
        latitude (float): Latitude geográfica.
        longitude (float): Longitude geográfica.
    """

    class Meta:
        model = Location
        fields = ['id', 'name', 'latitude', 'longitude']


class CreateLocationSchema(Schema):
    """
    Schema de entrada para cadastrar uma nova localização.

    Attributes:
        name (str): Nome da localização.
        latitude (float): Latitude geográfica.
        longitude (float): Longitude geográfica.
    """

    name: str
    latitude: float
    longitude: float
