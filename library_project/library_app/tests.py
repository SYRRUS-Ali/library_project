import json
from datetime import timedelta
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.admin.sites import AdminSite

from .models import (
    Author, Publisher, Book, Branch, BookInventory,
    Faculty, BookFacultyUsage, Student, Loan, LibraryBusinessError
)
from .forms import (
    AuthorForm, PublisherForm, BookForm, BranchForm,
    FacultyForm, StudentForm, LoanForm, InventoryForm
)
from .admin import (
    AuthorAdmin, PublisherAdmin, BookAdmin, BranchAdmin,
    BookInventoryAdmin, FacultyAdmin, BookFacultyUsageAdmin,
    StudentAdmin, LoanAdmin
)
from .views import is_librarian

User = get_user_model()


class ModelTests(TestCase):
    """Тесты для моделей приложения"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Создание тестовых объектов
        self.author = Author.objects.create(
            last_name='Толстой',
            first_name='Лев',
            middle_name='Николаевич'
        )
        
        self.publisher = Publisher.objects.create(
            name='Эксмо',
            address='Москва, ул. Пушкина, д. 1'
        )
        
        self.book = Book.objects.create(
            title='Война и мир',
            publisher=self.publisher,
            publication_year=1869,
            page_count=1225,
            price=1500.00
        )
        self.book.authors.add(self.author)
        
        self.branch = Branch.objects.create(
            name='Центральная библиотека',
            address='Москва, ул. Ленина, д. 1'
        )
        
        self.faculty = Faculty.objects.create(
            name='Филологический факультет',
            description='Факультет изучения языков и литературы'
        )
        
        self.student = Student.objects.create(
            last_name='Иванов',
            first_name='Иван',
            student_id='12345',
            faculty=self.faculty
        )
        
        self.inventory = BookInventory.objects.create(
            book=self.book,
            branch=self.branch,
            total_copies=10,
            available_copies=10
        )

    def test_author_creation(self):
        """Тест создания автора"""
        self.assertEqual(str(self.author), 'Толстой Лев Николаевич')
        self.assertEqual(self.author.last_name, 'Толстой')
        self.assertEqual(self.author.first_name, 'Лев')
        self.assertEqual(self.author.middle_name, 'Николаевич')
        print("test_author_creation: Done")

    def test_author_clean_validation(self):
        """Тест валидации автора"""
        # Тест с пустой фамилией
        author_invalid = Author(
            last_name='   ',
            first_name='Тест',
            middle_name='Тестович'
        )
        with self.assertRaises(ValidationError):
            author_invalid.full_clean()
        print("test_author_clean_validation: Done")

    def test_publisher_creation(self):
        """Тест создания издательства"""
        self.assertEqual(str(self.publisher), 'Эксмо')
        self.assertEqual(self.publisher.name, 'Эксмо')
        print("test_publisher_creation: Done")

    def test_book_creation(self):
        """Тест создания книги"""
        self.assertEqual(str(self.book), 'Война и мир (1869)')
        self.assertEqual(self.book.title, 'Война и мир')
        self.assertEqual(self.book.publication_year, 1869)
        self.assertEqual(self.book.page_count, 1225)
        self.assertIn(self.author, self.book.authors.all())
        print("test_book_creation: Done")

    def test_book_clean_validation(self):
        """Тест валидации книги"""
        # Тест с неверным годом издания
        book_invalid = Book(
            title='Тестовая книга',
            publisher=self.publisher,
            publication_year=500,  # Неверный год
            page_count=100,
            price=500.00
        )
        with self.assertRaises(ValidationError):
            book_invalid.full_clean()
        print("test_book_clean_validation: Done")

    def test_branch_creation(self):
        """Тест создания филиала"""
        self.assertEqual(str(self.branch), 'Центральная библиотека')
        self.assertEqual(self.branch.name, 'Центральная библиотека')
        print("test_branch_creation: Done")

    def test_faculty_creation(self):
        """Тест создания факультета"""
        self.assertEqual(str(self.faculty), 'Филологический факультет')
        print("test_faculty_creation: Done")

    def test_student_creation(self):
        """Тест создания студента"""
        self.assertEqual(str(self.student), 'Иванов Иван (12345)')
        self.assertEqual(self.student.get_full_name(), 'Иванов Иван')
        print("test_student_creation: Done")

    def test_inventory_creation(self):
        """Тест создания инвентаря"""
        expected_str = f'Война и мир в Центральная библиотека: 10/10'
        self.assertEqual(str(self.inventory), expected_str)
        self.assertEqual(self.inventory.total_copies, 10)
        self.assertEqual(self.inventory.available_copies, 10)
        print("test_inventory_creation: Done")

    def test_inventory_clean_validation(self):
        """Тест валидации инвентаря"""
        # Тест с доступными экземплярами больше общего количества
        inventory_invalid = BookInventory(
            book=self.book,
            branch=self.branch,
            total_copies=5,
            available_copies=10  # Больше общего количества
        )
        with self.assertRaises(ValidationError):
            inventory_invalid.full_clean()
        print("test_inventory_clean_validation: Done")

    def test_loan_creation_and_business_logic(self):
        """Тест создания выдачи и бизнес-логики"""
        # Создание выдачи
        loan = Loan.objects.create(
            student=self.student,
            book=self.book,
            branch=self.branch,
            created_by=self.user
        )
        
        # Проверка, что количество доступных экземпляров уменьшилось
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.available_copies, 9)
        
        # Возврат книги
        loan.is_returned = True
        loan.save()
        
        # Проверка, что количество доступных экземпляров увеличилось
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.available_copies, 10)
        self.assertIsNotNone(loan.return_date)
        print("test_loan_creation_and_business_logic: Done")

    def test_book_faculty_usage_creation(self):
        """Тест создания использования книги факультетом"""
        usage = BookFacultyUsage.objects.create(
            book=self.book,
            branch=self.branch,
            faculty=self.faculty
        )
        
        expected_str = f'Филологический факультет использует Война и мир в Центральная библиотека'
        self.assertEqual(str(usage), expected_str)
        print("test_book_faculty_usage_creation: Done")

    def test_book_faculty_usage_validation(self):
        """Тест валидации использования книги факультетом"""
        # Создаем использование с книгой, которой нет в инвентаре
        another_book = Book.objects.create(
            title='Другая книга',
            publication_year=2000,
            page_count=100,
            price=500.00
        )
        
        usage_invalid = BookFacultyUsage(
            book=another_book,  # Этой книги нет в инвентаре филиала
            branch=self.branch,
            faculty=self.faculty
        )
        
        with self.assertRaises(ValidationError):
            usage_invalid.full_clean()
        print("test_book_faculty_usage_validation: Done")


class FormTests(TestCase):
    """Тесты для форм приложения"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.author = Author.objects.create(
            last_name='Достоевский',
            first_name='Федор',
            middle_name='Михайлович'
        )
        
        self.publisher = Publisher.objects.create(
            name='АСТ',
            address='Москва'
        )
        
        self.book = Book.objects.create(
            title='Преступление и наказание',
            publisher=self.publisher,
            publication_year=1866,
            page_count=671,
            price=1200.00
        )
        self.book.authors.add(self.author)
        
        self.branch = Branch.objects.create(
            name='Главный филиал',
            address='Санкт-Петербург'
        )
        
        self.faculty = Faculty.objects.create(
            name='Юридический факультет'
        )
        
        self.student = Student.objects.create(
            last_name='Петров',
            first_name='Петр',
            student_id='54321',
            faculty=self.faculty
        )
        
        self.inventory = BookInventory.objects.create(
            book=self.book,
            branch=self.branch,
            total_copies=5,
            available_copies=5
        )

    def test_author_form_valid(self):
        """Тест валидной формы автора"""
        form_data = {
            'last_name': 'Пушкин',
            'first_name': 'Александр',
            'middle_name': 'Сергеевич'
        }
        form = AuthorForm(data=form_data)
        self.assertTrue(form.is_valid())
        print("test_author_form_valid: Done")

    def test_author_form_invalid(self):
        """Тест невалидной формы автора"""
        form_data = {
            'last_name': '',  # Пустая фамилия
            'first_name': 'Александр',
            'middle_name': 'Сергеевич'
        }
        form = AuthorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors)
        print("test_author_form_invalid: Done")

    def test_book_form_valid(self):
        """Тест валидной формы книги"""
        form_data = {
            'title': 'Евгений Онегин',
            'authors': [self.author.id],
            'publisher': self.publisher.id,
            'publication_year': 1833,
            'page_count': 320,
            'illustration_count': 10,
            'price': 800.00
        }
        form = BookForm(data=form_data)
        self.assertTrue(form.is_valid())
        print("test_book_form_valid: Done")

    def test_loan_form_valid(self):
        """Тест валидной формы выдачи"""
        form_data = {
            'student': self.student.id,
            'book': self.book.id,
            'branch': self.branch.id
        }
        form = LoanForm(data=form_data)
        self.assertTrue(form.is_valid())
        print("test_loan_form_valid: Done")

    def test_loan_form_no_inventory_validation(self):
        """Тест валидации выдачи при отсутствии инвентаря"""
        # Создаем книгу без инвентаря
        another_book = Book.objects.create(
            title='Книга без инвентаря',
            publication_year=2000,
            page_count=100,
            price=500.00
        )
        
        form_data = {
            'student': self.student.id,
            'book': another_book.id,
            'branch': self.branch.id
        }
        form = LoanForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        print("test_loan_form_no_inventory_validation: Done")

    def test_inventory_form_valid(self):
        """Тест валидной формы инвентаря"""
        # Create a new book and branch to avoid unique constraint issues
        new_book = Book.objects.create(
            title='Новая книга для теста инвентаря',
            publisher=self.publisher,
            publication_year=2023,
            page_count=200,
            price=800.00
        )
        new_book.authors.add(self.author)

        new_branch = Branch.objects.create(
            name='Новый филиал для теста',
            address='Тестовый адрес'
        )

        form_data = {
            'book': new_book.id,
            'branch': new_branch.id,
            'total_copies': 15,
            'available_copies': 15
        }
        form = InventoryForm(data=form_data)

        # Debug if needed
        if not form.is_valid():
            print(f"Inventory form errors: {form.errors}")

        self.assertTrue(form.is_valid())

        # Also test that the form saves correctly
        if form.is_valid():
            inventory = form.save()
            self.assertEqual(inventory.total_copies, 15)
            self.assertEqual(inventory.available_copies, 15)

        print("test_inventory_form_valid: Done")

    def test_inventory_form_invalid_copies(self):
        """Тест невалидной формы инвентаря с неверным количеством копий"""
        form_data = {
            'book': self.book.id,
            'branch': self.branch.id,
            'total_copies': 5,
            'available_copies': 10  # Больше общего количества
        }
        form = InventoryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        print("test_inventory_form_invalid_copies: Done")


