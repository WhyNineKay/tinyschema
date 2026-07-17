from typing import Any

import pytest

from tinyschema import DataInterface, Field, Schema, SchemaManager


class MemoryInterface(DataInterface):
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data
        self.saved: dict[str, Any] | None = None

    def load(self) -> dict[str, Any]:
        return self.data

    def save(self, data: dict[str, Any]) -> None:
        self.saved = data


def test_manager_loads_and_validates() -> None:
    interface = MemoryInterface({})
    manager = SchemaManager(Schema([Field("name", str, default="Unknown")]), interface)

    assert manager.load_and_validate() == {"name": "Unknown"}


def test_manager_validates_before_saving_by_default() -> None:
    interface = MemoryInterface({})
    manager = SchemaManager(Schema([Field("name", str, default="Unknown")]), interface)

    manager.save_data({})

    assert interface.saved == {"name": "Unknown"}


def test_manager_can_save_without_validation() -> None:
    interface = MemoryInterface({})
    manager = SchemaManager(
        Schema([Field("name", str, default="Unknown")]),
        interface,
        validate_on_save=False,
    )

    manager.save_data({"extra": True})

    assert interface.saved == {"extra": True}


def test_manager_rejects_non_boolean_validation_flag() -> None:
    with pytest.raises(TypeError, match="validate_on_save"):
        SchemaManager(
            Schema([]),
            MemoryInterface({}),
            validate_on_save=None,  # type: ignore[arg-type]
        )
