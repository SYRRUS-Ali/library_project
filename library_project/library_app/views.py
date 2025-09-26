from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import JsonResponse
from django.utils import timezone

from .models import Book, Branch, Faculty, Student, Loan, BookInventory, BookFacultyUsage
from .forms import BookForm, BranchForm, InventoryQueryForm, BookUsageForm, LoanForm, BookFacultyUsageForm, CustomUserCreationForm, CustomAuthenticationForm
from .services import (
    InventoryService, 
    FacultyUsageService, 
    LoanService, 
    AnalyticsService,
    get_copies_in_branch,
    get_faculties_using_book_in_branch
)

class HomeView(generic.TemplateView):
    """Dashboard home page"""
    template_name = 'library_app/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_books'] = Book.objects.count()
        context['total_branches'] = Branch.objects.count()
        context['total_loans'] = Loan.objects.count()
        context['overdue_loans'] = LoanService.get_overdue_loans().count()
        context['recent_books'] = Book.objects.order_by('-created_at')[:5]
        context['recent_loans'] = Loan.objects.select_related('book', 'student').order_by('-issue_date')[:5]
        return context

# Book Views
class BookListView(LoginRequiredMixin, generic.ListView):
    """Book list view with search functionality"""
    model = Book
    template_name = 'library_app/book_list.html'
    context_object_name = 'books'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Book.objects.select_related('publisher').prefetch_related('authors')
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(authors__first_name__icontains=search_query) |
                Q(authors__last_name__icontains=search_query) |
                Q(isbn__icontains=search_query) |
                Q(publisher__name__icontains=search_query)
            ).distinct()
        
        return queryset.order_by('title')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

class BookDetailView(LoginRequiredMixin, generic.DetailView):
    """Book detail view with inventory and usage information"""
    model = Book
    template_name = 'library_app/book_detail.html'
    context_object_name = 'book'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        
        # Get inventory across all branches
        context['inventory'] = BookInventory.objects.filter(book=book).select_related('branch')
        
        # Get faculty usage
        context['faculty_usage'] = BookFacultyUsage.objects.filter(book=book).select_related('faculty', 'branch')
        
        # Get loan statistics
        context['total_loans'] = Loan.objects.filter(book=book).count()
        context['unique_students'] = LoanService.get_unique_students_borrowed_book(book.id)
        
        return context

