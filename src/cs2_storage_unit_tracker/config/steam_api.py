"""Configuration for the Steam Community Market API client.

This module provides default configuration, request rate limiting calculations,
and constants for interacting with the Steam Community Market API.
"""

from dataclasses import dataclass
from types import MappingProxyType


def calculate_request_interval(
    request_limit_per_min: int, request_margin_percent: int
) -> float:
    """Calculate the minimum interval between API requests.

    Computes the required delay between consecutive requests to stay within
    API rate limits, with an additional safety margin to avoid throttling.

    Args:
        request_limit_per_min: Maximum allowed requests per minute.
        request_margin_percent: Safety margin as a percentage above the
            calculated interval (e.g., 20 means 20% margin). Higher values
            create longer delays to be more conservative.

    Returns:
        Minimum interval in seconds between requests, rounded to 2 decimal
        places.

    Example:
        >>> calculate_request_interval(20, 20)
        3.6
    """
    return round(60 / request_limit_per_min * (request_margin_percent / 100 + 1), 2)


@dataclass(frozen=True, slots=True, kw_only=True)
class SteamApi:
    """Configuration settings for Steam Community Market API requests.

    This immutable dataclass defines all configuration parameters needed to
    interact with the Steam Community Market API, including endpoint details,
    supported currencies, and request rate limiting controls.

    Attributes:
        domain: Base URL of the Steam Community.
        path: API endpoint path for price overview queries.
        listings_path: API endpoint path for market listings, formatted with
            the app ID placeholder {app_id}.
        url_params_keys: Immutable mapping of URL parameter names used in API
            requests (currency, appid, market_hash_name).
        timeout: Request timeout in seconds. Default is 5 seconds.
        expected_fields: Immutable mapping of field names expected in API
            responses (success, lowest_price, volume, median_price).
        currencies: Immutable mapping of ISO 4217 currency codes to their
            corresponding Steam currency IDs. Sourced from
            https://partner.steamgames.com/doc/store/pricing/currencies.
        request_limit_per_min: Maximum allowed requests per minute according
            to Steam API terms. Default is 20 requests/minute.
        request_limit_per_day: Maximum allowed requests per day according to
            Steam API terms. Default is 666 requests/day.
        request_margin_percent: Safety margin percentage applied to rate limit
            calculations to avoid throttling. Default is 20%, creating a
            conservative buffer above the theoretical limit.
        request_interval: Calculated minimum interval in seconds between
            consecutive requests, derived from request_limit_per_min and
            request_margin_percent. Automatically computed at initialization.
    """

    domain: str = "https://steamcommunity.com"
    path: str = "/market/priceoverview/"
    listings_path: str = "/market/listings/{app_id}/"

    url_params_keys: MappingProxyType[str, str] = MappingProxyType(
        {
            "currency": "currency",
            "appid": "appid",
            "market_hash_name": "market_hash_name",
        }
    )

    timeout: int = 5

    expected_fields: MappingProxyType[str, str] = MappingProxyType(
        {
            "success": "success",
            "lowest_price": "lowest_price",
            "volume": "volume",
            "median_price": "median_price",
        }
    )

    # Currencies were taken from: https://partner.steamgames.com/doc/store/pricing/currencies
    currencies: MappingProxyType[str, int] = MappingProxyType(
        {
            "USD": 1,
            "GBP": 2,
            "EUR": 3,
            "CHF": 4,
            "PLN": 6,
            "BRL": 7,
            "JPY": 8,
            "NOK": 9,
            "IDR": 10,
            "MYR": 11,
            "PHP": 12,
            "SGD": 13,
            "THB": 14,
            "VND": 15,
            "KRW": 16,
            "UAH": 18,
            "MXN": 19,
            "CAD": 20,
            "AUD": 21,
            "NZD": 22,
            "CNY": 23,
            "INR": 24,
            "CLP": 25,
            "PEN": 26,
            "COP": 27,
            "ZAR": 28,
            "HKD": 29,
            "TWD": 30,
            "SAR": 31,
            "AED": 32,
            "ILS": 35,
            "KZT": 37,
            "KWD": 38,
            "QAR": 39,
            "CRC": 40,
            "UYU": 41,
        }
    )
    # Steam API limit is 20 per min
    request_limit_per_min: int = 20

    # Steam API limit is 1000 per day
    request_limit_per_day: int = 666

    # 20% is save tested value
    request_margin_percent: int = 20

    request_interval: float = calculate_request_interval(
        request_limit_per_min, request_margin_percent
    )


#: Global instance of Steam API configuration used across the application.
STEAM_API_CONFIG = SteamApi()
