# TinySchema

TinySchema is a small validation library for dictionary-shaped Python data. It
validates types and values, fills defaults, handles nested structures, and can
repair invalid values as part of validation.

## Installation

```console
python -m pip install git+https://github.com/WhyNineKay/tinyschema.git
```

```console
uv add git+https://github.com/WhyNineKay/tinyschema.git
```

TinySchema requires Python 3.10 or newer.

## Quick start

```python
from tinyschema import Field, LengthValidator, Schema

schema = Schema([
    Field("name", str, default="Unknown"),
    Field("count", int, required=True),
])

schema.validate({"name": "Ada", "count": 3})
# {"name": "Ada", "count": 3}
```

A schema returns a new dictionary containing its declared fields. Missing optional
fields receive their defaults, missing required fields raise an error, and unknown
input keys are discarded.

## Core concepts

- A `Schema` describes a dictionary as a list of fields.
- A `Field` defines a key's type, presence, default, and validation rules.
- A `Validator` decides whether a value is acceptable.
- A `Remedy` can transform an invalid value so validation can succeed.

Validators and remedies are deliberately separate: the validator defines the
rule, while its remedies define the repairs you are willing to make.

```python
from tinyschema import (
    Field,
    LengthValidator,
    TruncateStringRemedy,
)

title = Field(
    "title",
    str,
    default="Untitled",
    validators=[LengthValidator(
        min_length=1,
        max_length=50,
        remedies=[TruncateStringRemedy(50)],
    )],
)
```

When a value is invalid, remedies are tried in order. Validation stops after the
first remedy that makes the value valid; otherwise `ValidationError` is raised.

## What it supports

- Required fields and validated defaults
- Nullable optional fields with `default=None`
- Nested dictionaries with `nested_fields`
- Repeated values with `iterable_template`
- Ordered validation and normalization
- JSON file loading and saving through `SchemaManager`
- Custom validators, remedies, and data interfaces

Built-in validators cover types, string lengths, numeric ranges, email addresses,
and regular expressions. Built-in remedies include string cleanup, truncation and
padding, regex replacement, type conversion, numeric clamping, and email
normalization.

## JSON files

`SchemaManager` connects a schema to a data source. TinySchema includes a JSON
interface and can be extended with other storage backends.

```python
from pathlib import Path
from tinyschema import JSONFileInterface, SchemaManager

manager = SchemaManager(schema, JSONFileInterface(Path("data.json")))
data = manager.load()
manager.save(data)
```

Loads are always validated. Saves are validated by default.

## Errors

- `FieldRequiredError` — a required field is missing
- `FieldTypeError` — a value has the wrong type
- `ValidationError` — a value fails its validators and cannot be remedied

All TinySchema validation exceptions inherit from `TinySchemaError`.

## Development

```console
uv sync --extra dev
uv run pytest
uv run mypy
uv run ruff check .
```

## License

TinySchema is available under the [MIT License](LICENSE).
