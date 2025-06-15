import httpx
import stamina
from loguru import logger


@stamina.retry(on=httpx.HTTPStatusError, attempts=5, wait_initial=1)
def get_current_temperature(latitude: float, longitude: float) -> float:
    """
    Obtém a temperatura atual para uma localização específica usando a API Open-Meteo.

    Args:
        latitude (float): Latitude da localização.
        longitude (float): Longitude da localização.

    Returns:
        float: Temperatura atual em graus Celsius.

    Raises:
        httpx.HTTPStatusError: Se a requisição falhar ou retornar um status de erro.
    """
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'current_weather': True,
    }
    logger.info(
        f'Requisitando temperatura para lat={latitude}, lon={longitude}'
    )

    try:
        with httpx.Client(http2=True) as client:
            response = client.get(
                'https://api.open-meteo.com/v1/forecast', params=params
            )
            response.raise_for_status()
            data = response.json()
            temp = data['current_weather']['temperature']
            logger.success(f'Temperatura encontrada: {temp}°C')
            return temp
    except httpx.HTTPStatusError as e:
        logger.error(f'Erro HTTP {e.response.status_code}: {e.response.text}')
        raise e
