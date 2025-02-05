from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class City(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def clean(self):
        if not self.name:
            raise ValidationError('Название города обязательно.')

        if self.latitude is None:
            raise ValidationError('Широта обязательна.')
        if self.longitude is None:
            raise ValidationError('Долгота обязательна.')

        if self.latitude is not None and not (-90 <= self.latitude <= 90):
            raise ValidationError(
                'Широта должна быть в диапазоне от -90 до 90.')

        if self.longitude is not None and not (-180 <= self.longitude <= 180):
            raise ValidationError(
                'Долгота должна быть в диапазоне от -180 до 180.')

    def __str__(self):
        return self.name


class UserCity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'city')

    def __str__(self):
        return f"{self.city.name}"
