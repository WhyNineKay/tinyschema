import re

import pytest

from tinyschema.errors import ValidationError
from tinyschema.remedies import ClampNumberRemedy, StripWhitespaceRemedy, TypeCastRemedy
from tinyschema.validators import (
    EmailValidator,
    LengthValidator,
    RangeValidator,
    RegexValidator,
    TypeValidator,
    Validator,
)


def test_validator_is_abstract() -> None:
    with pytest.raises(TypeError):
        Validator()  # type: ignore[abstract]


def test_type_validator_accepts_expected_type_and_can_remedy() -> None:
    validator = TypeValidator(int, remedies=[TypeCastRemedy(int)])

    assert validator.validate("count", 1) == 1
    assert validator.validate("count", "2") == 2


def test_validator_tries_remedies_in_sequence() -> None:
    validator = LengthValidator(min_length=4, remedies=[StripWhitespaceRemedy()])

    assert validator.validate("name", "  abc  ") == "  abc  "
    with pytest.raises(ValidationError):
        validator.validate("name", " x ")


@pytest.mark.parametrize(
    ("validator", "valid", "invalid"),
    [
        (LengthValidator(1, 3), "ab", ""),
        (EmailValidator(), "a@example.com", "invalid"),
        (RangeValidator(0, 5), 3, 10),
        (RegexValidator(r"^[A-Z]+$"), "ABC", "abc"),
    ],
)
def test_builtin_validators(validator: object, valid: object, invalid: object) -> None:
    assert validator.validate("value", valid) == valid  # type: ignore[attr-defined]
    with pytest.raises(ValidationError):
        validator.validate("value", invalid)  # type: ignore[attr-defined]


def test_range_validator_can_clamp_invalid_value() -> None:
    validator = RangeValidator(0, 5, remedies=[ClampNumberRemedy(0, 5)])

    assert validator.validate("amount", 10) == 5


@pytest.mark.parametrize(
    ("factory", "error"),
    [
        (lambda: LengthValidator(-1), ValueError),
        (lambda: LengthValidator(3, 2), ValueError),
        (lambda: LengthValidator("1"), TypeError),
        (lambda: RangeValidator(5, 1), ValueError),
        (lambda: RangeValidator("0", 1), TypeError),
        (lambda: RegexValidator("["), re.error),
        (lambda: TypeValidator("str"), TypeError),
        (lambda: LengthValidator(remedies=[object()]), TypeError),
    ],
)
def test_validator_constructor_rejects_invalid_configuration(
    factory: object,
    error: type[Exception],
) -> None:
    with pytest.raises(error):
        factory()  # type: ignore[operator]
