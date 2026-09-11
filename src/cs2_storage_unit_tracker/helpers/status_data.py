from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from cs2_storage_unit_tracker.config.models.portfolio_model import Item
from cs2_storage_unit_tracker.formatting.currency import CurrencyFormatter
from cs2_storage_unit_tracker.helpers.decimal import round_decimal


@dataclass(slots=True)
class ProgressCounters:
    pending: int
    outdated_total: int
    total_items_count: int
    successful: int = 0
    failed: int = 0

    def as_kwargs(self) -> dict[str, int]:
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
