class TinySchemaError(Exception):
    """Base class for all TinySchema errors."""

    pass


class FieldError(TinySchemaError):
    """Base class for all Field-related errors."""

    pass


class FieldRequiredError(FieldError):
    """Raised when a required field is missing."""

    pass


class FieldTypeError(FieldError):
    """Raised when a field has an incorrect type."""

    pass


class ValidationError(TinySchemaError):
    """Raised when validation fails."""

    pass
