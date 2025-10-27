# TinySchema
A minimalistic schema validation library for Python.

Developers define `Schema` objects, using `Field` instances to specify the expected structure and types of data. The library provides functionality to load and validate data against these schemas, attempting to 'fix' values into the correct types or formats where possible.

## Key Points/Features

- **Schema Consistency**: The library ensures that ALL data will conform to the schema, with no missing fields or values. This allows for less overhead for the developer when working with validated data.
- 