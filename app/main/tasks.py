import asyncio
import logging
from asgiref.sync import sync_to_async
from .models import City

import logging
from .config import openmeteo, setup_logging

setup_logging()
logger = logging.getLogger(__name__)


async def periodic_update():
    logger.info("Запуск periodic_update")
    while True:
        await update_cache_async()
        await asyncio.sleep(15 * 60)


async def update_cache_async():
    logger.info("Начало обновления кеша")
    @sync_to_async
    def get_cities():
        return list(City.objects.all())
    cities = await get_cities()

    url = "https://api.open-meteo.com/v1/forecast"

    for city in cities:
        params = {
            "latitude": city.latitude,
            "longitude": city.longitude,
            "hourly": "temperature_2m,wind_speed_10m,pressure_msl"
        }
        responses = await asyncio.to_thread(openmeteo.weather_api, url, params=params)
        logger.debug(
            f"Данные получены для координат: {city.latitude}, {city.longitude}")

    logger.info("Обновление кеша завершено")
