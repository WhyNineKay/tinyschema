from typing import List, Any

from .errors import FieldRequiredError, FieldTypeError, ValidationError
from .validators import Validator


class Field:
    def __init__(self,
                 name: str,
                 required: bool = None,
                 validators: List[Validator] = None,
                 nested_fields: List['Field'] = None,
                 default: Any = None
                 ) -> None:
        """
        :param name: Name of the key in the data dictionary.
        :param required: Whether the field is required or not. Defaults to False.
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

        # Pre-parse the default value against validators if applicable
        if self._default is not None and not self._nested_fields:
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
            if validator.attempt_fix:
                value = validator.validate(self.name, value)
            else:
                validator.validate(self.name, value)

        return value


    def parse(self, value: Any) -> Any:
        """
        Parse and validate the given value according to the field's configuration.

        :param value: The value to be parsed and validated.
        :return: The validated (and possibly transformed) value.
        :raises FieldRequiredError: If a required field is missing.
        :raises FieldTypeError: If the value is of the wrong type for nested fields.
        :raises ValidationError: If a validator fails.
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
            if validator.attempt_fix:
                value = validator.validate(self.name, value)
            else:
                validator.validate(self.name, value)

        return value
