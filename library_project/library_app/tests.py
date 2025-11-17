# test_dev_branch.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from library_app.models import Book, Author, Publisher, Student, Faculty

User = get_user_model()

class DevBranchTests(TestCase):
    """Тесты для DEV ветки - смешанные результаты"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='devuser',
            password='testpass123'
        )
        self.author = Author.objects.create(last_name='Dev', first_name='Author')
        self.publisher = Publisher.objects.create(name='Dev Publisher')
        self.faculty = Faculty.objects.create(name='Dev Faculty')
        self.student = Student.objects.create(
            last_name='Dev',
            first_name='Student', 
            student_id='DEV001',
            faculty=self.faculty
        )
        self.book = Book.objects.create(
            title='Dev Branch Book',
            publisher=self.publisher,
            publication_year=2023,
            page_count=200,
            price=750.00
        )
        self.book.authors.add(self.author)
    
    def test_dev_successful_operations(self):
        """Успешные операции в dev ветке"""
        self.client.login(username='devuser', password='testpass123')
        response = self.client.get(reverse('author_list'))
        self.assertEqual(response.status_code, 200)
        print("test_dev_successful_operations: Done")
    
    def test_dev_student_management(self):
        """Тест управления студентами в dev ветке"""
        self.client.login(username='devuser', password='testpass123')
        response = self.client.get(reverse('student_list'))
        self.assertEqual(response.status_code, 200)
        print("test_dev_student_management: Done")
