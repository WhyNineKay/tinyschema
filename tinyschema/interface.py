import json
from pathlib import Path
from typing import Dict


class DataInterface:
    """Base class for data loading and saving interfaces."""

    def load(self) -> Dict:
        """
        Load data from a source.

        :return: The loaded data as a dictionary.
        """
        raise NotImplementedError("Subclasses must implement the load method.")

    def save(self, data: Dict) -> None:
        """
        Save data to a source.

        :param data: The data dictionary to be saved.
        """
        raise NotImplementedError("Subclasses must implement the save method.")


class FileInterface(DataInterface):
    """Base class for file-based data loading and saving interfaces."""

    def __init__(self,
                 file_path: Path,
                 create_if_missing: bool = None,
                 template_data: Dict = None
                 ) -> None:
        """
        :param file_path: Path to the file for loading/saving data.
        :param create_if_missing: Whether to create the file if it does not exist. Defaults to False.
        :param template_data: Template data to use when creating a new file. Defaults to an empty dictionary.
        :raises TypeError: If parameters are of incorrect types.
        """
        self._file_path = file_path

        if create_if_missing is None:
            self._create_if_missing = False
        elif isinstance(create_if_missing, bool):
            self._create_if_missing = create_if_missing
        else:
            raise TypeError("Parameter 'create_if_missing' must be of type bool.")

        if template_data is None:
            self._template_data = {}
        elif isinstance(template_data, dict):
            self._template_data = template_data
        else:
            raise TypeError("Parameter 'template_data' must be of type dict.")

    @property
    def template_data(self) -> Dict:
        return self._template_data

    @property
    def file_path(self) -> Path:
        return self._file_path

    @property
    def create_if_missing(self) -> bool:
        return self._create_if_missing

    def _save_template_data(self) -> None:
        self.save(self._template_data)

    def load(self) -> Dict:
        """
        Load data from the file.

        :return: The loaded data as a dictionary.
        """
        if not self._file_path.exists():
            if self._create_if_missing:
                # Create the file and populate it with the template data
                self._file_path.touch()

                self._save_template_data()

            else:
                raise FileNotFoundError(f"File '{self._file_path}' does not exist.")

    def save(self, data: Dict) -> None:
        """
        Save data to the file.

        :param data: The data dictionary to be saved.
        """
        raise NotImplementedError("Subclasses must implement the save method.")


class JSONFileInterface(FileInterface):
    """JSON file-based data loading and saving interface."""

    def load(self) -> Dict:
        """
        Load data from the JSON file.

        :return: The loaded data as a dictionary.
        """
        super().load()

        with self._file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return data

    def save(self, data: Dict) -> None:
        """
        Save data to the JSON file.

        :param data: The data dictionary to be saved.
        """
        with self._file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
