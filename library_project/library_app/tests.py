# test_feature_branch.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from library_app.models import Book, Author, Publisher

User = get_user_model()

class FeatureBranchTests(TestCase):
    """Тесты для FEATURE ветки - все тесты проходят успешно"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='featureuser',
            password='testpass123'
        )
        self.author = Author.objects.create(last_name='Тестов', first_name='Автор')
        self.publisher = Publisher.objects.create(name='Тестовое издательство')
        self.book = Book.objects.create(
            title='Тестовая книга',
            publisher=self.publisher,
            publication_year=2023,
            page_count=100,
            price=500.00
        )
        self.book.authors.add(self.author)
    
    def test_feature_book_creation(self):
        """Тест создания книги в feature ветке"""
        self.client.login(username='featureuser', password='testpass123')
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
        print("test_feature_book_creation: Done")
    
    def test_feature_home_page(self):
        """Тест главной страницы в feature ветке"""
        self.client.login(username='featureuser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        print("test_feature_home_page: Done")
    
    def test_feature_api_access(self):
        """Тест доступа к API в feature ветке"""
        self.client.login(username='featureuser', password='testpass123')
        response = self.client.get(reverse('api_book_list'))
        self.assertEqual(response.status_code, 200)
        print("test_feature_api_access: Done")
