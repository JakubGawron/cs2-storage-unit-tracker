"""Entry point for the CS2 Storage Unit Tracker application.

This module serves as the main entry point, initializing the application
and handling top-level error management. It creates a fully configured
application instance and executes its main loop, catching configuration
errors and delegating them to the appropriate error handler.
"""

from cs2_storage_unit_tracker.cli import create_app
from cs2_storage_unit_tracker.cli.app import App
from cs2_storage_unit_tracker.helpers.errors import (
    ConfigError,
    handle_config_error,
)


def main() -> None:
    """Initialize and run the application with configuration error handling.

    Creates a fully configured App instance via the factory function and
    executes its main loop. Catches ConfigError exceptions during app
    creation or execution and delegates them to the application error handler.

    Raises:
        SystemExit: May be raised by handle_config_error depending on error
            severity and configured error handling behavior.
        Other exceptions not caught by this function may propagate up to the
            Python interpreter.
    """
    try:
        app: App = create_app()
        app.run()

    except ConfigError as exc:
        handle_config_error(exc)


if __name__ == "__main__":
    main()
