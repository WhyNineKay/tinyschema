from pathlib import Path

from tinyschema import Schema, Field, JSONFileInterface, SchemaManager, validators
from tinyschema.validators import TypeValidator, LengthValidator
from tinyschema.remedies import TruncateStringRemedy, ClampNumberRemedy


def main() -> None:
    schema = Schema(
        fields=[
            Field(
                name="name",
                item_type=str,
                required=False,
                validators=[
                    TypeValidator(str),
                    LengthValidator(min_length=1, max_length=100, remedies=[TruncateStringRemedy(100)])
                ],
                default="Unknown"
            ),
            Field(
                name="contact",
                item_type=dict,
                required=True,
                nested_fields=[
                    Field(
                        name="email",
                        item_type=str,
                        required=False,
                        validators=[
                            TypeValidator(str),
                            LengthValidator(min_length=5, max_length=100, remedies=[TruncateStringRemedy(100)])
                        ],
                        default="unknown@example.com"
                    )
                ],
            ),
            Field(
                name="amounts",
                item_type=list,
                required=True,
                iterable_template=Field(
                    name="amount",
                    item_type=int,
                    required=True,
                    validators=[validators.RangeValidator(minimum=0, maximum=5, remedies=[ClampNumberRemedy(minimum=0, maximum=5)])],
                )
            )
        ]
    )

    interface = JSONFileInterface(Path("example_data.json"), True)
    manager = SchemaManager(schema, interface)

    data = manager.load_and_validate()

    print(data)


if __name__ == '__main__':
    main()
