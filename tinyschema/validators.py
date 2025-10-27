from typing import Any, Type
from .errors import ValidationError
import re


class Validator:
    def __init__(self, attempt_fix: bool = False) -> None:
        self._attempt_fix = attempt_fix

    @property
    def attempt_fix(self) -> bool:
        return self._attempt_fix

    def validate(self, field_name: str, value: Any) -> Any:
        """
        Validate the given value.

        :param field_name: Name of the field being validated.
        :param value: The value to be validated.
        :return: The validated (and possibly transformed) value.
        :raises ValidationError: If validation fails.
        """

        raise NotImplementedError("Subclasses must implement the validate method.")


class TypeValidator(Validator):
    """
    Validates that a value is of a specified type.

    Does not accept attempt_fix; type mismatches will raise a ValidationError.

    Will perform an 'isinstance' check against the expected type.
    """

    def __init__(self, expected_type: Type) -> None:
        super().__init__(attempt_fix=False)
        self._expected_type = expected_type

    def validate(self, field_name: str, value: Any) -> Any:
        if not isinstance(value, self._expected_type):
            raise ValidationError(f"Field '{field_name}' expects type {self._expected_type.__name__}, "
                                  f"got {type(value).__name__}.")
        return value


class LengthValidator(Validator):
    """
    Validates that a string's length is within specified bounds.

    Accepts attempt_fix; if the string is too long, it will be truncated. However, if the string is too short,
    a ValidationError will be raised.
    """

    def __init__(self, min_length: int = 0, max_length: int = None, attempt_fix: bool = False) -> None:
        super().__init__(attempt_fix)
        self._min_length = min_length
        self._max_length = max_length

    def validate(self, field_name: str, value: Any) -> Any:
        if not isinstance(value, str):
            raise ValidationError(f"Field '{field_name}' expects a string for length validation.")

        length = len(value)

        if length < self._min_length:
            raise ValidationError(f"Field '{field_name}' length {length} is less than minimum {self._min_length}.")

        if self._max_length is not None and length > self._max_length:
            if self.attempt_fix:
                value = value[:self._max_length]
            else:
                raise ValidationError(f"Field '{field_name}' length {length} exceeds maximum {self._max_length}.")

        return value


class EmailValidator(Validator):
    """
    Validates that a string is a valid email address.

    Does not accept attempt_fix; invalid emails will raise a ValidationError.
    """

    def __init__(self) -> None:
        super().__init__(False)

    def validate(self, field_name: str, value: Any) -> Any:
        if not isinstance(value, str):
            raise ValidationError(f"Field '{field_name}' expects a string for email validation.")

        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

        if not re.match(email_regex, value):
            raise ValidationError(f"Field '{field_name}' contains an invalid email address.")

        return value
