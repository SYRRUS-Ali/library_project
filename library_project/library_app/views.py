from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.db import models
from django.db.models import Q, Count, Sum, Avg
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError
from django.utils import timezone
from django.core.exceptions import PermissionDenied, ValidationError
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import timedelta

from .models import (
    Author, Publisher, Book, Branch, BookInventory, 
    Faculty, BookFacultyUsage, Student, Loan
)
from .forms import (
    BookForm, AuthorForm, PublisherForm, BranchForm, 
    FacultyForm, StudentForm, LoanForm, InventoryForm,
    BookFacultyUsageForm
)

def badFunction():
    x = 1
    y = 2
    print(X + y)  # خطأ: X غير معرّف


# Custom exception handlers
def handler403(request, exception):
    return render(request, 'library_app/errors/403.html', status=403)

def handler404(request, exception):
    return render(request, 'library_app/errors/404.html', status=404)

def handler500(request):
    return render(request, 'library_app/errors/500.html', status=500)

# Utility functions
def is_librarian(user):
    return user.is_authenticated and (user.is_staff or user.groups.filter(name='Librarians').exists())

def librarian_required(view_func):
    decorated_view_func = login_required(user_passes_test(
        is_librarian, 
        login_url='login',
        redirect_field_name=None
    )(view_func))
    return decorated_view_func

# Authentication Views
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'library_app/auth/register.html', {
        'form': form,
        'title': 'Регистрация'
    })

def home(request):
    """Главная страница с общей статистикой"""
    total_books = Book.objects.count()
    total_students = Student.objects.count()
    active_loans = Loan.objects.filter(is_returned=False).count()
    total_branches = Branch.objects.count()
    
    recent_books = Book.objects.order_by('-created_at')[:5]
    recent_loans = Loan.objects.select_related('student', 'book').order_by('-issue_date')[:5]
    
    context = {
        'title': 'Главная - Библиотечная система',
        'total_books': total_books,
        'total_students': total_students,
        'active_loans': active_loans,
        'total_branches': total_branches,
        'recent_books': recent_books,
        'recent_loans': recent_loans,
    }
    return render(request, 'library_app/home.html', context)

# Book Views
class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'library_app/books/book_list.html'
    context_object_name = 'books'
    paginate_by = 20
    ordering = ['title']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        year_filter = self.request.GET.get('year', '')
        publisher_filter = self.request.GET.get('publisher', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(authors__last_name__icontains=search_query) |
                Q(authors__first_name__icontains=search_query)
            ).distinct()
        
        if year_filter:
            queryset = queryset.filter(publication_year=year_filter)
        
        if publisher_filter:
            queryset = queryset.filter(publisher__id=publisher_filter)
        
        return queryset.select_related('publisher').prefetch_related('authors')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список книг'
        context['publishers'] = Publisher.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['year_filter'] = self.request.GET.get('year', '')
        context['publisher_filter'] = self.request.GET.get('publisher', '')
        return context

class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'library_app/books/book_detail.html'
    context_object_name = 'book'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Книга: {self.object.title}'
        context['inventory'] = BookInventory.objects.filter(book=self.object).select_related('branch')
        context['faculty_usage'] = BookFacultyUsage.objects.filter(book=self.object).select_related('faculty', 'branch')
        context['loan_history'] = Loan.objects.filter(book=self.object).select_related('student', 'branch')[:10]
        return context

class BookCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'library_app/books/book_form.html'
    success_url = reverse_lazy('book_list')
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить книгу'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Книга успешно добавлена!')
        return super().form_valid(form)

class BookUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'library_app/books/book_form.html'
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('book_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактировать: {self.object.title}'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Книга успешно обновлена!')
        return super().form_valid(form)

class BookDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Book
    template_name = 'library_app/books/book_confirm_delete.html'
    success_url = reverse_lazy('book_list')
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удалить книгу: {self.object.title}'
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Книга успешно удалена!')
        return super().delete(request, *args, **kwargs)

@login_required
def book_usage(request, pk):
    """Статистика использования книги по факультетам"""
    book = get_object_or_404(Book, pk=pk)
    
    # Get usage statistics
    usage_stats = BookFacultyUsage.objects.filter(book=book).values(
        'faculty__name'
    ).annotate(
        usage_count=Count('id')
    ).order_by('-usage_count')
    
    # Calculate total usage and percentages
    total_usage = sum(stat['usage_count'] for stat in usage_stats)
    
    # Add percentage to each stat
    for stat in usage_stats:
        if total_usage > 0:
            stat['percentage'] = (stat['usage_count'] / total_usage) * 100
        else:
            stat['percentage'] = 0
    
    # Get most used faculty
    most_used_faculty = usage_stats[0]['faculty__name'] if usage_stats else None
    
    context = {
        'title': f'Использование книги: {book.title}',
        'book': book,
        'usage_stats': usage_stats,
        'total_usage': total_usage,
        'most_used_faculty': most_used_faculty,
    }
    return render(request, 'library_app/books/book_usage.html', context)

# Author Views
class AuthorListView(LoginRequiredMixin, ListView):
    model = Author
    template_name = 'library_app/authors/author_list.html'
    context_object_name = 'authors'
    paginate_by = 20
    ordering = ['last_name', 'first_name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(last_name__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(middle_name__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список авторов'
        context['search_query'] = self.request.GET.get('search', '')
        return context

class AuthorDetailView(LoginRequiredMixin, DetailView):
    model = Author
    template_name = 'library_app/authors/author_detail.html'
    context_object_name = 'author'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Автор: {self.object}'
        
        # Calculate additional statistics
        books = self.object.books.all()
        context['total_pages'] = sum(book.page_count for book in books)
        context['average_pages'] = context['total_pages'] / len(books) if books else 0
        
        # Find largest and newest books
        if books:
            context['largest_book'] = max(books, key=lambda x: x.page_count)
            context['newest_book'] = max(books, key=lambda x: x.publication_year)
        else:
            context['largest_book'] = None
            context['newest_book'] = None
        
        return context

class AuthorCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Author
    form_class = AuthorForm
    template_name = 'library_app/authors/author_form.html'
    success_url = reverse_lazy('author_list')
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить автора'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Автор успешно добавлен!')
        return super().form_valid(form)

class AuthorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Author
    form_class = AuthorForm
    template_name = 'library_app/authors/author_form.html'
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('author_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактировать автора: {self.object}'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Автор успешно обновлен!')
        return super().form_valid(form)

class AuthorDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Author
    template_name = 'library_app/authors/author_confirm_delete.html'
    success_url = reverse_lazy('author_list')
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удалить автора: {self.object}'
        context['books_count'] = self.object.books.count()
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Автор успешно удален!')
        return super().delete(request, *args, **kwargs)

# Publisher Views (similar pattern as Author views)
class PublisherListView(LoginRequiredMixin, ListView):
    model = Publisher
    template_name = 'library_app/publishers/publisher_list.html'
    context_object_name = 'publishers'
    paginate_by = 20
    ordering = ['name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список издательств'
        context['search_query'] = self.request.GET.get('search', '')
        return context

class PublisherDetailView(LoginRequiredMixin, DetailView):
    model = Publisher
    template_name = 'library_app/publishers/publisher_detail.html'
    context_object_name = 'publisher'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Издательство: {self.object.name}'
        context['books'] = self.object.book_set.all().select_related('publisher')
        return context

class PublisherCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Publisher
    form_class = PublisherForm
    template_name = 'library_app/publishers/publisher_form.html'
    success_url = reverse_lazy('publisher_list')
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить издательство'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Издательство успешно добавлено!')
        return super().form_valid(form)

class PublisherUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Publisher
    form_class = PublisherForm
    template_name = 'library_app/publishers/publisher_form.html'
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('publisher_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактировать издательство: {self.object.name}'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Издательство успешно обновлено!')
        return super().form_valid(form)

class PublisherDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Publisher
    template_name = 'library_app/publishers/publisher_confirm_delete.html'
    success_url = reverse_lazy('publisher_list')
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удалить издательство: {self.object.name}'
        context['books_count'] = self.object.book_set.count()
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Издательство успешно удалено!')
        return super().delete(request, *args, **kwargs)

# Branch Views
class BranchListView(LoginRequiredMixin, ListView):
    model = Branch
    template_name = 'library_app/branches/branch_list.html'
    context_object_name = 'branches'
    ordering = ['name']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список филиалов'
        return context

class BranchDetailView(LoginRequiredMixin, DetailView):
    model = Branch
    template_name = 'library_app/branches/branch_detail.html'
    context_object_name = 'branch'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Филиал: {self.object.name}'
        context['inventory'] = BookInventory.objects.filter(branch=self.object).select_related('book')
        context['active_loans'] = Loan.objects.filter(branch=self.object, is_returned=False).count()
        return context

class BranchCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Branch
    form_class = BranchForm
    template_name = 'library_app/branches/branch_form.html'
    success_url = reverse_lazy('branch_list')
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить филиал'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Филиал успешно добавлен!')
        return super().form_valid(form)

class BranchUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Branch
    form_class = BranchForm
    template_name = 'library_app/branches/branch_form.html'
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('branch_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактировать филиал: {self.object.name}'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Филиал успешно обновлен!')
        return super().form_valid(form)

class BranchDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Branch
    template_name = 'library_app/branches/branch_confirm_delete.html'
    success_url = reverse_lazy('branch_list')
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удалить филиал: {self.object.name}'
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Филиал успешно удален!')
        return super().delete(request, *args, **kwargs)

# Faculty Views
class FacultyListView(LoginRequiredMixin, ListView):
    model = Faculty
    template_name = 'library_app/faculties/faculty_list.html'
    context_object_name = 'faculties'
    ordering = ['name']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список факультетов'
        return context

class FacultyDetailView(LoginRequiredMixin, DetailView):
    model = Faculty
    template_name = 'library_app/faculties/faculty_detail.html'
    context_object_name = 'faculty'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Факультет: {self.object.name}'
        context['students_count'] = self.object.students.count()
        context['book_usage'] = BookFacultyUsage.objects.filter(faculty=self.object).select_related('book', 'branch')
        return context

class FacultyCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Faculty
    form_class = FacultyForm
    template_name = 'library_app/faculties/faculty_form.html'
    success_url = reverse_lazy('faculty_list')
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить факультет'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Факультет успешно добавлен!')
        return super().form_valid(form)

class FacultyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Faculty
    form_class = FacultyForm
    template_name = 'library_app/faculties/faculty_form.html'
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('faculty_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактировать факультет: {self.object.name}'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Факультет успешно обновлен!')
        return super().form_valid(form)

class FacultyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Faculty
    template_name = 'library_app/faculties/faculty_confirm_delete.html'
    success_url = reverse_lazy('faculty_list')
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удалить факультет: {self.object.name}'
        context['students_count'] = self.object.students.count()
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Факультет успешно удален!')
        return super().delete(request, *args, **kwargs)

# Student Views
class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'library_app/students/student_list.html'
    context_object_name = 'students'
    paginate_by = 20
    ordering = ['last_name', 'first_name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        faculty_filter = self.request.GET.get('faculty', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(last_name__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(student_id__icontains=search_query)
            )
        
        if faculty_filter:
            queryset = queryset.filter(faculty__id=faculty_filter)
        
        return queryset.select_related('faculty')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список студентов'
        context['faculties'] = Faculty.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['faculty_filter'] = self.request.GET.get('faculty', '')
        return context

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'library_app/students/student_detail.html'
    context_object_name = 'student'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Студент: {self.object.get_full_name()}'
        context['active_loans'] = Loan.objects.filter(student=self.object, is_returned=False).select_related('book', 'branch')
        context['loan_history'] = Loan.objects.filter(student=self.object).select_related('book', 'branch')[:10]
        return context

class StudentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'library_app/students/student_form.html'
    success_url = reverse_lazy('student_list')
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить студента'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Студент успешно добавлен!')
        return super().form_valid(form)

class StudentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'library_app/students/student_form.html'
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('student_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактировать студента: {self.object.get_full_name()}'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Студент успешно обновлен!')
        return super().form_valid(form)

class StudentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Student
    template_name = 'library_app/students/student_confirm_delete.html'
    success_url = reverse_lazy('student_list')
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удалить студента: {self.object.get_full_name()}'
        context['loans_count'] = self.object.loans.count()
        return context
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Студент успешно удален!')
        return super().delete(request, *args, **kwargs)

# Loan Views
class LoanListView(LoginRequiredMixin, ListView):
    model = Loan
    template_name = 'library_app/loans/loan_list.html'
    context_object_name = 'loans'
    paginate_by = 20
    ordering = ['-issue_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.GET.get('status', '')
        branch_filter = self.request.GET.get('branch', '')
        
        if status_filter == 'active':
            queryset = queryset.filter(is_returned=False)
        elif status_filter == 'returned':
            queryset = queryset.filter(is_returned=True)
        
        if branch_filter:
            queryset = queryset.filter(branch__id=branch_filter)
        
        return queryset.select_related('student', 'book', 'branch', 'created_by')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список выдач'
        context['branches'] = Branch.objects.all()
        context['status_filter'] = self.request.GET.get('status', '')
        context['branch_filter'] = self.request.GET.get('branch', '')
        context['active_loans_count'] = Loan.objects.filter(is_returned=False).count()
        return context

class LoanDetailView(LoginRequiredMixin, DetailView):
    model = Loan
    template_name = 'library_app/loans/loan_detail.html'
    context_object_name = 'loan'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Выдача: {self.object}'
        
        # Calculate overdue status
        if not self.object.is_returned:
            overdue_days = (timezone.now() - self.object.issue_date).days
            context['is_overdue'] = overdue_days > 30
            context['overdue_days'] = overdue_days - 30 if overdue_days > 30 else 0
        
        return context

class LoanCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Loan
    form_class = LoanForm
    template_name = 'library_app/loans/loan_form.html'
    success_url = reverse_lazy('loan_list')
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Выдать книгу'
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Книга успешно выдана!')
            return response
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Ошибка при выдаче книги. Проверьте введенные данные.')
        return super().form_invalid(form)

class LoanReturnView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Loan
    fields = []  # No fields needed for return
    template_name = 'library_app/loans/loan_return.html'
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('loan_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Возврат книги: {self.object}'
        return context
    
    def form_valid(self, form):
        self.object.is_returned = True
        self.object.return_date = timezone.now()
        self.object.save()
        
        # Update inventory
        inventory = BookInventory.objects.get(
            book=self.object.book, 
            branch=self.object.branch
        )
        inventory.available_copies += 1
        inventory.save()
        
        messages.success(self.request, 'Книга успешно возвращена!')
        return redirect(self.get_success_url())

class LoanDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Loan
    template_name = 'library_app/loans/loan_confirm_delete.html'
    success_url = reverse_lazy('loan_list')
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удалить выдачу: {self.object}'
        return context
    
    def delete(self, request, *args, **kwargs):
        loan = self.get_object()
        if not loan.is_returned:
            # Return book to inventory if not returned
            inventory = BookInventory.objects.get(
                book=loan.book, 
                branch=loan.branch
            )
            inventory.available_copies += 1
            inventory.save()
        
        messages.success(request, 'Запись о выдаче успешно удалена!')
        return super().delete(request, *args, **kwargs)

# Inventory Views
class InventoryListView(LoginRequiredMixin, ListView):
    model = BookInventory
    template_name = 'library_app/inventory/inventory_list.html'
    context_object_name = 'inventory'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        branch_filter = self.request.GET.get('branch', '')
        book_filter = self.request.GET.get('book', '')
        
        if branch_filter:
            queryset = queryset.filter(branch__id=branch_filter)
        
        if book_filter:
            queryset = queryset.filter(book__title__icontains=book_filter)
        
        return queryset.select_related('book', 'branch')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Управление инвентарем'
        context['branches'] = Branch.objects.all()
        context['branch_filter'] = self.request.GET.get('branch', '')
        context['book_filter'] = self.request.GET.get('book', '')
        return context

class InventoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = BookInventory
    form_class = InventoryForm
    template_name = 'library_app/inventory/inventory_form.html'
    success_url = reverse_lazy('inventory_list')
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить запись в инвентарь'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Запись в инвентарь успешно добавлена!')
        return super().form_valid(form)

class InventoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BookInventory
    form_class = InventoryForm
    template_name = 'library_app/inventory/inventory_form.html'
    
    def test_func(self):
        return is_librarian(self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('inventory_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактировать инвентарь: {self.object}'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Запись в инвентарь успешно обновлена!')
        return super().form_valid(form)

@login_required
def inventory_query(request):
    """Специальный запрос для поиска книг в инвентаре"""
    branches = Branch.objects.all()
    books = []
    selected_branch = None
    search_query = ''
    
    if request.method == 'GET' and 'branch' in request.GET:
        branch_id = request.GET.get('branch')
        search_query = request.GET.get('search', '')
        
        if branch_id:
            selected_branch = get_object_or_404(Branch, id=branch_id)
            books = BookInventory.objects.filter(branch=selected_branch)
            
            if search_query:
                books = books.filter(book__title__icontains=search_query)
            
            books = books.select_related('book')
    
    context = {
        'title': 'Поиск в инвентаре',
        'branches': branches,
        'books': books,
        'selected_branch': selected_branch,
        'search_query': search_query,
    }
    return render(request, 'library_app/inventory/inventory_query.html', context)

# Report Views
class ReportsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'library_app/reports/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Отчеты и аналитика'
        
        # Основная статистика для дашборда
        context['total_books'] = Book.objects.count()
        context['total_students'] = Student.objects.count()
        context['active_loans'] = Loan.objects.filter(is_returned=False).count()
        context['total_branches'] = Branch.objects.count()
        context['total_loans'] = Loan.objects.count()
        context['total_authors'] = Author.objects.count()
        context['total_publishers'] = Publisher.objects.count()
        context['total_faculties'] = Faculty.objects.count()
        
        # Статистика для карточек отчетов
        # Популярные книги - количество уникальных книг с выдачами
        context['popular_books_count'] = Loan.objects.values('book').distinct().count()
        
        # Активные студенты - количество уникальных студентов с выдачами
        context['active_students_count'] = Loan.objects.values('student').distinct().count()
        
        # Факультеты
        context['faculties_count'] = Faculty.objects.count()
        
        # Инвентарь
        inventory_stats = BookInventory.objects.aggregate(
            total_copies=Sum('total_copies'),
            available_copies=Sum('available_copies')
        )
        context['total_inventory'] = inventory_stats['total_copies'] or 0
        context['available_copies'] = inventory_stats['available_copies'] or 0
        
        # Максимальные значения для отображения
        # Самая популярная книга
        max_book_loans = Loan.objects.values('book__title').annotate(
            count=Count('id')
        ).order_by('-count').first()
        context['max_loans'] = max_book_loans['count'] if max_book_loans else 0
        
        # Самый активный студент
        max_student_loans = Loan.objects.values('student').annotate(
            count=Count('id')
        ).order_by('-count').first()
        context['max_student_loans'] = max_student_loans['count'] if max_student_loans else 0
        
        # Процент возвратов
        returned_loans = Loan.objects.filter(is_returned=True).count()
        context['return_rate'] = round((returned_loans / context['total_loans'] * 100), 1) if context['total_loans'] > 0 else 0
        
        # Статистика по факультетам
        faculty_stats = Loan.objects.values('student__faculty__name').annotate(
            count=Count('id')
        ).order_by('-count').first()
        context['max_faculty_usage'] = faculty_stats['count'] if faculty_stats else 0
        
        # Последние активности
        context['recent_loans'] = Loan.objects.select_related('student', 'book', 'branch').order_by('-issue_date')[:5]
        
        # Статистика по филиалам
        context['branch_stats'] = Branch.objects.annotate(
            book_count=Count('inventory', distinct=True),
            active_loans_count=Count('loans', filter=Q(loans__is_returned=False))
        )[:3]
        
        # Статистика по жанрам/категориям (если есть поле category в Book)
        try:
            # Если у книг есть поле category или genre
            genre_stats = Book.objects.values('category').annotate(
                count=Count('id')
            ).order_by('-count')[:5]
            context['genre_stats'] = genre_stats
        except:
            context['genre_stats'] = []
        
        return context

# API Views
@require_http_methods(["GET"])
def api_book_list(request):
    """API endpoint for book list"""
    books = Book.objects.select_related('publisher').prefetch_related('authors')
    
    # Filtering
    search = request.GET.get('search', '')
    if search:
        books = books.filter(title__icontains=search)
    
    year = request.GET.get('year', '')
    if year:
        books = books.filter(publication_year=year)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 20))
    start = (page - 1) * per_page
    end = start + per_page
    
    total_count = books.count()
    books = books[start:end]
    
    data = {
        'count': total_count,
        'page': page,
        'per_page': per_page,
        'results': [
            {
                'id': book.id,
                'title': book.title,
                'publication_year': book.publication_year,
                'page_count': book.page_count,
                'price': float(book.price),
                'publisher': book.publisher.name if book.publisher else None,
                'authors': [str(author) for author in book.authors.all()],
                'created_at': book.created_at.isoformat(),
            }
            for book in books
        ]
    }
    
    return JsonResponse(data)

@require_http_methods(["GET"])
def api_book_detail(request, pk):
    """API endpoint for book detail"""
    try:
        book = Book.objects.select_related('publisher').prefetch_related('authors').get(pk=pk)
        
        data = {
            'id': book.id,
            'title': book.title,
            'publication_year': book.publication_year,
            'page_count': book.page_count,
            'illustration_count': book.illustration_count,
            'price': float(book.price),
            'publisher': {
                'id': book.publisher.id if book.publisher else None,
                'name': book.publisher.name if book.publisher else None,
            },
            'authors': [
                {
                    'id': author.id,
                    'last_name': author.last_name,
                    'first_name': author.first_name,
                    'middle_name': author.middle_name,
                }
                for author in book.authors.all()
            ],
            'created_at': book.created_at.isoformat(),
            'updated_at': book.updated_at.isoformat(),
        }
        
        return JsonResponse(data)
    
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)

@require_http_methods(["GET"])
def api_inventory_list(request):
    """API endpoint for inventory list"""
    inventory = BookInventory.objects.select_related('book', 'branch')
    
    # Filtering
    branch_id = request.GET.get('branch_id')
    if branch_id:
        inventory = inventory.filter(branch_id=branch_id)
    
    book_id = request.GET.get('book_id')
    if book_id:
        inventory = inventory.filter(book_id=book_id)
    
    data = {
        'results': [
            {
                'id': item.id,
                'book': {
                    'id': item.book.id,
                    'title': item.book.title,
                },
                'branch': {
                    'id': item.branch.id,
                    'name': item.branch.name,
                },
                'total_copies': item.total_copies,
                'available_copies': item.available_copies,
                'last_updated': item.last_updated.isoformat(),
            }
            for item in inventory
        ]
    }
    
    return JsonResponse(data)

@require_http_methods(["GET"])
def api_loan_list(request):
    """API endpoint for loan list"""
    loans = Loan.objects.select_related('student', 'book', 'branch')
    
    # Filtering
    status = request.GET.get('status')
    if status == 'active':
        loans = loans.filter(is_returned=False)
    elif status == 'returned':
        loans = loans.filter(is_returned=True)
    
    student_id = request.GET.get('student_id')
    if student_id:
        loans = loans.filter(student_id=student_id)
    
    data = {
        'results': [
            {
                'id': loan.id,
                'student': {
                    'id': loan.student.id,
                    'name': loan.student.get_full_name(),
                    'student_id': loan.student.student_id,
                },
                'book': {
                    'id': loan.book.id,
                    'title': loan.book.title,
                },
                'branch': {
                    'id': loan.branch.id,
                    'name': loan.branch.name,
                },
                'issue_date': loan.issue_date.isoformat(),
                'return_date': loan.return_date.isoformat() if loan.return_date else None,
                'is_returned': loan.is_returned,
            }
            for loan in loans
        ]
    }
    
    return JsonResponse(data)

# Additional utility views
@login_required
def api_book_inventory(request, book_id):
    """API для получения инвентаря по книге"""
    book = get_object_or_404(Book, id=book_id)
    inventory = BookInventory.objects.filter(book=book).select_related('branch')
    
    data = {
        'book': {
            'id': book.id,
            'title': book.title,
        },
        'inventory': [
            {
                'branch': item.branch.name,
                'total_copies': item.total_copies,
                'available_copies': item.available_copies,
            }
            for item in inventory
        ]
    }
    
    return JsonResponse(data)

@login_required
def api_branch_books(request, branch_id):
    """API для получения книг в филиале"""
    branch = get_object_or_404(Branch, id=branch_id)
    inventory = BookInventory.objects.filter(branch=branch, available_copies__gt=0).select_related('book')
    
    data = {
        'branch': {
            'id': branch.id,
            'name': branch.name,
        },
        'books': [
            {
                'id': item.book.id,
                'title': item.book.title,
                'authors': item.book.get_authors_display(),
                'available_copies': item.available_copies,
            }
            for item in inventory
        ]
    }
    

    return JsonResponse(data)
