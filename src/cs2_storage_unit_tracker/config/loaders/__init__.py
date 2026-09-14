"""Application configuration file management API.

This module provides the public interface for configuration file handling.
It re-exports FileLoader, which manages loading and saving application
configuration files across multiple domains (portfolio, runtime, sync status,
user settings) using TOML serialization.

Attributes:
    FileLoader: High-level interface for reading and writing typed configuration
        models to TOML files. Manages multiple configuration domains and handles
        serialization via a shared TOML loader.
"""

from cs2_storage_unit_tracker.config.loaders.file_loader import FileLoader

__all__: list[str] = ["FileLoader"]
