class ValidationFrameworkError(Exception):
    """Base exception for validation framework errors."""


class FileReadError(ValidationFrameworkError):
    """Raised when an input file cannot be read."""


class MissingColumnError(ValidationFrameworkError):
    """Raised when a required column is missing."""


class SheetNotFoundError(ValidationFrameworkError):
    """Raised when an expected Excel sheet is unavailable."""
