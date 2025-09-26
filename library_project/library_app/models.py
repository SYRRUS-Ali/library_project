from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class BaseModel(models.Model):
    """Abstract base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        abstract = True

class UserProfile(models.Model):
    """User profile extending Django's built-in User model"""
    USER_TYPE_CHOICES = (
        ('admin', 'Administrator'),
        ('librarian', 'Librarian'),
        ('student', 'Student'),
        ('faculty', 'Faculty Member'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES, 
        default='student',
        verbose_name=_('User Type')
    )
    phone_number = models.CharField(max_length=15, blank=True, verbose_name=_('Phone Number'))
    address = models.TextField(blank=True, verbose_name=_('Address'))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_('Date of Birth'))
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        null=True, 
        blank=True,
        verbose_name=_('Profile Picture')
    )
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"

    def is_admin_user(self):
        return self.user_type == 'admin' or self.user.is_superuser

    def is_librarian_user(self):
        return self.user_type == 'librarian' or self.is_admin_user()

    def is_student_user(self):
        return self.user_type == 'student'

    def is_faculty_user(self):
        return self.user_type == 'faculty'

    def get_absolute_url(self):
        return reverse('profile')

# Signals to automatically create/update user profile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Author(BaseModel):
    first_name = models.CharField(max_length=100, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=100, verbose_name=_('Last Name'))
    patronymic = models.CharField(max_length=100, blank=True, verbose_name=_('Patronymic'))
    bio = models.TextField(blank=True, verbose_name=_('Biography'))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_('Date of Birth'))
    date_of_death = models.DateField(null=True, blank=True, verbose_name=_('Date of Death'))
    nationality = models.CharField(max_length=100, blank=True, verbose_name=_('Nationality'))

    class Meta:
        verbose_name = _('Author')
        verbose_name_plural = _('Authors')
        unique_together = (('first_name', 'last_name', 'patronymic'),)
        ordering = ['last_name', 'first_name']

    def __str__(self):
        if self.patronymic:
            return f"{self.last_name} {self.first_name} {self.patronymic}"
        return f"{self.last_name} {self.first_name}"

    def get_absolute_url(self):
        return reverse('author-detail', kwargs={'pk': self.pk})

    @property
    def full_name(self):
        if self.patronymic:
            return f"{self.last_name} {self.first_name} {self.patronymic}"
        return f"{self.last_name} {self.first_name}"

class Publisher(BaseModel):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))
    address = models.TextField(blank=True, verbose_name=_('Address'))
    website = models.URLField(blank=True, verbose_name=_('Website'))
    email = models.EmailField(blank=True, verbose_name=_('Email'))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Phone'))

    class Meta:
        verbose_name = _('Publisher')
        verbose_name_plural = _('Publishers')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('publisher-detail', kwargs={'pk': self.pk})

class Book(BaseModel):
    GENRE_CHOICES = (
        ('fiction', _('Fiction')),
        ('non-fiction', _('Non-Fiction')),
        ('science', _('Science')),
        ('technology', _('Technology')),
        ('history', _('History')),
        ('biography', _('Biography')),
        ('children', _('Children')),
        ('textbook', _('Textbook')),
        ('reference', _('Reference')),
        ('other', _('Other')),
    )
    
    title = models.CharField(max_length=500, db_index=True, verbose_name=_('Title'))
    authors = models.ManyToManyField(Author, related_name='books', verbose_name=_('Authors'))
    publisher = models.ForeignKey(
        Publisher, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_('Publisher')
    )
    year = models.PositiveSmallIntegerField(
        null=True, 
        blank=True, 
        verbose_name=_('Publication Year'),
        help_text=_('Format: YYYY')
    )
    pages = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        verbose_name=_('Number of Pages')
    )
    illustrations = models.PositiveIntegerField(
        default=0, 
        verbose_name=_('Number of Illustrations')
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name=_('Price'),
        help_text=_('In local currency')
    )
    isbn = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name=_('ISBN'),
        help_text=_('International Standard Book Number')
    )
    genre = models.CharField(
        max_length=20,
        choices=GENRE_CHOICES,
        default='other',
        verbose_name=_('Genre')
    )
    description = models.TextField(blank=True, verbose_name=_('Description'))
    cover_image = models.ImageField(
        upload_to='book_covers/', 
        null=True, 
        blank=True,
        verbose_name=_('Cover Image')
    )
    language = models.CharField(
        max_length=50,
        default='English',
        verbose_name=_('Language')
    )
    edition = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_('Edition')
    )

    class Meta:
        verbose_name = _('Book')
        verbose_name_plural = _('Books')
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['year']),
            models.Index(fields=['isbn']),
            models.Index(fields=['genre']),
        ]
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', kwargs={'pk': self.pk})

    def clean(self):
        """Business logic validation"""
        from django.utils import timezone
        
        if self.year and self.year > timezone.now().year:
            raise ValidationError(_('Publication year cannot be in the future'))
        
        if self.pages and self.pages < 1:
            raise ValidationError(_('Number of pages must be at least 1'))
        
        if self.price and self.price < 0:
            raise ValidationError(_('Price cannot be negative'))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def author_names(self):
        return ", ".join([str(author) for author in self.authors.all()])

