class _Missing:
    """Marker used when a field value or default was not supplied."""

    __slots__ = ()

    def __repr__(self) -> str:
        return "<missing>"


MISSING = _Missing()
