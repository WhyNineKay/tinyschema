import re
from typing import Any, Type, Optional, Callable


class Remedy:
    @classmethod
    def apply(cls, field_name: str, value: Any) -> Any:
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
        self._max_length = max_length

    def apply(self, field_name: str, value: Any) -> Any:
        if isinstance(value, str):
            return value[:self._max_length]
        return value


class PadStringRemedy(Remedy):
    def __init__(self, min_length: int, padding: str = " ") -> None:
        self._min_length = min_length
        self._padding = padding

    def apply(self, field_name: str, value: Any) -> Any:
        if not isinstance(value, str):
            return value

        if len(value) >= self._min_length:
            return value

        missing = self._min_length - len(value)
        return value + (self._padding * missing)


class ReplaceStringRemedy(Remedy):
    def __init__(self, old: str, new: str) -> None:
        self._old = old
        self._new = new

    def apply(self, field_name: str, value: Any) -> Any:
        if isinstance(value, str):
            return value.replace(self._old, self._new)
        return value


class RegexSubRemedy(Remedy):
    def __init__(self, pattern: str, replacement: str) -> None:
        self._pattern = pattern
        self._replacement = replacement

    def apply(self, field_name: str, value: Any) -> Any:
        if isinstance(value, str):
            return re.sub(self._pattern, self._replacement, value)
        return value


class TypeCastRemedy(Remedy):
    def __init__(self, target_type: Type) -> None:
        self._target_type = target_type

    def apply(self, field_name: str, value: Any) -> Any:
        try:
            return self._target_type(value)
        except (ValueError, TypeError):
            return value


class ClampNumberRemedy(Remedy):
    def __init__(self, minimum: Optional[float] = None, maximum: Optional[float] = None) -> None:
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
        self._func = func

    def apply(self, field_name: str, value: Any) -> Any:
        return self._func(field_name, value)

