from django.test import TestCase, Client
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Bookmark, Category


class BookmarksAPITests(TestCase):
    def setUp(self):
        # Налаштування користувача, авторизації та тестових даних
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {self.access_token}'

        # URLs
        self.list_url = reverse('bookmark_list_api')

        # Дані для тестів
        self.category = Category.objects.create(name="Test Category")
        self.bookmark = Bookmark.objects.create(
            title="Test Bookmark", url="https://example.com", category=self.category, favorite=True
        )

    # Юніт-тест: перевірка створення закладки
    def test_create_bookmark(self):
        """Перевірка створення нової закладки"""
        data = {'title': 'New Bookmark', 'url': 'https://newexample.com', 'category_id': self.category.id}
        response = self.client.post(self.list_url, data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Bookmark.objects.count(), 2)

    # Юніт-тест: перевірка створення закладки з некоректними даними
    def test_create_bookmark_invalid_data(self):
        """Перевірка створення закладки з некоректними даними"""
        data = {'url': 'https://example.com', 'category_id': self.category.id}  # Відсутній title
        response = self.client.post(self.list_url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.json())

    # Інтеграційний тест: оновлення закладки
    def test_update_bookmark(self):
        """Позитивний сценарій оновлення закладки"""
        update_url = reverse('bookmark_detail_api', kwargs={'pk': self.bookmark.pk})
        data = {'title': 'Updated Bookmark', 'url': self.bookmark.url, 'category_id': self.category.id, 'favorite': False}
        response = self.client.put(update_url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.bookmark.refresh_from_db()
        self.assertEqual(self.bookmark.title, 'Updated Bookmark')
        self.assertFalse(self.bookmark.favorite)

    # Інтеграційний тест: спроба оновити закладку з некоректними даними
    def test_update_bookmark_invalid_data(self):
        """Негативний сценарій оновлення закладки"""
        update_url = reverse('bookmark_detail_api', kwargs={'pk': self.bookmark.pk})
        data = {'title': '', 'url': self.bookmark.url, 'category_id': self.category.id}  # Некоректний title
        response = self.client.put(update_url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.json())

    # Інтеграційний тест: видалення закладки
    def test_delete_bookmark(self):
        """Позитивний сценарій видалення закладки"""
        delete_url = reverse('bookmark_detail_api', kwargs={'pk': self.bookmark.pk})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Bookmark.objects.count(), 0)

    # Інтеграційний тест: спроба видалити неіснуючу закладку
    def test_delete_nonexistent_bookmark(self):
        """Негативний сценарій видалення закладки"""
        delete_url = reverse('bookmark_detail_api', kwargs={'pk': 999})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())

    # Інтеграційний тест: доступ до чужих закладок
    def test_access_restricted_bookmark(self):
        """Перевірка доступу до закладок, що не належать користувачеві"""
        another_user = User.objects.create_user(username='anotheruser', password='password')
        bookmark = Bookmark.objects.create(title="Other Bookmark", url="https://other.com", category=self.category)
        detail_url = reverse('bookmark_detail_api', kwargs={'pk': bookmark.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)  # Доступ дозволений для всіх (змінити за потреби)

    # Енд-то-енд тест: повний сценарій роботи із закладкою
    def test_bookmark_full_lifecycle(self):
        """Повний сценарій створення, оновлення, видалення закладки"""
        # Створення нової закладки
        create_data = {'title': 'Lifecycle Bookmark', 'url': 'https://lifecycle.com', 'category_id': self.category.id}
        create_response = self.client.post(self.list_url, create_data, content_type='application/json')
        self.assertEqual(create_response.status_code, 201)
        bookmark_id = create_response.json()['id']

        # Перевірка деталей створеної закладки
        detail_url = reverse('bookmark_detail_api', kwargs={'pk': bookmark_id})
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()['title'], 'Lifecycle Bookmark')

        # Оновлення закладки
        update_data = {'title': 'Updated Bookmark', 'url': 'https://updated-lifecycle.com', 'category_id': self.category.id}
        update_response = self.client.put(detail_url, update_data, content_type='application/json')
        self.assertEqual(update_response.status_code, 200)

        # Видалення закладки
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, 204)
