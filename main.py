from pathlib import Path
from tinyschema import Schema, Field, JSONFileInterface, SchemaManager
from tinyschema.validators import TypeValidator, LengthValidator, EmailValidator


def main() -> None:
    schema = Schema(
        fields=[
            Field(
                name="name",
                required=False,
                validators=[
                    TypeValidator(str),
                    LengthValidator(min_length=1, max_length=100, attempt_fix=True)
                ],
                default="Unknown"
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

    interface = JSONFileInterface(Path("example_data.json"), True)
    manager = SchemaManager(schema, interface)

    data = manager.load_and_validate()

    print(data)


if __name__ == '__main__':
    main()
