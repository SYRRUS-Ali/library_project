from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
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
        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'middle_name': 'Отчество',
        }

    def clean(self):
        cleaned_data = super().clean()
        last_name = cleaned_data.get('last_name')
        first_name = cleaned_data.get('first_name')
        
        if last_name and not last_name.strip():
            raise ValidationError({'last_name': 'Фамилия автора обязательна'})
        if first_name and not first_name.strip():
            raise ValidationError({'first_name': 'Имя автора обязательно'})
        
        return cleaned_data

class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ['name', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'name': 'Название издательства',
            'address': 'Адрес',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and not name.strip():
            raise ValidationError('Название издательства обязательно')
        return name

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'authors', 'publisher', 'publication_year', 
                 'page_count', 'illustration_count', 'price']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'authors': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'publisher': forms.Select(attrs={'class': 'form-select'}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1000, 'max': 2100}),
            'page_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'illustration_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
        }
        labels = {
            'title': 'Название книги',
            'authors': 'Авторы',
            'publisher': 'Издательство',
            'publication_year': 'Год издания',
            'page_count': 'Количество страниц',
            'illustration_count': 'Количество иллюстраций',
            'price': 'Стоимость',
        }

    def clean_publication_year(self):
        year = self.cleaned_data.get('publication_year')
        if year and (year < 1000 or year > 2100):
            raise ValidationError('Год издания должен быть между 1000 и 2100')
        return year

    def clean_page_count(self):
        pages = self.cleaned_data.get('page_count')
        if pages and pages <= 0:
            raise ValidationError('Количество страниц должно быть больше 0')
        return pages

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise ValidationError('Стоимость должна быть больше 0')
        return price

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'name': 'Название филиала',
            'address': 'Адрес',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and not name.strip():
            raise ValidationError('Название филиала обязательно')
        return name

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if address and not address.strip():
            raise ValidationError('Адрес филиала обязателен')
        return address

class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'name': 'Название факультета',
            'description': 'Описание',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and not name.strip():
            raise ValidationError('Название факультета обязательно')
        return name

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['last_name', 'first_name', 'student_id', 'faculty']
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'student_id': 'Номер студенческого билета',
            'faculty': 'Факультет',
        }

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name and not last_name.strip():
            raise ValidationError('Фамилия студента обязательна')
        return last_name

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name and not first_name.strip():
            raise ValidationError('Имя студента обязательно')
        return first_name

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if student_id and not student_id.strip():
            raise ValidationError('Номер студенческого билета обязателен')
        return student_id

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['student', 'book', 'branch']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'book': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'student': 'Студент',
            'book': 'Книга',
            'branch': 'Филиал',
        }

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        book = cleaned_data.get('book')
        branch = cleaned_data.get('branch')

        if student and book and branch:
            # Check if book is available in the branch
            try:
                inventory = BookInventory.objects.get(book=book, branch=branch)
                if inventory.available_copies <= 0:
                    raise ValidationError('Нет доступных экземпляров этой книги в указанном филиале')
            except BookInventory.DoesNotExist:
                raise ValidationError('Книга не найдена в инвентаре указанного филиала')

        return cleaned_data

class InventoryForm(forms.ModelForm):
    class Meta:
        model = BookInventory
        fields = ['book', 'branch', 'total_copies', 'available_copies']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
        labels = {
            'book': 'Книга',
            'branch': 'Филиал',
            'total_copies': 'Общее количество экземпляров',
            'available_copies': 'Доступное количество экземпляров',
        }

    def clean(self):
        cleaned_data = super().clean()
        total_copies = cleaned_data.get('total_copies')
        available_copies = cleaned_data.get('available_copies')

        if total_copies is not None and available_copies is not None:
            if available_copies > total_copies:
                raise ValidationError('Доступные экземпляры не могут превышать общее количество')
            if total_copies < 0:
                raise ValidationError('Общее количество экземпляров не может быть отрицательным')

        return cleaned_data

class BookFacultyUsageForm(forms.ModelForm):
    class Meta:
        model = BookFacultyUsage
        fields = ['book', 'branch', 'faculty']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'book': 'Книга',
            'branch': 'Филиал',
            'faculty': 'Факультет',
        }

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        branch = cleaned_data.get('branch')

        if book and branch:
            # Check if book exists in branch inventory
            if not BookInventory.objects.filter(book=book, branch=branch).exists():
                raise ValidationError('Книга не найдена в инвентаре указанного филиала')

        return cleaned_data

# Search and Filter Forms
class BookSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по названию или автору...'
        }),
        label='Поиск'
    )
    year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Год издания',
            'min': 1000,
            'max': 2100
        }),
        label='Год издания'
    )
    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Издательство'
    )

class StudentSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по фамилии, имени или номеру билета...'
        }),
        label='Поиск'
    )
    faculty = forms.ModelChoiceField(
        queryset=Faculty.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Факультет'
    )

class LoanSearchForm(forms.Form):
    STATUS_CHOICES = [
        ('', 'Все статусы'),
        ('active', 'Активные'),
        ('returned', 'Возвращенные'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Статус'
    )
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Филиал'
    )

class InventorySearchForm(forms.Form):
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Филиал'
    )
    book = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по названию книги...'
        }),
        label='Книга'
    )

class ReportSearchForm(forms.Form):
    PERIOD_CHOICES = [
        ('all', 'За все время'),
        ('year', 'За последний год'),
        ('month', 'За последний месяц'),
    ]
    
    period = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Период'
    )
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Филиал'
    )
    faculty = forms.ModelChoiceField(
        queryset=Faculty.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Факультет'
    )