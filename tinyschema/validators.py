import re
from abc import ABC, abstractmethod
from typing import Any

from .errors import ValidationError
from .remedies import Remedy


class Validator(ABC):
    def __init__(self, remedies: list[Remedy] | None = None) -> None:
        """
        Base class for validators that can be applied to field values.

        :param remedies: Remedies that may fix invalid values.
        """
        if remedies is None:
            self._remedies: list[Remedy] = []
        elif isinstance(remedies, list) and all(
            isinstance(remedy, Remedy) for remedy in remedies
        ):
            self._remedies = remedies
        else:
            raise TypeError("Parameter 'remedies' must be a list of Remedy instances.")

    def validate(self, field_name: str, value: Any) -> Any:
        """
        Validate and remedy the given value according to the validator's rules.

        Remedies are applied in order until the value becomes valid. A value
        that remains invalid raises ValidationError.
        """
        if self._is_valid(value):
            return value

        for remedy in self._remedies:
            value = remedy.apply(field_name, value)

            if self._is_valid(value):
                return value

        raise self._make_error(field_name, value)

    @abstractmethod
    def _is_valid(self, value: Any) -> bool:
        raise NotImplementedError("Subclasses must implement _is_valid.")

    @abstractmethod
    def _make_error(self, field_name: str, value: Any) -> ValidationError:
        raise NotImplementedError("Subclasses must implement _make_error.")


class TypeValidator(Validator):
    """
    Validates that a value is of a specified type.

    If remedies are supplied, they can attempt to convert the value before failure.
    """

    def __init__(
        self,
        expected_type: type[Any],
        remedies: list[Remedy] | None = None,
    ) -> None:
        super().__init__(remedies)
        if expected_type is Any or not isinstance(expected_type, type):
            raise TypeError("Parameter 'expected_type' must be a type.")
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
        max_length: int | None = None,
        remedies: list[Remedy] | None = None,
    ) -> None:
        super().__init__(remedies)
        if not isinstance(min_length, int) or isinstance(min_length, bool):
            raise TypeError("Parameter 'min_length' must be an integer.")
        if max_length is not None and (
            not isinstance(max_length, int) or isinstance(max_length, bool)
        ):
            raise TypeError("Parameter 'max_length' must be an integer or None.")
        if min_length < 0:
            raise ValueError("Parameter 'min_length' cannot be negative.")
        if max_length is not None and max_length < min_length:
            raise ValueError("Parameter 'max_length' cannot be less than 'min_length'.")
        self._min_length = min_length
        self._max_length = max_length

    def _is_valid(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        length = len(value)

        if length < self._min_length:
            return False

        return self._max_length is None or length <= self._max_length

    def _make_error(self, field_name: str, value: Any) -> ValidationError:
        if not isinstance(value, str):
            return ValidationError(
                f"Field '{field_name}' expects a string for length validation."
            )

        length = len(value)

        if length < self._min_length:
            return ValidationError(
                f"Field '{field_name}' length {length} is less than "
                f"minimum {self._min_length}."
            )

        if self._max_length is not None and length > self._max_length:
            return ValidationError(
                f"Field '{field_name}' length {length} exceeds "
                f"maximum {self._max_length}."
            )

        return ValidationError(f"Field '{field_name}' failed length validation.")


class EmailValidator(Validator):
    """
    Validates that a string is a valid email address.

    Remedies can normalize simple formatting issues before failure.
    """

    EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

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
        minimum: float | None = None,
        maximum: float | None = None,
        remedies: list[Remedy] | None = None,
    ) -> None:
        super().__init__(remedies)
        for name, bound in (("minimum", minimum), ("maximum", maximum)):
            if bound is not None and (
                not isinstance(bound, (int, float)) or isinstance(bound, bool)
            ):
                raise TypeError(f"Parameter '{name}' must be a number or None.")
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError("Parameter 'minimum' cannot exceed 'maximum'.")
        self._minimum = minimum
        self._maximum = maximum

    def _is_valid(self, value: Any) -> bool:
        if not isinstance(value, (int, float)):
            return False

        if self._minimum is not None and value < self._minimum:
            return False

        return self._maximum is None or value <= self._maximum

    def _make_error(self, field_name: str, value: Any) -> ValidationError:
        if not isinstance(value, (int, float)):
            return ValidationError(
                f"Field '{field_name}' expects a number for range validation."
            )

        if self._minimum is not None and value < self._minimum:
            return ValidationError(
                f"Field '{field_name}' value {value} is less than "
                f"minimum {self._minimum}."
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

    def __init__(self, pattern: str, remedies: list[Remedy] | None = None) -> None:
        super().__init__(remedies)
        if not isinstance(pattern, str):
            raise TypeError("Parameter 'pattern' must be a string.")
        self._compiled_pattern = re.compile(pattern)

    def _is_valid(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False

        return self._compiled_pattern.match(value) is not None

    def _make_error(self, field_name: str, value: Any) -> ValidationError:
        if not isinstance(value, str):
            return ValidationError(
                f"Field '{field_name}' expects a string for regex validation."
            )

        return ValidationError(
            f"Field '{field_name}' does not match the required format."
        )
