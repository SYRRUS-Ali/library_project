# https://chat.deepseek.com/a/chat/s/2199d2f0-32a3-4eaf-95d7-f04ff2532bdc

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import (
    UserProfile, Author, Publisher, Book, Branch, BookInventory,
    Faculty, BookFacultyUsage, Student, Loan, Reservation, Fine
)

class UserProfileInline(admin.StackedInline):
    model = 'library_app.UserProfile'  # Use string reference
    can_delete = False
    verbose_name_plural = _('Profile')
    fields = ('user_type', 'phone_number', 'address')
    readonly_fields = ('user',)

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_user_type', 'is_staff')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    def get_user_type(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.get_user_type_display()
        return _('Not set')
    get_user_type.short_description = _('User Type')

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Now safely import models for the rest of the admin registrations
try:
    from .models import (
        Author, Publisher, Book, Branch, BookInventory,
        Faculty, BookFacultyUsage, Student, Loan, Reservation, Fine
    )
    
    # Author Admin
    @admin.register(Author)
    class AuthorAdmin(admin.ModelAdmin):
        list_display = ('last_name', 'first_name', 'patronymic')
        search_fields = ('first_name', 'last_name', 'patronymic')
    
    # Publisher Admin
    @admin.register(Publisher)
    class PublisherAdmin(admin.ModelAdmin):
        list_display = ('name',)
        search_fields = ('name',)
    
    # Book Admin
    @admin.register(Book)
    class BookAdmin(admin.ModelAdmin):
        list_display = ('title', 'year', 'publisher')
        list_filter = ('year',)
        search_fields = ('title', 'isbn')
    
    # Branch Admin
    @admin.register(Branch)
    class BranchAdmin(admin.ModelAdmin):
        list_display = ('name', 'code')
        search_fields = ('name', 'code')
    
    # BookInventory Admin
    @admin.register(BookInventory)
    class BookInventoryAdmin(admin.ModelAdmin):
        list_display = ('book', 'branch', 'total_copies', 'available_copies')
        list_filter = ('branch',)
    
    # Faculty Admin
    @admin.register(Faculty)
    class FacultyAdmin(admin.ModelAdmin):
        list_display = ('name', 'code')
        search_fields = ('name', 'code')
    
    # BookFacultyUsage Admin
    @admin.register(BookFacultyUsage)
    class BookFacultyUsageAdmin(admin.ModelAdmin):
        list_display = ('book', 'faculty', 'branch')
        list_filter = ('faculty', 'branch')
    
    # Student Admin
    @admin.register(Student)
    class StudentAdmin(admin.ModelAdmin):
        list_display = ('student_id', 'get_user_name', 'faculty')
        search_fields = ('student_id', 'user__username')
        
        def get_user_name(self, obj):
            return obj.user.username
        get_user_name.short_description = _('Username')
    
    # Loan Admin
    @admin.register(Loan)
    class LoanAdmin(admin.ModelAdmin):
        list_display = ('book', 'student', 'issue_date', 'due_date', 'status')
        list_filter = ('status', 'branch')
    
    # Reservation Admin
    @admin.register(Reservation)
    class ReservationAdmin(admin.ModelAdmin):
        list_display = ('book', 'student', 'reservation_date', 'status')
        list_filter = ('status',)
    
    # Fine Admin
    @admin.register(Fine)
    class FineAdmin(admin.ModelAdmin):
        list_display = ('student', 'amount', 'paid')
        list_filter = ('paid',)

except ImportError as e:
    print(f"Warning: Could not import models for admin registration: {e}")
    print("Some admin features may not be available until migrations are complete.")

# Custom admin site settings
admin.site.site_header = _('Library Management System Administration')
admin.site.site_title = _('Library Management System')
admin.site.index_title = _('Dashboard')
