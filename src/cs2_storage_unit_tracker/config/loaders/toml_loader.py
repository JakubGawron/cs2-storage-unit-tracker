import tomllib
from pathlib import Path
from typing import Any, Literal

import tomli_w
from pydantic import BaseModel, ValidationError

from cs2_storage_unit_tracker.helpers.errors import ConfigError


class TomlLoader:
    def load[ConfigModel: BaseModel](
        self,
        path: Path,
        model: type[ConfigModel],
        context: dict[str, Any] | None = None,
    ) -> ConfigModel:
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
        data: dict[str, Any] = config.model_dump(mode=mode)

        with path.open("wb") as file:
            tomli_w.dump(data, file)
