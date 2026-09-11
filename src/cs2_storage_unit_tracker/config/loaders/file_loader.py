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
    paths: Paths
    loader = TomlLoader()

    def load_portfolio(self) -> Portfolio:
        return self.loader.load(path=self.paths.portfolio, model=Portfolio)

    def load_runtime(self, context: dict[str, Any]) -> Runtime:
        return self.loader.load(path=self.paths.runtime, model=Runtime, context=context)

    def save_runtime(self, runtime: Runtime) -> None:
        self.loader.save(path=self.paths.runtime, mode="python", config=runtime)

    def load_sync_status(self) -> SyncStatus:
        return self.loader.load(path=self.paths.sync_status, model=SyncStatus)

    def save_sync_status(self, sync_status: SyncStatus) -> None:
        self.loader.save(path=self.paths.sync_status, mode="json", config=sync_status)

    def load_user_settings(self, context: dict[str, Any]) -> UserSettings:
        return self.loader.load(
            path=self.paths.user_settings, model=UserSettings, context=context
        )