class Branch(BaseModel):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))
    address = models.TextField(blank=True, verbose_name=_('Address'))
    code = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name=_('Branch Code'),
        help_text=_('Internal branch identifier')
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Phone'))
    email = models.EmailField(blank=True, verbose_name=_('Email'))
    opening_hours = models.TextField(blank=True, verbose_name=_('Opening Hours'))
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_branches',
        verbose_name=_('Manager')
    )

    class Meta:
        verbose_name = _('Branch')
        verbose_name_plural = _('Branches')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('branch-detail', kwargs={'pk': self.pk})

class BookInventory(BaseModel):
    book = models.ForeignKey(
        Book, 
        on_delete=models.CASCADE, 
        related_name='inventories',
        verbose_name=_('Book')
    )
    branch = models.ForeignKey(
        Branch, 
        on_delete=models.CASCADE, 
        related_name='inventories',
        verbose_name=_('Branch')
    )
    total_copies = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total Copies')
    )
    available_copies = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Available Copies')
    )
    shelf_location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Shelf Location')
    )

    class Meta:
        verbose_name = _('Book Inventory')
        verbose_name_plural = _('Book Inventories')
        unique_together = (('book', 'branch'),)
        indexes = [
            models.Index(fields=['book', 'branch']),
            models.Index(fields=['available_copies']),
        ]

    def __str__(self):
        return f"{self.book} @ {self.branch} : {self.total_copies}"

    def clean(self):
        """Business logic validation"""
        if self.available_copies > self.total_copies:
            raise ValidationError(_('Available copies cannot exceed total copies'))
        
        if self.total_copies < 0 or self.available_copies < 0:
            raise ValidationError(_('Copy counts cannot be negative'))

    def save(self, *args, **kwargs):
        """Ensure validation runs on save"""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_available(self):
        return self.available_copies > 0

class Faculty(BaseModel):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Name'))
    code = models.CharField(max_length=50, blank=True, verbose_name=_('Faculty Code'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    dean = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dean_of_faculties',
        verbose_name=_('Dean')
    )

    class Meta:
        verbose_name = _('Faculty')
        verbose_name_plural = _('Faculties')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('faculty-detail', kwargs={'pk': self.pk})

class BookFacultyUsage(BaseModel):
    book = models.ForeignKey(
        Book, 
        on_delete=models.CASCADE, 
        related_name='usages',
        verbose_name=_('Book')
    )
    faculty = models.ForeignKey(
        Faculty, 
        on_delete=models.CASCADE, 
        related_name='book_usages',
        verbose_name=_('Faculty')
    )
    branch = models.ForeignKey(
        Branch, 
        on_delete=models.CASCADE, 
        related_name='book_usages',
        verbose_name=_('Branch')
    )
    course_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Course Code')
    )
    course_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Course Name')
    )
    semester = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Semester')
    )
    academic_year = models.CharField(
        max_length=9,
        blank=True,
        verbose_name=_('Academic Year'),
        help_text=_('Format: YYYY-YYYY')
    )

    class Meta:
        verbose_name = _('Book Faculty Usage')
        verbose_name_plural = _('Book Faculty Usages')
        unique_together = (('book', 'faculty', 'branch'),)
        indexes = [
            models.Index(fields=['book', 'faculty', 'branch']),
        ]

    def __str__(self):
        return f"{self.book} used by {self.faculty} @ {self.branch}"

    def get_absolute_url(self):
        return reverse('bookfacultyusage-detail', kwargs={'pk': self.pk})

