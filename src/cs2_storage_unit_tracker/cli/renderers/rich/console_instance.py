"""Shared rich console instance for CLI output and rendering.

This module provides a singleton Console instance used throughout the application
for rendering rich-formatted output. All styled text, panels, progress indicators,
and live updates are rendered through this console to ensure consistent formatting
and output behavior across the CLI.

This console instance should be imported and used by all rendering modules rather
than creating separate Console instances.

Attributes:
    console: A rich Console instance configured for standard output rendering.
"""

from rich.console import Console

console = Console()
