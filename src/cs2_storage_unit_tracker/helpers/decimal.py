"""Utilities for rounding decimal values.

This module provides functions for standardizing decimal precision,
particularly for financial calculations and currency formatting.
"""

from decimal import ROUND_HALF_UP, Decimal


def round_decimal(value: Decimal) -> Decimal:
    """Round a Decimal value to two decimal places using half-up rounding.

    Rounds the input to exactly two decimal places using the ROUND_HALF_UP
    strategy, where values exactly halfway between two possible results are
    rounded away from zero. This is the standard rounding method for
    financial calculations and currency amounts.

    Args:
        value: The Decimal value to round.

    Returns:
        A Decimal rounded to two decimal places.

    Raises:
        AttributeError: If value does not have a quantize method (e.g., if
            value is not a Decimal).
        decimal.InvalidOperation: If value is a special Decimal value such
            as Infinity or NaN, or if quantization fails due to precision
            constraints.

    Examples:
        >>> round_decimal(Decimal("10.125"))
        Decimal('10.13')
        >>> round_decimal(Decimal("10.124"))
        Decimal('10.12')
    """
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
