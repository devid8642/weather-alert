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
    queryset = TemperatureLog.objects.all()

    if location_id is not None:
        queryset = queryset.filter(location_id=location_id)

    logs = [log async for log in queryset.order_by('-timestamp')]
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
    try:
        log = await TemperatureLog.objects.aget(id=id)
    except TemperatureLog.DoesNotExist:
        return 404, MessageSchema(
            message='Registro de temperatura não encontrado'
        )
    return log
