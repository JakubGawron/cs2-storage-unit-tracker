from dataclasses import dataclass
from enum import IntEnum, StrEnum
from types import MappingProxyType


class Style(StrEnum):
    DEFAULT = "#dddddd"
    DEFAULT_HIGHLIGHT = "bold #ffffff"

    FAILED_HEADER = "#dd0000"
    FAILED_HIGHLIGHT = "bold #ff0000"

    SUCCESSFUL_HEADER = "#00dd00"
    SUCCESSFUL_HEADER_HIGHLIGHT = "bold #00ff00"

    ITEM_HEADER = "underline bold #5ccfe6"
    ITEM_FIELD = "#005fd7"

    REPORT_HEADER = "underline bold #dfbfff"
    REPORT_FIELD = "#8700af"

    POSITIVE_PROFIT = "bold #00ff00"
    NEGATIVE_PROFIT = "bold #ff0000"


class LayoutWidth(IntEnum):
    HEADER = 78
    ITEM_FIELD = 20
    PRICE = 20
    REPORT_FIELD = 20
    STATUS = 26


class Key(StrEnum):
    ADD_TASK = "add_task"
    STATUS_HEADER = "status_header"

    ITEM_HEADER = "item_header"
    ITEM_FIELDS = "item_fields"

    ITEM_POSITIVE_PROFIT = "item_positive_profit"
    ITEM_NEGATIVE_PROFIT = "item_negative_profit"

    ITEM_POSITIVE = "item_positive"
    ITEM_NEGATIVE = "item_negative"
    ITEM_FAILED = "item_failed"

    REPORT_HEADER = "report_header"
    REPORT_FIELDS = "report_fields"

    REPORT_POSITIVE_PROFIT = "report_positive_profit"
    REPORT_NEGATIVE_PROFIT = "report_negative_profit"

    REPORT_POSITIVE = "report_positive"
    REPORT_NEGATIVE = "report_negative"
    REPORT_FAILED = "report_failed"


class Type(StrEnum):
    TASK = "task"
    STATUS = "status"

    ITEM = "item"
    ITEM_HEADER = "item_header"
    ITEM_DETAILS = "item_details"

    REPORT = "report"
    REPORT_HEADER = "report_header"
    REPORT_DETAILS = "report_details"


@dataclass(frozen=True, slots=True, kw_only=True)
class Segment:
    text: str
    style: Style
    min_width: int | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class Group:
    segments: tuple[Segment, ...]
    min_width: int | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class Template:
    type: Type
    content: tuple[Segment | Group | Key, ...]


