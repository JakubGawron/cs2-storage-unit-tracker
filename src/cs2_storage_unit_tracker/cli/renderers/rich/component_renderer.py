from collections.abc import Generator, Iterable
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

from cs2_storage_unit_tracker.cli.content.rich import components
from cs2_storage_unit_tracker.cli.renderers.rich.console_instance import console
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.status import Status
from rich.text import Text


@dataclass(frozen=True, slots=True)
class RichComponentRenderer:
    live: Live
    status: Status
    progress: Progress

    @staticmethod
    def _check_type(
        received_type: components.Type, expected_types: list[components.Type]
    ) -> None:
        if received_type not in expected_types:
            raise ValueError(
                f"Invalid type: {received_type!r}. Expected: {expected_types!r}"
            )

    def _get_template_typecheck(
        self, key: components.Key, expected_types: list[components.Type]
    ) -> components.Template:
        try:
            template: components.Template = components.COMPONENTS[key]
            self._check_type(received_type=template.type, expected_types=expected_types)
            return template
        except KeyError as exc:
            raise ValueError(
                f"No message template exists for key {key.value!r}"
            ) from exc

    def _flatten_and_format(
        self,
        content: tuple[components.Segment | components.Group | components.Key, ...],
        variables: dict[str, Any] | None = None,
    ) -> list[tuple[str, str]]:
        result: list[tuple[str, str]] = []
        has_variables: bool = variables is not None

        for item in content:
            if isinstance(item, components.Key):
                template: components.Template = components.COMPONENTS[item]
                resolved: list[tuple[str, str]] = self._flatten_and_format(
                    template.content, variables
                )
                result.extend(resolved)

            elif isinstance(item, components.Group):
                group_parts: list[tuple[str, str]] = []

                for segment in item.segments:
                    text: str = (
                        segment.text.format_map(variables)
                        if has_variables
                        else segment.text
                    )

                    if segment.min_width is not None:
                        text = text.ljust(segment.min_width)

                    group_parts.append((text, segment.style.value))

                if item.min_width is not None:
                    current_width: int = sum(len(text) for text, _ in group_parts)
                    padding: int = max(0, item.min_width - current_width)

                    result.extend(group_parts)

                    if padding:
                        result.append((" " * padding, ""))
                else:
                    result.extend(group_parts)

            else:
                text = item.text.format_map(variables) if has_variables else item.text
                if item.min_width is not None:
                    text = text.ljust(item.min_width)
                result.append((text, item.style.value))

        return result

    def progress_add_task(
        self, key: components.Key, variables: dict[str, Any] | None = None
    ) -> TaskID:
        template: components.Template = self._get_template_typecheck(
            key=key, expected_types=[components.Type.TASK]
        )

        parts: list[tuple[str, str]] = self._flatten_and_format(
            content=template.content, variables=variables
        )

        return self.progress.add_task(description=Text.assemble(*parts).markup)

    def progress_track_task(
        self,
        outdated_items: Iterable[Any],
        task_id: TaskID,
    ) -> Iterable[Any]:
        return self.progress.track(sequence=outdated_items, task_id=task_id)

    def progress_advance_task(
        self,
        task_id: TaskID,
    ) -> None:
        self.progress.update(task_id=task_id, advance=1)

    def status_update(
        self,
        key: components.Key,
        variables: dict[str, Any] | None = None,
    ) -> None:
        template: components.Template = self._get_template_typecheck(
            key=key, expected_types=[components.Type.ITEM, components.Type.REPORT]
        )

        parts: list[tuple[str, str]] = self._flatten_and_format(
            content=template.content, variables=variables
        )

        self.status.update(status=Text.assemble(*parts))


@contextmanager
def rich_live_component_renderer() -> Generator[RichComponentRenderer]:
    status: Status = console.status("")
    progress = Progress()

    with Live(Panel(Group(status, progress)), console=console) as live:
        rich_component_renderer = RichComponentRenderer(live, status, progress)
        yield rich_component_renderer
