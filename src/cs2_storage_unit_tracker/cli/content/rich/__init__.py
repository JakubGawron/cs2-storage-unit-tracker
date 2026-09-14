"""Unified access to template key enumerations for components and messages.

This module re-exports `Key` enum classes from the components and messages
subsystems with disambiguating aliases, enabling convenient imports in code
that needs to reference template identifiers from both systems.

Exports:
    components_key: Enum of unique identifiers for component templates in
        the structured report rendering system.
    messages_key: Enum of unique identifiers for message templates in
        the notification and confirmation system.
"""

from cs2_storage_unit_tracker.cli.content.rich.components import Key as components_key
from cs2_storage_unit_tracker.cli.content.rich.messages import Key as messages_key

__all__: list[str] = ["components_key", "messages_key"]
