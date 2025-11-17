from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Author, Publisher, Book, Branch, BookInventory,
    Faculty, BookFacultyUsage, Student, Loan
)

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['last_name', 'first_name', 'middle_name']
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ['name', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'authors', 'publisher', 'publication_year', 
                 'page_count', 'illustration_count', 'price']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'page_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'illustration_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'authors': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'publisher': forms.Select(attrs={'class': 'form-control'}),
        }

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['last_name', 'first_name', 'student_id', 'faculty']
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'faculty': forms.Select(attrs={'class': 'form-control'}),
        }

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['student', 'book', 'branch']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'book': forms.Select(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        book = cleaned_data.get('book')
        branch = cleaned_data.get('branch')
        
        if student and book and branch:
            # Check if student already has this book
            active_loan = Loan.objects.filter(
                student=student, 
                book=book, 
                is_returned=False
            ).exists()
            
            if active_loan:
                raise ValidationError('Студент уже имеет эту книгу на руках')
            
            # Check inventory
            try:
                inventory = BookInventory.objects.get(book=book, branch=branch)
                if inventory.available_copies <= 0:
                    raise ValidationError('Нет доступных экземпляров этой книги в указанном филиале')
            except BookInventory.DoesNotExist:
                raise ValidationError('Книга не найдена в инвентаре указанного филиала')

class InventoryForm(forms.ModelForm):
    class Meta:
        model = BookInventory
        fields = ['book', 'branch', 'total_copies', 'available_copies']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-control'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        total_copies = cleaned_data.get('total_copies')
        available_copies = cleaned_data.get('available_copies')
        
        if total_copies is not None and available_copies is not None:
            if available_copies > total_copies:
                raise ValidationError('Доступные экземпляры не могут превышать общее количество')

class BookFacultyUsageForm(forms.ModelForm):
    class Meta:
        model = BookFacultyUsage
        fields = ['book', 'branch', 'faculty']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control'}),
            'branch': forms.Select(attrs={'class': 'form-control'}),
            'faculty': forms.Select(attrs={'class': 'form-control'}),
        }
        
