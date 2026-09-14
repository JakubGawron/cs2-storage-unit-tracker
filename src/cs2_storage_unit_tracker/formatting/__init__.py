"""Currency formatting and localization for numeric values.

This module provides utilities for formatting decimal numbers as localized
currency strings, supporting both source and converted currency display with
automatic locale-aware number representation.

The primary entry point is the create_currency_formatter factory function,
which constructs a CurrencyFormatter instance configured for a specific pair
of currencies and formatting preferences.
"""

from cs2_storage_unit_tracker.formatting.currency import create_currency_formatter

__all__: list[str] = ["create_currency_formatter"]
