"""Rendering module for rich-formatted CLI messages.

This module provides the RichMessageRenderer class, which renders predefined message
templates from the messages registry to the console using the rich library. It supports
formatted text output with variable substitution, user confirmation prompts, and console
clearing.

The renderer ensures type safety by validating that templates match their expected
message types (PRINT, CONFIRM, etc.) before rendering.
"""

from dataclasses import dataclass
from typing import Any

from rich.prompt import Confirm
from rich.text import Text

from cs2_storage_unit_tracker.cli.content.rich import messages
from cs2_storage_unit_tracker.cli.renderers.rich.console_instance import console


@dataclass(frozen=True, slots=True)
class RichMessageRenderer:
    """Renders rich-formatted message templates to the console.

    This renderer validates and processes message templates from the messages registry,
    supporting formatted output with optional variable substitution, confirmation
    prompts, and console state management. All output is rendered through a shared
    console instance to ensure consistent formatting.

    The class uses a frozen dataclass with slots for immutability and memory efficiency.
    All methods are designed to work with the predefined message registry.
    """

    @staticmethod
    def _check_type(received_type: messages.Type, expected_type: messages.Type) -> None:
        """Validate that a template type matches the expected type.

        Args:
            received_type: The type received from the template.
            expected_type: The type expected for this operation.

        Raises:
            ValueError: If received_type does not match expected_type.
        """
        if received_type is not expected_type:
            raise ValueError(
                f"Invalid type: {received_type!r}. Expected: {expected_type!r}"
            )

    def _get_template_typecheck(
        self, key: messages.Key, expected_type: messages.Type
    ) -> messages.Template:
        """Fetch and validate a message template by key and type.

        Retrieves a template from the messages registry and ensures it matches
        the expected type. This provides type safety when rendering templates
        for specific operations (e.g., PRINT, CONFIRM).

        Args:
            key: The unique identifier of the message template to retrieve.
            expected_type: The required type of the template.

        Returns:
            The validated template matching the given key and type.

        Raises:
            ValueError: If no template exists for the key or if the template
                type does not match the expected type.
        """
        try:
            template: messages.Template = messages.MESSAGES[key]
            self._check_type(received_type=template.type, expected_type=expected_type)
            return template
        except KeyError as exc:
            raise ValueError(
                f"No message template exists for key {key.value!r}"
            ) from exc

    @staticmethod
    def _format_text_parts(
        segments: tuple[messages.Segment, ...], variables: dict[str, Any] | None = None
    ) -> list[tuple[str, str]]:
        """Format message segments into rich-compatible text parts.

        Converts template segments into tuples of (text, style) pairs suitable for
        rich.text.Text.assemble(). Optionally performs variable substitution on
        segment text using the provided variables dictionary.

        Args:
            segments: A tuple of Segment objects to format.
            variables: Optional dictionary of variables for text substitution.
                If provided, segment text is formatted using str.format_map().
                Defaults to None (no substitution).

        Returns:
            A list of (text, style_value) tuples where style_value is the string
            representation of the segment's style.
        """
        if variables is None:
            parts: list[tuple[str, str]] = [
                (segment.text, segment.style.value) for segment in segments
            ]
        else:
            parts: list[tuple[str, str]] = [
                (
                    segment.text.format_map(variables),
                    segment.style.value,
                )
                for segment in segments
            ]
        return parts

    def print(self, key: messages.Key, variables: dict[str, Any] | None = None) -> None:
        """Print a formatted message to the console.

        Retrieves and renders a message template marked as PRINT type, optionally
        substituting variables into the message text. The message includes an icon
        and styled text segments as defined in the template.

        Args:
            key: The unique identifier of the message template to print.
            variables: Optional dictionary of variables for text substitution within
                the message segments. Defaults to None (no substitution).

        Raises:
            ValueError: If no template exists for the key or if the template
                type is not PRINT.
        """
        template: messages.Template = self._get_template_typecheck(
            key=key, expected_type=messages.Type.PRINT
        )

        parts: list[tuple[str, str]] = [
            (template.icon, ""),
            *self._format_text_parts(segments=template.segments, variables=variables),
        ]

        console.print(Text.assemble(*parts))

    def confirm(
        self,
        key: messages.Key,
        default: bool = False,
        variables: dict[str, Any] | None = None,
    ) -> bool:
        """Display a confirmation prompt to the user.

        Retrieves and renders a message template marked as CONFIRM type as an
        interactive confirmation prompt. The user must respond with 'y' or 'n'
        to proceed. Optionally substitutes variables into the prompt text.

        Args:
            key: The unique identifier of the message template to display.
            default: The default response if the user presses Enter without input.
                Defaults to False (no).
            variables: Optional dictionary of variables for text substitution within
                the message segments. Defaults to None (no substitution).

        Returns:
            True if the user confirms (responds 'y'), False otherwise (responds 'n'
            or accepts the default).

        Raises:
            ValueError: If no template exists for the key or if the template
                type is not CONFIRM.
        """
        template: messages.Template = self._get_template_typecheck(
            key=key, expected_type=messages.Type.CONFIRM
        )

        parts: list[tuple[str, str]] = [
            (template.icon, ""),
            *self._format_text_parts(segments=template.segments, variables=variables),
        ]

        result: bool = Confirm.ask(
            Text.assemble(*parts), default=default, console=console
        )

        return result

    @staticmethod
    def clear() -> None:
        """Clear the console display.

        Removes all content from the console, resetting it to an empty state.
        Useful for cleaning up the terminal before rendering new content or
        after long-running operations.
        """
        console.clear()
