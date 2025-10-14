"""
Field definitions for TinySchema.
"""
from typing import List, Any

from tinyschema.errors import FieldRequiredError, FieldTypeError


class Validator:
    pass


class Field:
    def __init__(self,
                 name: str,
                 required: bool = None,
                 validators: List[Validator] = None,
                 nested_fields: List['Field'] = None,
                 default: Any = None
                 ) -> None:
        """
        Initialize a Field instance.

        :param name: Name of the key in the data dictionary.
        :param required: Whether the field is required or not.
        :param validators: List of Validator instances to validate the field's value.
        :param nested_fields: List of nested Field instances for complex structures.
        :param default: Default value if the field is not required.
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

        self._default = default

        # Check for redundant parameters
        if self._nested_fields and self._validators:
            raise ValueError("Field using 'nested_fields' cannot have 'validators'.")

        if self._required and self._default is not None:
            raise ValueError("Field that is required cannot have a 'default' value.")
        if not self._required and self._default is None:
            raise ValueError("Field that is not required must have a 'default' value.")

    @property
    def name(self) -> str:
        return self._name

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

    def parse(self, value: Any) -> Any:
        """
        Parse and validate the given value according to the field's configuration.

        :param value: The value to be parsed and validated.
        :return: The validated (and possibly transformed) value.
        :raises ValueError: If validation fails or required field is missing.
        """
        if value is None:
            if self._required:
                raise FieldRequiredError(f"Field '{self._name}' is required but missing.")
            else:
                return self._default

        if self._nested_fields:
            if not isinstance(value, dict):
                raise FieldTypeError(f"Field '{self._name}' expects a dictionary for nested fields.")

            parsed_value = {}

            for field in self._nested_fields:
                field_value = value.get(field.name, None)
                parsed_value[field.name] = field.parse(field_value)

            return parsed_value

        for validator in self._validators:
            # validator.validate() may raise a ValidationError
            new_value = validator.validate(self.name, value)

            if validator.attempt_fix:
                value = new_value

        return value
