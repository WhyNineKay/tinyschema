from typing import List

from .field import Field


class Schema:
    def __init__(self, fields: List[Field]) -> None:
        """
        :param fields: List of Field instances that define the schema.
        :raises TypeError: If fields is not a list of Field instances.
        """

        if isinstance(fields, list) and all(isinstance(field, Field) for field in fields):
            self._fields = fields
        else:
            raise TypeError("Parameter 'fields' must be a list of Field instances.")

    @property
    def fields(self) -> List[Field]:
        """
        Get the list of Field instances that define the schema.

        :return: The list of Field instances.
        """
        return self._fields

    def validate(self, data: dict) -> dict:
        """
        Validate the given data dictionary against the schema.

        :param data: The data dictionary to be validated.
        :return: The validated (and possibly transformed) data dictionary.
        :raises ValidationError: If validation fails for any field.
        :raises FieldRequiredError: If a required field is missing.
        :raises FieldTypeError: If a nested field has an incorrect type.
        :return: The validated data.
        """

        if not isinstance(data, dict):
            raise TypeError(
                f"Schema.validate expects 'data' to be a dict, got {type(data).__name__}."
            )

        validated_data = {}

        for field in self._fields:
            # Get the field data from the input dictionary, defaulting to None if not present
            field_data = data.get(field.name, None)

            # Parse and validate the field data
            validated_data[field.name] = field.parse(field_data)

        return validated_data
