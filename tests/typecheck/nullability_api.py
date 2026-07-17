from tinyschema import Field, LengthValidator, Schema, StripWhitespaceRemedy

nullable_string = Field("name", str, required=False, default=None)
validated_string = Field(
    "title",
    str,
    validators=[LengthValidator(1, remedies=[StripWhitespaceRemedy()])],
    default=None,
)
string_with_default = Field("name", str, required=False, default="Unknown")
factory_nullable_string = Field(
    "name",
    str,
    required=False,
    default_factory=lambda: None,
)
required_payload = Field("payload", dict, required=True)

# The ignore is intentional and checked by strict mypy: None is not item_type.
invalid_none_type = Field(
    "invalid",
    None,  # type: ignore[arg-type]
    required=False,
    default=None,
)

schema = Schema(
    [
        nullable_string,
        validated_string,
        string_with_default,
        factory_nullable_string,
        required_payload,
    ]
)
schema.validate({"name": None, "payload": {}})
