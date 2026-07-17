import pytest

from tinyschema import Field, Schema


def test_schema_requires_a_list_of_fields() -> None:
    with pytest.raises(TypeError, match="list of Field"):
        Schema((Field("value", str, required=True),))  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="list of Field"):
        Schema([object()])  # type: ignore[list-item]


def test_schema_requires_dictionary_input() -> None:
    schema = Schema([])

    with pytest.raises(TypeError, match="expects 'data' to be a dict"):
        schema.validate([])  # type: ignore[arg-type]


def test_schema_drops_unknown_keys() -> None:
    schema = Schema([Field("known", str, required=True)])

    assert schema.validate({"known": "value", "unknown": 1}) == {"known": "value"}


def test_duplicate_field_names_use_the_last_field_result() -> None:
    schema = Schema(
        [
            Field("value", str, default="first"),
            Field("value", str, default="second"),
        ]
    )

    assert schema.validate({}) == {"value": "second"}
