from django.db import models, transaction
from django.db.models import Sum, Count, Q, F
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Book, Branch, BookInventory, Faculty, BookFacultyUsage, Student, Loan
from .exceptions import LibraryBusinessError

class InventoryService:
    """Service for inventory-related operations"""
    
    @staticmethod
    def get_copies_in_branch(book_id: int, branch_id: int) -> int:
        """
        Get total copies of a book in a specific branch
        Requirement 1: For a specified branch — count number of copies of a specified book
        """
        try:
            result = BookInventory.objects.filter(
                book_id=book_id, 
                branch_id=branch_id
            ).aggregate(total=Sum('total_copies'))
            
            return result['total'] or 0
        except Exception as e:
            raise LibraryBusinessError(f"Error getting copies count: {str(e)}")
    
    @staticmethod
    def get_available_copies_in_branch(book_id: int, branch_id: int) -> int:
        """Get available copies of a book in a specific branch"""
        try:
            result = BookInventory.objects.filter(
                book_id=book_id, 
                branch_id=branch_id
            ).aggregate(available=Sum('available_copies'))
            
            return result['available'] or 0
        except Exception as e:
            raise LibraryBusinessError(f"Error getting available copies: {str(e)}")
    
    @staticmethod
    @transaction.atomic
    def update_inventory(book_id: int, branch_id: int, delta: int) -> None:
        """Update inventory counts atomically"""
        inventory, created = BookInventory.objects.get_or_create(
            book_id=book_id,
            branch_id=branch_id,
            defaults={'total_copies': 0, 'available_copies': 0}
        )
        
        if delta > 0:
            inventory.total_copies += delta
            inventory.available_copies += delta
        elif delta < 0:
            if inventory.total_copies + delta < 0:
                raise LibraryBusinessError("Cannot have negative total copies")
            inventory.total_copies += delta
            inventory.available_copies = max(0, inventory.available_copies + delta)
        
        inventory.full_clean()
        inventory.save()

class FacultyUsageService:
    """Service for faculty usage operations"""
    
    @staticmethod
    def get_faculties_using_book_in_branch(book_id: int, branch_id: int):
        """
        Get faculties using a book in a specific branch
        Requirement 2: For a specified book — count number of faculties that use it in a given branch
        """
        try:
            return Faculty.objects.filter(
                book_usages__book_id=book_id,
                book_usages__branch_id=branch_id
            ).distinct().order_by('name')
        except Exception as e:
            raise LibraryBusinessError(f"Error getting faculty usage: {str(e)}")
    
    @staticmethod
    def get_faculty_usage_count(book_id: int, branch_id: int) -> int:
        """Get count of faculties using a book in a branch"""
        return FacultyUsageService.get_faculties_using_book_in_branch(book_id, branch_id).count()
    
    @staticmethod
    def add_faculty_usage(book_id: int, faculty_id: int, branch_id: int) -> BookFacultyUsage:
        """Add faculty usage record"""
        try:
            usage, created = BookFacultyUsage.objects.get_or_create(
                book_id=book_id,
                faculty_id=faculty_id,
                branch_id=branch_id
            )
            return usage
        except Exception as e:
            raise LibraryBusinessError(f"Error adding faculty usage: {str(e)}")

class LoanService:
    """Service for loan operations"""
    
    @staticmethod
    @transaction.atomic
    def issue_loan(student_id: int, book_id: int, branch_id: int, days: int = 14) -> Loan:
        """
        Issue a new loan with business validations
        """
        # Check if book is available
        available_copies = InventoryService.get_available_copies_in_branch(book_id, branch_id)
        if available_copies <= 0:
            raise LibraryBusinessError("No available copies of this book in the selected branch")
        
        # Check if student has active loans for same book
        active_loans = Loan.objects.filter(
            student_id=student_id,
            book_id=book_id,
            status='active'
        ).count()
        
        if active_loans > 0:
            raise LibraryBusinessError("Student already has an active loan for this book")
        
        # Create loan
        loan = Loan(
            student_id=student_id,
            book_id=book_id,
            branch_id=branch_id,
            issue_date=timezone.now().date(),
            due_date=timezone.now().date() + timezone.timedelta(days=days)
        )
        
        loan.full_clean()
        loan.save()
        
        # Update inventory
        InventoryService.update_inventory(book_id, branch_id, -1)
        
        return loan
    
    @staticmethod
    @transaction.atomic
    def return_loan(loan_id: int) -> Loan:
        """Return a loan and update inventory"""
        try:
            loan = Loan.objects.get(id=loan_id)
            
            if loan.status == 'returned':
                raise LibraryBusinessError("Loan is already returned")
            
            loan.return_date = timezone.now().date()
            loan.status = 'returned'
            loan.full_clean()
            loan.save()
            
            # Update inventory
            InventoryService.update_inventory(loan.book_id, loan.branch_id, 1)
            
            return loan
        except Loan.DoesNotExist:
            raise LibraryBusinessError("Loan not found")
    
    @staticmethod
    def get_unique_students_borrowed_book(book_id: int) -> int:
        """Get count of unique students who borrowed a specific book"""
        return Loan.objects.filter(book_id=book_id).values('student').distinct().count()
    
    @staticmethod
    def get_overdue_loans():
        """Get all overdue loans"""
        return Loan.objects.filter(
            due_date__lt=timezone.now().date(),
            status='active'
        )

class AnalyticsService:
    """Service for reporting and analytics"""
    
    @staticmethod
    def get_most_borrowed_books(limit: int = 10):
        """Get most borrowed books"""
        return Book.objects.annotate(
            loan_count=Count('loans')
        ).order_by('-loan_count')[:limit]
    
    @staticmethod
    def get_branch_utilization():
        """Get branch utilization statistics"""
        return Branch.objects.annotate(
            total_books=Sum('inventories__total_copies'),
            available_books=Sum('inventories__available_copies'),
            utilization_rate=(
                (F('total_books') - F('available_books')) / 
                F('total_books') * 100
            ) if F('total_books') > 0 else 0
        )
    
    @staticmethod
    def get_faculty_book_usage():
        """Get book usage by faculty"""
        return Faculty.objects.annotate(
            book_count=Count('book_usages', distinct=True)
        ).order_by('-book_count')

# Helper functions for the required package procedures
def get_copies_in_branch(book_id: int, branch_id: int) -> int:
    """Public interface for requirement 1"""
    return InventoryService.get_copies_in_branch(book_id, branch_id)

def get_faculties_using_book_in_branch(book_id: int, branch_id: int):
    """Public interface for requirement 2"""
    return FacultyUsageService.get_faculties_using_book_in_branch(book_id, branch_id)

def get_faculty_usage_count(book_id: int, branch_id: int) -> int:
    """Public interface for requirement 2 count"""
    return FacultyUsageService.get_faculty_usage_count(book_id, branch_id)