class BookCreateView(LoginRequiredMixin, generic.CreateView):
    """Create new book - Requirement 3"""
    model = Book
    form_class = BookForm
    template_name = 'library_app/book_form.html'
    success_url = reverse_lazy('book-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Book created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Book'
        context['submit_text'] = 'Create Book'
        return context

class BookUpdateView(LoginRequiredMixin, generic.UpdateView):
    """Update book - Requirement 3"""
    model = Book
    form_class = BookForm
    template_name = 'library_app/book_form.html'
    success_url = reverse_lazy('book-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Book updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Book: {self.object.title}'
        context['submit_text'] = 'Update Book'
        return context

# Branch Views
class BranchListView(LoginRequiredMixin, generic.ListView):
    """Branch list view"""
    model = Branch
    template_name = 'library_app/branch_list.html'
    context_object_name = 'branches'
    paginate_by = 20
    
    def get_queryset(self):
        return Branch.objects.annotate(
            total_books=Count('inventories'),
            total_copies=Count('inventories__total_copies')
        ).order_by('name')

class BranchDetailView(LoginRequiredMixin, generic.DetailView):
    """Branch detail view with inventory"""
    model = Branch
    template_name = 'library_app/branch_detail.html'
    context_object_name = 'branch'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        branch = self.get_object()
        
        # Get inventory with book details
        context['inventory'] = BookInventory.objects.filter(
            branch=branch
        ).select_related('book').order_by('book__title')
        
        context['total_books'] = context['inventory'].count()
        context['total_copies'] = sum(inv.total_copies for inv in context['inventory'])
        context['available_copies'] = sum(inv.available_copies for inv in context['inventory'])
        
        return context

class BranchCreateView(LoginRequiredMixin, generic.CreateView):
    """Create new branch - Requirement 4"""
    model = Branch
    form_class = BranchForm
    template_name = 'library_app/branch_form.html'
    success_url = reverse_lazy('branch-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Branch created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Branch'
        context['submit_text'] = 'Create Branch'
        return context

class BranchUpdateView(LoginRequiredMixin, generic.UpdateView):
    """Update branch - Requirement 4"""
    model = Branch
    form_class = BranchForm
    template_name = 'library_app/branch_form.html'
    success_url = reverse_lazy('branch-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Branch updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Branch: {self.object.name}'
        context['submit_text'] = 'Update Branch'
        return context

# Special Function Views (Requirements 1 & 2)
class InventoryQueryView(LoginRequiredMixin, generic.FormView):
    """Inventory query view - Requirement 1"""
    template_name = 'library_app/inventory_query.html'
    form_class = InventoryQueryForm
    
    def form_valid(self, form):
        book = form.cleaned_data['book']
        branch = form.cleaned_data['branch']
        copies_count = form.get_copies_count()
        
        context = self.get_context_data()
        context['result'] = {
            'book': book,
            'branch': branch,
            'copies_count': copies_count,
            'has_result': True
        }
        return render(self.request, self.template_name, context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Inventory Query'
        context['submit_text'] = 'Check Inventory'
        return context

class BookUsageView(LoginRequiredMixin, generic.FormView):
    """Book usage view - Requirement 2"""
    template_name = 'library_app/book_usage.html'
    form_class = BookUsageForm
    
    def form_valid(self, form):
        book = form.cleaned_data['book']
        branch = form.cleaned_data['branch']
        
        faculties = get_faculties_using_book_in_branch(book.id, branch.id)
        faculties_count = faculties.count()
        
        context = self.get_context_data()
        context['result'] = {
            'book': book,
            'branch': branch,
            'faculties': faculties,
            'faculties_count': faculties_count,
            'has_result': True
        }
        return render(self.request, self.template_name, context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Book Usage by Faculty'
        context['submit_text'] = 'Check Usage'
        return context

# Loan Views
class LoanListView(LoginRequiredMixin, generic.ListView):
    """Loan list view"""
    model = Loan
    template_name = 'library_app/loan_list.html'
    context_object_name = 'loans'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Loan.objects.select_related('book', 'student', 'branch')
        
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-issue_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        return context

class LoanCreateView(LoginRequiredMixin, generic.CreateView):
    """Create new loan"""
    model = Loan
    form_class = LoanForm
    template_name = 'library_app/loan_form.html'
    success_url = reverse_lazy('loan-list')
    
    def form_valid(self, form):
        loan = form.save(commit=False)
        loan.issue_date = timezone.now().date()
        loan.status = 'active'
        
        try:
            loan.save()
            messages.success(self.request, 'Book issued successfully!')
            return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f'Error issuing book: {str(e)}')
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Issue New Loan'
        context['submit_text'] = 'Issue Book'
        return context

def return_loan(request, pk):
    """Return a loan"""
    loan = get_object_or_404(Loan, pk=pk)
    
    if request.method == 'POST':
        try:
            LoanService.return_loan(loan.id)
            messages.success(request, 'Book returned successfully!')
        except Exception as e:
            messages.error(request, f'Error returning book: {str(e)}')
    
    return redirect('loan-list')

# Faculty Views
class FacultyListView(LoginRequiredMixin, generic.ListView):
    """Faculty list view"""
    model = Faculty
    template_name = 'library_app/faculty_list.html'
    context_object_name = 'faculties'
    paginate_by = 20

class FacultyDetailView(LoginRequiredMixin, generic.DetailView):
    """Faculty detail view with book usage"""
    model = Faculty
    template_name = 'library_app/faculty_detail.html'
    context_object_name = 'faculty'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faculty = self.get_object()
        
        context['book_usages'] = BookFacultyUsage.objects.filter(
            faculty=faculty
        ).select_related('book', 'branch')
        
        context['students'] = Student.objects.filter(faculty=faculty)
        
        return context

# Student Views
class StudentListView(LoginRequiredMixin, generic.ListView):
    """Student list view"""
    model = Student
    template_name = 'library_app/student_list.html'
    context_object_name = 'students'
    paginate_by = 20
    
    def get_queryset(self):
        return Student.objects.select_related('faculty').order_by('last_name', 'first_name')

class StudentDetailView(LoginRequiredMixin, generic.DetailView):
    """Student detail view with loan history"""
    model = Student
    template_name = 'library_app/student_detail.html'
    context_object_name = 'student'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        
        context['loans'] = Loan.objects.filter(student=student).select_related('book', 'branch')
        context['active_loans'] = context['loans'].filter(status='active')
        context['overdue_loans'] = context['loans'].filter(status='overdue')
        
        return context

# API Views for AJAX calls
def get_available_copies(request):
    """Get available copies for book in branch (AJAX)"""
    book_id = request.GET.get('book_id')
    branch_id = request.GET.get('branch_id')
    
    if book_id and branch_id:
        available = InventoryService.get_available_copies_in_branch(int(book_id), int(branch_id))
        return JsonResponse({'available': available})
    
    return JsonResponse({'error': 'Invalid parameters'}, status=400)

def get_branch_books(request, branch_id):
    """Get books available in a specific branch (AJAX)"""
    books = BookInventory.objects.filter(
        branch_id=branch_id, 
        available_copies__gt=0
    ).select_related('book').values('book__id', 'book__title')
    
    return JsonResponse(list(books), safe=False)

# Permission check functions
def is_admin_user(user):
    return user.is_authenticated and (user.is_superuser or user.user_type == 'admin')

def is_librarian_user(user):
    return user.is_authenticated and (user.user_type == 'librarian' or is_admin_user(user))

def is_student_user(user):
    return user.is_authenticated and user.user_type == 'student'

# Mixin for permission-based access
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_admin_user(self.request.user)

class LibrarianRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_librarian_user(self.request.user)

class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_student_user(self.request.user)

# Authentication views
def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-login after registration
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to the library system.')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'library_app/auth/register.html', {'form': form})

def login_view(request):
    """Custom login view"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'library_app/auth/login.html', {'form': form})

# Update existing views to use permission mixins
class BookCreateView(LibrarianRequiredMixin, BookCreateView):
    """Only librarians and admins can create books"""
    pass

class BookUpdateView(LibrarianRequiredMixin, BookUpdateView):
    """Only librarians and admins can update books"""
    pass

class BranchCreateView(LibrarianRequiredMixin, BranchCreateView):
    """Only librarians and admins can create branches"""
    pass

class BranchUpdateView(LibrarianRequiredMixin, BranchUpdateView):
    """Only librarians and admins can update branches"""
    pass

class LoanCreateView(LibrarianRequiredMixin, LoanCreateView):
    """Only librarians and admins can create loans"""
    pass

# Profile view
@login_required
def profile_view(request):
    """User profile view with loan statistics"""
    user = request.user
    user_loans = Loan.objects.filter(student__user=user) if hasattr(user, 'student') else Loan.objects.none()
    
    context = {
        'user': user,
        'total_loans': user_loans.count(),
        'active_loans': user_loans.filter(status='active').count(),
        'overdue_loans': user_loans.filter(status='overdue').count(),
        'recent_loans': user_loans.order_by('-issue_date')[:5]
    }
    return render(request, 'library_app/auth/profile.html', context)
