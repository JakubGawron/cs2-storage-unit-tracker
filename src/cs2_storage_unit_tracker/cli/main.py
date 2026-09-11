from cs2_storage_unit_tracker.cli import create_app
from cs2_storage_unit_tracker.cli.app import App
from cs2_storage_unit_tracker.helpers.errors import (
    ConfigError,
    handle_config_error,
)


def main() -> None:
    try:
        app: App = create_app()
        app.run()

    except ConfigError as exc:
        handle_config_error(exc)


if __name__ == "__main__":
    main()
