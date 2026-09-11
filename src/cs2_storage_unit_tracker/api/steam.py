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
    api_client: ApiClient
    steam_api_settings: SteamApiSettings

    def get_price(self, item_url: HttpUrl) -> Decimal:

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
    url = HttpUrl(STEAM_API_CONFIG.domain + STEAM_API_CONFIG.path)
    return SteamApiClient(
        api_client=api_client.scoped(url=url), steam_api_settings=steam_api_settings
    )
