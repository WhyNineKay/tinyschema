import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

Data = dict[str, Any]


class DataInterface(ABC):
    """Source used to load and save schema data."""

    @abstractmethod
    def load(self) -> Data:
        """Load and return a data dictionary."""
        raise NotImplementedError("Subclasses must implement the load method.")

    @abstractmethod
    def save(self, data: Data) -> None:
        """Save a data dictionary."""
        raise NotImplementedError("Subclasses must implement the save method.")


class FileInterface(DataInterface, ABC):
    """Base class for file-backed data interfaces."""

    def __init__(
        self,
        file_path: Path,
        create_if_missing: bool = False,
        template_data: Data | None = None,
    ) -> None:
        if not isinstance(file_path, Path):
            raise TypeError("Parameter 'file_path' must be a pathlib.Path instance.")
        if not isinstance(create_if_missing, bool):
            raise TypeError("Parameter 'create_if_missing' must be of type bool.")
        if template_data is not None and not isinstance(template_data, dict):
            raise TypeError("Parameter 'template_data' must be of type dict.")

        self._file_path = file_path
        self._create_if_missing = create_if_missing
        self._template_data = template_data if template_data is not None else {}

    @property
    def template_data(self) -> Data:
        return self._template_data

    @property
    def file_path(self) -> Path:
        return self._file_path

    @property
    def create_if_missing(self) -> bool:
        return self._create_if_missing

    def _ensure_file_exists(self) -> None:
        if self._file_path.exists():
            return

        if not self._create_if_missing:
            raise FileNotFoundError(f"File '{self._file_path}' does not exist.")

        self._file_path.touch()
        self.save(self._template_data)


class JSONFileInterface(FileInterface):
    """Load and save dictionaries as UTF-8 JSON files."""

    def load(self) -> Data:
        self._ensure_file_exists()

        with self._file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise TypeError("JSON data must contain an object at the document root.")

        return data

    def save(self, data: Data) -> None:
        if not isinstance(data, dict):
            raise TypeError("Parameter 'data' must be of type dict.")

        with self._file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
