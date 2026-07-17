from pathlib import Path

from tinyschema import (
    ClampNumberRemedy,
    Field,
    JSONFileInterface,
    LengthValidator,
    RangeValidator,
    Schema,
    SchemaManager,
    TruncateStringRemedy,
)


def main() -> None:
    schema = Schema(
        [
            Field("archived", bool, default=None),
            Field(
                "name",
                str,
                validators=[
                    LengthValidator(
                        min_length=1,
                        max_length=100,
                        remedies=[TruncateStringRemedy(100)],
                    )
                ],
                default="Unset",
            ),
            Field(
                "contact",
                dict,
                required=True,
                nested_fields=[
                    Field("email", str, default="unknown@example.com"),
                ],
            ),
            Field(
                "amounts",
                list,
                required=True,
                iterable_template=Field(
                    "amount",
                    int,
                    required=True,
                    validators=[
                        RangeValidator(
                            minimum=0,
                            maximum=5,
                            remedies=[ClampNumberRemedy(minimum=0, maximum=5)],
                        )
                    ],
                ),
            ),
        ]
    )

    data_path = Path(__file__).with_name("example_data.json")
    interface = JSONFileInterface(data_path)
    manager = SchemaManager(schema, interface)
    data = manager.load_and_validate()
    print(data)


if __name__ == "__main__":
    main()
