import pytest

from tinyschema import Field
from tinyschema.errors import FieldRequiredError, FieldTypeError


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"name": 1, "item_type": str, "required": True}, "name"),
        ({"name": "value", "item_type": "str", "required": True}, "item_type"),
        ({"name": "value", "item_type": str, "required": "yes"}, "required"),
        (
            {
                "name": "value",
                "item_type": str,
                "required": True,
                "validators": [object()],
            },
            "validators",
        ),
        (
            {
                "name": "value",
                "item_type": dict,
                "required": True,
                "nested_fields": [object()],
            },
            "nested_fields",
        ),
        (
            {
                "name": "value",
                "item_type": list,
                "required": True,
                "iterable_template": object(),
            },
            "iterable_template",
        ),
    ],
)
def test_constructor_rejects_invalid_arguments(
    kwargs: dict[str, object], message: str
) -> None:
    with pytest.raises(TypeError, match=message):
        Field(**kwargs)  # type: ignore[arg-type]


def test_optional_field_requires_a_default() -> None:
    with pytest.raises(ValueError, match="not required must have"):
        Field("value", str)


def test_required_field_rejects_a_default() -> None:
    with pytest.raises(ValueError, match="required cannot have"):
        Field("value", str, required=True, default="value")


def test_default_and_factory_are_mutually_exclusive() -> None:
    with pytest.raises(ValueError, match="Cannot specify both"):
        Field(
            "value",
            str,
            default="value",
            default_factory=lambda: "factory",
        )


def test_nested_fields_and_iterable_template_are_mutually_exclusive() -> None:
    child = Field("child", str, required=True)

    with pytest.raises(ValueError, match="both"):
        Field(
            "value",
            dict,
            required=True,
            nested_fields=[child],
            iterable_template=child,
        )


def test_nested_fields_and_validators_are_mutually_exclusive() -> None:
    from tinyschema.validators import LengthValidator

    with pytest.raises(ValueError, match="cannot have 'validators'"):
        Field(
            "value",
            dict,
            required=True,
            nested_fields=[Field("child", str, required=True)],
            validators=[LengthValidator()],
        )


def test_mutable_defaults_are_copied_for_each_parse() -> None:
    default: list[int] = []
    field = Field("values", list, default=default)

    from tinyschema._sentinels import MISSING

    parsed_one = field.parse(MISSING)
    parsed_two = field.parse(MISSING)
    parsed_one.append(1)

    assert parsed_two == []
    assert field.default == []


def test_nested_fields_are_parsed() -> None:
    field = Field(
        "contact",
        dict,
        required=True,
        nested_fields=[Field("email", str, default="unknown@example.com")],
    )

    assert field.parse({}) == {"email": "unknown@example.com"}
    with pytest.raises(FieldTypeError):
        field.parse([])


@pytest.mark.parametrize("value", [[1, 2], (1, 2), {1, 2}])
def test_iterable_templates_normalize_supported_iterables_to_lists(
    value: object,
) -> None:
    field = Field(
        "values",
        type(value),
        required=True,
        iterable_template=Field("item", int, required=True),
    )

    assert sorted(field.parse(value)) == [1, 2]


def test_required_field_reports_missing_value() -> None:
    from tinyschema._sentinels import MISSING

    with pytest.raises(FieldRequiredError):
        Field("value", str, required=True).parse(MISSING)
