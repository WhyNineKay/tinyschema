# TinySchema

TinySchema is a small runtime validation library for dictionary-shaped Python
data. A schema is an ordered list of fields, and each field has one concrete
runtime type.

## Installation

```console
python -m pip install tinyschema
```

TinySchema requires Python 3.10 or newer and has no runtime dependencies.

## Quick start

```python
from tinyschema import Field, LengthValidator, Schema

schema = Schema([
    Field(
        "name",
        str,
        validators=[LengthValidator(min_length=1, max_length=100)],
        default=None,
    ),
    Field("count", int, required=True),
])

schema.validate({"name": "Ada", "count": 3})
# {"name": "Ada", "count": 3}
```

## Fields and defaults

`item_type` strictly checks every non-`None` value using `isinstance`. Required
fields must be present and cannot have defaults. Optional fields must have a
`default` or `default_factory`.

```python
Field("identifier", int, required=True)
Field("display_name", str, default="Unknown")
Field("tags", list, default_factory=list)
```

A non-`None` default must match `item_type` and pass the field's validation.
Factories are resolved once when the field is created; missing values receive a
deep copy of the normalized result.

### Nullable fields

`default=None` makes an optional field nullable:

```python
schema = Schema([Field("name", str, default=None)])

schema.validate({})                 # {"name": None}
schema.validate({"name": None})   # {"name": None}
schema.validate({"name": "Ada"})  # {"name": "Ada"}
```

An accepted `None` bypasses nested, iterable, and validator processing. Passing
`None` as `item_type` is invalid.

## Validators and remedies

Validators reject invalid values with `ValidationError`. Remedies can transform
an invalid value before the validator retries it.

```python
from tinyschema import LengthValidator, StripWhitespaceRemedy

validator = LengthValidator(
    min_length=1,
    max_length=20,
    remedies=[StripWhitespaceRemedy()],
)
```

Built-in validators are `TypeValidator`, `LengthValidator`, `EmailValidator`,
`RangeValidator`, and `RegexValidator`. Built-in remedies are available directly
from `tinyschema` and from `tinyschema.remedies`.

## Nested data

```python
contact = Field(
    "contact",
    dict,
    required=True,
    nested_fields=[
        Field("email", str, default="unknown@example.com"),
    ],
)
```

Nested fields define the output keys for the nested dictionary. Unknown keys are
discarded.

## Iterable data

```python
amounts = Field(
    "amounts",
    list,
    required=True,
    iterable_template=Field("amount", int, required=True),
)
```

Iterable templates support lists, tuples, and sets when the field's `item_type`
matches the supplied collection. Their normalized output is always a list.

## Files and schema management

`JSONFileInterface` loads and saves dictionaries in UTF-8 JSON files.
`SchemaManager` connects an interface to a schema and validates saves by default.

```python
from pathlib import Path
from tinyschema import JSONFileInterface, SchemaManager

interface = JSONFileInterface(Path("data.json"), create_if_missing=True)
manager = SchemaManager(schema, interface)
data = manager.load_and_validate()
manager.save_data(data)
```

JSON documents must contain an object at the root.

## Errors

- `FieldRequiredError`: a required key is missing.
- `FieldTypeError`: a value does not match its field type.
- `ValidationError`: a validator cannot accept or remedy a value.
- `TypeError` or `ValueError`: a schema component is configured incorrectly.

## Behaviour notes

- Schema output contains only declared fields; unknown input keys are dropped.
- Duplicate field names are permitted, but the final field result wins.
- `default_factory` is evaluated once during field construction.
- Iterable values are normalized to lists.

## Development

```console
python -m pip install -e ".[dev]"
python -m pytest
python -m mypy
ruff check .
ruff format --check .
python -m build
```
