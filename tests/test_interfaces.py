import json
from pathlib import Path

import pytest

from tinyschema.interface import DataInterface, JSONFileInterface


def test_data_interface_is_abstract() -> None:
    with pytest.raises(TypeError):
        DataInterface()  # type: ignore[abstract]


def test_json_interface_raises_for_missing_file(tmp_path: Path) -> None:
    interface = JSONFileInterface(tmp_path / "missing.json")

    with pytest.raises(FileNotFoundError):
        interface.load()


def test_json_interface_rejects_non_boolean_creation_flag(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="create_if_missing"):
        JSONFileInterface(
            tmp_path / "data.json",
            create_if_missing=None,  # type: ignore[arg-type]
        )


def test_json_interface_creates_missing_file_from_template(tmp_path: Path) -> None:
    path = tmp_path / "created.json"
    interface = JSONFileInterface(
        path,
        create_if_missing=True,
        template_data={"created": True},
    )

    assert interface.load() == {"created": True}
    assert json.loads(path.read_text(encoding="utf-8")) == {"created": True}


def test_json_interface_round_trips_data(tmp_path: Path) -> None:
    path = tmp_path / "data.json"
    path.write_text("{}", encoding="utf-8")
    interface = JSONFileInterface(path)

    interface.save({"value": 1})

    assert interface.load() == {"value": 1}


def test_json_interface_rejects_non_object_root(tmp_path: Path) -> None:
    path = tmp_path / "list.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(TypeError, match="object at the document root"):
        JSONFileInterface(path).load()
