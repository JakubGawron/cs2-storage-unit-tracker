from dataclasses import dataclass
from typing import Any

from cs2_storage_unit_tracker.config import Paths
from cs2_storage_unit_tracker.config.loaders.toml_loader import TomlLoader
from cs2_storage_unit_tracker.config.models import (
    Portfolio,
    Runtime,
    SyncStatus,
    UserSettings,
)


@dataclass(frozen=True, slots=True)
class FileLoader:
    """Manages loading and saving application configuration files.

    This loader provides a high-level interface for reading and writing configuration
    data from TOML files to typed configuration models. It handles multiple configuration
    domains (portfolio, runtime, sync status, user settings) using a shared TOML loader.

    Attributes:
        paths: Paths object containing file paths to all configuration files.
        loader: TomlLoader instance used for file I/O and serialization.
    """

    paths: Paths
    loader = TomlLoader()

    def load_portfolio(self) -> Portfolio:
        """Load the portfolio configuration from disk.

        Returns:
            Portfolio: Deserialized portfolio configuration model.

        Raises:
            ConfigError: If the portfolio configuration file is not found, contains
                invalid TOML, or fails Pydantic model validation.
        """
        return self.loader.load(path=self.paths.portfolio, model=Portfolio)

    def load_runtime(self, context: dict[str, Any]) -> Runtime:
        """Load the runtime configuration with context information.

        Loads runtime configuration and passes context data to Pydantic's model
        validation. Context is typically used for dynamic validation rules or
        environment-specific settings.

        Args:
            context: Dictionary of context variables passed to Pydantic validation.
                Can include environment information, runtime state, or custom validators.

        Returns:
            Runtime: Deserialized runtime configuration model.

        Raises:
            ConfigError: If the runtime configuration file is not found, contains
                invalid TOML, or fails Pydantic model validation.
        """
        return self.loader.load(path=self.paths.runtime, model=Runtime, context=context)

    def save_runtime(self, runtime: Runtime) -> None:
        """Save the runtime configuration to disk in Python format.

        Serializes the runtime configuration model to TOML format using Python
        serialization mode, then writes it to the runtime configuration file.

        Args:
            runtime: Runtime configuration model to persist.

        Raises:
            IOError: If the file cannot be written to disk.
            ValueError: If the runtime model cannot be serialized.
        """
        self.loader.save(path=self.paths.runtime, mode="python", config=runtime)

    def load_sync_status(self) -> SyncStatus:
        """Load the sync status configuration from disk.

        Returns:
            SyncStatus: Deserialized sync status configuration model.

        Raises:
            ConfigError: If the sync status configuration file is not found, contains
                invalid TOML, or fails Pydantic model validation.
        """
        return self.loader.load(path=self.paths.sync_status, model=SyncStatus)

    def save_sync_status(self, sync_status: SyncStatus) -> None:
        """Save the sync status configuration to disk in JSON format.

        Serializes the sync status configuration model to TOML format using JSON
        serialization mode, then writes it to the sync status configuration file.

        Args:
            sync_status: SyncStatus configuration model to persist.

        Raises:
            IOError: If the file cannot be written to disk.
            ValueError: If the sync status model cannot be serialized.
        """
        self.loader.save(path=self.paths.sync_status, mode="json", config=sync_status)

    def load_user_settings(self, context: dict[str, Any]) -> UserSettings:
        """Load the user settings configuration with context information.

        Loads user settings configuration and passes context data to Pydantic's model
        validation. Context is typically used for dynamic validation rules or
        environment-specific settings.

        Args:
            context: Dictionary of context variables passed to Pydantic validation.
                Can include environment information, user state, or custom validators.

        Returns:
            UserSettings: Deserialized user settings configuration model.

        Raises:
            ConfigError: If the user settings configuration file is not found, contains
                invalid TOML, or fails Pydantic model validation.
        """
        return self.loader.load(
            path=self.paths.user_settings, model=UserSettings, context=context
        )
