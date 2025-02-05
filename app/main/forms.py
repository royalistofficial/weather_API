from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserCity, City
from django.core.exceptions import ValidationError


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('Email обязателен.')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError('username обязателен.')
        if User.objects.filter(username=username).exists():
            raise ValidationError(
                'Пользователь с таким именем уже существует.')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise ValidationError('Пароль обязателен.')
        return password


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class AddCityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name', 'latitude', 'longitude']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'placeholder': 'Введите название города'}), 'latitude': forms.NumberInput(
                attrs={
                    'placeholder': 'Введите широту'}), 'longitude': forms.NumberInput(
                        attrs={
                            'placeholder': 'Введите долготу'}), }

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')

        if not cleaned_data.get('name'):
            self.add_error('name', 'Название города обязательно.')
        if latitude is None:
            self.add_error('latitude', 'Широта обязательна.')
        if longitude is None:
            self.add_error('longitude', 'Долгота обязательна.')

        if latitude is not None and not isinstance(latitude, (float, int)):
            self.add_error('latitude', 'Широта должна быть числом.')
        if longitude is not None and not isinstance(longitude, (float, int)):
            self.add_error('longitude', 'Долгота должна быть числом.')

        if latitude is not None and not (-90 <= latitude <= 90):
            self.add_error(
                'latitude',
                'Широта должна быть в диапазоне от -90 до 90.')

        if longitude is not None and not (-180 <= longitude <= 180):
            self.add_error(
                'longitude',
                'Долгота должна быть в диапазоне от -180 до 180.')

        return cleaned_data


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Start Date'
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='End Date'
    )
    cities = forms.ModelChoiceField(
        queryset=UserCity.objects.none(),
        label='Select City',
        required=False
    )
    parameters = forms.MultipleChoiceField(
        choices=[
            ("temperature_2m", "Температура на высоте 2м"),
            ("relative_humidity_2m", "Относительная влажность на высоте 2м"),
            ("dew_point_2m", "Точка росы на высоте 2м"),
            ("apparent_temperature", "Ощущаемая температура"),
            ("precipitation_probability", "Вероятность осадков"),
            ("precipitation", "Осадки"),
            ("rain", "Дождь"),
            ("showers", "Ливни"),
            ("snowfall", "Снегопад"),
            ("snow_depth", "Глубина снега"),
            ("weather_code", "Код погоды"),
            ("pressure_msl", "Давление на уровне моря"),
            ("surface_pressure", "Поверхностное давление"),
            ("cloud_cover", "Облачность"),
            ("cloud_cover_low", "Низкая облачность"),
            ("cloud_cover_mid", "Средняя облачность"),
            ("cloud_cover_high", "Высокая облачность"),
            ("visibility", "Видимость"),
            ("evapotranspiration", "Эвапотранспирация"),
            ("et0_fao_evapotranspiration", "Эвапотранспирация ET0 FAO"),
            ("vapour_pressure_deficit", "Дефицит парциального давления"),
            ("wind_speed_10m", "Скорость ветра на высоте 10м"),
            ("wind_speed_80m", "Скорость ветра на высоте 80м"),
            ("wind_speed_120m", "Скорость ветра на высоте 120м"),
            ("wind_speed_180m", "Скорость ветра на высоте 180м"),
            ("wind_direction_10m", "Направление ветра на высоте 10м"),
            ("wind_direction_80m", "Направление ветра на высоте 80м"),
            ("wind_direction_120m", "Направление ветра на высоте 120м"),
            ("wind_direction_180m", "Направление ветра на высоте 180м"),
            ("wind_gusts_10m", "Порывы ветра на высоте 10м"),
            ("temperature_80m", "Температура на высоте 80м"),
            ("temperature_120m", "Температура на высоте 120м"),
            ("temperature_180m", "Температура на высоте 180м"),
            ("soil_temperature_0cm", "Температура почвы на глубине 0см"),
            ("soil_temperature_6cm", "Температура почвы на глубине 6см"),
            ("soil_temperature_18cm", "Температура почвы на глубине 18см"),
            ("soil_temperature_54cm", "Температура почвы на глубине 54см"),
            ("soil_moisture_0_to_1cm", "Влажность почвы на глубине 0-1см"),
            ("soil_moisture_1_to_3cm", "Влажность почвы на глубине 1-3см"),
            ("soil_moisture_3_to_9cm", "Влажность почвы на глубине 3-9см"),
            ("soil_moisture_9_to_27cm", "Влажность почвы на глубине 9-27см"),
            ("soil_moisture_27_to_81cm", "Влажность почвы на глубине 27-81см"),
        ],
        label='Select Parameters',
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            user_cities = UserCity.objects.filter(
                user=user).select_related('city')
            self.fields['cities'].queryset = user_cities

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        today = timezone.now().date()

        if start_date is None:
            raise ValidationError('Дата начала не может быть пустой.')

        if end_date is None:
            raise ValidationError('Дата окончания не может быть пустой.')

        if start_date and end_date:
            if end_date <= start_date:
                raise ValidationError(
                    'Дата окончания должна быть позже даты начала.')

            if start_date > today or end_date > today:
                raise ValidationError('Даты должны быть до текущего числа.')

        return cleaned_data
