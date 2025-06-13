from ninja import Router

from apps.api.schemas import MessageSchema

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
    location = await Location.objects.acreate(**payload.model_dump())
    return location


@location_router.get('/', response=list[LocationSchema])
async def list_locations(request):
    """
    Lista todas as localizações cadastradas.

    Returns:
        list[LocationSchema]: Lista de localizações.
    """
    queryset = Location.objects.all()
    locations = [location async for location in queryset]
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
    try:
        location = await Location.objects.aget(id=id)
    except Location.DoesNotExist:
        return 404, MessageSchema(message='Localidade não encontrada')
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
    try:
        location = await Location.objects.aget(id=id)
        await location.adelete()
        return 204, None
    except Location.DoesNotExist:
        return 404, MessageSchema(message='Localidade não encontrada')
