import tinyschema


def test_every_declared_public_name_is_exported() -> None:
    assert all(hasattr(tinyschema, name) for name in tinyschema.__all__)
