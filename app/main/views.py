from .forms import RegistrationForm, LoginForm, AddCityForm, DateRangeForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .config import openmeteo, setup_logging
from asgiref.sync import sync_to_async
from django.contrib.auth import login
from .models import UserCity
import pandas as pd
import asyncio
import logging

setup_logging()
logger = logging.getLogger(__name__)


async def fetch_weather_data(city):
    try:
        logger.info(f"Получение данных о погоде для города: {city.name}")
        weather_data = await get_weather_data(city.latitude, city.longitude)
        return city.name, {
            "weather": weather_data,
            "city": city
        }
    except Exception as e:
        logger.error(
            f"Ошибка при получении данных о погоде для города {
                city.name}: {e}")
        return city.name, None


async def index(request):
    logger.debug(f"Запрос index")

    @sync_to_async
    def get_user_cities(user):
        if user.is_authenticated:
            return list(
                UserCity.objects.filter(
                    user=user).select_related('city'))
        return []
    user_cities = await get_user_cities(request.user)

    tasks = [fetch_weather_data(user_city.city) for user_city in user_cities]
    results = await asyncio.gather(*tasks)

    cities_weather_data = {
        name: data for name, data in results if data is not None
    }
    user_data = {
        'user': request.user,
        "cities_weather_data": cities_weather_data}
    
    html = await sync_to_async(render)(request, 'index.html', user_data)

    return html


async def registration(request):
    form = None

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if await sync_to_async(form.is_valid)():
            user = await sync_to_async(form.save)(commit=False)
            user.set_password(form.cleaned_data['password'])
            await sync_to_async(user.save)()
            await sync_to_async(login)(request, user)
            logger.info(f"Пользователь {user.username} зарегистрирован.")
            return redirect('main:index')
    else:
        form = await sync_to_async(RegistrationForm)()

    html = await sync_to_async(render)(request, 'registration.html', {'form': form})
    return html


async def myLogin(request):
    form = None

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if await sync_to_async(form.is_valid)():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = await sync_to_async(authenticate)(request, username=username, password=password)

            if user is not None:
                await sync_to_async(login)(request, user)
                logger.info(f"Пользователь {username} вошел в систему.")
                return redirect('main:index')
            else:
                form.add_error(
                    None, "Неправильное имя пользователя или пароль")
                logger.warning(f"Неудачная попытка входа {username}.")
    else:
        form = await sync_to_async(LoginForm)()

    html = await sync_to_async(render)(request, 'login.html', {'form': form})
    return html


async def myLogout(request):
    @sync_to_async
    def get_username(request):
        return request.user.username if request.user.is_authenticated else None

    username = await get_username(request)

    await sync_to_async(logout)(request)

    logger.info(f"Пользователь {username} вышел.")
    return redirect('main:index')


@login_required
async def weather_view(request):
    temperature = None
    wind_speed = None
    pressure = None
    error = None

    if request.method == 'GET':
        latitude = request.GET.get('latitude')
        longitude = request.GET.get('longitude')

        try:
            latitude = float(request.GET.get('latitude', '').replace(',', '.'))
            longitude = float(
                request.GET.get(
                    'longitude',
                    '').replace(',', '.'))
        except ValueError:
            error = 'Пожалуйста, укажите корректные значения для широты и долготы.'
            latitude = None
            longitude = None

        if latitude is not None and longitude is not None:
            try:
                logger.info(
                    f"Получение данных о погоде для координат: {latitude}, {longitude}")
                weather_data = await get_weather_data(latitude, longitude)

                temperature = weather_data['temperature']
                wind_speed = weather_data['wind_speed']
                pressure = weather_data['pressure']

                if temperature is None:
                    error = "Не удалось получить данные о погоде."
            except Exception as e:
                logger.error(f"Ошибка при получении данных о погоде: {e}")
                error = "Произошла ошибка при получении данных о погоде."
        elif error is None:
            error = 'Пожалуйста, укажите широту и долготу.'

    user_cities = user_cities = await sync_to_async(
        lambda: list(UserCity.objects.filter(user=request.user).select_related('city'))
    )()
    cities = {user_city.city.name: user_city.city for user_city in user_cities}

    html = await sync_to_async(render)(request, 'weather.html', {
        'temperature': temperature,
        'wind_speed': wind_speed,
        'pressure': pressure,
        'error': error,
        'cities': cities,
    })

    return html


