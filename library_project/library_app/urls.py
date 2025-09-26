from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.HomeView.as_view(), name='home'),
    
    # Books - Requirement 3
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('books/add/', views.BookCreateView.as_view(), name='book-add'),
    path('books/<int:pk>/edit/', views.BookUpdateView.as_view(), name='book-edit'),
    
    # Branches - Requirement 4
    path('branches/', views.BranchListView.as_view(), name='branch-list'),
    path('branches/<int:pk>/', views.BranchDetailView.as_view(), name='branch-detail'),
    path('branches/add/', views.BranchCreateView.as_view(), name='branch-add'),
    path('branches/<int:pk>/edit/', views.BranchUpdateView.as_view(), name='branch-edit'),
    
    # Special Functions - Requirements 1 & 2
    path('inventory/query/', views.InventoryQueryView.as_view(), name='inventory-query'),
    path('book/usage/', views.BookUsageView.as_view(), name='book-usage'),
    
    # Loans
    path('loans/', views.LoanListView.as_view(), name='loan-list'),
    path('loans/add/', views.LoanCreateView.as_view(), name='loan-add'),
    path('loans/<int:pk>/return/', views.return_loan, name='loan-return'),
    
    # Faculties
    path('faculties/', views.FacultyListView.as_view(), name='faculty-list'),
    path('faculties/<int:pk>/', views.FacultyDetailView.as_view(), name='faculty-detail'),
    
    # Students
    path('students/', views.StudentListView.as_view(), name='student-list'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    
    # API endpoints
    path('api/available-copies/', views.get_available_copies, name='api-available-copies'),
    path('api/branch/<int:branch_id>/books/', views.get_branch_books, name='api-branch-books'),

    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),

]