import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from cs2_storage_unit_tracker.cli.content.rich import components
from cs2_storage_unit_tracker.cli.renderers.txt.renderer import (
    TextRenderer,
)


@dataclass(slots=True, kw_only=True)
class MarkdownDocument:
    reports_path: Path
    last_run: datetime

    _renderer = TextRenderer()
    _parts: list[str] = field(default_factory=lambda: list[str]())
    _existing_content: str = ""

    def __post_init__(self) -> None:
        if self.path.exists():
            content: str = self.path.read_text(encoding="utf-8")
            self._existing_content = self._extract_existing_content(content)

    @property
    def path(self) -> Path:
        return self.reports_path / f"portfolio_{self.last_run.date()}.txt"

    @staticmethod
    def _extract_existing_content(content: str) -> str:
        parts: list[str | Any] = re.split(
            r"(?=\n{2})",
            content,
            maxsplit=1,
        )

        return parts[1] if len(parts) > 1 else ""

    def _render(
        self,
        key: components.Key,
        variables: dict[str, Any] | None = None,
    ) -> str:
        return self._renderer.render(
            key=key,
            variables=variables,
        )

    def add(
        self,
        key: components.Key,
        variables: dict[str, Any] | None = None,
    ) -> None:
        self._parts.append(self._render(key, variables))

    def render(
        self,
        key: components.Key,
        variables: dict[str, Any] | None = None,
    ) -> str:
        current: str = self._render(key, variables)
        return current + self._existing_content[1:] + "".join(self._parts)

    def save(
        self,
        key: components.Key,
        variables: dict[str, Any] | None = None,
    ) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            self.render(key, variables),
            encoding="utf-8",
        )

    def clear(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8")
        self._existing_content = ""
        self._parts.clear()
