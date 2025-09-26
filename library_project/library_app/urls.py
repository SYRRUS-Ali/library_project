from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from . import views
from .views import (
    BookListView, BookDetailView, BookCreateView, BookUpdateView, BookDeleteView,
    AuthorListView, AuthorDetailView, AuthorCreateView, AuthorUpdateView, AuthorDeleteView,
    PublisherListView, PublisherDetailView, PublisherCreateView, PublisherUpdateView, PublisherDeleteView,
    BranchListView, BranchDetailView, BranchCreateView, BranchUpdateView, BranchDeleteView,
    FacultyListView, FacultyDetailView, FacultyCreateView, FacultyUpdateView, FacultyDeleteView,
    StudentListView, StudentDetailView, StudentCreateView, StudentUpdateView, StudentDeleteView,
    LoanListView, LoanDetailView, LoanCreateView, LoanReturnView, LoanDeleteView,
    InventoryListView, InventoryCreateView, InventoryUpdateView, ReportsDashboardView
)

urlpatterns = [
    # Admin
    
    # Authentication
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='library_app/auth/login.html',
        extra_context={'title': 'Вход в систему'}
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(
        template_name='library_app/auth/logout.html',
        extra_context={'title': 'Выход из системы'}
    ), name='logout'),
    path('accounts/register/', views.register, name='register'),
    
    # Home
    path('', views.home, name='home'),
    
    # Books
    path('books/', BookListView.as_view(), name='book_list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('books/add/', BookCreateView.as_view(), name='book_add'),
    path('books/<int:pk>/edit/', BookUpdateView.as_view(), name='book_edit'),
    path('books/<int:pk>/delete/', BookDeleteView.as_view(), name='book_delete'),
    path('books/<int:pk>/usage/', views.book_usage, name='book_usage'),
    
    # Authors
    path('authors/', AuthorListView.as_view(), name='author_list'),
    path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author_detail'),
    path('authors/add/', AuthorCreateView.as_view(), name='author_add'),
    path('authors/<int:pk>/edit/', AuthorUpdateView.as_view(), name='author_edit'),
    path('authors/<int:pk>/delete/', AuthorDeleteView.as_view(), name='author_delete'),
    
    # Publishers
    path('publishers/', PublisherListView.as_view(), name='publisher_list'),
    path('publishers/<int:pk>/', PublisherDetailView.as_view(), name='publisher_detail'),
    path('publishers/add/', PublisherCreateView.as_view(), name='publisher_add'),
    path('publishers/<int:pk>/edit/', PublisherUpdateView.as_view(), name='publisher_edit'),
    path('publishers/<int:pk>/delete/', PublisherDeleteView.as_view(), name='publisher_delete'),
    
    # Branches
    path('branches/', BranchListView.as_view(), name='branch_list'),
    path('branches/<int:pk>/', BranchDetailView.as_view(), name='branch_detail'),
    path('branches/add/', BranchCreateView.as_view(), name='branch_add'),
    path('branches/<int:pk>/edit/', BranchUpdateView.as_view(), name='branch_edit'),
    path('branches/<int:pk>/delete/', BranchDeleteView.as_view(), name='branch_delete'),
    
    # Faculties
    path('faculties/', FacultyListView.as_view(), name='faculty_list'),
    path('faculties/<int:pk>/', FacultyDetailView.as_view(), name='faculty_detail'),
    path('faculties/add/', FacultyCreateView.as_view(), name='faculty_add'),
    path('faculties/<int:pk>/edit/', FacultyUpdateView.as_view(), name='faculty_edit'),
    path('faculties/<int:pk>/delete/', FacultyDeleteView.as_view(), name='faculty_delete'),
    
    # Students
    path('students/', StudentListView.as_view(), name='student_list'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student_detail'),
    path('students/add/', StudentCreateView.as_view(), name='student_add'),
    path('students/<int:pk>/edit/', StudentUpdateView.as_view(), name='student_edit'),
    path('students/<int:pk>/delete/', StudentDeleteView.as_view(), name='student_delete'),
    
    # Loans
    path('loans/', LoanListView.as_view(), name='loan_list'),
    path('loans/<int:pk>/', LoanDetailView.as_view(), name='loan_detail'),
    path('loans/add/', LoanCreateView.as_view(), name='loan_add'),
    path('loans/<int:pk>/return/', LoanReturnView.as_view(), name='loan_return'),
    path('loans/<int:pk>/delete/', LoanDeleteView.as_view(), name='loan_delete'),
    
    # Inventory
    path('inventory/query/', views.inventory_query, name='inventory_query'),
    path('inventory/manage/', InventoryListView.as_view(), name='inventory_list'),
    path('inventory/add/', InventoryCreateView.as_view(), name='inventory_add'),
    path('inventory/<int:pk>/edit/', InventoryUpdateView.as_view(), name='inventory_edit'),
    
    # Reports
    path('reports/', ReportsDashboardView.as_view(), name='reports_dashboard'),
    # API
    path('api/books/', views.api_book_list, name='api_book_list'),
    path('api/books/<int:pk>/', views.api_book_detail, name='api_book_detail'),
    path('api/inventory/', views.api_inventory_list, name='api_inventory_list'),
    path('api/loans/', views.api_loan_list, name='api_loan_list'),
    
    # Error pages
    path('403/', TemplateView.as_view(template_name='library_app/errors/403.html'), name='error_403'),
    path('404/', TemplateView.as_view(template_name='library_app/errors/404.html'), name='error_404'),
    path('500/', TemplateView.as_view(template_name='library_app/errors/500.html'), name='error_500'),
]

# Обработчики ошибок
handler403 = 'library_app.views.handler403'
handler404 = 'library_app.views.handler404'
handler500 = 'library_app.views.handler500'