@login_required
async def add_city(request):
    form = None
    if request.method == 'POST':
        form = AddCityForm(request.POST)
        if await sync_to_async(form.is_valid)():
            city = await sync_to_async(form.save)()
            await sync_to_async(UserCity.objects.get_or_create)(user=request.user, city=city)
            logger.info(
                f"Пользователь {
                    request.user.username} добавил город: {
                    city.name}.")
            return redirect('main:index')
    else:
        form = AddCityForm()

    html = await sync_to_async(render)(request, 'add_city.html', {'form': form})
    return html


@login_required
async def delete_city(request, city_id):
    if request.method == 'GET':
        user_city = await sync_to_async(get_object_or_404)(UserCity, id=city_id, user=request.user)
        await sync_to_async(user_city.delete)()
        logger.info(
            f"Пользователь {
                request.user.username} удалил город с ID: {city_id}.")
    return redirect('main:index')


@login_required
async def city_weather(request):
    async def get_date_range_form(data, user):
        return await sync_to_async(DateRangeForm)(data, user=user)

    form = await get_date_range_form(None, request.user)
    if request.method == 'POST':
        form = await sync_to_async(DateRangeForm)(request.POST, user=request.user)
        if await sync_to_async(form.is_valid)():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            selected_cities = form.cleaned_data['cities']
            selected_parameters = form.cleaned_data['parameters']

            logger.debug(
                f"Пользователь {
                    request.user.username} запрашивает погоду для города: " f"{
                    selected_cities.city.name} с {start_date} по {end_date} для параметров: {selected_parameters}")

            try:
                hourly_dataframe = await get_weather_parameters(
                    selected_cities.city.latitude,
                    selected_cities.city.longitude,
                    start_date,
                    end_date,
                    selected_parameters
                )
                context = {
                    'form': form,
                    'hourly_dataframe': hourly_dataframe,
                }
                logger.info("Данные о погоде успешно получены.")
                return await sync_to_async(render)(request, 'city_weather.html', context)

            except Exception as e:
                logger.error(f"Ошибка при получении данных о погоде: {e}")
                form.add_error(
                    None,
                    "Произошла ошибка при получении данных о погоде. Пожалуйста, попробуйте еще раз.")

    html = await sync_to_async(render)(request, 'city_weather.html', {'form': form})
    return html


async def get_weather_data(latitude, longitude):
    logger.debug(
        f"Запрос параметров погоды для координат: ({latitude}, {longitude})")
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,wind_speed_10m,pressure_msl"
    }

    try:
        responses = await asyncio.to_thread(openmeteo.weather_api, url, params=params)

        response = responses[0]
        hourly = response.Hourly()

        latest_data = {
            "temperature": hourly.Variables(0).ValuesAsNumpy()[-1],
            "wind_speed": hourly.Variables(1).ValuesAsNumpy()[-1],
            "pressure": hourly.Variables(2).ValuesAsNumpy()[-1],
        }

        logger.debug(
            f"Данные получены для координат: {latitude}, {longitude}")
        return latest_data

    except Exception as e:
        logger.error(
            f"Ошибка при получении данных для координат {latitude}, {longitude}: {e}")
        return None


async def get_weather_parameters(
        latitude,
        longitude,
        start_date,
        end_date,
        selected_parameters):
    logger.debug(f"Запрос параметров погоды для координат: ({latitude}, {longitude}) "
                 f"с {start_date} по {end_date} для параметров: {selected_parameters}")

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": selected_parameters,
        "start_date": start_date,
        "end_date": end_date
    }

    try:
        responses = await asyncio.to_thread(openmeteo.weather_api, url, params=params)
        response = responses[0]
        hourly = response.Hourly()

        hourly_data = {"date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )}

        for i, param in enumerate(selected_parameters):
            hourly_data[param] = hourly.Variables(i).ValuesAsNumpy()

        hourly_dataframe = pd.DataFrame(data=hourly_data)
        logger.debug(f"Данные о погоде успешно получены: {hourly_dataframe}")
        return hourly_dataframe

    except Exception as e:
        logger.error(f"Ошибка при получении данных о погоде: {e}")
        raise
