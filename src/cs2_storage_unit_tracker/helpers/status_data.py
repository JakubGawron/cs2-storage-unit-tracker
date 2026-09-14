"""Portfolio item and report financial calculation utilities.

This module provides dataclasses and functions for computing portfolio
metrics, including item-level profit calculations and aggregated report
summaries. Calculations include purchase/selling costs, profit margins,
return on investment (ROI), and optional currency exchange conversions.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from cs2_storage_unit_tracker.config.models.portfolio_model import Item
from cs2_storage_unit_tracker.formatting.currency import CurrencyFormatter
from cs2_storage_unit_tracker.helpers.decimal import round_decimal


@dataclass(slots=True)
class ProgressCounters:
    """Tracks synchronization and update progress metrics for a portfolio.

    Attributes:
        pending: Number of items awaiting price synchronization.
        outdated_total: Total count of outdated price entries across items.
        total_items_count: Total number of items in the portfolio.
        successful: Number of successfully synchronized items. Defaults to 0.
        failed: Number of items with synchronization failures. Defaults to 0.
    """

    pending: int
    outdated_total: int
    total_items_count: int
    successful: int = 0
    failed: int = 0

    def as_kwargs(self) -> dict[str, int]:
        """Convert progress counters to a keyword arguments dictionary.

        Returns a dictionary mapping counter names to their integer values,
        suitable for passing as template variables or function kwargs.

        Returns:
            A dictionary with keys: pending_count, outdated_total, failed_count,
            successful_count, and total_items_count.
        """
        return {
            "pending_count": self.pending,
            "outdated_total": self.outdated_total,
            "failed_count": self.failed,
            "successful_count": self.successful,
            "total_items_count": self.total_items_count,
        }


def calculate_item(
    pending_count: int,
    outdated_total: int,
    failed_count: int,
    successful_count: int,
    total_items_count: int,
    item_name: str,
    item_details: Item,
    item_selling_price: Decimal,
    exchange_rate: Decimal | None,
    currency_formatter: CurrencyFormatter,
) -> dict[str, Any]:
    """Calculate detailed financial metrics for a portfolio item.

    Computes purchase and selling costs, profit, margin, and ROI for an item
    based on quantity and unit prices. Results include both raw decimal values
    and formatted display strings. If an exchange rate is provided, generates
    additional converted currency values for the display output.

    Args:
        pending_count: Number of items awaiting price synchronization.
        outdated_total: Total count of outdated price entries.
        failed_count: Number of items with synchronization failures.
        successful_count: Number of items successfully synchronized.
        total_items_count: Total items in the portfolio.
        item_name: Display name of the item.
        item_details: Item configuration containing quantity and purchase price.
        item_selling_price: Current unit selling price (Decimal).
        exchange_rate: Currency exchange multiplier, or None for single-currency
            display. When provided, generates converted values.
        currency_formatter: Formatter for converting Decimal values to display
            strings with proper currency and precision.

    Returns:
        A dictionary with two keys:
            - "values": Raw Decimal values (units, cost, price, profit).
            - "display": Formatted display strings and progress counts, including
              item name, quantity, unit/total prices, profit, margin, ROI,
              and optionally exchanged values (empty strings if no exchange_rate).

    Note:
        All Decimal calculations use ROUND_HALF_UP strategy via round_decimal().
        Profit margin and ROI default to Decimal("0.00") if selling or purchase
        totals are zero, respectively.
    """

    item_quantity: int = item_details.quantity

    item_purchase_price: Decimal = round_decimal(item_details.purchase_price_per_item)
    item_purchase_total: Decimal = round_decimal(item_quantity * item_purchase_price)
    item_selling_total: Decimal = round_decimal(item_quantity * item_selling_price)

    item_profit_value: Decimal = round_decimal(item_selling_total - item_purchase_total)

    item_profit_margin: Decimal = (
        round_decimal((item_profit_value / item_selling_total) * Decimal(100))
        if item_selling_total != 0
        else Decimal("0.00")
    )

    item_roi: Decimal = (
        round_decimal((item_profit_value / item_purchase_total) * Decimal(100))
        if item_purchase_total != 0
        else Decimal("0.00")
    )

    values: dict[str, Any] = {
        "units": item_quantity,
        "cost": item_purchase_total,
        "price": item_selling_total,
        "profit": item_profit_value,
    }

    display: dict[str, Any] = {
        "pending_count": pending_count,
        "outdated_total": outdated_total,
        "failed_count": failed_count,
        "successful_count": successful_count,
        "total_items_count": total_items_count,
        "item_name": item_name,
        "item_quantity": item_quantity,
        "item_purchase_price": currency_formatter.format_decimal(
            number=item_purchase_price
        ),
        "item_purchase_total": currency_formatter.format_decimal(
            number=item_purchase_total
        ),
        "item_selling_price": currency_formatter.format_decimal(
            number=item_selling_price
        ),
        "item_selling_total": currency_formatter.format_decimal(
            number=item_selling_total
        ),
        "item_profit_value": currency_formatter.format_decimal(
            number=item_profit_value
        ),
        "item_profit_margin": item_profit_margin,
        "item_roi": item_roi,
        "exchanged_item_purchase_price": "",
        "exchanged_item_purchase_total": "",
        "exchanged_item_selling_price": "",
        "exchanged_item_selling_total": "",
        "exchanged_item_profit_value": "",
    }

    if exchange_rate is not None:
        display["exchanged_item_purchase_price"] = currency_formatter.format_decimal(
            number=item_purchase_price * exchange_rate, for_exchange=True
        )
        display["exchanged_item_purchase_total"] = currency_formatter.format_decimal(
            number=item_purchase_total * exchange_rate, for_exchange=True
        )
        display["exchanged_item_selling_price"] = currency_formatter.format_decimal(
            number=item_selling_price * exchange_rate, for_exchange=True
        )
        display["exchanged_item_selling_total"] = currency_formatter.format_decimal(
            number=item_selling_total * exchange_rate, for_exchange=True
        )
        display["exchanged_item_profit_value"] = currency_formatter.format_decimal(
            number=item_profit_value * exchange_rate, for_exchange=True
        )

    data: dict[str, Any] = {
        "values": values,
        "display": display,
    }

    return data


def calculate_report(
    pending_count: int,
    outdated_total: int,
    failed_count: int,
    successful_count: int,
    total_items_count: int,
    total_units: int,
    total_cost: Decimal,
    total_price: Decimal,
    exchange_rate: Decimal | None,
    currency_formatter: CurrencyFormatter,
) -> dict[str, Any]:
    """Calculate aggregated financial summary metrics for the entire portfolio.

    Computes total profit, margin, and ROI across all items in the portfolio.
    Results include both raw Decimal values and formatted display strings. If an
    exchange rate is provided, generates additional converted currency values for
    the display output.

    Args:
        pending_count: Number of items awaiting price synchronization.
        outdated_total: Total count of outdated price entries.
        failed_count: Number of items with synchronization failures.
        successful_count: Number of items successfully synchronized.
        total_items_count: Total items in the portfolio.
        total_units: Aggregate quantity of all items.
        total_cost: Sum of all purchase totals (Decimal).
        total_price: Sum of all selling totals (Decimal).
        exchange_rate: Currency exchange multiplier, or None for single-currency
            display. When provided, generates converted values.
        currency_formatter: Formatter for converting Decimal values to display
            strings with proper currency and precision.

    Returns:
        A dictionary with two keys:
            - "values": Raw Decimal values (price, profit).
            - "display": Formatted display strings and progress counts, including
              totals for units, costs, prices, profit, margin, ROI, and
              optionally exchanged values (empty strings if no exchange_rate).

    Note:
        All Decimal calculations use ROUND_HALF_UP strategy via round_decimal().
        Total margin and ROI default to Decimal("0.00") if total price or cost
        are zero, respectively.
    """

    total_profit: Decimal = round_decimal(total_price - total_cost)

    total_margin: Decimal = (
        round_decimal((total_profit / total_price) * Decimal(100))
        if total_price != 0
        else Decimal("0.00")
    )

    total_roi: Decimal = (
        round_decimal((total_profit / total_cost) * Decimal(100))
        if total_cost != 0
        else Decimal("0.00")
    )

    values: dict[str, Any] = {"price": total_price, "profit": total_profit}

    display: dict[str, Any] = {
        "pending_count": pending_count,
        "outdated_total": outdated_total,
        "failed_count": failed_count,
        "successful_count": successful_count,
        "total_items_count": total_items_count,
        "total_units": total_units,
        "total_cost": currency_formatter.format_decimal(number=total_cost),
        "total_price": currency_formatter.format_decimal(number=total_price),
        "total_profit": currency_formatter.format_decimal(number=total_profit),
        "total_margin": total_margin,
        "total_roi": total_roi,
        "exchanged_total_cost": "",
        "exchanged_total_price": "",
        "exchanged_total_profit": "",
    }

    if exchange_rate is not None:
        display["exchanged_total_cost"] = currency_formatter.format_decimal(
            number=total_cost * exchange_rate, for_exchange=True
        )
        display["exchanged_total_price"] = currency_formatter.format_decimal(
            number=total_price * exchange_rate, for_exchange=True
        )
        display["exchanged_total_profit"] = currency_formatter.format_decimal(
            number=total_profit * exchange_rate, for_exchange=True
        )

    data: dict[str, Any] = {
        "values": values,
        "display": display,
    }

    return data
