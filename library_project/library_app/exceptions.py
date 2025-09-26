class LibraryBusinessError(Exception):
    """Base exception for library business rule violations"""
    pass

class InventoryError(LibraryBusinessError):
    """Inventory-related business errors"""
    pass

class LoanError(LibraryBusinessError):
    """Loan-related business errors"""
    pass

class ValidationError(LibraryBusinessError):
    """Validation errors"""
    pass