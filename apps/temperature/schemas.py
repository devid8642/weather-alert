from ninja import ModelSchema

from .models import TemperatureLog


class TemperatureLogSchema(ModelSchema):
    """
    Schema de saída para exibir informações de um registro de temperatura.

    Attributes:
        id (int): Identificador único do registro.
        location_id (int): ID da localização associada.
        temperature (float): Temperatura registrada.
        timestamp (datetime): Data e hora do registro.
    """

    class Meta:
        model = TemperatureLog
        fields = ['id', 'location', 'temperature', 'timestamp']
