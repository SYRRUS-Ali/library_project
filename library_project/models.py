from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class LibraryBusinessError(Exception):
    """Пользовательское исключение для ошибок бизнес-логики библиотеки"""
    pass

class Author(models.Model):
    """Модель автора книги"""
    last_name = models.CharField(_('фамилия'), max_length=100)
    first_name = models.CharField(_('имя'), max_length=100)
    middle_name = models.CharField(_('отчество'), max_length=100, blank=True, null=True)
    nickname = models.CharField(_('Nickname'), max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = _('автор')
        verbose_name_plural = _('авторы')
        ordering = ['last_name', 'first_name']
        unique_together = ['last_name', 'first_name', 'middle_name']
    
    def __str__(self):
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"
    
    def clean(self):
        """Валидация данных автора"""
        if not self.last_name.strip():
            raise ValidationError({'last_name': _('Фамилия автора обязательна')})
        if not self.first_name.strip():
            raise ValidationError({'first_name': _('Имя автора обязательно')})

class Publisher(models.Model):
    """Модель издательства"""
    name = models.CharField(_('название'), max_length=200, unique=True)
    address = models.TextField(_('адрес'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('издательство')
        verbose_name_plural = _('издательства')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Валидация данных издательства"""
        if not self.name.strip():
            raise ValidationError({'name': _('Название издательства обязательно')})

class Book(models.Model):
    """Модель книги"""
    title = models.CharField(_('название'), max_length=300)
    authors = models.ManyToManyField(Author, verbose_name=_('авторы'), related_name='books')
    isbn = models.CharField(max_length=20, null=True, blank=True)
    publisher = models.ForeignKey(
        Publisher, 
        verbose_name=_('издательство'), 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    publication_year = models.PositiveIntegerField(
        _('год издания'), 
        null=True, 
        blank=True,
        help_text=_('Год издания книги')
    )
    page_count = models.PositiveIntegerField(
        _('количество страниц'), 
        default=1,
        help_text=_('Общее количество страниц в книге')
    )
    illustration_count = models.PositiveIntegerField(
        _('количество иллюстраций'), 
        default=0,
        help_text=_('Количество иллюстраций в книге')
    )
    price = models.DecimalField(
        _('стоимость'), 
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text=_('Стоимость книги в рублях')
    )
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('книга')
        verbose_name_plural = _('книги')
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['publication_year']),
        ]
    
    def __str__(self):
        year_display = self.publication_year if self.publication_year else 'н/д'
        return f"{self.title} ({year_display})"
    
    def clean(self):
        """Валидация данных книги"""
        if not self.title.strip():
            raise ValidationError({'title': _('Название книги обязательно')})
        if self.publication_year and (self.publication_year < 1000 or self.publication_year > 2100):
            raise ValidationError({'publication_year': _('Год издания должен быть между 1000 и 2100')})
        if self.page_count < 1:
            raise ValidationError({'page_count': _('Количество страниц должно быть больше 0')})
        if self.price < 0:
            raise ValidationError({'price': _('Стоимость не может быть отрицательной')})
    
    def get_authors_display(self):
        """Возвращает строку с авторами книги"""
        return ", ".join(str(author) for author in self.authors.all())

class Branch(models.Model):
    """Модель филиала библиотеки"""
    name = models.CharField(_('название'), max_length=200, unique=True)
    address = models.TextField(_('адрес'), blank=True, null=True)
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('филиал')
        verbose_name_plural = _('филиалы')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Валидация данных филиала"""
        if not self.name.strip():
            raise ValidationError({'name': _('Название филиала обязательно')})

class BookInventory(models.Model):
    """Модель инвентаризации книг в филиалах"""
    book = models.ForeignKey(
        Book, 
        verbose_name=_('книга'), 
        on_delete=models.CASCADE, 
        related_name='inventory'
    )
    branch = models.ForeignKey(
        Branch, 
        verbose_name=_('филиал'), 
        on_delete=models.CASCADE, 
        related_name='inventory'
    )
    total_copies = models.PositiveIntegerField(
        _('общее количество экземпляров'), 
        default=0
    )
    available_copies = models.PositiveIntegerField(
        _('доступное количество экземпляров'), 
        default=0
    )
    last_updated = models.DateTimeField(_('последнее обновление'), auto_now=True)
    
    class Meta:
        verbose_name = _('инвентаризация')
        verbose_name_plural = _('инвентаризация')
        unique_together = ['book', 'branch']
        ordering = ['branch', 'book']
    
    def __str__(self):
        return f"{self.book.title} в {self.branch.name}: {self.available_copies}/{self.total_copies}"
    
    def clean(self):
        """Валидация данных инвентаризации"""
        if self.available_copies > self.total_copies:
            raise ValidationError({
                'available_copies': _('Доступные экземпляры не могут превышать общее количество')
            })
        if self.total_copies < 0:
            raise ValidationError({
                'total_copies': _('Общее количество экземпляров не может быть отрицательным')
            })
    
    def save(self, *args, **kwargs):
        """Переопределение save для автоматической валидации"""
        self.full_clean()
        super().save(*args, **kwargs)

class Faculty(models.Model):
    """Модель факультета"""
    name = models.CharField(_('название'), max_length=200, unique=True)
    description = models.TextField(_('описание'), blank=True, null=True)
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('факультет')
        verbose_name_plural = _('факультеты')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Валидация данных факультета"""
        if not self.name.strip():
            raise ValidationError({'name': _('Название факультета обязательно')})

class BookFacultyUsage(models.Model):
    """Модель использования книги факультетом в филиале"""
    book = models.ForeignKey(
        Book, 
        verbose_name=_('книга'), 
        on_delete=models.CASCADE, 
        related_name='faculty_usage'
    )
    branch = models.ForeignKey(
        Branch, 
        verbose_name=_('филиал'), 
        on_delete=models.CASCADE, 
        related_name='faculty_usage'
    )
    faculty = models.ForeignKey(
        Faculty, 
        verbose_name=_('факультет'), 
        on_delete=models.CASCADE, 
        related_name='book_usage'
    )
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('использование книги факультетом')
        verbose_name_plural = _('использование книг факультетами')
        unique_together = ['book', 'branch', 'faculty']
        ordering = ['faculty', 'book']
    
    def __str__(self):
        return f"{self.faculty.name} использует {self.book.title} в {self.branch.name}"
    
    def clean(self):
        """Валидация данных использования"""
        # Проверка, что книга есть в инвентаре филиала
        if not BookInventory.objects.filter(book=self.book, branch=self.branch).exists():
            raise ValidationError(_('Книга не найдена в инвентаре указанного филиала'))

class Student(models.Model):
    """Модель студента"""
    last_name = models.CharField(_('фамилия'), max_length=100)
    first_name = models.CharField(_('имя'), max_length=100)
    student_id = models.CharField(_('номер студенческого билета'), max_length=20, unique=True)
    faculty = models.ForeignKey(
        Faculty, 
        verbose_name=_('факультет'), 
        on_delete=models.CASCADE, 
        related_name='students'
    )
    created_at = models.DateTimeField(_('дата создания'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('студент')
        verbose_name_plural = _('студенты')
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['last_name', 'first_name']),
        ]
    
    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.student_id})"
    
    def clean(self):
        """Валидация данных студента"""
        if not self.last_name.strip():
            raise ValidationError({'last_name': _('Фамилия студента обязательна')})
        if not self.first_name.strip():
            raise ValidationError({'first_name': _('Имя студента обязательно')})
        if not self.student_id.strip():
            raise ValidationError({'student_id': _('Номер студенческого билета обязателен')})
    
    def get_full_name(self):
        """Возвращает полное имя студента"""
        return f"{self.last_name} {self.first_name}"

class Loan(models.Model):
    """Модель выдачи книги студенту"""
    student = models.ForeignKey(
        Student, 
        verbose_name=_('студент'), 
        on_delete=models.CASCADE, 
        related_name='loans'
    )
    book = models.ForeignKey(
        Book, 
        verbose_name=_('книга'), 
        on_delete=models.CASCADE, 
        related_name='loans'
    )
    branch = models.ForeignKey(
        Branch, 
        verbose_name=_('филиал'), 
        on_delete=models.CASCADE, 
        related_name='loans'
    )
    issue_date = models.DateTimeField(_('дата выдачи'), auto_now_add=True)
    return_date = models.DateTimeField(_('дата возврата'), blank=True, null=True)
    is_returned = models.BooleanField(_('возвращена'), default=False)
    created_by = models.ForeignKey(
        User, 
        verbose_name=_('создано пользователем'), 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_loans'
    )
    
    class Meta:
        verbose_name = _('выдача')
        verbose_name_plural = _('выдачи')
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['issue_date']),
            models.Index(fields=['is_returned']),
        ]
    
    def __str__(self):
        status = "возвращена" if self.is_returned else "не возвращена"
        return f"{self.student} - {self.book} ({status})"
    
    def clean(self):
        """Валидация данных выдачи"""
        # Проверка доступности книги в филиале
        if not self.pk:  # Только для новых выдач
            try:
                inventory = BookInventory.objects.get(book=self.book, branch=self.branch)
                if inventory.available_copies <= 0:
                    raise ValidationError(_('Нет доступных экземпляров этой книги в указанном филиале'))
            except BookInventory.DoesNotExist:
                raise ValidationError(_('Книга не найдена в инвентаре указанного филиала'))
        
        # Проверка дат
        if self.return_date and self.return_date < self.issue_date:
            raise ValidationError({'return_date': _('Дата возврата не может быть раньше даты выдачи')})
    
    def save(self, *args, **kwargs):
        """Переопределение save для обработки бизнес-логики"""
        is_new = self.pk is None
        
        if is_new:
            # Уменьшаем количество доступных экземпляров
            inventory = BookInventory.objects.get(book=self.book, branch=self.branch)
            if inventory.available_copies <= 0:
                raise LibraryBusinessError(_('Нет доступных экземпляров для выдачи'))
            
            inventory.available_copies -= 1
            inventory.save()
        
        elif self.is_returned and not self.return_date:
            # Автоматически устанавливаем дату возврата при отметке о возврате
            from django.utils import timezone
            self.return_date = timezone.now()
            
            # Увеличиваем количество доступных экземпляров
            inventory = BookInventory.objects.get(book=self.book, branch=self.branch)
            inventory.available_copies += 1
            inventory.save()
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Переопределение delete для корректного управления инвентарем"""
        if not self.is_returned:
            # Увеличиваем количество доступных экземпляров при удалении не возвращенной книги
            inventory = BookInventory.objects.get(book=self.book, branch=self.branch)
            inventory.available_copies += 1
            inventory.save()
        
        super().delete(*args, **kwargs)
