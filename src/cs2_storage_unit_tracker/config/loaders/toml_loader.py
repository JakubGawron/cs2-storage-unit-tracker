import tomllib
from pathlib import Path
from typing import Any, Literal

import tomli_w
from pydantic import BaseModel, ValidationError

from cs2_storage_unit_tracker.helpers.errors import ConfigError


class TomlLoader:
    """Generic TOML file loader and saver with Pydantic model validation.

    This utility class handles reading and writing TOML configuration files with
    automatic deserialization to typed Pydantic models and serialization back to
    TOML format. It provides error handling for file I/O, TOML parsing, and model
    validation failures.
    """

    def load[ConfigModel: BaseModel](
        self,
        path: Path,
        model: type[ConfigModel],
        context: dict[str, Any] | None = None,
    ) -> ConfigModel:
        """Load and deserialize a TOML file into a typed Pydantic model.

        Reads a TOML file from disk, parses it, and validates the contents against
        the provided Pydantic model class. Optionally passes context data to the
        model's validation process for dynamic validation rules.

        Args:
            path: File path to the TOML configuration file.
            model: Pydantic BaseModel subclass to deserialize the TOML data into.
            context: Optional dictionary of context variables passed to Pydantic's
                model_validate() for use in validators or custom validation logic.
                Defaults to None.

        Returns:
            An instance of the provided model class with data loaded from the TOML file.

        Raises:
            ConfigError: If the file is not found, contains invalid TOML syntax,
                or fails Pydantic model validation. The exception wraps the original
                error with the file path for diagnostics.
        """
        try:
            with path.open("rb") as file:
                data: dict[str, Any] = tomllib.load(file)

        except FileNotFoundError as exc:
            raise ConfigError(
                message="Configuration file not found", path=path
            ) from exc
        except tomllib.TOMLDecodeError as exc:
            raise ConfigError(message="Invalid TOML format in", path=path) from exc

        try:
            return model.model_validate(data, context=context)
        except ValidationError as exc:
            raise ConfigError(message="Invalid configuration in", path=path) from exc

    def save(
        self,
        path: Path,
        mode: Literal["json", "python"],
        config: BaseModel,
    ) -> None:
        """Serialize a Pydantic model to a TOML file.

        Converts a Pydantic model instance to a dictionary using the specified
        serialization mode, then writes the result to a TOML file on disk.

        Args:
            path: File path where the TOML file will be written. Parent directories
                must exist.
            mode: Serialization mode for Pydantic's model_dump(). Either "json" for
                JSON-compatible serialization or "python" for Python-native types.
            config: Pydantic BaseModel instance to serialize and persist.

        Raises:
            IOError: If the file cannot be written to disk (e.g., permission denied,
                invalid path).
            ValueError: If the model cannot be serialized in the specified mode.
        """
        data: dict[str, Any] = config.model_dump(mode=mode)

        with path.open("wb") as file:
            tomli_w.dump(data, file)
