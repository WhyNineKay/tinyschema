from typing import Any

from .interface import DataInterface
from .schema import Schema


class SchemaManager:
    """Coordinate schema validation with a data interface."""

    def __init__(
        self,
        schema: Schema,
        interface: DataInterface,
        validate_on_save: bool = True,
    ) -> None:
        if not isinstance(schema, Schema):
            raise TypeError("Parameter 'schema' must be an instance of Schema.")
        if not isinstance(interface, DataInterface):
            raise TypeError(
                "Parameter 'interface' must be an instance of DataInterface."
            )
        if not isinstance(validate_on_save, bool):
            raise TypeError("Parameter 'validate_on_save' must be of type bool.")

        self._schema = schema
        self._interface = interface
        self._validate_on_save = validate_on_save

    @property
    def schema(self) -> Schema:
        return self._schema

    @property
    def interface(self) -> DataInterface:
        return self._interface

    @property
    def validate_on_save(self) -> bool:
        return self._validate_on_save

    def load_and_validate(self) -> dict[str, Any]:
        """Load data from the interface and validate it against the schema."""
        return self._schema.validate(self._interface.load())

    def save_data(self, data: dict[str, Any]) -> None:
        """Save data, validating it first when configured to do so."""
        if self._validate_on_save:
            data = self._schema.validate(data)

        self._interface.save(data)
