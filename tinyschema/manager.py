from .schema import Schema
from .interface import DataInterface


class SchemaManager:
    def __init__(self,
                 schema: Schema,
                 interface: DataInterface,
                 validate_on_save: bool = None
                 ) -> None:
        """
        :param schema: The Schema instance to manage.
        :param interface: The DataInterface instance for data operations.
        :param validate_on_save: Whether to validate data before saving (recommended). Defaults to True.
        :raises TypeError: If parameters are of incorrect types.
        """

        if not isinstance(schema, Schema):
            raise TypeError("Parameter 'schema' must be an instance of Schema.")
        self._schema = schema

        if not isinstance(interface, DataInterface):
            raise TypeError("Parameter 'interface' must be an instance of DataInterface.")
        self._interface = interface

        if validate_on_save is None:
            self._validate_on_save = True
        elif isinstance(validate_on_save, bool):
            self._validate_on_save = validate_on_save
        else:
            raise TypeError("Parameter 'validate_on_save' must be of type bool.")

    @property
    def schema(self) -> Schema:
        return self._schema

    @property
    def interface(self) -> DataInterface:
        return self._interface

    def load_and_validate(self) -> dict:
        """
        Load data using the interface and validate it against the schema.

        Raises interface related errors specified by DataInterface.
        Raises schema errors specified below.

        :return: The validated data dictionary.
        :raises ValidationError: If validation fails.
        :raises FieldRequiredError: If a required field is missing.
        :raises FieldTypeError: If a nested field has an incorrect type.
        """

        data = self._interface.load()

        validated_data = self._schema.validate(data)

        return validated_data

    def save_data(self, data: dict) -> None:
        """
        Save data using the interface.

        Raises interface related errors specified by DataInterface.

        :param data: The data dictionary to be saved.
        """

        if self._validate_on_save:
            # Validate data before saving
            validated_data = self._schema.validate(data)
            self._interface.save(validated_data)

        else:
            self._interface.save(data)
