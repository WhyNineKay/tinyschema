from typing import Any

import pytest

from tinyschema import Field, Schema
from tinyschema.errors import FieldRequiredError, FieldTypeError, ValidationError
from tinyschema.validators import LengthValidator, TypeValidator


def test_none_default_accepts_missing_key() -> None:
    field = Field("value", str, required=False, default=None)
    schema = Schema([field])

    assert field.item_type is str
    assert field.has_default is True
    assert field.default is None
    assert schema.validate({}) == {"value": None}


def test_none_default_accepts_explicit_none() -> None:
    schema = Schema([Field("value", str, required=False, default=None)])

    assert schema.validate({"value": None}) == {"value": None}


def test_nullable_field_accepts_declared_type() -> None:
    schema = Schema([Field("value", str, required=False, default=None)])

    assert schema.validate({"value": "present"}) == {"value": "present"}


def test_nullable_field_rejects_wrong_non_none_type() -> None:
    schema = Schema([Field("value", str, required=False, default=None)])

    with pytest.raises(FieldTypeError, match="expects type str"):
        schema.validate({"value": 1})


def test_validators_are_skipped_for_accepted_none() -> None:
    schema = Schema(
        [
            Field(
                "value",
                str,
                required=False,
                validators=[TypeValidator(str), LengthValidator(min_length=1)],
                default=None,
            )
        ]
    )

    assert schema.validate({"value": None}) == {"value": None}


def test_validators_still_run_for_non_none_values() -> None:
    schema = Schema(
        [
            Field(
                "value",
                str,
                required=False,
                validators=[LengthValidator(min_length=1)],
                default=None,
            )
        ]
    )

    with pytest.raises(ValidationError, match="less than minimum"):
        schema.validate({"value": ""})


def test_non_none_default_must_match_item_type() -> None:
    with pytest.raises(ValueError, match="does not conform"):
        Field("value", str, required=False, default=1)


def test_non_none_default_runs_through_validators() -> None:
    with pytest.raises(ValueError, match="does not conform"):
        Field(
            "value",
            str,
            required=False,
            validators=[LengthValidator(min_length=1)],
            default="",
        )


def test_default_factory_returning_none_makes_field_nullable() -> None:
    schema = Schema([Field("value", str, required=False, default_factory=lambda: None)])

    assert schema.validate({}) == {"value": None}
    assert schema.validate({"value": None}) == {"value": None}


def test_default_factory_returning_wrong_type_fails() -> None:
    with pytest.raises(ValueError, match="does not conform"):
        Field("value", str, required=False, default_factory=lambda: 1)


def test_required_field_rejects_explicit_none() -> None:
    schema = Schema([Field("value", str, required=True)])

    with pytest.raises(FieldTypeError, match="expects type str"):
        schema.validate({"value": None})


def test_required_field_rejects_missing_key() -> None:
    schema = Schema([Field("value", str, required=True)])

    with pytest.raises(FieldRequiredError):
        schema.validate({})


def test_nested_field_can_default_to_none() -> None:
    schema = Schema(
        [
            Field(
                "contact",
                dict,
                required=False,
                nested_fields=[Field("email", str, required=True)],
                default=None,
            )
        ]
    )

    assert schema.validate({}) == {"contact": None}
    assert schema.validate({"contact": None}) == {"contact": None}


def test_iterable_field_can_default_to_none() -> None:
    schema = Schema(
        [
            Field(
                "values",
                list,
                required=False,
                iterable_template=Field("item", int, required=True),
                default=None,
            )
        ]
    )

    assert schema.validate({}) == {"values": None}
    assert schema.validate({"values": None}) == {"values": None}
    assert schema.validate({"values": [1, 2]}) == {"values": [1, 2]}


def test_none_item_type_is_rejected() -> None:
    with pytest.raises(TypeError, match="must be a type"):
        Field("value", None, required=False, default=None)  # type: ignore[arg-type]


def test_typing_any_is_not_a_concrete_item_type() -> None:
    with pytest.raises(TypeError, match="must be a type"):
        Field("value", Any, required=True)


def test_default_and_default_factory_conflict_when_default_is_none() -> None:
    with pytest.raises(ValueError, match="Cannot specify both"):
        Field(
            "value",
            str,
            required=False,
            default=None,
            default_factory=lambda: None,
        )