class ViewTests(TestCase):
    """Тесты для представлений приложения"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
        self.factory = RequestFactory()
        
        # Создание пользователей
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        self.librarian_user = User.objects.create_user(
            username='librarian',
            password='librarianpass123',
            email='librarian@example.com'
        )
        
        # Создание группы библиотекарей
        librarian_group, created = Group.objects.get_or_create(name='Librarians')
        self.librarian_user.groups.add(librarian_group)
        
        # Создание тестовых объектов
        self.author = Author.objects.create(
            last_name='Толстой',
            first_name='Лев'
        )
        
        self.publisher = Publisher.objects.create(
            name='Эксмо',
            address='Москва'
        )
        
        self.book = Book.objects.create(
            title='Война и мир',
            publisher=self.publisher,
            publication_year=1869,
            page_count=1225,
            price=1500.00
        )
        self.book.authors.add(self.author)
        
        self.branch = Branch.objects.create(
            name='Центральная библиотека',
            address='Москва'
        )
        
        self.faculty = Faculty.objects.create(
            name='Филологический факультет'
        )
        
        self.student = Student.objects.create(
            last_name='Иванов',
            first_name='Иван',
            student_id='12345',
            faculty=self.faculty
        )
        
        self.inventory = BookInventory.objects.create(
            book=self.book,
            branch=self.branch,
            total_copies=10,
            available_copies=10
        )

    def test_home_view_authenticated(self):
        """Тест главной страницы для аутентифицированного пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        print("test_home_view_authenticated: Done")

    def test_home_view_unauthenticated(self):
        """Тест главной страницы для неаутентифицированного пользователя"""
        response = self.client.get(reverse('home'))
        # Проверяем любой возможный статус
        self.assertIn(response.status_code, [200, 302])
        print("test_home_view_unauthenticated: Done")

    def test_book_list_view(self):
        """Тест списка книг"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
        print("test_book_list_view: Done")

    def test_book_list_search(self):
        """Тест поиска в списке книг"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('book_list') + '?search=война')
        self.assertEqual(response.status_code, 200)
        print("test_book_list_search: Done")

    def test_book_detail_view(self):
        """Тест детальной страницы книги"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('book_detail', args=[self.book.id]))
        self.assertEqual(response.status_code, 200)
        print("test_book_detail_view: Done")

    def test_author_list_view(self):
        """Тест списка авторов"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('author_list'))
        self.assertEqual(response.status_code, 200)
        print("test_author_list_view: Done")

    def test_student_list_view(self):
        """Тест списка студентов"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('student_list'))
        self.assertEqual(response.status_code, 200)
        print("test_student_list_view: Done")

    def test_loan_list_view(self):
        """Тест списка выдач"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('loan_list'))
        self.assertEqual(response.status_code, 200)
        print("test_loan_list_view: Done")

    def test_book_create_view_permission(self):
        """Тест разрешений для создания книги"""
        # Обычный пользователь не должен иметь доступ
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('book_add'))
        self.assertEqual(response.status_code, 403)  # Forbidden
        print("test_book_create_view_permission: Done")

    def test_is_librarian_function(self):
        """Тест функции проверки библиотекаря"""
        # Обычный пользователь
        self.assertFalse(is_librarian(self.user))
        
        # Библиотекарь
        self.assertTrue(is_librarian(self.librarian_user))
        
        # Суперпользователь
        superuser = User.objects.create_superuser(
            username='superuser',
            password='superpass123',
            email='super@example.com'
        )
        self.assertTrue(is_librarian(superuser))
        print("test_is_librarian_function: Done")

    def test_api_book_list(self):
        """Тест API списка книг"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('api_book_list'))
        self.assertEqual(response.status_code, 200)
        print("test_api_book_list: Done")

    def test_api_book_detail(self):
        """Тест API детальной информации о книге"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('api_book_detail', args=[self.book.id]))
        self.assertEqual(response.status_code, 200)
        print("test_api_book_detail: Done")

    def test_api_book_detail_not_found(self):
        """Тест API для несуществующей книги"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('api_book_detail', args=[999]))  # Несуществующий ID
        self.assertEqual(response.status_code, 404)
        print("test_api_book_detail_not_found: Done")

    def test_api_inventory_list(self):
        """Тест API списка инвентаря"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('api_inventory_list'))
        self.assertEqual(response.status_code, 200)
        print("test_api_inventory_list: Done")

    def test_login_view(self):
        """Тест представления входа"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        print("test_login_view: Done")


class AdminTests(TestCase):
    """Тесты для админ-панели"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.site = AdminSite()
        
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@example.com'
        )
        
        self.author = Author.objects.create(
            last_name='Толстой',
            first_name='Лев'
        )
        
        self.publisher = Publisher.objects.create(
            name='Эксмо',
            address='Москва'
        )
        
        self.book = Book.objects.create(
            title='Война и мир',
            publisher=self.publisher,
            publication_year=1869,
            page_count=1225,
            price=1500.00
        )
        
        self.branch = Branch.objects.create(
            name='Центральная библиотека',
            address='Москва'
        )
        
        self.faculty = Faculty.objects.create(
            name='Филологический факультет'
        )
        
        self.student = Student.objects.create(
            last_name='Иванов',
            first_name='Иван',
            student_id='12345',
            faculty=self.faculty
        )

    def test_author_admin(self):
        """Тест админ-класса Author"""
        author_admin = AuthorAdmin(Author, self.site)
        
        # Проверка list_display
        self.assertEqual(author_admin.list_display, ('last_name', 'first_name', 'middle_name'))
        print("test_author_admin: Done")

    def test_book_admin(self):
        """Тест админ-класса Book"""
        book_admin = BookAdmin(Book, self.site)
        
        self.assertEqual(book_admin.list_display, 
                        ('title', 'publication_year', 'publisher', 'page_count', 'price'))
        print("test_book_admin: Done")

    def test_loan_admin(self):
        """Тест админ-класса Loan"""
        loan_admin = LoanAdmin(Loan, self.site)
        
        self.assertEqual(loan_admin.list_display, 
                        ('student', 'book', 'branch', 'issue_date', 'return_date', 'is_returned'))
        print("test_loan_admin: Done")

    def test_student_admin(self):
        """Тест админ-класса Student"""
        student_admin = StudentAdmin(Student, self.site)
        
        self.assertEqual(student_admin.list_display, 
                        ('last_name', 'first_name', 'student_id', 'faculty', 'created_at'))
        print("test_student_admin: Done")

    def test_inventory_admin(self):
        """Тест админ-класса BookInventory"""
        inventory_admin = BookInventoryAdmin(BookInventory, self.site)
        
        self.assertEqual(inventory_admin.list_display, 
                        ('book', 'branch', 'total_copies', 'available_copies', 'last_updated'))
        print("test_inventory_admin: Done")


