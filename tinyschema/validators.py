import re
from typing import Any, Type, List, Optional

from .errors import ValidationError
from .remedies import Remedy


class Validator:
    def __init__(self, remedies: Optional[List[Remedy]] = None) -> None:
        """
        Base class for validators that can be applied to field values.

        :param remedies: Optional list of Remedy instances that can be applied to fix validation errors.
        """
        self._remedies = remedies if remedies is not None else []

    def validate(self, field_name: str, value: Any) -> Any:
        """
        Validate and remedy the given value according to the validator's rules.

        If the value fails validation, the validator will apply the remedies in order.
        Afterward, the validator checks again. If it is still invalid, ValidationError is raised.
        """
        if self._is_valid(value):
            return value

        for remedy in self._remedies:
            value = remedy.apply(field_name, value)

            if self._is_valid(value):
                return value

        raise self._make_error(field_name, value)

    def _is_valid(self, value: Any) -> bool:
        raise NotImplementedError("Subclasses must implement _is_valid.")

    def _make_error(self, field_name: str, value: Any) -> ValidationError:
        raise NotImplementedError("Subclasses must implement _make_error.")


class TypeValidator(Validator):
    """
    Validates that a value is of a specified type.

    If remedies are supplied, they can attempt to convert the value before failure.
    """

    def __init__(self, expected_type: Type, remedies: Optional[List[Remedy]] = None) -> None:
        super().__init__(remedies)
        self._expected_type = expected_type

    def _is_valid(self, value: Any) -> bool:
        return isinstance(value, self._expected_type)

    def _make_error(self, field_name: str, value: Any) -> ValidationError:
        return ValidationError(
            f"Field '{field_name}' expects type {self._expected_type.__name__}, "
            f"got {type(value).__name__}."
        )


class LengthValidator(Validator):
    """
    Validates that a string's length is within specified bounds.

    Remedies can be used to strip, truncate, pad, or otherwise transform the string.
    """

    def __init__(
        self,
        min_length: int = 0,
        max_length: Optional[int] = None,
        remedies: Optional[List[Remedy]] = None
    ) -> None:
        super().__init__(remedies)
        self._min_length = min_length
        self._max_length = max_length

    def _is_valid(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        length = len(value)

        if length < self._min_length:
            return False

        if self._max_length is not None and length > self._max_length:
            return False

        return True

    def _make_error(self, field_name: str, value: Any) -> ValidationError:
        if not isinstance(value, str):
            return ValidationError(
                f"Field '{field_name}' expects a string for length validation."
            )

        length = len(value)

        if length < self._min_length:
            return ValidationError(
                f"Field '{field_name}' length {length} is less than minimum {self._min_length}."
            )

        if self._max_length is not None and length > self._max_length:
            return ValidationError(
                f"Field '{field_name}' length {length} exceeds maximum {self._max_length}."
            )

        return ValidationError(f"Field '{field_name}' failed length validation.")


class EmailValidator(Validator):
    """
    Validates that a string is a valid email address.

    Remedies can be used to strip whitespace, lowercase, or normalize simple formatting issues.
    """

    EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    def __init__(self, remedies: Optional[List[Remedy]] = None) -> None:
        super().__init__(remedies)

    def _is_valid(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        return re.match(self.EMAIL_REGEX, value) is not None

    def _make_error(self, field_name: str, value: Any) -> ValidationError:
        if not isinstance(value, str):
            return ValidationError(
                f"Field '{field_name}' expects a string for email validation."
            )

        return ValidationError(
            f"Field '{field_name}' contains an invalid email address."
        )


class RangeValidator(Validator):
    """
    Validates that a number is within a given range.
    """

    def __init__(
        self,
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
        remedies: Optional[List[Remedy]] = None
    ) -> None:
        super().__init__(remedies)
        self._minimum = minimum
        self._maximum = maximum

    def _is_valid(self, value: Any) -> bool:
        if not isinstance(value, (int, float)):
            return False

        if self._minimum is not None and value < self._minimum:
            return False

        if self._maximum is not None and value > self._maximum:
            return False

        return True

    def _make_error(self, field_name: str, value: Any) -> ValidationError:
        if not isinstance(value, (int, float)):
            return ValidationError(
                f"Field '{field_name}' expects a number for range validation."
            )

        if self._minimum is not None and value < self._minimum:
            return ValidationError(
                f"Field '{field_name}' value {value} is less than minimum {self._minimum}."
            )

        if self._maximum is not None and value > self._maximum:
            return ValidationError(
                f"Field '{field_name}' value {value} exceeds maximum {self._maximum}."
            )

        return ValidationError(f"Field '{field_name}' failed range validation.")


class RegexValidator(Validator):
    """
    Validates that a string matches a regular expression.
    """

    def __init__(self, pattern: str, remedies: Optional[List[Remedy]] = None) -> None:
        super().__init__(remedies)
        self._pattern = pattern

    def _is_valid(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        return re.match(self._pattern, value) is not None

    def _make_error(self, field_name: str, value: Any) -> ValidationError:
        if not isinstance(value, str):
            return ValidationError(
                f"Field '{field_name}' expects a string for regex validation."
            )

        return ValidationError(
            f"Field '{field_name}' does not match the required format."
        )