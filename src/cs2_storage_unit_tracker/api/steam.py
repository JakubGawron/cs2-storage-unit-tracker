from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from urllib.parse import unquote

from price_parser import Price
from pydantic import HttpUrl, ValidationError

from cs2_storage_unit_tracker.api.client import ApiClient
from cs2_storage_unit_tracker.config import STEAM_API_CONFIG
from cs2_storage_unit_tracker.config.models import (
    SteamApiSettings,
    SteamPriceoverview,
)
from cs2_storage_unit_tracker.helpers.errors import ApiResponseError, SteamApiParseError


@dataclass(frozen=True, slots=True, kw_only=True)
class SteamApiClient:
    """Client for retrieving item prices from the Steam Community Market API.

    This class provides a wrapper around the Steam API for fetching current market
    prices for items. It handles URL parsing, API communication, response validation,
    and price extraction.

    Attributes:
        api_client: The HTTP client used to communicate with the Steam API.
        steam_api_settings: Configuration settings for Steam API requests, including
            app ID and currency preferences.
    """

    api_client: ApiClient
    steam_api_settings: SteamApiSettings

    def get_price(self, item_url: HttpUrl) -> Decimal:
        """Retrieve the current market price for a Steam item.

        Extracts the item name from the provided Steam Community Market URL, queries
        the Steam API for price data, and returns the lowest available price or the
        median price as a fallback.

        Args:
            item_url: The Steam Community Market URL for the item in the format
                `{domain}/listings/{app_id}/{item_name}`.

        Returns:
            The current market price as a Decimal value, representing either the
            lowest ask price or median price if lowest is unavailable.

        Raises:
            SteamApiParseError: If the price data cannot be parsed from the API response
                (e.g., price is None after parsing).
            ApiResponseError: If the API response is invalid or fails validation against
                the expected schema.
        """
        item_name: str = unquote(
            str(item_url).removeprefix(
                STEAM_API_CONFIG.domain
                + STEAM_API_CONFIG.listings_path.format(
                    app_id=self.steam_api_settings.app_id
                )
            )
        )
        data: Any = self.api_client.get(
            timeout=STEAM_API_CONFIG.timeout,
            params={
                STEAM_API_CONFIG.url_params_keys[
                    "currency"
                ]: STEAM_API_CONFIG.currencies[self.steam_api_settings.currency],
                STEAM_API_CONFIG.url_params_keys[
                    "appid"
                ]: self.steam_api_settings.app_id,
                STEAM_API_CONFIG.url_params_keys["market_hash_name"]: item_name,
            },
        )
        try:
            validated_data: SteamPriceoverview = SteamPriceoverview.model_validate(data)
            raw_price: str | None = (
                validated_data.lowest_price or validated_data.median_price
            )
            price: Decimal | None = Price.fromstring(
                price=raw_price, currency_hint=self.steam_api_settings.currency
            ).amount

            if price is None:
                raise SteamApiParseError("Parsed price is None")

            return price

        except ValidationError as exc:
            raise ApiResponseError(
                f"Steam API returned an invalid response: {exc}"
            ) from exc


def create_steam_api_client(
    steam_api_settings: SteamApiSettings, api_client: ApiClient
) -> SteamApiClient:
    """Factory function to create and configure a Steam API client.

    Creates a new SteamApiClient instance with the provided settings and an API
    client scoped to the Steam API domain. This ensures all requests are directed
    to the correct Steam API endpoint.

    Args:
        steam_api_settings: Configuration for Steam API interactions, including
            app ID and currency settings.
        api_client: The base HTTP client to be scoped to the Steam API domain.

    Returns:
        A fully configured SteamApiClient instance ready for making Steam API requests.
    """
    url = HttpUrl(STEAM_API_CONFIG.domain + STEAM_API_CONFIG.path)
    return SteamApiClient(
        api_client=api_client.scoped(url=url), steam_api_settings=steam_api_settings
    )
