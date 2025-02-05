from .forms import RegistrationForm, LoginForm, AddCityForm, DateRangeForm
from django.contrib.auth.models import User
from django.test import TestCase
from .models import UserCity, City
from django.utils import timezone


class RegistrationFormTest(TestCase):

    def test_valid_form(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'securepassword123'
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_duplicate_email(self):
        User.objects.create_user(
            username='existinguser',
            email='testuser@example.com',
            password='password123')
        form_data = {
            'username': 'newuser',
            'email': 'testuser@example.com',
            'password': 'securepassword123'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(
            form.errors['email'],
            ['Пользователь с таким email уже существует.'])

    def test_duplicate_username(self):
        User.objects.create_user(
            username='existinguser',
            email='existinguser@example.com',
            password='password123')
        form_data = {
            'username': 'existinguser',
            'email': 'newuser@example.com',
            'password': 'securepassword123'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertEqual(
            form.errors['username'],
            ['Пользователь с таким именем уже существует.'])

    def test_empty_fields(self):
        form_data = {
            'username': '',
            'email': '',
            'password': ''
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password', form.errors)


class LoginFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='securepassword123')

    def test_valid_form(self):
        form_data = {
            'username': 'testuser',
            'password': 'securepassword123'
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_empty_fields(self):
        form_data = {
            'username': '',
            'password': ''
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)


class AddCityFormTest(TestCase):

    def test_valid_form(self):
        form_data = {
            'name': 'Test City',
            'latitude': 45.0,
            'longitude': 90.0
        }
        form = AddCityForm(data=form_data)
        self.assertTrue(form.is_valid())
        city = form.save()
        self.assertEqual(City.objects.count(), 1)
        self.assertEqual(City.objects.get().name, 'Test City')

    def test_invalid_latitude(self):
        form_data = {
            'name': 'Test City',
            'latitude': 100.0,
            'longitude': 90.0
        }
        form = AddCityForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('latitude', form.errors)
        self.assertEqual(
            form.errors['latitude'],
            ['Широта должна быть в диапазоне от -90 до 90.'])

    def test_invalid_longitude(self):
        form_data = {
            'name': 'Test City',
            'latitude': 45.0,
            'longitude': 200.0
        }
        form = AddCityForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('longitude', form.errors)
        self.assertEqual(
            form.errors['longitude'],
            ['Долгота должна быть в диапазоне от -180 до 180.'])

    def test_empty_fields(self):
        form_data = {
            'name': '',
            'latitude': '',
            'longitude': ''
        }
        form = AddCityForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('latitude', form.errors)
        self.assertIn('longitude', form.errors)


class DateRangeFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='password123')
        self.city = City.objects.create(
            name='Test City', latitude=0.0, longitude=0.0)
        UserCity.objects.create(user=self.user, city=self.city)

    def test_valid_form(self):
        form_data = {
            'start_date': timezone.now().date() - timezone.timedelta(days=10),
            'end_date': timezone.now().date() - timezone.timedelta(days=9),
            'cities': self.city.id,
            'parameters': ['temperature_2m', 'precipitation']
        }
        form = DateRangeForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_empty_fields(self):
        form_data = {
            'start_date': '',
            'end_date': '',
            'cities': '',
            'parameters': []
        }
        form = DateRangeForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('start_date', form.errors)
        self.assertIn('end_date', form.errors)

    def test_cities_queryset(self):
        form = DateRangeForm(user=self.user)
        self.assertEqual(form.fields['cities'].queryset.count(), 1)

    def test_end_date_before_start_date(self):
        form_data = {
            'start_date': timezone.now().date() - timezone.timedelta(days=5),
            'end_date': timezone.now().date() - timezone.timedelta(days=6),
            'cities': self.city.id,
        }
        form = DateRangeForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_dates_in_future(self):
        form_data = {
            'start_date': timezone.now().date() + timezone.timedelta(days=1),
            'end_date': timezone.now().date() + timezone.timedelta(days=2),
            'cities': self.city.id,
        }
        form = DateRangeForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
