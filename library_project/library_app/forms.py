from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Book, Author, Publisher, Branch, Faculty, Student, BookFacultyUsage, Loan, CustomUser
from .services import InventoryService, LoanService

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'authors', 'publisher', 'year', 'pages', 
                 'illustrations', 'price', 'isbn']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1000, 'max': 2025}),
            'pages': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'illustrations': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'authors': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'publisher': forms.Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'year': 'Publication year (YYYY format)',
            'isbn': 'International Standard Book Number',
        }

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year and year > timezone.now().year:
            raise ValidationError('Publication year cannot be in the future')
        return year

    def clean_pages(self):
        pages = self.cleaned_data.get('pages')
        if pages and pages < 1:
            raise ValidationError('Number of pages must be at least 1')
        return pages

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'code', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class InventoryQueryForm(forms.Form):
    """Form for inventory query (Requirement 1)"""
    book = forms.ModelChoiceField(
        queryset=Book.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Book"
    )
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Branch"
    )

    def get_copies_count(self):
        """Get copies count based on form data"""
        if self.is_valid():
            book = self.cleaned_data['book']
            branch = self.cleaned_data['branch']
            return InventoryService.get_copies_in_branch(book.id, branch.id)
        return 0

class BookUsageForm(forms.Form):
    """Form for book usage query (Requirement 2)"""
    book = forms.ModelChoiceField(
        queryset=Book.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Book"
    )
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Select Branch"
    )

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['student', 'book', 'branch', 'due_date']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'book': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        book = cleaned_data.get('book')
        branch = cleaned_data.get('branch')

        if student and book and branch:
            # Check availability
            available = InventoryService.get_available_copies_in_branch(book.id, branch.id)
            if available <= 0:
                raise ValidationError('No available copies of this book in the selected branch')

            # Check if student already has this book
            active_loans = Loan.objects.filter(
                student=student,
                book=book,
                status='active'
            ).exists()
            
            if active_loans:
                raise ValidationError('Student already has an active loan for this book')

        return cleaned_data

class BookFacultyUsageForm(forms.ModelForm):
    class Meta:
        model = BookFacultyUsage
        fields = ['book', 'faculty', 'branch']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-select'}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
        }

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', 'user_type', 'phone_number', 'address')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})
