"""Rich console renderer for template-based component display with live updates.

This module provides a renderer that consumes structured component templates and
renders them to a rich console with support for live status updates, progress
tracking, and dynamic variable substitution. It handles hierarchical template
composition, text styling, and layout width constraints.
"""

from collections.abc import Generator, Iterable
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.status import Status
from rich.text import Text

from cs2_storage_unit_tracker.cli.content.rich import components
from cs2_storage_unit_tracker.cli.renderers.flatten import flatten_and_format
from cs2_storage_unit_tracker.cli.renderers.rich.console_instance import console


@dataclass(frozen=True, slots=True)
class RichComponentRenderer:
    """Renders structured component templates to a rich console with live updates.

    This class manages the rendering pipeline for rich-formatted components,
    combining live updates, status messages, and progress tracking. It resolves
    template hierarchies, substitutes variables, applies styling, and enforces
    layout width constraints for consistent output formatting.

    Attributes:
        live: A rich Live instance managing the live display panel.
        status: A rich Status instance for displaying current operation status.
        progress: A rich Progress instance for tracking task completion.
    """

    live: Live
    status: Status
    progress: Progress

    @staticmethod
    def _check_type(
        received_type: components.Type, expected_types: list[components.Type]
    ) -> None:
        """Validate that a template type matches expected types.

        Args:
            received_type: The Type enum value to validate.
            expected_types: A list of Type enum values that are valid for the context.

        Raises:
            ValueError: If received_type is not in expected_types.
        """
        if received_type not in expected_types:
            raise ValueError(
                f"Invalid type: {received_type!r}. Expected: {expected_types!r}"
            )

    def _get_template_typecheck(
        self, key: components.Key, expected_types: list[components.Type]
    ) -> components.Template:
        """Retrieve and validate a template by key and expected type.

        Fetches a template from the COMPONENTS registry and validates that its
        type matches one of the expected types. This ensures type safety when
        retrieving templates for specific rendering contexts.

        Args:
            key: The Key enum value identifying the template to retrieve.
            expected_types: A list of Type enum values that are valid for this context.

        Returns:
            The Template object corresponding to the provided key.

        Raises:
            ValueError: If no template exists for the key or if the template's
                type does not match any of the expected_types.
        """
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
        """Recursively flatten and format template content with variable substitution.

        Processes a hierarchical template content tuple, recursively resolving
        template references (Key objects), formatting text with provided variables,
        applying layout width constraints, and preparing styled segments for
        rich console rendering.

        Segments are padded to their min_width if specified. Groups are padded
        collectively to their min_width after all member segments are formatted.
        Template references are resolved recursively and their flattened content
        is inserted in place.

        Args:
            content: A tuple of Segment, Group, or Key objects defining template content.
            variables: A dictionary of variable names and values for format string
                substitution. If None, no substitution is performed. Defaults to None.

        Returns:
            A list of (text, style) tuples, where text is the formatted text string
            and style is the rich-compatible style string value.
        """
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
        """Add a progress task with formatted text from a template.

        Retrieves a TASK-type template, flattens and formats its content,
        and creates a new progress task with the formatted description.

        Args:
            key: The Key enum value identifying a TASK-type template.
            variables: A dictionary of variable names and values for template
                substitution. If None, no substitution is performed. Defaults to None.

        Returns:
            A TaskID identifier for the newly created progress task.

        Raises:
            ValueError: If no template exists for the key or if the template's
                type is not Type.TASK.
        """
        template: components.Template = self._get_template_typecheck(
            key=key, expected_types=[components.Type.TASK]
        )

        parts: list[tuple[str, components.Style | None]] = flatten_and_format(
            content=template.content,
            variables=variables,
        )

        rich_parts: list[tuple[str, str]] = [
            (text, style.value if style is not None else "") for text, style in parts
        ]
        return self.progress.add_task(description=Text.assemble(*rich_parts).markup)

    def progress_track_task(
        self,
        outdated_items: Iterable[Any],
        task_id: TaskID,
    ) -> Iterable[Any]:
        """Iterate over a sequence while tracking progress for a task.

        Wraps an iterable with rich progress tracking, updating the progress
        display for the specified task as items are consumed.

        Args:
            outdated_items: An iterable of items to track progress over.
            task_id: The TaskID of the progress task to update.

        Returns:
            An iterable that yields items from outdated_items with progress tracking.
        """
        return self.progress.track(sequence=outdated_items, task_id=task_id)

    def progress_advance_task(
        self,
        task_id: TaskID,
    ) -> None:
        """Advance a progress task by one unit.

        Increments the completion counter for the specified progress task,
        updating the live display.

        Args:
            task_id: The TaskID of the progress task to advance.
        """
        self.progress.update(task_id=task_id, advance=1)

    def status_update(
        self,
        key: components.Key,
        variables: dict[str, Any] | None = None,
    ) -> None:
        """Update the status display with formatted content from a template.

        Retrieves an ITEM or REPORT-type template, flattens and formats its content,
        and updates the live status panel with the rendered text.

        Args:
            key: The Key enum value identifying an ITEM or REPORT-type template.
            variables: A dictionary of variable names and values for template
                substitution. If None, no substitution is performed. Defaults to None.

        Raises:
            ValueError: If no template exists for the key or if the template's
                type is neither Type.ITEM nor Type.REPORT.
        """
        template: components.Template = self._get_template_typecheck(
            key=key, expected_types=[components.Type.ITEM, components.Type.REPORT]
        )

        parts: list[tuple[str, str]] = self._flatten_and_format(
            content=template.content, variables=variables
        )

        self.status.update(status=Text.assemble(*parts))


@contextmanager
def rich_live_component_renderer() -> Generator[RichComponentRenderer]:
    """Context manager providing a configured rich component renderer.

    Creates and yields a RichComponentRenderer with initialized Live, Status,
    and Progress instances within a managed console panel. The live display is
    automatically cleaned up upon context exit.

    Yields:
        A RichComponentRenderer instance ready for rendering components.

    Example:
        with rich_live_component_renderer() as renderer:
            task_id = renderer.progress_add_task(Key.TASK_NAME)
            renderer.status_update(Key.STATUS_ITEM)
            for item in renderer.progress_track_task(items, task_id):
                # Process item
                renderer.progress_advance_task(task_id)
    """
    status: Status = console.status("")
    progress = Progress()

    with Live(Panel(Group(status, progress)), console=console) as live:
        rich_component_renderer = RichComponentRenderer(live, status, progress)
        yield rich_component_renderer
