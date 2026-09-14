"""Message template system for user-facing notifications and confirmations.

This module provides a structured system for displaying styled messages with icons,
supporting both informational output and user confirmations. Templates combine
segments of styled text with optional icons to create consistent, formatted messages
throughout the application.
"""

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType


class Icon(StrEnum):
    """Enumeration of visual icons for message categorization.

    Each icon provides a visual indicator of message severity or status,
    enhancing user comprehension at a glance.
    """

    SUCCESS = "✅  "
    WARNING = "⚠️   "
    ERROR = "❌  "


class Style(StrEnum):
    """Enumeration of text styling options for message segments.

    Styles define colors and text decorations compatible with the rich library,
    enabling visual emphasis and semantic color-coding of message content.
    """

    SUCCESS = "#00dd00"
    SUCCESS_HIGHLIGHT = "bold #00ff00"

    WARNING = "#ddd000"
    WARNING_HIGHLIGHT = "bold #fff000"

    ERROR = "#dd0000"
    ERROR_HIGHLIGHT = "bold #ff0000"


class Key(StrEnum):
    """Enumeration of unique identifiers for retrieving message templates.

    Keys serve as lookup identifiers for predefined messages in the MESSAGES
    registry, enabling type-safe message retrieval and consistent messaging.
    """

    CONFIG_ERROR = "config_error"
    LAST_CURRENCY_EXCHANGE_FAIL = "last_currency_exchange_fail"
    RATE_EXCHANGE_FAIL = "rate_exchange_fail"
    ALREADY_FINISHED = "already_finished"
    ALREADY_RUN = "already_run"
    DAILY_LIMIT = "daily_limit"
    PARTIAL_RUN = "partial_run"
    INTERRUPTED_PROGRAM = "interrupted_program"


class Type(StrEnum):
    """Enumeration of template interaction types.

    Types indicate whether a template represents informational output that should
    be printed or an action requiring user confirmation.
    """

    PRINT = "print"
    CONFIRM = "confirm"


@dataclass(frozen=True, slots=True, kw_only=True)
class Segment:
    """A styled text segment within a message template.

    A segment represents a continuous portion of text with uniform styling.
    Multiple segments compose a complete message, allowing fine-grained control
    over text appearance. Segment text may contain format placeholders
    (e.g., "{variable}") for dynamic content substitution.

    Attributes:
        text: The text content, optionally containing format placeholders.
        style: The Style enum value defining visual presentation and color.
    """

    text: str
    style: Style


@dataclass(frozen=True, slots=True, kw_only=True)
class Template:
    """A complete message template with type, styling, and optional icon.

    Templates define structured messages combining multiple styled segments,
    an interaction type, and an optional visual icon. They serve as blueprints
    for rendering messages with consistent formatting and presentation.

    Attributes:
        type: The Type enum value indicating whether the message should be printed
            or requires user confirmation.
        segments: An ordered tuple of Segment objects that compose the message.
            Segments are rendered sequentially to form the complete message.
        icon: An Icon enum value or custom string prepended to the message.
            Defaults to an empty string, indicating no icon. Common practice is to
            use an Icon enum value for consistency.
    """

    type: Type
    segments: tuple[Segment, ...]
    icon: str | Icon = ""


"""Immutable registry of predefined message templates.

A MappingProxyType providing read-only access to all message templates keyed by
their unique Key enum values. Templates in this registry support format string
substitution via placeholders (e.g., "{message}", "{limit}") to enable dynamic
message generation while maintaining consistent styling and structure.
"""
MESSAGES: MappingProxyType[Key, Template] = MappingProxyType(
    {
        Key.CONFIG_ERROR: Template(
            type=Type.PRINT,
            segments=(
                Segment(text="{message} ", style=Style.ERROR),
                Segment(text="'{path}'", style=Style.ERROR_HIGHLIGHT),
            ),
            icon=Icon.ERROR,
        ),
        Key.LAST_CURRENCY_EXCHANGE_FAIL: Template(
            type=Type.CONFIRM,
            segments=(
                Segment(
                    text="Unable to convert the previously used currency. Would you like to reset your progress and start over? You can try again later if you choose No.",
                    style=Style.WARNING,
                ),
            ),
            icon=Icon.WARNING,
        ),
        Key.RATE_EXCHANGE_FAIL: Template(
            type=Type.CONFIRM,
            segments=(
                Segment(
                    text="Unable to get current currency rate for exchange. Run anyway?",
                    style=Style.WARNING,
                ),
            ),
            icon=Icon.WARNING,
        ),
        Key.ALREADY_FINISHED: Template(
            type=Type.CONFIRM,
            segments=(
                Segment(
                    text="You have already generated the report for this period. Run it again?",
                    style=Style.SUCCESS,
                ),
                Segment(
                    text=" (This will erase the current report)",
                    style=Style.ERROR,
                ),
            ),
            icon=Icon.SUCCESS,
        ),
        Key.ALREADY_RUN: Template(
            type=Type.CONFIRM,
            segments=(
                Segment(
                    text="You have already run that program during this period. Run it again?",
                    style=Style.WARNING,
                ),
            ),
            icon=Icon.WARNING,
        ),
        Key.DAILY_LIMIT: Template(
            type=Type.PRINT,
            segments=(
                Segment(text="Daily request limit (", style=Style.ERROR),
                Segment(text="{limit}", style=Style.ERROR_HIGHLIGHT),
                Segment(text=") reached. Try again tomorrow.", style=Style.ERROR),
            ),
            icon=Icon.ERROR,
        ),
        Key.PARTIAL_RUN: Template(
            type=Type.CONFIRM,
            segments=(
                Segment(
                    text="Only (",
                    style=Style.WARNING,
                ),
                Segment(
                    text="{completable_requests}/{outdated_total}",
                    style=Style.WARNING_HIGHLIGHT,
                ),
                Segment(text=") will be completed. Run anyway?", style=Style.WARNING),
            ),
            icon=Icon.WARNING,
        ),
        Key.INTERRUPTED_PROGRAM: Template(
            type=Type.PRINT,
            segments=(
                Segment(
                    text="Program interrupted (KeyboardInterrupt).",
                    style=Style.WARNING,
                ),
            ),
            icon=Icon.WARNING,
        ),
    }
)
