import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


class Remedy(ABC):
    @abstractmethod
    def apply(self, field_name: str, value: Any) -> Any:
        """
        Apply the remedy to the given value.

        :param field_name: Name of the field being remedied.
        :param value: The value to be remedied.
        :return: The transformed value.
        :raises NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the apply method.")


class StripWhitespaceRemedy(Remedy):
    def apply(self, field_name: str, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip()
        return value


class LowercaseRemedy(Remedy):
    def apply(self, field_name: str, value: Any) -> Any:
        if isinstance(value, str):
            return value.lower()
        return value


class UppercaseRemedy(Remedy):
    def apply(self, field_name: str, value: Any) -> Any:
        if isinstance(value, str):
            return value.upper()
        return value


class TitleCaseRemedy(Remedy):
    def apply(self, field_name: str, value: Any) -> Any:
        if isinstance(value, str):
            return value.title()
        return value


class TruncateStringRemedy(Remedy):
    def __init__(self, max_length: int) -> None:
        if not isinstance(max_length, int) or isinstance(max_length, bool):
            raise TypeError("Parameter 'max_length' must be an integer.")
        if max_length < 0:
            raise ValueError("Parameter 'max_length' cannot be negative.")
        self._max_length = max_length

    def apply(self, field_name: str, value: Any) -> Any:
        if isinstance(value, str):
            return value[: self._max_length]
        return value


class PadStringRemedy(Remedy):
    def __init__(self, min_length: int, padding: str = " ") -> None:
        if not isinstance(min_length, int) or isinstance(min_length, bool):
            raise TypeError("Parameter 'min_length' must be an integer.")
        if min_length < 0:
            raise ValueError("Parameter 'min_length' cannot be negative.")
        if not isinstance(padding, str):
            raise TypeError("Parameter 'padding' must be a string.")
        if not padding:
            raise ValueError("Parameter 'padding' cannot be empty.")
        self._min_length = min_length
        self._padding = padding

    def apply(self, field_name: str, value: Any) -> Any:
        if not isinstance(value, str):
            return value

        if len(value) >= self._min_length:
            return value

        missing = self._min_length - len(value)
        repeated_padding = self._padding * ((missing // len(self._padding)) + 1)
        return value + repeated_padding[:missing]


class ReplaceStringRemedy(Remedy):
    def __init__(self, old: str, new: str) -> None:
        if not isinstance(old, str) or not isinstance(new, str):
            raise TypeError("Parameters 'old' and 'new' must be strings.")
        self._old = old
        self._new = new

    def apply(self, field_name: str, value: Any) -> Any:
        if isinstance(value, str):
            return value.replace(self._old, self._new)
        return value


class RegexSubRemedy(Remedy):
    def __init__(self, pattern: str, replacement: str) -> None:
        if not isinstance(pattern, str) or not isinstance(replacement, str):
            raise TypeError("Parameters 'pattern' and 'replacement' must be strings.")
        self._replacement = replacement
        self._compiled_pattern = re.compile(pattern)

    def apply(self, field_name: str, value: Any) -> Any:
        if isinstance(value, str):
            return self._compiled_pattern.sub(self._replacement, value)
        return value


class TypeCastRemedy(Remedy):
    def __init__(self, target_type: type[Any]) -> None:
        if target_type is Any or not isinstance(target_type, type):
            raise TypeError("Parameter 'target_type' must be a type.")
        self._target_type = target_type

    def apply(self, field_name: str, value: Any) -> Any:
        try:
            return self._target_type(value)
        except (ValueError, TypeError):
            return value


class ClampNumberRemedy(Remedy):
    def __init__(
        self,
        minimum: float | None = None,
        maximum: float | None = None,
    ) -> None:
        for name, bound in (("minimum", minimum), ("maximum", maximum)):
            if bound is not None and (
                not isinstance(bound, (int, float)) or isinstance(bound, bool)
            ):
                raise TypeError(f"Parameter '{name}' must be a number or None.")
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError("Parameter 'minimum' cannot exceed 'maximum'.")
        self._minimum = minimum
        self._maximum = maximum

    def apply(self, field_name: str, value: Any) -> Any:
        if not isinstance(value, (int, float)):
            return value

        if self._minimum is not None and value < self._minimum:
            value = self._minimum

        if self._maximum is not None and value > self._maximum:
            value = self._maximum

        return value


class EmailNormalizeRemedy(Remedy):
    def apply(self, field_name: str, value: Any) -> Any:
        if not isinstance(value, str):
            return value

        value = value.strip()
        value = value.lower()
        value = value.replace(" ", "")

        return value


class CustomRemedy(Remedy):
    def __init__(self, func: Callable[[str, Any], Any]) -> None:
        if not callable(func):
            raise TypeError("Parameter 'func' must be callable.")
        self._func = func

    def apply(self, field_name: str, value: Any) -> Any:
        return self._func(field_name, value)