class IntegrationTests(TestCase):
    """Интеграционные тесты"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
        
        # Создание суперпользователя
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@example.com'
        )
        
        # Создание тестовых данных
        self.author = Author.objects.create(
            last_name='Толстой',
            first_name='Лев'
        )
        
        self.publisher = Publisher.objects.create(
            name='Эксмо',
            address='Москва'
        )
        
        self.book = Book.objects.create(
            title='Война и мир',
            publisher=self.publisher,
            publication_year=1869,
            page_count=1225,
            price=1500.00
        )
        self.book.authors.add(self.author)
        
        self.branch = Branch.objects.create(
            name='Центральная библиотека',
            address='Москва'
        )
        
        self.faculty = Faculty.objects.create(
            name='Филологический факультет'
        )
        
        self.student = Student.objects.create(
            last_name='Иванов',
            first_name='Иван',
            student_id='12345',
            faculty=self.faculty
        )
        
        self.inventory = BookInventory.objects.create(
            book=self.book,
            branch=self.branch,
            total_copies=10,
            available_copies=10
        )

    def test_complete_loan_workflow(self):
        """Тест полного рабочего процесса выдачи книги"""
        # Вход в систему
        self.client.login(username='admin', password='adminpass123')
        
        # Создание выдачи
        response = self.client.post(reverse('loan_add'), {
            'student': self.student.id,
            'book': self.book.id,
            'branch': self.branch.id
        })
        
        # Проверка успешного создания
        self.assertEqual(response.status_code, 302)  # Редирект после успешного создания
        print("test_complete_loan_workflow: Done")

    def test_book_creation_workflow(self):
        """Тест рабочего процесса создания книги"""
        self.client.login(username='admin', password='adminpass123')
        
        # Создание новой книги
        response = self.client.post(reverse('book_add'), {
            'title': 'Анна Каренина',
            'authors': [self.author.id],
            'publisher': self.publisher.id,
            'publication_year': 1877,
            'page_count': 864,
            'illustration_count': 5,
            'price': 1300.00
        })
        
        self.assertEqual(response.status_code, 302)  # Редирект после успешного создания
        print("test_book_creation_workflow: Done")

    def test_inventory_management_workflow(self):
        """Тест рабочего процесса управления инвентарем"""
        self.client.login(username='admin', password='adminpass123')
        
        # Обновление инвентаря
        response = self.client.post(reverse('inventory_edit', args=[self.inventory.id]), {
            'book': self.book.id,
            'branch': self.branch.id,
            'total_copies': 15,
            'available_copies': 15
        })
        
        self.assertEqual(response.status_code, 302)  # Редирект после успешного обновления
        print("test_inventory_management_workflow: Done")


class ErrorHandlingTests(TestCase):
    """Тесты обработки ошибок"""

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_403_error_handler(self):
        """Тест обработчика ошибки 403"""
        response = self.client.get('/403/')
        self.assertEqual(response.status_code, 200)
        print("test_403_error_handler: Done")

    def test_404_error_handler(self):
        """Тест обработчика ошибки 404"""
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)
        print("test_404_error_handler: Done")

    def test_custom_403_view(self):
        """Тест кастомного представления 403"""
        from .views import handler403
        request = self.factory.get('/')
        response = handler403(request, Exception())
        self.assertEqual(response.status_code, 403)
        print("test_custom_403_view: Done")

    def test_custom_404_view(self):
        """Тест кастомного представления 404"""
        from .views import handler404
        request = self.factory.get('/')
        response = handler404(request, Exception())
        self.assertEqual(response.status_code, 404)
        print("test_custom_404_view: Done")


class EdgeCaseTests(TestCase):
    """Тесты для граничных случаев"""

    def setUp(self):
        self.author = Author.objects.create(
            last_name='Тестов',
            first_name='Автор'
        )
        
        self.publisher = Publisher.objects.create(
            name='Тестовое издательство'
        )

    def test_book_with_minimal_data(self):
        """Тест создания книги с минимальными данными"""
        book = Book.objects.create(
            title='Минимальная книга',
            publication_year=2000,
            page_count=1,
            price=0.01  # Минимальная цена
        )
        self.assertEqual(book.title, 'Минимальная книга')
        self.assertEqual(book.page_count, 1)
        print("test_book_with_minimal_data: Done")

    def test_book_with_maximum_data(self):
        """Тест создания книги с максимальными данными"""
        book = Book.objects.create(
            title='К' * 300,  # Максимальная длина
            publisher=self.publisher,
            publication_year=2100,  # Максимальный год
            page_count=99999,  # Большое количество страниц
            price=9999999.99,  # Большая цена
            illustration_count=99999
        )
        book.authors.add(self.author)
        
        self.assertEqual(len(book.title), 300)
        self.assertEqual(book.publication_year, 2100)
        print("test_book_with_maximum_data: Done")

    def test_student_with_special_characters(self):
        """Тест создания студента со специальными символами"""
        faculty = Faculty.objects.create(name='Факультет')
        
        student = Student.objects.create(
            last_name='Иванов-Петров',
            first_name='Мария-Анна',
            student_id='ABC-123/45',
            faculty=faculty
        )
        
        self.assertEqual(student.last_name, 'Иванов-Петров')
        self.assertEqual(student.first_name, 'Мария-Анна')
        print("test_student_with_special_characters: Done")
