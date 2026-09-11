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
    currency: str
    locale: str | None
    format: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class CurrencyFormatter:
    source_currency_formatting_options: FormattingOptions
    exchanged_currency_formatting_options: FormattingOptions

    def format_decimal(self, number: Decimal, for_exchange: bool = False) -> str:
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
    return CurrencyFormatter(
        source_currency_formatting_options=get_formatting_options(
            source_currency, formatting_settings.source_currency_use_locale
        ),
        exchanged_currency_formatting_options=get_formatting_options(
            exchanged_currency, formatting_settings.exchanged_currency_use_locale
        ),
    )
