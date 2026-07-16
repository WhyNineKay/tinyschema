from copy import deepcopy
from typing import List, Any, Optional, Dict, Union, Callable, Type

from .errors import FieldRequiredError, FieldTypeError, ValidationError
from .validators import Validator

"""
ItemField > Field without key. Only used in lists.
Field > Field with key. Used in dicts and as nested fields in ItemField.
IterableField > Field for lists. Contains an ItemField to define the schema for items in the list.
"""


class Field:
    def __init__(self,
                 name: str,
                 item_type: Optional[Type],
                 required: Optional[bool] = None,
                 validators: Optional[List[Validator]] = None,
                 nested_fields: Optional[List['Field']] = None,
                 iterable_template: Optional['Field'] = None,
                 default: Any = None,
                 default_factory: Optional[Callable[[], Any]] = None
                 ) -> None:
        """
        :param name: Name of the key in the data dictionary.
        :param required: Whether the field is required or not. Defaults to False.
        :param validators: List of Validator instances to validate the field's value.
        :param nested_fields: List of nested Field instances for validating nested dictionaries.
        :param iterable_template: A template Field for validating items in a list. Only used for iterable fields.
        :param default: Default value if the field is not required.
        :param default_factory: A callable that returns the default value if the field is not required.
        :raises TypeError: If parameters are of incorrect types.
        :raises ValueError: If there are conflicting parameters.

        The default value becomes redundant if the field is required.

        A Field that is required cannot have a default value.
        Conversely, a Field that is not required must have a default value.

        A Field that uses nested_fields cannot have validators, as validation is handled by the nested fields.
        """

        if isinstance(name, str):
            self._name = name
        else:
            raise TypeError("Parameter 'name' must be a string.")

        if item_type is not None and not isinstance(item_type, type):
            raise TypeError("Parameter 'item_type' must be a type")

        self._item_type = item_type

        if required is None:
            self._required = False
        elif isinstance(required, bool):
            self._required = required
        else:
            raise TypeError("Parameter 'required' must be of type bool.")

        if validators is None:
            self._validators = []
        elif isinstance(validators, list) and all(isinstance(v, Validator) for v in validators):
            self._validators = validators
        else:
            raise TypeError("Parameter 'validators' must be a list of Validator instances.")

        if nested_fields is None:
            self._nested_fields = []
        elif isinstance(nested_fields, list) and all(isinstance(f, Field) for f in nested_fields):
            self._nested_fields = nested_fields
        else:
            raise TypeError("Parameter 'nested_fields' must be a list of Field instances.")


        if iterable_template is not None and not isinstance(iterable_template, Field):
            raise TypeError("Parameter 'iterable_template' must be a Field instance.")

        self._iterable_template = iterable_template

        if default_factory is not None:
            if not callable(default_factory):
                raise TypeError("Parameter 'default_factory' must be a callable that returns a default value.")

            self._default = default_factory()
        else:
            self._default = default

        if default is not None and default_factory is not None:
            raise ValueError("Cannot specify both 'default' and 'default_factory'. Use one or the other.")

        # Check for redundant parameters
        if self._nested_fields and self._validators:
            raise ValueError("Field using 'nested_fields' cannot have 'validators'.")

        if self._required and self._default is not None:
            raise ValueError("Field that is required cannot have a 'default' value.")
        if not self._required and self._default is None:
            raise ValueError("Field that is not required must have a 'default' value.")


        # Pick either nested fields or iterable_template, but not both
        if self._nested_fields and self._iterable_template:
            raise ValueError("Field cannot have both 'nested_fields' and 'iterable_template'.")

        # Pre-parse the default value against validators if applicable
        if self._default is not None:
            if self._nested_fields:
                try:
                    self._default = self._pre_parse_nested_default()
                except (FieldRequiredError, FieldTypeError, ValidationError) as e:
                    raise ValueError(
                        f"Default value for field '{self._name}' does not conform to the nested schema: {e}"
                    )
            else:
                try:
                    self._default = self._pre_parse_default_against_validators()
                except ValidationError as e:
                    raise ValueError(
                        f"Default value for field '{self._name}' does not conform to the specified validators: {e}"
                    )

    @property
    def name(self) -> str:
        return self._name

    @property
    def item_type(self) -> Optional[Type]:
        return self._item_type

    @property
    def required(self) -> bool:
        return self._required

    @property
    def validators(self) -> List[Validator]:
        return self._validators

    @property
    def nested_fields(self) -> List['Field']:
        return self._nested_fields

    @property
    def default(self) -> Any:
        return self._default

    def __repr__(self) -> str:
        return (f"Field(name={self._name}, required={self._required}, "
                f"validators={self._validators}, nested_fields={self._nested_fields}, "
                f"default={self._default})")

    def __str__(self) -> str:
        return f"Field('{self._name}')"

    def _pre_parse_default_against_validators(self) -> Any:
        """
        Pre-parse the default value against the field's validators.

        :return: The validated (and possibly transformed) default value.
        :raises ValidationError: If a validator fails on the default value.
        """
        value = self._default

        for validator in self._validators:
            value = validator.validate(self.name, value)

        return value

    def _pre_parse_nested_default(self) -> Any:
        """Validate and normalize the default value for nested fields."""
        default_value = self._default

        if not isinstance(default_value, dict):
            raise FieldTypeError(
                f"Field '{self._name}' expects default value to be a dict for nested fields."
            )

        parsed_value = {}

        for field in self._nested_fields:
            nested_value = default_value.get(field.name, None)
            parsed_value[field.name] = field.parse(nested_value)

        return parsed_value

    def parse(self, value: Any) -> Any:
        """
        Parse and validate the given value according to the field's configuration.

        :param value: The value to be parsed and validated.
        :return: The validated (and possibly transformed) value.
        :raises FieldRequiredError: If a required field is missing.
        :raises FieldTypeError: If the value is of the wrong type for nested fields.
        :raises ValidationError: If a validator fails.
        """
        # Check for required field
        if value is None:
            if self._required:
                raise FieldRequiredError(f"Field '{self._name}' is required but missing.")
            else:
                return deepcopy(self._default)

        # Check for the item type if specified
        if self._item_type is not None and not isinstance(value, self._item_type):
            raise FieldTypeError(
                f"Field '{self._name}' expects type {self._item_type.__name__}, "
                f"got {type(value).__name__}."
            )

        # If there is an iterable template, validate each item in the iterable
        if self._iterable_template is not None:
            if not isinstance(value, (list, tuple, set)):
                raise FieldTypeError(
                    f"Field '{self._name}' expects a list, tuple or set for iterable fields, got {type(value).__name__}."
                )

            parsed_list = []

            for item in value:
                parsed_item = self._iterable_template.parse(item)
                parsed_list.append(parsed_item)

            return parsed_list

        # If there are nested fields, validate the value against them
        if self._nested_fields:
            if not isinstance(value, dict):
                raise FieldTypeError(
                    f"Field '{self._name}' expects a dict for nested fields, got {type(value).__name__}."
                )

            parsed_value = {}
            for field in self._nested_fields:
                nested_value = value.get(field.name, None)
                parsed_value[field.name] = field.parse(nested_value)

            return parsed_value

        # Apply validators sequentially to the value
        for validator in self._validators:
            value = validator.validate(self._name, value)

        return value
