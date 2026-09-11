from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType


class Icon(StrEnum):
    SUCCESS = "✅  "
    WARNING = "⚠️   "
    ERROR = "❌  "


class Style(StrEnum):
    SUCCESS = "#00dd00"
    SUCCESS_HIGHLIGHT = "bold #00ff00"

    WARNING = "#ddd000"
    WARNING_HIGHLIGHT = "bold #fff000"

    ERROR = "#dd0000"
    ERROR_HIGHLIGHT = "bold #ff0000"


class Key(StrEnum):
    CONFIG_ERROR = "config_error"
    LAST_CURRENCY_EXCHANGE_FAIL = "last_currency_exchange_fail"
    RATE_EXCHANGE_FAIL = "rate_exchange_fail"
    ALREADY_FINISHED = "already_finished"
    ALREADY_RUN = "already_run"
    DAILY_LIMIT = "daily_limit"
    PARTIAL_RUN = "partial_run"
    INTERRUPTED_PROGRAM = "interrupted_program"


class Type(StrEnum):
    PRINT = "print"
    CONFIRM = "confirm"


@dataclass(frozen=True, slots=True, kw_only=True)
class Segment:
    text: str
    style: Style


@dataclass(frozen=True, slots=True, kw_only=True)
class Template:
    type: Type
    segments: tuple[Segment, ...]
    icon: str | Icon = ""


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
