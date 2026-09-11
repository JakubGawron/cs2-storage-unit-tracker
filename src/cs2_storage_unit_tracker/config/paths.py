from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Paths:
    root_dir: Path
    project_dir: Path

    @property
    def portfolio(self) -> Path:
        return self.root_dir / "settings" / "portfolio.toml"

    @property
    def runtime(self) -> Path:
        return self.project_dir / "data" / "runtime.toml"

    @property
    def sync_status(self) -> Path:
        return self.project_dir / "data" / "sync_status.toml"

    @property
    def user_settings(self) -> Path:
        return self.root_dir / "settings" / "settings.toml"
