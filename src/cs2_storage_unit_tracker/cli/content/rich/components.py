"""Template-based configuration system for styled reporting output.

This module defines the structure for creating templated reports with rich styling,
layout constraints, and dynamic content substitution. It provides enums for styling,
layout dimensions, component keys, and templates that combine segments and groups
into structured output formats.
"""

from dataclasses import dataclass
from enum import IntEnum, StrEnum
from types import MappingProxyType


class Style(StrEnum):
    """Enumeration of predefined styles for text rendering.

    Each style defines visual attributes compatible with rich library formatting,
    including colors and text decorations (bold, underline, etc.).
    """

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
    """Enumeration of predefined minimum width constraints for layout components.

    These values define the minimum character width allocated to different
    content sections to ensure consistent alignment and readability.
    """

    HEADER = 78
    ITEM_FIELD = 20
    PRICE = 20
    REPORT_FIELD = 20
    STATUS = 26


class Key(StrEnum):
    """Enumeration of component identifiers for template references.

    Keys serve as unique identifiers for template components and can reference
    other templates, enabling hierarchical composition and reuse.
    """

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

    TEXT_ITEM_POSITIVE = "text_item_positive"
    TEXT_ITEM_NEGATIVE = "text_item_negative"


class Type(StrEnum):
    """Enumeration of top-level template types for categorization and rendering.

    Types classify templates by their primary function and content structure,
    enabling type-aware rendering and processing logic.
    """

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
    """An indivisible unit of styled text content.

    A segment represents a single text string with associated styling and optional
    layout constraints. Segments are the atomic building blocks of template output.

    Attributes:
        text: The text content, which may contain format placeholders (e.g., "{value}").
        style: The Style enum value defining visual presentation.
        min_width: Optional minimum character width for alignment. If None, no width
            constraint is applied. Defaults to None.
    """

    text: str
    style: Style
    min_width: int | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class Group:
    """A collection of segments grouped for layout and styling consistency.

    Groups combine multiple segments into a single unit with a collective minimum
    width constraint, enabling aligned columns and structured layouts.

    Attributes:
        segments: A tuple of Segment objects comprising this group.
        min_width: Optional minimum character width applied to the entire group.
            If None, no width constraint is applied. Defaults to None.
    """

    segments: tuple[Segment, ...]
    min_width: int | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class Template:
    """A structured template combining type metadata with content definition.

    Templates define the complete structure of a renderable component, including
    its type classification and ordered content composed of segments, groups, and
    references to other templates.

    Attributes:
        type: The Type enum value categorizing this template's purpose and content.
        content: An ordered tuple of Segment objects, Group objects, or Key references
            to other templates. The sequence defines rendering order.
    """

    type: Type
    content: tuple[Segment | Group | Key, ...]


"""Immutable registry of reusable component templates for structured report rendering.

A MappingProxyType providing read-only access to all component templates keyed by
their unique Key enum values. Templates in this registry support hierarchical
composition, allowing templates to reference other templates for modular content
structure. Each template combines segments, groups, and nested template references,
with support for format string substitution via placeholders (e.g., "{pending_count}",
"{total_cost}") and layout width constraints to enable dynamic, consistently
formatted report generation.
"""
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
        Key.TEXT_ITEM_POSITIVE: Template(
            type=Type.ITEM,
            content=(
                Key.ITEM_HEADER,
                Key.ITEM_FIELDS,
                Key.ITEM_POSITIVE_PROFIT,
            ),
        ),
        Key.TEXT_ITEM_NEGATIVE: Template(
            type=Type.ITEM,
            content=(
                Key.ITEM_HEADER,
                Key.ITEM_FIELDS,
                Key.ITEM_NEGATIVE_PROFIT,
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
