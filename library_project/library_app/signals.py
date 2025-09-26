from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import BookInventory, Loan
from .exceptions import LibraryBusinessError

@receiver(pre_save, sender=BookInventory)
def validate_book_inventory(sender, instance, **kwargs):
    """
    Signal to validate book inventory before saving
    Requirement 5: Implement hooks/triggers for business logic
    """
    if instance.total_copies < 0:
        raise LibraryBusinessError('Total copies cannot be negative')
    
    if instance.available_copies < 0:
        raise LibraryBusinessError('Available copies cannot be negative')
    
    if instance.available_copies > instance.total_copies:
        raise LibraryBusinessError('Available copies cannot exceed total copies')

@receiver(pre_save, sender=Loan)
def validate_loan_dates(sender, instance, **kwargs):
    """
    Validate loan dates before saving
    Requirement 5: Implement hooks/triggers for business logic
    """
    if instance.return_date and instance.return_date < instance.issue_date:
        raise LibraryBusinessError('Return date cannot be before issue date')
    
    if instance.due_date < instance.issue_date:
        raise LibraryBusinessError('Due date cannot be before issue date')

@receiver(post_save, sender=Loan)
def update_loan_status(sender, instance, created, **kwargs):
    """
    Update loan status based on dates after saving
    Requirement 5: Implement hooks/triggers for business logic
    """
    from django.utils import timezone
    
    if instance.return_date:
        instance.status = 'returned'
    elif timezone.now().date() > instance.due_date:
        instance.status = 'overdue'
    else:
        instance.status = 'active'
    
    # Avoid infinite recursion
    if instance.status != instance._original_status:
        instance.save(update_fields=['status'])

@receiver(pre_save)
def store_original_status(sender, instance, **kwargs):
    """
    Store original status for comparison
    """
    if sender == Loan and instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            instance._original_status = original.status
        except sender.DoesNotExist:
            instance._original_status = instance.status
    else:
        instance._original_status = getattr(instance, 'status', None)