COMPONENTS: MappingProxyType[Key, Template] = MappingProxyType(
    {
        Key.ADD_TASK: Template(
            type=Type.TASK,
            content=(
                Segment(
                    text="  Calculating prices ",
                    style=Style.DEFAULT_HIGHLIGHT,
                ),
            ),
        ),
        Key.STATUS_HEADER: Template(
            type=Type.STATUS,
            content=(
                Group(
                    segments=(
                        Segment(
                            text="Pending: (",
                            style=Style.DEFAULT,
                        ),
                        Segment(
                            text="{pending_count}/{outdated_total}",
                            style=Style.DEFAULT_HIGHLIGHT,
                        ),
                        Segment(
                            text=")",
                            style=Style.DEFAULT,
                        ),
                    ),
                    min_width=LayoutWidth.STATUS,
                ),
                Group(
                    segments=(
                        Segment(
                            text="Failed: (",
                            style=Style.FAILED_HEADER,
                        ),
                        Segment(
                            text="{failed_count}/{outdated_total}",
                            style=Style.FAILED_HIGHLIGHT,
                        ),
                        Segment(
                            text=")",
                            style=Style.FAILED_HEADER,
                        ),
                    ),
                    min_width=LayoutWidth.STATUS,
                ),
                Group(
                    segments=(
                        Segment(
                            text="Successful: (",
                            style=Style.SUCCESSFUL_HEADER,
                        ),
                        Segment(
                            text="{successful_count}/{total_items_count}",
                            style=Style.SUCCESSFUL_HEADER_HIGHLIGHT,
                        ),
                        Segment(
                            text=")\n",
                            style=Style.SUCCESSFUL_HEADER,
                        ),
                    ),
                    min_width=LayoutWidth.STATUS,
                ),
            ),
        ),
        Key.ITEM_HEADER: Template(
            type=Type.ITEM_HEADER,
            content=(
                Segment(
                    text="\n{item_name}",
                    style=Style.ITEM_HEADER,
                    min_width=LayoutWidth.HEADER,
                ),
            ),
        ),
        Key.ITEM_FIELDS: Template(
            type=Type.ITEM_DETAILS,
            content=(
                Segment(
                    text="\nQuantity: ",
                    style=Style.ITEM_FIELD,
                    min_width=LayoutWidth.ITEM_FIELD,
                ),
                Segment(
                    text="{item_quantity}",
                    style=Style.DEFAULT_HIGHLIGHT,
                ),
                Segment(
                    text="\nUnit cost: ",
                    style=Style.ITEM_FIELD,
                    min_width=LayoutWidth.ITEM_FIELD,
                ),
                Segment(
                    text="{item_purchase_price}",
                    style=Style.DEFAULT,
                    min_width=LayoutWidth.PRICE,
                ),
                Segment(
                    text="{exchanged_item_purchase_price}",
                    style=Style.DEFAULT,
                    min_width=LayoutWidth.PRICE,
                ),
                Segment(
                    text="\nTotal cost: ",
                    style=Style.ITEM_FIELD,
                    min_width=LayoutWidth.ITEM_FIELD,
                ),
                Segment(
                    text="{item_purchase_total}",
                    style=Style.DEFAULT_HIGHLIGHT,
                    min_width=LayoutWidth.PRICE,
                ),
                Segment(
                    text="{exchanged_item_purchase_total}",
                    style=Style.DEFAULT_HIGHLIGHT,
                    min_width=LayoutWidth.PRICE,
                ),
                Segment(
                    text="\nUnit price: ",
                    style=Style.ITEM_FIELD,
                    min_width=LayoutWidth.ITEM_FIELD,
                ),
                Segment(
                    text="{item_selling_price}",
                    style=Style.DEFAULT,
                    min_width=LayoutWidth.PRICE,
                ),
                Segment(
                    text="{exchanged_item_selling_price}",
                    style=Style.DEFAULT,
                    min_width=LayoutWidth.PRICE,
                ),
                Segment(
                    text="\nTotal price: ",
                    style=Style.ITEM_FIELD,
                    min_width=LayoutWidth.ITEM_FIELD,
                ),
                Segment(
                    text="{item_selling_total}",
                    style=Style.DEFAULT_HIGHLIGHT,
                    min_width=LayoutWidth.PRICE,
                ),
                Segment(
                    text="{exchanged_item_selling_total}",
                    style=Style.DEFAULT_HIGHLIGHT,
                    min_width=LayoutWidth.PRICE,
                ),
            ),
        ),
        Key.ITEM_POSITIVE_PROFIT: Template(
            type=Type.ITEM_DETAILS,
            content=(
                Segment(
                    text="\nProfit: ",
                    style=Style.ITEM_FIELD,
                    min_width=LayoutWidth.ITEM_FIELD,
                ),
                Segment(
                    text="{item_profit_value}",
                    style=Style.POSITIVE_PROFIT,
                    min_width=LayoutWidth.PRICE,
                ),
                Segment(
                    text="{exchanged_item_profit_value}",
                    style=Style.POSITIVE_PROFIT,
                    min_width=LayoutWidth.PRICE,
                ),
                Segment(
                    text="\nMargin: ",
                    style=Style.ITEM_FIELD,
                    min_width=LayoutWidth.ITEM_FIELD,
                ),
                Segment(text="{item_profit_margin}% ▲", style=Style.POSITIVE_PROFIT),
                Segment(
                    text="\nROI: ",
                    style=Style.ITEM_FIELD,
                    min_width=LayoutWidth.ITEM_FIELD,
                ),
                Segment(text="{item_roi}% ▲\n", style=Style.POSITIVE_PROFIT),
            ),
        ),
        Key.ITEM_NEGATIVE_PROFIT: Template(
            type=Type.ITEM_DETAILS,
            content=(
                Segment(
                    text="\nProfit: ",
                    style=Style.ITEM_FIELD,
                    min_width=LayoutWidth.ITEM_FIELD,
                ),
                Segment(
                    text="{item_profit_value}",
                    style=Style.NEGATIVE_PROFIT,
                    min_width=LayoutWidth.PRICE,
                ),
                Segment(
                    text="{exchanged_item_profit_value}",
                    style=Style.NEGATIVE_PROFIT,
                    min_width=LayoutWidth.PRICE,
                ),
                Segment(
                    text="\nMargin: ",
                    style=Style.ITEM_FIELD,
                    min_width=LayoutWidth.ITEM_FIELD,
                ),
                Segment(text="{item_profit_margin}% ▼", style=Style.NEGATIVE_PROFIT),
                Segment(
                    text="\nROI: ",
                    style=Style.ITEM_FIELD,
                    min_width=LayoutWidth.ITEM_FIELD,
                ),
                Segment(text="{item_roi}% ▼\n", style=Style.NEGATIVE_PROFIT),
            ),
        ),
        Key.ITEM_POSITIVE: Template(
            type=Type.ITEM,
            content=(
                Key.STATUS_HEADER,
                Key.ITEM_HEADER,
                Key.ITEM_FIELDS,
                Key.ITEM_POSITIVE_PROFIT,
            ),
        ),
        Key.ITEM_NEGATIVE: Template(
            type=Type.ITEM,
            content=(
                Key.STATUS_HEADER,
                Key.ITEM_HEADER,
                Key.ITEM_FIELDS,
                Key.ITEM_NEGATIVE_PROFIT,
            ),
        ),
        Key.ITEM_FAILED: Template(
            type=Type.ITEM,
            content=(
                Key.STATUS_HEADER,
                Key.ITEM_HEADER,
                Key.ITEM_FIELDS,
            ),
        ),
        Key.REPORT_HEADER: Template(
            type=Type.REPORT_HEADER,
            content=(
                Segment(
                    text="\nPortfolio Performance Report",
                    style=Style.REPORT_HEADER,
                    min_width=LayoutWidth.HEADER,
                ),
            ),
        ),
        Key.REPORT_FIELDS: Template(
            type=Type.REPORT_DETAILS,
            content=(
                Segment(
                    text="\nTotal units: ",
                    style=Style.REPORT_FIELD,
                    min_width=LayoutWidth.REPORT_FIELD,
                ),
                Segment(
                    text="{total_units}",
                    style=Style.DEFAULT_HIGHLIGHT,
                ),
                Segment(
                    text="\nTotal cost: ",
                    style=Style.REPORT_FIELD,
                    min_width=LayoutWidth.REPORT_FIELD,
                ),
                Segment(
                    text="{total_cost}",
                    style=Style.DEFAULT,
                    min_width=LayoutWidth.PRICE,
                ),
                Segment(
                    text="{exchanged_total_cost}",
                    style=Style.DEFAULT,
                    min_width=LayoutWidth.PRICE,
                ),
                Segment(
                    text="\nTotal price: ",
                    style=Style.REPORT_FIELD,
                    min_width=LayoutWidth.REPORT_FIELD,
                ),
                Segment(
                    text="{total_price}",
                    style=Style.DEFAULT_HIGHLIGHT,
                    min_width=LayoutWidth.PRICE,
                ),
                Segment(
                    text="{exchanged_total_price}",
                    style=Style.DEFAULT_HIGHLIGHT,
                    min_width=LayoutWidth.PRICE,
                ),
            ),
        ),
        Key.REPORT_POSITIVE_PROFIT: Template(
            type=Type.REPORT_DETAILS,
            content=(
                Segment(
                    text="\nTotal profit: ",
                    style=Style.REPORT_FIELD,
                    min_width=LayoutWidth.REPORT_FIELD,
                ),
                Segment(
                    text="{total_profit}",
                    style=Style.POSITIVE_PROFIT,
                    min_width=LayoutWidth.PRICE,
                ),
                Segment(
                    text="{exchanged_total_profit}",
                    style=Style.POSITIVE_PROFIT,
                    min_width=LayoutWidth.PRICE,
                ),
                Segment(
                    text="\nTotal margin: ",
                    style=Style.REPORT_FIELD,
                    min_width=LayoutWidth.REPORT_FIELD,
                ),
                Segment(text="{total_margin}% ▲", style=Style.POSITIVE_PROFIT),
                Segment(
                    text="\nTotal ROI: ",
                    style=Style.REPORT_FIELD,
                    min_width=LayoutWidth.REPORT_FIELD,
                ),
                Segment(text="{total_roi}% ▲\n\n\n", style=Style.POSITIVE_PROFIT),
            ),
        ),
        Key.REPORT_NEGATIVE_PROFIT: Template(
            type=Type.REPORT_DETAILS,
            content=(
                Segment(
                    text="\nTotal profit: ",
                    style=Style.REPORT_FIELD,
                    min_width=LayoutWidth.REPORT_FIELD,
                ),
                Segment(
                    text="{total_profit}",
                    style=Style.NEGATIVE_PROFIT,
                    min_width=LayoutWidth.PRICE,
                ),
                Segment(
                    text="{exchanged_total_profit}",
                    style=Style.NEGATIVE_PROFIT,
                    min_width=LayoutWidth.PRICE,
                ),
                Segment(
                    text="\nTotal margin: ",
                    style=Style.REPORT_FIELD,
                    min_width=LayoutWidth.REPORT_FIELD,
                ),
                Segment(text="{total_margin}% ▼", style=Style.NEGATIVE_PROFIT),
                Segment(
                    text="\nTotal ROI: ",
                    style=Style.REPORT_FIELD,
                    min_width=LayoutWidth.REPORT_FIELD,
                ),
                Segment(text="{total_roi}% ▼\n\n\n", style=Style.NEGATIVE_PROFIT),
            ),
        ),
        Key.REPORT_POSITIVE: Template(
            type=Type.REPORT,
            content=(
                Key.STATUS_HEADER,
                Key.REPORT_HEADER,
                Key.REPORT_FIELDS,
                Key.REPORT_POSITIVE_PROFIT,
            ),
        ),
        Key.REPORT_NEGATIVE: Template(
            type=Type.REPORT,
            content=(
                Key.STATUS_HEADER,
                Key.REPORT_HEADER,
                Key.REPORT_FIELDS,
                Key.REPORT_NEGATIVE_PROFIT,
            ),
        ),
        Key.REPORT_FAILED: Template(
            type=Type.REPORT,
            content=(
                Key.STATUS_HEADER,
                Key.REPORT_HEADER,
                Key.REPORT_FIELDS,
            ),
        ),
    }
)
