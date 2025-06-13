from ninja import Router

from apps.location.models import Location
from weather_alert.api.schemas import MessageSchema

from .models import Alert, AlertConfig
from .schemas import (
    AlertConfigSchema,
    AlertSchema,
    CreateAlertConfigSchema,
    UpdateAlertConfigSchema,
)

alert_config_router = Router(tags=['Alert Configs'])
alert_router = Router(tags=['Alerts'])


# Alert Config Endpoints


@alert_config_router.post(
    '/', response={200: AlertConfigSchema, 404: MessageSchema}
)
async def create_alert_config(request, payload: CreateAlertConfigSchema):
    """
    Cria uma nova configuração de alerta.

    Args:
        payload (CreateAlertConfigSchema): Dados da configuração a ser criada.

    Returns:
        200: Configuração criada com sucesso.
        404: Se a localidade informada não for encontrada.
    """
    try:
        location = await Location.objects.aget(id=payload.location)
    except Location.DoesNotExist:
        return 404, MessageSchema(message='Localidade não encontrada')

    alert_config = await AlertConfig.objects.acreate(
        location=location,
        temperature_threshold=payload.temperature_threshold,
        check_interval_minutes=payload.check_interval_minutes,
    )
    return alert_config


@alert_config_router.get('/', response=list[AlertConfigSchema])
async def list_alert_configs(request):
    """
    Lista todas as configurações de alerta cadastradas.

    Returns:
        list[AlertConfigSchema]: Lista de configurações de alerta.
    """
    queryset = AlertConfig.objects.all()
    alert_configs = [config async for config in queryset]
    return alert_configs


@alert_config_router.get(
    '/{id}/', response={200: AlertConfigSchema, 404: MessageSchema}
)
async def get_alert_config(request, id: int):
    """
    Recupera uma configuração de alerta pelo seu ID.

    Args:
        id (int): Identificador da configuração.

    Returns:
        200: Configuração de alerta encontrada.
        404: Se a configuração não existir.
    """
    try:
        config = await AlertConfig.objects.aget(id=id)
        return config
    except AlertConfig.DoesNotExist:
        return 404, MessageSchema(
            message='Configuração de alerta não encontrada'
        )


@alert_config_router.put(
    '/{id}/', response={200: AlertConfigSchema, 404: MessageSchema}
)
async def update_alert_config(
    request, id: int, payload: UpdateAlertConfigSchema
):
    """
    Atualiza uma configuração de alerta existente.

    Args:
        id (int): Identificador da configuração.
        payload (UpdateAlertConfigSchema): Dados a serem atualizados.

    Returns:
        200: Configuração atualizada.
        404: Se a configuração não existir.
    """
    try:
        config = await AlertConfig.objects.aget(id=id)
    except AlertConfig.DoesNotExist:
        return 404, MessageSchema(
            message='Configuração de alerta não encontrada'
        )

    update_data = payload.model_dump(exclude_unset=True)

    for attr, value in update_data.items():
        setattr(config, attr, value)
    await config.asave()

    return config


@alert_config_router.delete('/{id}/', response={204: None, 404: MessageSchema})
async def delete_alert_config(request, id: int):
    """
    Remove uma configuração de alerta.

    Args:
        id (int): Identificador da configuração.

    Returns:
        204: Configuração removida.
        404: Se a configuração não existir.
    """
    try:
        config = await AlertConfig.objects.aget(id=id)
        await config.adelete()
        return 204, None
    except AlertConfig.DoesNotExist:
        return 404, MessageSchema(
            message='Configuração de alerta não encontrada'
        )


# Alert Endpoints


@alert_router.get('/', response=list[AlertSchema])
async def list_alerts(request, location_id: int = None):
    """
    Lista todos os alertas, podendo ser filtrados por localidade.

    Args:
        location_id (int, opcional): Filtrar alertas por ID da localidade.

    Returns:
        list[AlertSchema]: Lista de alertas.
    """
    if location_id:
        queryset = Alert.objects.filter(location_id=location_id)
    else:
        queryset = Alert.objects.all()

    alerts = [alert async for alert in queryset]
    return alerts


@alert_router.get('/{id}/', response={200: AlertSchema, 404: MessageSchema})
async def get_alert(request, id: int):
    """
    Recupera os detalhes de um alerta pelo seu ID.

    Args:
        id (int): Identificador do alerta.

    Returns:
        200: Alerta encontrado.
        404: Se o alerta não existir.
    """
    try:
        alert = await Alert.objects.aget(id=id)
        return alert
    except Alert.DoesNotExist:
        return 404, MessageSchema(message='Alerta não encontrado')