class Student(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name=_('User')
    )
    student_id = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name=_('Student ID')
    )
    faculty = models.ForeignKey(
        Faculty, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_('Faculty')
    )
    enrollment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Enrollment Date')
    )
    graduation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Graduation Date')
    )
    current_semester = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_('Current Semester')
    )

    class Meta:
        verbose_name = _('Student')
        verbose_name_plural = _('Students')
        ordering = ['user__last_name', 'user__first_name']
        indexes = [
            models.Index(fields=['student_id']),
        ]

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name() or self.user.username}"

    def get_absolute_url(self):
        return reverse('student-detail', kwargs={'pk': self.pk})

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email

class Loan(BaseModel):
    LOAN_STATUS = (
        ('active', _('Active')),
        ('returned', _('Returned')),
        ('overdue', _('Overdue')),
        ('lost', _('Lost')),
    )
    
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE, 
        related_name='loans',
        verbose_name=_('Student')
    )
    book = models.ForeignKey(
        Book, 
        on_delete=models.CASCADE, 
        related_name='loans',
        verbose_name=_('Book')
    )
    branch = models.ForeignKey(
        Branch, 
        on_delete=models.CASCADE, 
        related_name='loans',
        verbose_name=_('Branch')
    )
    issue_date = models.DateField(verbose_name=_('Issue Date'))
    due_date = models.DateField(verbose_name=_('Due Date'))
    return_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_('Return Date')
    )
    status = models.CharField(
        max_length=10, 
        choices=LOAN_STATUS, 
        default='active',
        verbose_name=_('Status')
    )
    fine_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Fine Amount')
    )
    notes = models.TextField(blank=True, verbose_name=_('Notes'))
    issued_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_loans',
        verbose_name=_('Issued By')
    )

    class Meta:
        verbose_name = _('Loan')
        verbose_name_plural = _('Loans')
        indexes = [
            models.Index(fields=['issue_date']),
            models.Index(fields=['due_date']),
            models.Index(fields=['status']),
        ]
        ordering = ['-issue_date']

    def __str__(self):
        return f"Loan: {self.book} to {self.student} @ {self.issue_date}"

    def get_absolute_url(self):
        return reverse('loan-detail', kwargs={'pk': self.pk})

    def clean(self):
        """Business logic validation"""
        from django.utils import timezone
        
        if self.return_date and self.return_date < self.issue_date:
            raise ValidationError(_('Return date cannot be before issue date'))
        
        if self.due_date < self.issue_date:
            raise ValidationError(_('Due date cannot be before issue date'))
        
        if self.fine_amount < 0:
            raise ValidationError(_('Fine amount cannot be negative'))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.status == 'active' and timezone.now().date() > self.due_date

    @property
    def days_overdue(self):
        from django.utils import timezone
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0

class Reservation(BaseModel):
    """Model for book reservations"""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name=_('Student')
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name=_('Book')
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name=_('Branch')
    )
    reservation_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Reservation Date')
    )
    expiry_date = models.DateTimeField(
        verbose_name=_('Expiry Date')
    )
    status = models.CharField(
        max_length=20,
        choices=(
            ('pending', _('Pending')),
            ('fulfilled', _('Fulfilled')),
            ('cancelled', _('Cancelled')),
            ('expired', _('Expired')),
        ),
        default='pending',
        verbose_name=_('Status')
    )

    class Meta:
        verbose_name = _('Reservation')
        verbose_name_plural = _('Reservations')
        unique_together = (('student', 'book', 'branch'),)
        ordering = ['-reservation_date']

    def __str__(self):
        return f"Reservation: {self.book} by {self.student}"

    def clean(self):
        from django.utils import timezone
        if self.expiry_date <= timezone.now():
            raise ValidationError(_('Expiry date must be in the future'))

class Fine(BaseModel):
    """Model for tracking fines"""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='fines',
        verbose_name=_('Student')
    )
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='fines',
        verbose_name=_('Loan')
    )
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name=_('Amount')
    )
    reason = models.TextField(verbose_name=_('Reason'))
    paid = models.BooleanField(default=False, verbose_name=_('Paid'))
    paid_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Paid Date')
    )

    class Meta:
        verbose_name = _('Fine')
        verbose_name_plural = _('Fines')
        ordering = ['-created_at']

    def __str__(self):
        return f"Fine: {self.amount} for {self.student}"

    def clean(self):
        if self.amount < 0:
            raise ValidationError(_('Fine amount cannot be negative'))