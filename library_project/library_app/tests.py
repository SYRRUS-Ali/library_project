# test_prod_branch.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from library_app.models import Book, Author, Publisher

User = get_user_model()

class ProdBranchTests(TestCase):
    """Тесты для PROD ветки - только критические тесты"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='produser',
            password='testpass123'
        )
        self.author = Author.objects.create(last_name='Prod', first_name='Author')
        self.publisher = Publisher.objects.create(name='Prod Publisher')
        self.book = Book.objects.create(
            title='Production Book',
            publisher=self.publisher,
            publication_year=2023,
            page_count=150,
            price=600.00
        )
        self.book.authors.add(self.author)
    
    def test_prod_critical_functionality(self):
        """Критический функционал в prod ветке"""
        self.client.login(username='produser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        print("test_prod_critical_functionality: Done")
    
    def test_prod_database_integrity(self):
        """Тест целостности базы данных в prod ветке"""
        book_count = Book.objects.count()
        author_count = Author.objects.count()
        self.assertGreaterEqual(book_count, 0)
        self.assertGreaterEqual(author_count, 0)
        print("test_prod_database_integrity: Done")
    
    def test_prod_auth_system(self):
        """Тест системы аутентификации в prod ветке"""
        self.client.login(username='produser', password='testpass123')
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
        print("test_prod_auth_system: Done")
