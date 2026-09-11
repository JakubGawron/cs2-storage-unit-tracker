from dataclasses import dataclass
from types import MappingProxyType


def calculate_request_interval(
    request_limit_per_min: int, request_margin_percent: int
) -> float:
    return round(60 / request_limit_per_min * (request_margin_percent / 100 + 1), 2)


@dataclass(frozen=True, slots=True, kw_only=True)
class SteamApi:
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


STEAM_API_CONFIG = SteamApi()
