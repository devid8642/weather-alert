import pytest
from ninja.testing import TestAsyncClient

from weather_alert.apps.location.models import Location


@pytest.fixture
def create_location_data():
    return {
        'name': 'Recife Antigo',
        'latitude': -8.0628,
        'longitude': -34.8711,
    }


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_create_location(
    api_client: TestAsyncClient, create_location_data
):
    response = await api_client.post('locations/', json=create_location_data)
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == create_location_data['name']
    assert await Location.objects.filter(name='Recife Antigo').aexists()


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_list_locations(
    api_client: TestAsyncClient, create_location_data
):
    await Location.objects.acreate(**create_location_data)

    response = await api_client.get('locations/')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(location['name'] == 'Recife Antigo' for location in data)


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_get_location(api_client: TestAsyncClient, create_location_data):
    location = await Location.objects.acreate(**create_location_data)

    response = await api_client.get(f'locations/{location.id}/')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == location.name

    response_not_found = await api_client.get('locations/99999/')
    assert response_not_found.status_code == 404
    assert response_not_found.json()['message'] == 'Localidade não encontrada'


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_delete_location(
    api_client: TestAsyncClient, create_location_data
):
    location = await Location.objects.acreate(**create_location_data)

    response = await api_client.delete(f'locations/{location.id}/')
    assert response.status_code == 204
    assert not await Location.objects.filter(id=location.id).aexists()

    response_not_found = await api_client.delete(f'locations/{location.id}/')
    assert response_not_found.status_code == 404
    assert response_not_found.json()['message'] == 'Localidade não encontrada'
