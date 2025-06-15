from loguru import logger
from ninja import Router

from weather_alert.api.schemas import MessageSchema

from .models import Location
from .schemas import CreateLocationSchema, LocationSchema

location_router = Router(tags=['Locations'])


@location_router.post('/', response=LocationSchema)
async def create_location(request, payload: CreateLocationSchema):
    """
    Salva uma nova localização.

    Args:
        payload (CreateLocationSchema): Dados da localização a ser criada.

    Returns:
        LocationSchema: Dados da localização criada.
    """
    logger.info(f'Criando nova localização: {payload.name}')
    location = await Location.objects.acreate(**payload.model_dump())
    logger.success(
        f"Localização criada com sucesso: '{location.name}' (ID: {location.id})"
    )
    return location


@location_router.get('/', response=list[LocationSchema])
async def list_locations(request):
    """
    Lista todas as localizações cadastradas.

    Returns:
        list[LocationSchema]: Lista de localizações.
    """
    logger.info('Listando todas as localizações cadastradas')
    queryset = Location.objects.all()
    locations = [location async for location in queryset]
    logger.info(f'{len(locations)} localizações encontradas')
    return locations


@location_router.get(
    '/{id}/', response={200: LocationSchema, 404: MessageSchema}
)
async def get_location(request, id: int):
    """
    Recupera os detalhes de uma localização pelo seu ID.

    Args:
        id (int): Identificador da localização.

    Returns:
        200: Dados da localização, se encontrada.
        404: Mensagem de erro caso não seja encontrada.
    """
    logger.info(f'Buscando localização ID {id}')
    try:
        location = await Location.objects.aget(id=id)
    except Location.DoesNotExist:
        logger.warning(f'Localização ID {id} não encontrada')
        return 404, MessageSchema(message='Localidade não encontrada')

    logger.success(f"Localização ID {id} encontrada: '{location.name}'")
    return location


@location_router.delete('/{id}/', response={204: None, 404: MessageSchema})
async def delete_location(request, id: int):
    """
    Deleta uma localização pelo seu ID.

    Args:
        id (int): Identificador da localização.

    Returns:
        204: Nenhum conteúdo, se deletado com sucesso.
        404: Mensagem de erro caso não seja encontrada.
    """
    logger.info(f'Deletando localização ID {id}')
    try:
        location = await Location.objects.aget(id=id)
        await location.adelete()
        logger.success(f'Localização ID {id} deletada com sucesso')
        return 204, None
    except Location.DoesNotExist:
        logger.warning(f'Localização ID {id} não encontrada para deleção')
        return 404, MessageSchema(message='Localidade não encontrada')
