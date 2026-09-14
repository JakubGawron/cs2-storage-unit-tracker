"""Plain-text rendering of styled component templates.

This module converts component templates into plain-text output with ASCII
decorations (headers, dividers) based on style indicators. It handles
multi-line content, preserves styling semantics through text decoration,
and performs regex-based transformations on status output.
"""

import re
from typing import Any, LiteralString

from cs2_storage_unit_tracker.cli.content.rich import components
from cs2_storage_unit_tracker.cli.renderers.flatten import flatten_and_format

STATUS_HEADERS: set[components.Style] = {
    components.Style.FAILED_HEADER,
    components.Style.SUCCESSFUL_HEADER,
}


class TextRenderer:
    """Plain-text renderer for component templates with ASCII decorations.

    Renders component templates (referenced by Key) to plain-text strings with
    ASCII headers, dividers, and status decorations. Preserves line structure,
    applies variable substitution, and transforms status output using regex.

    Attributes:
        HEADER_WIDTH: Minimum character width for header and divider lines,
            derived from LayoutWidth.HEADER.
    """

    HEADER_WIDTH: components.LayoutWidth = components.LayoutWidth.HEADER

    def render(
        self,
        key: components.Key,
        variables: dict[str, Any] | None = None,
    ) -> str:
        """Render a component template to plain text with ASCII decorations.

        Resolves the template by key, applies variable substitution, flattens
        into lines, and renders each line with appropriate ASCII decorations
        (headers, dividers, or plain text) based on style indicators. Empty
        lines are skipped; output lines are normalized to \\n terminators.

        Args:
            key: Component template identifier to render from the COMPONENTS
                registry.
            variables: Optional dictionary of variables for substitution in
                template text via `str.format_map()`. If None, no substitution
                is performed.

        Returns:
            Plain-text string with ASCII decorations. Each line ends with \\n.
            Empty output returns an empty string.

        Raises:
            KeyError: If key is not found in the COMPONENTS registry.
            KeyError: If variable substitution fails due to missing keys in the
                variables dictionary.
            ValueError: If variable substitution fails due to invalid format
                string syntax in template content.
        """
        parts: list[tuple[str, components.Style | None]] = flatten_and_format(
            content=components.COMPONENTS[key].content,
            variables=variables,
        )

        lines: list[list[tuple[str, components.Style | None]]] = self._flatten_lines(
            parts
        )

        output: list[str] = []
        for line in lines:
            if not line:
                continue

            output.append(self._render_line(line))

        return "".join(output)

    @staticmethod
    def _flatten_lines(
        parts: list[tuple[str, components.Style | None]],
    ) -> list[list[tuple[str, components.Style | None]]]:
        """Split styled text parts into lines based on newline boundaries.

        Processes a flat list of (text, style) tuples, splitting multi-line
        text on \\n and \\r newline characters while preserving style
        associations. Empty text values and trailing whitespace are stripped
        from individual chunks. Each line is grouped as a separate list of
        (text, style) tuples.

        Args:
            parts: List of (text, style) tuples to split into lines.

        Returns:
            List of line groups, where each group is a list of (text, style)
            tuples belonging to the same line. Empty text chunks are excluded.
        """
        lines: list[list[tuple[str, components.Style | None]]] = []
        current: list[tuple[str, components.Style | None]] = []

        for text, style in parts:
            if not text:
                continue

            for chunk in text.splitlines(keepends=True):
                value: str = chunk.rstrip("\r\n")
                has_newline: bool = chunk.endswith(("\n", "\r"))

                if value:
                    current.append((value, style))

                if has_newline:
                    lines.append(current)
                    current = []

        if current:
            lines.append(current)

        return lines

    def _render_line(
        self,
        parts: list[tuple[str, components.Style | None]],
    ) -> str:
        """Render a single line with ASCII decoration based on style.

        Determines appropriate decoration (main header, item header, status,
        or plain text) based on the style indicators present in the line.
        Joins text parts, strips leading/trailing whitespace, and applies
        style-specific formatting. If no text remains after stripping,
        returns a single newline.

        Args:
            parts: List of (text, style) tuples comprising a single line.

        Returns:
            Formatted line string ending with \\n. Style-based decorations
            (divider lines) may span multiple lines in output.
        """
        styles: set[components.Style | None] = {style for _, style in parts}
        text: str = "".join(value for value, _ in parts).strip()

        if not text:
            return "\n"

        if styles & STATUS_HEADERS:
            return self._render_status(text)

        if components.Style.REPORT_HEADER in styles:
            return self._render_main_header(text)

        if components.Style.ITEM_HEADER in styles:
            return self._render_item_header(text)

        return f"{text}\n"

    def _render_main_header(self, text: str) -> str:
        """Render a main report header with top and bottom dividers.

        Formats the text between two lines of equals signs (=) matching
        HEADER_WIDTH, with blank lines between divider and text.

        Args:
            text: Header text to render.

        Returns:
            Formatted header string: equals divider, text, equals divider,
            each on separate lines ending with \\n.
        """
        line: LiteralString = "=" * self.HEADER_WIDTH

        return f"{line}\n{text}\n{line}\n"

    def _render_item_header(self, text: str) -> str:
        """Render an item section header with top and bottom dividers.

        Formats the text between two lines of hyphens (-) matching HEADER_WIDTH,
        with blank lines before and after the divider block.

        Args:
            text: Header text to render.

        Returns:
            Formatted item header string: blank lines, hyphen divider, text,
            hyphen divider, each on separate lines ending with \\n.
        """
        line: LiteralString = "-" * self.HEADER_WIDTH

        return f"\n\n{line}\n{text}\n{line}\n"

    def _render_status(self, text: str) -> str:
        """Render a status line with divider and regex substitution.

        Transforms progress indicators from parenthesized format (n/n) to
        bracketed format [n/n], then places the text between two lines of
        hyphens (-) matching HEADER_WIDTH. No trailing newline is appended.

        Args:
            text: Status text potentially containing progress indicators in
                the format (digit/digit).

        Returns:
            Formatted status string: hyphen divider, transformed text,
            hyphen divider, each on separate lines. Output does not end
            with \\n.
        """
        text = re.sub(
            r"\((\d+/\d+)\)",
            r"[\1]",
            text,
        )

        return f"{'-' * self.HEADER_WIDTH}\n{text}\n{'-' * self.HEADER_WIDTH}"
