from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class AccountsAPITests(TestCase):
    def setUp(self):
        # Налаштування клієнта та тестового користувача
        self.client = Client()

        # URLs
        self.register_url = reverse('register')
        self.login_url = reverse('token_obtain_pair')
        self.user_info_url = reverse('user_info')

        # Створення тестового користувача
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

    # Юніт-тести
    def test_register_user_success(self):
        """Перевірка успішної реєстрації користувача"""
        data = {
            'username': 'newuser',
            'password1': 'ComplexPassword123!',
            'password2': 'ComplexPassword123!',
            'email': 'newuser@example.com',
            'first_name': 'First',
            'last_name': 'Last'
        }
        response = self.client.post(self.register_url, data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.filter(username='newuser').count(), 1)

    def test_register_invalid_email(self):
        """Перевірка реєстрації з некоректним email"""
        data = {
            'username': 'invalidemailuser',
            'password1': 'ValidPassword123!',
            'password2': 'ValidPassword123!',
            'email': 'invalidemail'
        }
        response = self.client.post(self.register_url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json()['errors'])

    def test_register_passwords_dont_match(self):
        """Перевірка реєстрації з різними паролями"""
        data = {
            'username': 'userwithwrongpasswords',
            'password1': 'Password123!',
            'password2': 'Password321!',
            'email': 'user@example.com'
        }
        response = self.client.post(self.register_url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('password2', response.json()['errors'])

    def test_register_weak_password(self):
        """Перевірка реєстрації з простим паролем"""
        data = {
            'username': 'weakpassworduser',
            'password1': '12345',
            'password2': '12345',
            'email': 'weakuser@example.com'
        }
        response = self.client.post(self.register_url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('password2', response.json()['errors'])

    def test_register_duplicate_email(self):
        """Перевірка реєстрації з уже існуючим email"""
        data = {
            'username': 'newuser',
            'password1': 'ValidPassword123!',
            'password2': 'ValidPassword123!',
            'email': 'test@example.com'  # Email вже використовується
        }
        response = self.client.post(self.register_url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json()['errors'])

    # Інтеграційні тести
    def test_login_success(self):
        """Перевірка успішної авторизації через JWT"""
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(self.login_url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())

    def test_login_invalid_credentials(self):
        """Перевірка авторизації з некоректними даними"""
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(self.login_url, data, content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertIn('detail', response.json())

    def test_protected_endpoint_no_token(self):
        """Перевірка доступу до захищеного ендпоінту без токена"""
        response = self.client.get(self.user_info_url)
        self.assertEqual(response.status_code, 401)

    def test_protected_endpoint_with_token(self):
        """Перевірка доступу до захищеного ендпоінту з токеном"""
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {self.access_token}'
        response = self.client.get(self.user_info_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['username'], 'testuser')

    # End-to-End тест
    def test_end_to_end_register_login_access(self):
        """Цикл: реєстрація -> авторизація -> доступ до захищеного ендпоінту"""
        # Реєстрація
        register_data = {
            'username': 'e2euser',
            'password1': 'ComplexPassword123!',
            'password2': 'ComplexPassword123!',
            'email': 'e2euser@example.com'
        }
        register_response = self.client.post(self.register_url, register_data, content_type='application/json')
        self.assertEqual(register_response.status_code, 201)

        # Авторизація
        login_data = {'username': 'e2euser', 'password': 'ComplexPassword123!'}
        login_response = self.client.post(self.login_url, login_data, content_type='application/json')
        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.json().get('access')

        # Доступ до захищеного ресурсу
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
        user_info_response = self.client.get(self.user_info_url)
        self.assertEqual(user_info_response.status_code, 200)
        self.assertEqual(user_info_response.json()['username'], 'e2euser')
