from loguru import logger
from ninja import Query, Router

from weather_alert.api.schemas import MessageSchema

from .models import TemperatureLog
from .schemas import TemperatureLogSchema

temperature_router = Router(tags=['Temperature Logs'])


@temperature_router.get('/', response=list[TemperatureLogSchema])
async def list_temperature_logs(
    request, location_id: int = Query(default=None)
):
    """
    Lista todos os registros de temperatura, com opção de filtro por localização.

    Args:
        location_id (int, optional): ID da localização para filtrar os registros.

    Returns:
        list[TemperatureLogSchema]: Lista de registros de temperatura.
    """
    if location_id is not None:
        logger.info(
            f'Listando logs de temperatura para localidade ID {location_id}'
        )
        queryset = queryset.filter(location_id=location_id)
    else:
        logger.info('Listando todos os logs de temperatura')
        queryset = TemperatureLog.objects.all()

    logs = [log async for log in queryset.order_by('-timestamp')]
    logger.info(f'{len(logs)} registros de temperatura encontrados')
    return logs


@temperature_router.get(
    '/{id}/', response={200: TemperatureLogSchema, 404: MessageSchema}
)
async def get_temperature_log(request, id: int):
    """
    Recupera um registro de temperatura específico pelo ID.

    Args:
        id (int): Identificador do registro.

    Returns:
        200: Registro encontrado.
        404: Mensagem de erro caso não seja encontrado.
    """
    logger.info(f'Buscando registro de temperatura ID {id}')
    try:
        log = await TemperatureLog.objects.aget(id=id)
    except TemperatureLog.DoesNotExist:
        logger.warning(f'Registro de temperatura ID {id} não encontrado')
        return 404, MessageSchema(
            message='Registro de temperatura não encontrado'
        )

    logger.success(f'Registro de temperatura ID {id} encontrado')
    return log
