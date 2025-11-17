# test_dev_simple.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from library_app.models import Author, Book, Publisher, Student, Faculty

User = get_user_model()

class DevSimpleTests(TestCase):
    """Простые тесты для DEV ветки"""
    
    def setUp(self):
        # Создаем базовые тестовые данные
        self.user = User.objects.create_user(
            username='devuser',
            password='devpass123'
        )
        self.faculty = Faculty.objects.create(name='Факультет разработки')
    
    def test_dev_user_creation(self):
        """Тест создания пользователя в DEV"""
        user_count = User.objects.count()
        self.assertEqual(user_count, 1)
        print("test_dev_user_creation: Done")
    
    def test_dev_author_creation(self):
        """Тест создания автора в DEV"""
        author = Author.objects.create(
            last_name='Разработчик',
            first_name='Дев',
            middle_name='Тестович'
        )
        self.assertEqual(author.last_name, 'Разработчик')
        print("test_dev_author_creation: Done")
    
    def test_dev_book_creation(self):
        """Тест создания книги в DEV"""
        publisher = Publisher.objects.create(name='DEV Publishing')
        author = Author.objects.create(last_name='Author', first_name='Dev')
        
        book = Book.objects.create(
            title='DEV Book',
            publisher=publisher,
            publication_year=2024,
            page_count=100,
            price=999.99
        )
        book.authors.add(author)
        
        self.assertEqual(book.title, 'DEV Book')
        self.assertEqual(book.authors.count(), 1)
        print("test_dev_book_creation: Done")
    
    def test_dev_student_creation(self):
        """Тест создания студента в DEV"""
        student = Student.objects.create(
            last_name='Студентов',
            first_name='Дев',
            student_id='DEV2024',
            faculty=self.faculty
        )
        
        self.assertEqual(student.student_id, 'DEV2024')
        self.assertEqual(student.faculty.name, 'Факультет разработки')
        print("test_dev_student_creation: Done")
    
    def test_dev_multiple_books(self):
        """Тест создания нескольких книг в DEV"""
        publisher = Publisher.objects.create(name='Multi Publisher')
        
        # Создаем 3 книги
        for i in range(3):
            book = Book.objects.create(
                title=f'DEV Book {i+1}',
                publisher=publisher,
                publication_year=2024,
                page_count=100 + i*50,
                price=500.00 + i*100
            )
        
        self.assertEqual(Book.objects.count(), 3)
        print("test_dev_multiple_books: Done")
    
    def test_dev_search_books(self):
        """Тест поиска книг в DEV"""
        publisher = Publisher.objects.create(name='Search Publisher')
        book1 = Book.objects.create(
            title='Python Development',
            publisher=publisher,
            publication_year=2024,
            page_count=300,
            price=1200.00
        )
        book2 = Book.objects.create(
            title='Django Development', 
            publisher=publisher,
            publication_year=2024,
            page_count=400,
            price=1500.00
        )
        
        # Ищем книги по названию
        python_books = Book.objects.filter(title__contains='Python')
        django_books = Book.objects.filter(title__contains='Django')
        
        self.assertEqual(python_books.count(), 1)
        self.assertEqual(django_books.count(), 1)
        print("test_dev_search_books: Done")
    
    def test_dev_faculty_students(self):
        """Тест связи факультета и студентов в DEV"""
        # Создаем студентов для факультета
        for i in range(2):
            Student.objects.create(
                last_name=f'Студент{i}',
                first_name='Дев',
                student_id=f'STU{i}',
                faculty=self.faculty
            )
        
        self.assertEqual(self.faculty.students.count(), 2)
        print("test_dev_faculty_students: Done")
    
    def test_dev_book_price_calculation(self):
        """Тест расчетов с ценами книг в DEV"""
        publisher = Publisher.objects.create(name='Price Publisher')
        
        book1 = Book.objects.create(
            title='Дешевая книга',
            publisher=publisher,
            publication_year=2024,
            page_count=100,
            price=100.00
        )
        book2 = Book.objects.create(
            title='Дорогая книга',
            publisher=publisher, 
            publication_year=2024,
            page_count=500,
            price=2000.00
        )
        
        # Проверяем корректность цен
        self.assertLess(book1.price, book2.price)
        self.assertEqual(float(book1.price), 100.00)
        print("test_dev_book_price_calculation: Done")
    
    def test_dev_author_str_method(self):
        """Тест строкового представления автора в DEV"""
        author_with_middle = Author.objects.create(
            last_name='Иванов',
            first_name='Иван',
            middle_name='Иванович'
        )
        author_without_middle = Author.objects.create(
            last_name='Петров', 
            first_name='Петр'
        )
        
        self.assertEqual(str(author_with_middle), 'Иванов Иван Иванович')
        self.assertEqual(str(author_without_middle), 'Петров Петр')
        print("test_dev_author_str_method: Done")
    
    def test_dev_publisher_operations(self):
        """Тест операций с издательствами в DEV"""
        # Создаем несколько издательств
        publishers_data = [
            'DEV Publishing House',
            'Test Publishers', 
            'Development Books'
        ]
        
        for name in publishers_data:
            Publisher.objects.create(name=name)
        
        self.assertEqual(Publisher.objects.count(), 3)
        
        # Проверяем поиск
        dev_publisher = Publisher.objects.filter(name__contains='DEV').first()
        self.assertIsNotNone(dev_publisher)
        print("test_dev_publisher_operations: Done")
