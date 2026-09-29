from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import Any

from ._sentinels import MISSING
from .errors import FieldRequiredError, FieldTypeError, ValidationError
from .validators import Validator


class Field:
    """Describe and validate one value in a schema."""

    def __init__(
        self,
        name: str,
        item_type: type[Any],
        required: bool = False,
        validators: list[Validator] | None = None,
        nested_fields: list[Field] | None = None,
        iterable_template: Field | None = None,
        default: Any = MISSING,
        default_factory: Callable[[], Any] | None = None,
    ) -> None:
        self._name = self._validate_name(name)
        self._item_type = self._validate_item_type(item_type)
        self._required = self._validate_required(required)
        self._validators = self._validate_validators(validators)
        self._nested_fields = self._validate_nested_fields(nested_fields)
        self._iterable_template = self._validate_iterable_template(iterable_template)
        self._default, self._has_default = self._resolve_default(
            default,
            default_factory,
        )

        self._validate_configuration()
        self._allows_none = self._has_default and self._default is None
        self._validate_and_normalize_default()

    @staticmethod
    def _validate_name(name: str) -> str:
        if not isinstance(name, str):
            raise TypeError("Parameter 'name' must be a string.")
        return name

    @staticmethod
    def _validate_item_type(item_type: type[Any]) -> type[Any]:
        if item_type is Any or not isinstance(item_type, type):
            raise TypeError("Parameter 'item_type' must be a type.")
        return item_type

    @staticmethod
    def _validate_required(required: bool) -> bool:
        if not isinstance(required, bool):
            raise TypeError("Parameter 'required' must be of type bool.")
        return required

    @staticmethod
    def _validate_validators(
        validators: list[Validator] | None,
    ) -> list[Validator]:
        if validators is None:
            return []
        if not isinstance(validators, list) or not all(
            isinstance(validator, Validator) for validator in validators
        ):
            raise TypeError(
                "Parameter 'validators' must be a list of Validator instances."
            )
        return validators

    @staticmethod
    def _validate_nested_fields(
        nested_fields: list[Field] | None,
    ) -> list[Field]:
        if nested_fields is None:
            return []
        if not isinstance(nested_fields, list) or not all(
            isinstance(field, Field) for field in nested_fields
        ):
            raise TypeError(
                "Parameter 'nested_fields' must be a list of Field instances."
            )
        return nested_fields

    @staticmethod
    def _validate_iterable_template(iterable_template: Field | None) -> Field | None:
        if iterable_template is not None and not isinstance(iterable_template, Field):
            raise TypeError("Parameter 'iterable_template' must be a Field instance.")
        return iterable_template

    @staticmethod
    def _resolve_default(
        default: Any,
        default_factory: Callable[[], Any] | None,
    ) -> tuple[Any, bool]:
        default_was_supplied = default is not MISSING
        if default_was_supplied and default_factory is not None:
            raise ValueError(
                "Cannot specify both 'default' and 'default_factory'. "
                "Use one or the other."
            )
        if default_factory is None:
            return default, default_was_supplied
        if not callable(default_factory):
            raise TypeError(
                "Parameter 'default_factory' must be a callable that returns "
                "a default value."
            )
        # Factories are intentionally resolved once; missing values receive a
        # deep copy of the normalized result.
        return default_factory(), True

    def _validate_configuration(self) -> None:
        if self._nested_fields and self._validators:
            raise ValueError("Field using 'nested_fields' cannot have 'validators'.")
        if self._nested_fields and self._iterable_template:
            raise ValueError(
                "Field cannot have both 'nested_fields' and 'iterable_template'."
            )
        if self._required and self._has_default:
            raise ValueError("Field that is required cannot have a 'default' value.")
        if not self._required and not self._has_default:
            raise ValueError("Field that is not required must have a 'default' value.")

    def _validate_and_normalize_default(self) -> None:
        if not self._has_default:
            return
        try:
            self._default = self._parse_present_value(self._default)
        except (FieldRequiredError, FieldTypeError, ValidationError) as error:
            raise ValueError(
                f"Default value for field '{self._name}' does not conform "
                f"to the field schema: {error}"
            ) from error

    @property
    def name(self) -> str:
        return self._name

    @property
    def item_type(self) -> type[Any]:
        return self._item_type

    @property
    def required(self) -> bool:
        return self._required

    @property
    def validators(self) -> list[Validator]:
        return self._validators

    @property
    def nested_fields(self) -> list[Field]:
        return self._nested_fields

    @property
    def iterable_template(self) -> Field | None:
        return self._iterable_template

    @property
    def default(self) -> Any:
        return None if self._default is MISSING else self._default

    @property
    def has_default(self) -> bool:
        return self._has_default

    def __repr__(self) -> str:
        return (
            f"Field(name={self._name!r}, item_type={self._item_type.__name__}, "
            f"required={self._required}, default={self._default!r})"
        )

    def __str__(self) -> str:
        return f"Field({self._name!r})"

    def parse(self, value: Any) -> Any:
        """Validate and normalize a supplied or missing field value."""
        if value is MISSING:
            if self._required:
                raise FieldRequiredError(
                    f"Field '{self._name}' is required but missing."
                )
            return deepcopy(self._default)

        return self._parse_present_value(value)

    def _parse_present_value(self, value: Any) -> Any:
        if value is None and self._allows_none:
            return None

        if not isinstance(value, self._item_type):
            raise FieldTypeError(
                f"Field '{self._name}' expects type {self._item_type.__name__}, "
                f"got {type(value).__name__}."
            )

        if self._iterable_template is not None:
            return self._parse_iterable(value)
        if self._nested_fields:
            return self._parse_nested(value)
        return self._apply_validators(value)

    def _parse_iterable(self, value: Any) -> list[Any]:
        if not isinstance(value, (list, tuple, set)):
            raise FieldTypeError(
                f"Field '{self._name}' expects a list, tuple or set for iterable "
                f"fields, got {type(value).__name__}."
            )
        assert self._iterable_template is not None
        return [self._iterable_template.parse(item) for item in value]

    def _parse_nested(self, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise FieldTypeError(
                f"Field '{self._name}' expects a dict for nested fields, "
                f"got {type(value).__name__}."
            )
        return {
            field.name: field.parse(value.get(field.name, MISSING))
            for field in self._nested_fields
        }

    def _apply_validators(self, value: Any) -> Any:
        for validator in self._validators:
            value = validator.validate(self._name, value)
        return value
