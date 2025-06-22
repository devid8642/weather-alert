from loguru import logger
from ninja import Router

from weather_alert.api.schemas import MessageSchema
from weather_alert.api.security import n8n_header_key
from weather_alert.apps.location.models import Location

from .models import Alert, AlertConfig
from .schemas import (
    AlertConfigSchema,
    AlertSchema,
    CreateAlertConfigSchema,
    UpdateAlertConfigSchema,
)
from .services.alert_config_service import AlertConfigService

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
    logger.info(
        f'Criando configuração de alerta para localidade ID {payload.location}'
    )
    try:
        location = await Location.objects.aget(id=payload.location)
    except Location.DoesNotExist:
        logger.warning(
            f'Localidade ID {payload.location} não encontrada ao criar configuração de alerta'
        )
        return 404, MessageSchema(message='Localidade não encontrada')

    alert_config = (
        await AlertConfigService.create_alert_config_and_schedule_task(
            location=location,
            temperature_threshold=payload.temperature_threshold,
            check_interval_minutes=payload.check_interval_minutes,
        )
    )

    logger.success(
        f'Configuração de alerta criada para localidade ID {payload.location}'
    )
    return alert_config


@alert_config_router.get('/', response=list[AlertConfigSchema])
async def list_alert_configs(request):
    """
    Lista todas as configurações de alerta cadastradas.

    Returns:
        list[AlertConfigSchema]: Lista de configurações de alerta.
    """
    logger.info('Listando todas as configurações de alerta')
    queryset = AlertConfig.objects.all()
    alert_configs = [config async for config in queryset]
    logger.info(f'{len(alert_configs)} configurações de alerta encontradas')
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
    logger.info(f'Buscando configuração de alerta ID {id}')
    try:
        config = await AlertConfig.objects.aget(id=id)
        logger.success(f'Configuração de alerta ID {id} encontrada')
        return config
    except AlertConfig.DoesNotExist:
        logger.warning(f'Configuração de alerta ID {id} não encontrada.')
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
    logger.info(f'Atualizando configuração de alerta ID {id}')
    try:
        config = await AlertConfig.objects.aget(id=id)
    except AlertConfig.DoesNotExist:
        logger.warning(
            f'Configuração de alerta ID {id} não encontrada para atualização'
        )
        return 404, MessageSchema(
            message='Configuração de alerta não encontrada'
        )

    update_data = payload.model_dump(exclude_unset=True)

    updated_config = (
        await AlertConfigService.update_alert_config_and_schedule_task(
            alert_config=config,
            temperature_threshold=update_data.get('temperature_threshold'),
            check_interval_minutes=update_data.get('check_interval_minutes'),
        )
    )

    logger.success(f'Configuração de alerta ID {id} atualizada com sucesso')
    return updated_config


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
    logger.info(f'Removendo configuração de alerta ID {id}')
    try:
        config = await AlertConfig.objects.aget(id=id)
        await AlertConfigService.delete_alert_config_and_schedule_task(config)
        logger.success(f'Configuração de alerta ID {id} removida com sucesso')
        return 204, None
    except AlertConfig.DoesNotExist:
        logger.warning(
            f'Configuração de alerta ID {id} não encontrada para remoção'
        )
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
        logger.info(f'Listando alertas para localidade ID {location_id}')
        queryset = Alert.objects.select_related('location').filter(location_id=location_id)
    else:
        logger.info('Listando todos os alertas')
        queryset = Alert.objects.select_related('location').all()

    alerts = [alert async for alert in queryset]
    logger.info(f'{len(alerts)} alertas encontrados')

    return [
        AlertSchema(
            id=a.id,
            location_id=a.location.id,
            location_name=a.location.name,
            temperature=a.temperature,
            threshold=a.threshold,
            timestamp=a.timestamp,
            notified=a.notified,
        )
        for a in alerts
    ]


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
    logger.info(f'Buscando alerta ID {id}')
    try:
        alert = await Alert.objects.select_related('location').aget(id=id)
        logger.success(f'Alerta ID {id} encontrado')
        return AlertSchema(
            id=alert.id,
            location_id=alert.location.id,
            location_name=alert.location.name,
            temperature=alert.temperature,
            threshold=alert.threshold,
            timestamp=alert.timestamp,
            notified=alert.notified,
        )

    except Alert.DoesNotExist:
        logger.warning(f'Alerta ID {id} não encontrado')
        return 404, MessageSchema(message='Alerta não encontrado')


@alert_router.post(
    '/notify/{alert_id}/',
    response={200: MessageSchema, 404: MessageSchema},
    auth=n8n_header_key,
)
async def mark_alert_as_notified(request, alert_id: int):
    """
    Marca o alerta como notificado, apenas se a chave de autenticação do N8N for válida.

    Args:
        alert_id (int): Identificador do alerta a ser marcado como notificado.

    Returns:
        200: Alerta marcado como notificado com sucesso.
        404: Se o alerta não existir.
        401: Se a autenticação falhar
    """
    logger.info(f'Tentando marcar alerta ID {alert_id} como notificado')
    try:
        alert = await Alert.objects.aget(id=alert_id)
        alert.notified = True
        await alert.asave()
        logger.success(
            f'Alerta ID {alert_id} marcado como notificado com sucesso'
        )
        return 200, MessageSchema(
            message='Alerta marcado como notificado com sucesso'
        )
    except Alert.DoesNotExist:
        logger.warning(f'Alerta ID {alert_id} não encontrado para notificação')
        return 404, MessageSchema(message='Alerta não encontrado')
