import re

import pytest

from tinyschema.remedies import (
    ClampNumberRemedy,
    CustomRemedy,
    EmailNormalizeRemedy,
    LowercaseRemedy,
    PadStringRemedy,
    RegexSubRemedy,
    Remedy,
    ReplaceStringRemedy,
    StripWhitespaceRemedy,
    TitleCaseRemedy,
    TruncateStringRemedy,
    TypeCastRemedy,
    UppercaseRemedy,
)


def test_remedy_is_abstract() -> None:
    with pytest.raises(TypeError):
        Remedy()  # type: ignore[abstract]


@pytest.mark.parametrize(
    ("remedy", "value", "expected"),
    [
        (StripWhitespaceRemedy(), " value ", "value"),
        (LowercaseRemedy(), "VALUE", "value"),
        (UppercaseRemedy(), "value", "VALUE"),
        (TitleCaseRemedy(), "hello world", "Hello World"),
        (TruncateStringRemedy(3), "value", "val"),
        (PadStringRemedy(5, "x"), "ab", "abxxx"),
        (ReplaceStringRemedy("a", "b"), "a cat", "b cbt"),
        (RegexSubRemedy(r"\s+", "-"), "a b", "a-b"),
        (TypeCastRemedy(int), "4", 4),
        (ClampNumberRemedy(0, 10), 12, 10),
        (EmailNormalizeRemedy(), " A @Example.COM ", "a@example.com"),
    ],
)
def test_builtin_remedies(remedy: object, value: object, expected: object) -> None:
    assert remedy.apply("value", value) == expected  # type: ignore[attr-defined]


def test_remedies_leave_unsupported_values_unchanged() -> None:
    value = object()

    assert StripWhitespaceRemedy().apply("value", value) is value
    assert ClampNumberRemedy(0, 1).apply("value", value) is value
    assert TypeCastRemedy(int).apply("value", value) is value


def test_custom_remedy_receives_field_name_and_value() -> None:
    remedy = CustomRemedy(lambda field_name, value: f"{field_name}:{value}")

    assert remedy.apply("code", 3) == "code:3"


def test_padding_with_multiple_characters_stops_at_requested_length() -> None:
    assert PadStringRemedy(5, "xy").apply("value", "a") == "axyxy"


@pytest.mark.parametrize(
    ("factory", "error"),
    [
        (lambda: TruncateStringRemedy(-1), ValueError),
        (lambda: PadStringRemedy(-1), ValueError),
        (lambda: PadStringRemedy(1, ""), ValueError),
        (lambda: RegexSubRemedy("[", ""), re.error),
        (lambda: TypeCastRemedy("int"), TypeError),
        (lambda: ClampNumberRemedy(5, 1), ValueError),
        (lambda: CustomRemedy(1), TypeError),
    ],
)
def test_remedy_constructor_rejects_invalid_configuration(
    factory: object,
    error: type[Exception],
) -> None:
    with pytest.raises(error):
        factory()  # type: ignore[operator]
