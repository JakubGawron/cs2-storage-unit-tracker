"""Text-based report document management with content preservation.

This module provides TextDocument for creating and managing timestamped
text report files. It supports accumulating report sections, preserving
existing content from previous runs, and rendering templates to disk with
automatic directory creation.
"""

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
class TextDocument:
    """Text report document with content accumulation and preservation.

    Manages creation and updates of timestamped text report files. Supports
    rendering component templates to file, accumulating multiple sections,
    and preserving content from previous report runs. Files are stored in
    a specified directory with names derived from the run timestamp.

    The document uses a TextRenderer to convert component templates into
    plain-text output. On initialization, if the target file exists, its
    content (excluding the first section) is preserved and combined with
    new content during rendering.

    Attributes:
        reports_path: Directory path where report files are stored.
        last_run: Datetime of the report run, used to generate the filename.
    """

    reports_path: Path
    last_run: datetime

    _renderer = TextRenderer()
    _parts: list[str] = field(default_factory=lambda: list[str]())
    _existing_content: str = ""

    def __post_init__(self) -> None:
        """Initialize the document and load existing content if file exists.

        If the report file for this run already exists, reads its content
        and extracts everything after the first section (using double newline
        as delimiter) for preservation. This allows updates to earlier
        sections while retaining historical content.

        Raises:
            OSError: If reading the existing file fails due to permission
                or I/O errors.
            UnicodeDecodeError: If the existing file is not valid UTF-8 text.
        """
        if self.path.exists():
            content: str = self.path.read_text(encoding="utf-8")
            self._existing_content = self._extract_existing_content(content)

    @property
    def path(self) -> Path:
        """Generate the file path for the report based on the run date.

        Returns:
            Path object combining reports_path directory and a filename
            derived from last_run.date() in the format
            'portfolio_{YYYY-MM-DD}.txt'.
        """
        return self.reports_path / f"portfolio_{self.last_run.date()}.txt"

    @staticmethod
    def _extract_existing_content(content: str) -> str:
        """Extract content after the first section from a report file.

        Splits the content on the first occurrence of double newline (\\n{2}),
        which marks the boundary between the first section and subsequent
        sections. Returns all content after this boundary, preserving the
        leading newline of the second section if present.

        Args:
            content: Full text content from a report file.

        Returns:
            Content after the first double-newline boundary. If no boundary
            is found, returns an empty string. The returned string includes
            the leading newline if content had multiple sections.
        """
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
        """Render a component template to plain text.

        Delegates to the internal TextRenderer instance to convert a
        component template (identified by key) to plain-text output with
        optional variable substitution.

        Args:
            key: Component template identifier to render from the COMPONENTS
                registry.
            variables: Optional dictionary of variables for substitution in
                template text. If None, no substitution is performed.

        Returns:
            Plain-text string representation of the component template.

        Raises:
            KeyError: If key is not found in the COMPONENTS registry.
            KeyError: If variable substitution fails due to missing keys.
            ValueError: If variable substitution fails due to invalid format
                string syntax.
        """
        return self._renderer.render(
            key=key,
            variables=variables,
        )

    def add(
        self,
        key: components.Key,
        variables: dict[str, Any] | None = None,
    ) -> None:
        """Add a rendered component section to the document.

        Renders a component template and appends its output to the internal
        parts accumulator. This section will be included in the document
        when render() or save() is called.

        Args:
            key: Component template identifier to render and add.
            variables: Optional dictionary of variables for substitution in
                template text.

        Raises:
            KeyError: If key is not found in the COMPONENTS registry.
            KeyError: If variable substitution fails due to missing keys.
            ValueError: If variable substitution fails due to invalid format
                string syntax.
        """
        self._parts.append(self._render(key, variables))

    def render(
        self,
        key: components.Key,
        variables: dict[str, Any] | None = None,
    ) -> str:
        """Render the complete document with new and existing content.

        Combines three parts in order:
        1. The current template render (key with variables)
        2. Existing content from the previous run (all sections after the
           first, excluding the leading newline)
        3. All accumulated sections added via add()

        This composition allows the first section to be updated while
        preserving historical sections from previous runs.

        Args:
            key: Component template identifier for the first section.
            variables: Optional dictionary of variables for substitution in
                the first section template.

        Returns:
            Complete document text combining current render, existing
            preserved content, and accumulated parts.

        Raises:
            KeyError: If key is not found in the COMPONENTS registry.
            KeyError: If variable substitution fails due to missing keys.
            ValueError: If variable substitution fails due to invalid format
                string syntax.
        """
        current: str = self._render(key, variables)
        return current + self._existing_content[1:] + "".join(self._parts)

    def save(
        self,
        key: components.Key,
        variables: dict[str, Any] | None = None,
    ) -> None:
        """Render and save the complete document to disk.

        Renders the complete document (via render()) and writes it to the
        file specified by path. Creates the reports directory and all parent
        directories as needed.

        Args:
            key: Component template identifier for the first section.
            variables: Optional dictionary of variables for substitution in
                the first section template.

        Raises:
            KeyError: If key is not found in the COMPONENTS registry.
            KeyError: If variable substitution fails due to missing keys.
            ValueError: If variable substitution fails due to invalid format
                string syntax.
            OSError: If creating the directory or writing the file fails due
                to permission or I/O errors.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            self.render(key, variables),
            encoding="utf-8",
        )

    def clear(self) -> None:
        """Clear the document and reset state to empty.

        Writes an empty file to disk, clears all accumulated parts, and
        resets the existing content cache. Creates the reports directory
        if it does not exist. This operation effectively resets the document
        to a blank state.

        Raises:
            OSError: If creating the directory or writing the file fails due
                to permission or I/O errors.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8")
        self._existing_content = ""
        self._parts.clear()
