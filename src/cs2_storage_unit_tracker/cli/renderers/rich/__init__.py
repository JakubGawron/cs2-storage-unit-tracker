"""Rich library-based renderers for CLI output and templates.

This module provides high-level rendering interfaces for styled message and
component output using the rich library, supporting variable substitution,
interactive prompts, live updates, and progress tracking.

Exports:
    RichMessageRenderer: Renders message templates with variable substitution,
        styled output, and interactive confirmation prompts.
    rich_live_component_renderer: Context manager for hierarchical component
        rendering with live updates, status panels, and progress tracking.
"""

from cs2_storage_unit_tracker.cli.renderers.rich.component_renderer import (
    rich_live_component_renderer,
)
from cs2_storage_unit_tracker.cli.renderers.rich.message_renderer import (
    RichMessageRenderer,
)

__all__: list[str] = ["RichMessageRenderer", "rich_live_component_renderer"]
