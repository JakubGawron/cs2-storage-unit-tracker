"""Currency formatting and localization for numeric values.

This module provides utilities for formatting decimal numbers as localized
currency strings, supporting both source and converted currency display with
automatic locale-aware number representation.
"""

import decimal
from dataclasses import dataclass
from decimal import Decimal

from babel import Locale, UnknownLocaleError
from babel.numbers import format_currency

from cs2_storage_unit_tracker.config import USER_DEFAULTS
from cs2_storage_unit_tracker.config.models import (
    FormattingSettings,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class FormattingOptions:
    """Configuration for formatting a decimal number as currency.

    Attributes:
        currency: ISO 4217 currency code for the formatted output.
        locale: POSIX locale identifier (e.g., "en_US") used to determine
            locale-specific number formatting rules. If None, generic currency
            formatting without locale-specific rules is applied.
        format: CLDR number format pattern (e.g., "#,##0.00 ¤¤") used for
            custom number representation. If None, Babel's default format for
            the locale is used.
    """

    currency: str
    locale: str | None
    format: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class CurrencyFormatter:
    """Formats decimal numbers as localized currency strings.

    This formatter applies consistent formatting rules to both source and
    converted currency amounts, with automatic locale-aware number representation
    and ROUND_HALF_UP rounding behavior.

    Attributes:
        source_currency_formatting_options: Formatting configuration for the
            original/source currency amount.
        exchanged_currency_formatting_options: Formatting configuration for
            the converted/exchanged currency amount.
    """

    source_currency_formatting_options: FormattingOptions
    exchanged_currency_formatting_options: FormattingOptions

    def format_decimal(self, number: Decimal, for_exchange: bool = False) -> str:
        """Format a decimal number as a localized currency string.

        Applies the appropriate formatting options based on whether the number
        represents the source or exchanged currency amount. Uses ROUND_HALF_UP
        rounding behavior for consistent decimal rounding.

        Args:
            number: The decimal value to format.
            for_exchange: If False (default), format using source currency
                options. If True, format using exchanged currency options.

        Returns:
            Formatted currency string with locale-specific number representation
            and currency symbol or code.

        Example:
            >>> formatter = CurrencyFormatter(
            ...     source_currency_formatting_options=FormattingOptions(
            ...         currency="USD", locale="en_US", format=None
            ...     ),
            ...     exchanged_currency_formatting_options=FormattingOptions(
            ...         currency="EUR", locale="de_DE", format=None
            ...     ),
            ... )
            >>> formatter.format_decimal(Decimal("49.99"))
            '$49.99'
            >>> formatter.format_decimal(Decimal("45.50"), for_exchange=True)
            '45,50 €'
        """
        options: FormattingOptions = (
            self.source_currency_formatting_options
            if not for_exchange
            else self.exchanged_currency_formatting_options
        )
        with decimal.localcontext(decimal.Context(rounding=decimal.ROUND_HALF_UP)):
            return format_currency(
                number=number,
                currency=options.currency,
                locale=options.locale,
                format=options.format,
            )


def get_formatting_options(currency: str | None, use_locale: bool) -> FormattingOptions:
    """Create formatting options for a currency with optional locale support.

    Constructs a FormattingOptions object that specifies how a currency amount
    should be formatted. If locale support is enabled and a valid locale exists
    for the currency, locale-specific formatting rules are applied. Otherwise,
    a fallback CLDR format pattern is used.

    Args:
        currency: ISO 4217 currency code. If None, an empty string is used.
        use_locale: If True, attempt to apply locale-specific formatting rules
            for the given currency. If False, use the fallback format pattern.

    Returns:
        FormattingOptions configured for the specified currency with either
        locale-aware or fallback formatting settings.

    Raises:
        ValueError: If a locale is found for the currency but it is invalid
            or unrecognized by Babel. The exception message includes the
            invalid locale, currency code, and the underlying Babel error.

    Example:
        >>> get_formatting_options("USD", use_locale=True)
        FormattingOptions(currency='USD', locale='en_US', format=None)
        >>> get_formatting_options("EUR", use_locale=False)
        FormattingOptions(currency='EUR', locale=None, format='#,##0.00 ¤¤')
    """
    if currency is None:
        currency = ""

    options = FormattingOptions(
        currency=currency,
        locale=None,
        format=USER_DEFAULTS.formatting.fallback_format,
    )

    if not use_locale:
        return options

    locale: str | None = USER_DEFAULTS.formatting.currency_locales.get(currency)

    if locale is None:
        return options

    try:
        Locale.parse(locale)
    except UnknownLocaleError as exc:
        raise ValueError(
            f"Invalid locale '{locale}' for currency '{currency}': {exc}"
        ) from exc

    return FormattingOptions(
        currency=currency,
        locale=locale,
        format=None,
    )


def create_currency_formatter(
    source_currency: str,
    exchanged_currency: str | None,
    formatting_settings: FormattingSettings,
) -> CurrencyFormatter:
    """Create a formatter for source and exchanged currency amounts.

    Factory function that constructs a CurrencyFormatter by deriving formatting
    options for both the source currency and optionally the exchanged/converted
    currency based on the provided settings.

    Args:
        source_currency: ISO 4217 currency code of the original/source amount.
        exchanged_currency: ISO 4217 currency code to format the converted
            amount into. If None, the exchanged currency formatting options
            will use an empty currency code with fallback formatting.
        formatting_settings: Configuration specifying whether locale-aware
            formatting should be applied to source and exchanged amounts.

    Returns:
        A CurrencyFormatter instance configured with formatting options derived
        from the provided currencies and settings.

    Raises:
        ValueError: If any locale associated with the source or exchanged
            currency is invalid or unrecognized by Babel. See
            get_formatting_options for details.

    Example:
        >>> settings = FormattingSettings(
        ...     source_currency_use_locale=True,
        ...     exchanged_currency_use_locale=True,
        ... )
        >>> formatter = create_currency_formatter("USD", "EUR", settings)
        >>> formatter.format_decimal(Decimal("100.00"))
        '$100.00'
    """
    return CurrencyFormatter(
        source_currency_formatting_options=get_formatting_options(
            source_currency, formatting_settings.source_currency_use_locale
        ),
        exchanged_currency_formatting_options=get_formatting_options(
            exchanged_currency, formatting_settings.exchanged_currency_use_locale
        ),
    )
