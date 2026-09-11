from dataclasses import dataclass
from pathlib import Path

from cs2_storage_unit_tracker.cli.content.rich import messages_key
from cs2_storage_unit_tracker.cli.renderers.rich import RichMessageRenderer


@dataclass(frozen=True, slots=True)
class ConfigError(Exception):
    message: str
    path: Path

    def __post_init__(self) -> None:
        super().__init__(self.message)


def handle_config_error(exc: ConfigError) -> None:
    RichMessageRenderer().print(
        key=messages_key.CONFIG_ERROR,
        variables={
            "message": exc.message,
            "path": exc.path,
        },
    )


@dataclass(frozen=True, slots=True)
class ApiError(Exception):
    message: str

    def __post_init__(self) -> None:
        super().__init__(self.message)


class ApiRequestError(ApiError):
    pass


class ApiResponseError(ApiError):
    pass


class SteamApiParseError(ApiError):
    pass
