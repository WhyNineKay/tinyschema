from typing import Any

from ._sentinels import MISSING
from .field import Field


class Schema:
    """Validate dictionaries against an ordered collection of fields."""

    def __init__(self, fields: list[Field]) -> None:
        """
        :param fields: List of Field instances that define the schema.
        :raises TypeError: If fields is not a list of Field instances.
        """

        if isinstance(fields, list) and all(
            isinstance(field, Field) for field in fields
        ):
            self._fields = fields
        else:
            raise TypeError("Parameter 'fields' must be a list of Field instances.")

    @property
    def fields(self) -> list[Field]:
        """
        Get the list of Field instances that define the schema.

        :return: The list of Field instances.
        """
        return self._fields

    def validate(self, data: dict[Any, Any]) -> dict[str, Any]:
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
                "Schema.validate expects 'data' to be a dict, "
                f"got {type(data).__name__}."
            )

        # Unknown keys are intentionally dropped. If names are duplicated, the
        # final field result wins because dictionaries retain one value per key.
        return {
            field.name: field.parse(data.get(field.name, MISSING))
            for field in self._fields
        }
