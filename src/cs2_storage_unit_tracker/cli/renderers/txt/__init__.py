"""Text-based report document management API.

This module provides the public interface for text-based report document
handling. It re-exports MarkdownDocument, which manages creation and updates
of timestamped text report files with content accumulation and preservation.
"""

from cs2_storage_unit_tracker.cli.renderers.txt.document import TextDocument

__all__: list[str] = ["TextDocument"]
