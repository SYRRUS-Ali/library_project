from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Author, Publisher, Book, Branch, BookInventory, 
    Faculty, BookFacultyUsage, Student, Loan
)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name')
    list_filter = ('last_name',)
    search_fields = ('last_name', 'first_name', 'middle_name')
    ordering = ('last_name', 'first_name')

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name', 'address')
    ordering = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'publication_year', 'publisher', 'page_count', 'price')
    list_filter = ('publication_year', 'publisher')
    search_fields = ('title',)
    filter_horizontal = ('authors',)
    ordering = ('title',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'created_at')
    search_fields = ('name', 'address')
    ordering = ('name',)
    readonly_fields = ('created_at',)

@admin.register(BookInventory)
class BookInventoryAdmin(admin.ModelAdmin):
    list_display = ('book', 'branch', 'total_copies', 'available_copies', 'last_updated')
    list_filter = ('branch',)
    search_fields = ('book__title', 'branch__name')
    ordering = ('branch', 'book')
    readonly_fields = ('last_updated',)

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at',)

@admin.register(BookFacultyUsage)
class BookFacultyUsageAdmin(admin.ModelAdmin):
    list_display = ('book', 'branch', 'faculty', 'created_at')
    list_filter = ('branch', 'faculty')
    search_fields = ('book__title', 'faculty__name')
    ordering = ('faculty', 'book')
    readonly_fields = ('created_at',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'student_id', 'faculty', 'created_at')
    list_filter = ('faculty',)
    search_fields = ('last_name', 'first_name', 'student_id')
    ordering = ('last_name', 'first_name')
    readonly_fields = ('created_at',)

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('student', 'book', 'branch', 'issue_date', 'return_date', 'is_returned')
    list_filter = ('branch', 'is_returned', 'issue_date')
    search_fields = ('student__last_name', 'student__first_name', 'book__title')
    ordering = ('-issue_date',)
    readonly_fields = ('issue_date', 'created_by')
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

