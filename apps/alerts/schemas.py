from ninja import Field, ModelSchema, Schema
from typing import Optional
from .models import AlertConfig, Alert
from apps.location.models import Location


class AlertConfigSchema(ModelSchema):
    """
    Schema de saída para configuração de alerta.

    Attributes:
        id (int): Identificador único da configuração de alerta.
        location (Location): Localização associada à configuração de alerta.
        temperature_threshold (float): Limite de temperatura para disparo do alerta.
        check_interval_minutes (int): Intervalo em minutos para verificação da temperatura.
    """
    class Meta:
        model = AlertConfig
        fields = ['id', 'location', 'temperature_threshold', 'check_interval_minutes']


class CreateAlertConfigSchema(Schema):
    """
    Schema de entrada para criação de configuração de alerta.

    Attributes:
        location (int): Identificador da localização associada à configuração de alerta.
        temperature_threshold (float): Limite de temperatura para disparo do alerta.
        check_interval_minutes (int): Intervalo em minutos para verificação da temperatura.
    """
    location: int
    temperature_threshold: float
    check_interval_minutes: int = 30


class UpdateAlertConfigSchema(Schema):
    """
    Schema de entrada para atualização de configuração de alerta.

    Attributes:
        temperature_threshold (Optional[float]): Novo limite de temperatura para disparo do alerta.
        check_interval_minutes (Optional[int]): Novo intervalo em minutos para verificação da temperatura.
    """
    temperature_threshold: Optional[float] = None
    check_interval_minutes: Optional[int] = None


class AlertSchema(ModelSchema):
    """
    Schema de saída para alertas.

    Attributes:
        id (int): Identificador único do alerta.
        location (Location): Localização associada ao alerta.
        temperature (float): Temperatura registrada no momento do alerta.
        threshold (float): Limite de temperatura que disparou o alerta.
        timestamp (datetime): Data e hora em que o alerta foi registrado.
        notified (bool): Indica se a notificação do alerta foi enviada.
    """
    class Meta:
        model = Alert
        fields = ['id', 'location', 'temperature', 'threshold', 'timestamp', 'notified']
