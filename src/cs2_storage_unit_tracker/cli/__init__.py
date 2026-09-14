"""Command-line interface application and factory.

This module provides the primary public API for the CLI, exporting the main
application class and its factory function for initialization and dependency
injection.

Exports:
    App: Main CLI application class for managing command execution and error
        handling.
    create_app: Factory function that constructs and configures an App instance
        with all dependencies properly injected.

Example:
    >>> from cs2_storage_unit_tracker.cli import App, create_app
    >>> app: App = create_app()
    >>> app.run()
"""

from cs2_storage_unit_tracker.cli.app import App
from cs2_storage_unit_tracker.cli.app_factory import create_app

__all__: list[str] = ["App", "create_app"]
