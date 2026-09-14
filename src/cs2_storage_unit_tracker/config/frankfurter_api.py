"""Configuration for the Frankfurter currency exchange API client.

This module provides default configuration and constants for interacting with
the Frankfurter API (https://api.frankfurter.dev), a free currency exchange
rate API.
"""

from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True, slots=True, kw_only=True)
class FrankfurterApi:
    """Configuration settings for Frankfurter API requests.

    This immutable dataclass defines all configuration parameters needed to
    interact with the Frankfurter currency exchange API, including endpoint
    details, request settings, and supported currency codes.

    Attributes:
        domain: Base URL of the Frankfurter API.
        path: API endpoint path for currency rate queries.
        timeout: Request timeout in seconds. Default is 5 seconds.
        expected_fields: Immutable mapping of field names expected in API
            responses. Keys and values represent the required fields for
            exchange rate data (date, base currency, quote currency, rate).
        currencies: Frozenset of all supported ISO 4217 currency codes.
            Sourced from https://api.frankfurter.dev/v2/currencies.
            Contains 170+ currency codes including major and minor currencies.
    """

    domain: str = "https://api.frankfurter.dev"
    path: str = "/v2/rate/"

    timeout: int = 5

    expected_fields: MappingProxyType[str, str] = MappingProxyType(
        {"date": "date", "base": "base", "quote": "quote", "rate": "rate"}
    )

    # Currencies were taken from: https://api.frankfurter.dev/v2/currencies
    currencies: frozenset[str] = frozenset(
        {
            "GTQ",
            "SBD",
            "TTD",
            "PYG",
            "IRR",
            "SGD",
            "ZAR",
            "DKK",
            "OMR",
            "CRC",
            "LRD",
            "WST",
            "ZWG",
            "CNY",
            "LBP",
            "MYR",
            "SLE",
            "TJS",
            "AWG",
            "BWP",
            "BAM",
            "YER",
            "LAK",
            "PHP",
            "BND",
            "TRY",
            "CUP",
            "XPF",
            "ARS",
            "NOK",
            "KMF",
            "ILS",
            "MUR",
            "SAR",
            "IMP",
            "DJF",
            "UAH",
            "STN",
            "XPT",
            "FJD",
            "BDT",
            "BZD",
            "BTN",
            "MRU",
            "SCR",
            "CAD",
            "TOP",
            "XAF",
            "DOP",
            "RUB",
            "RSD",
            "TWD",
            "GEL",
            "SYP",
            "GNF",
            "AOA",
            "XDR",
            "PAB",
            "KYD",
            "GGP",
            "INR",
            "SOS",
            "NAD",
            "AZN",
            "GYD",
            "MKD",
            "COP",
            "CHF",
            "KGS",
            "MAD",
            "MXN",
            "HNL",
            "LKR",
            "BOB",
            "NPR",
            "RWF",
            "ERN",
            "DZD",
            "MMK",
            "GMD",
            "XPD",
            "BHD",
            "BMD",
            "MZN",
            "SHP",
            "HUF",
            "XCD",
            "IDR",
            "JEP",
            "MGA",
            "RON",
            "KZT",
            "JMD",
            "MVR",
            "SEK",
            "CNH",
            "CDF",
            "ISK",
            "JOD",
            "UZS",
            "VUV",
            "CVE",
            "EUR",
            "PLN",
            "MDL",
            "MOP",
            "MWK",
            "BSD",
            "KES",
            "GIP",
            "ALL",
            "GHS",
            "AUD",
            "JPY",
            "GBP",
            "BIF",
            "IQD",
            "NIO",
            "XAG",
            "TZS",
            "UYU",
            "BRL",
            "SRD",
            "SVC",
            "SDG",
            "CZK",
            "XCG",
            "NZD",
            "AED",
            "VES",
            "ZMW",
            "NGN",
            "MNT",
            "TND",
            "HKD",
            "BYN",
            "HTG",
            "PKR",
            "AFN",
            "FKP",
            "KPW",
            "USD",
            "KHR",
            "LSL",
            "TMT",
            "ETB",
            "KWD",
            "SZL",
            "EGP",
            "VND",
            "PEN",
            "LYD",
            "CLP",
            "THB",
            "PGK",
            "MRO",
            "KRW",
            "XOF",
            "AMD",
            "ANG",
            "QAR",
            "SSP",
            "XAU",
            "UGX",
            "BBD",
        }
    )


#: Global instance of Frankfurter API configuration used across the application.
FRANKFURTER_API_CONFIG = FrankfurterApi()
