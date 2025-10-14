from tinyschema import Schema, Field
from tinyschema.validators import TypeValidator, LengthValidator, EmailValidator


def main() -> None:
    schema = Schema(
        fields=[
            Field(
                name="name",
                required=True,
                validators=[
                    TypeValidator(str),
                    LengthValidator(min_length=1, max_length=100, attempt_fix=True)
                ]
            ),
            Field(
                name="email",
                required=True,
                validators=[
                    TypeValidator(str),
                    EmailValidator()
                ]
            ),
            Field(
                name="location",
                required=True,
                nested_fields=[
                    Field(
                        name="city",
                        required=True,
                        validators=[
                            TypeValidator(str),
                            LengthValidator(min_length=1, max_length=50, attempt_fix=True)
                        ]
                    ),
                    Field(
                        name="country",
                        required=True,
                        validators=[
                            TypeValidator(str),
                            LengthValidator(min_length=1, max_length=50, attempt_fix=True)
                        ]
                    )
                ]
            )
        ]
    )

