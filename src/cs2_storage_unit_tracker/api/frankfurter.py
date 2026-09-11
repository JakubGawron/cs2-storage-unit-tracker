from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from pydantic import HttpUrl, ValidationError

from cs2_storage_unit_tracker.api.client import ApiClient
from cs2_storage_unit_tracker.config import (
    FRANKFURTER_API_CONFIG,
)
from cs2_storage_unit_tracker.config.models import (
    FrankfurterApiSettings,
    FrankfurterRate,
)
from cs2_storage_unit_tracker.helpers.errors import ApiResponseError


@dataclass(frozen=True, slots=True, kw_only=True)
class FrankfurterApiClient:
    api_client: ApiClient
    frankfurter_api_settings: FrankfurterApiSettings

    def get_rate(
        self,
        source_currency: str,
        target_currency: str | None = None,
    ) -> Decimal:
        target_currency = target_currency or self.frankfurter_api_settings.to_currency

        if target_currency is None:
            raise ValueError("Target currency must be provided")

        url = HttpUrl(
            FRANKFURTER_API_CONFIG.domain
            + FRANKFURTER_API_CONFIG.path
            + source_currency
            + "/"
            + target_currency
        )

        data: Any = self.api_client.scoped(url=url).get(
            timeout=FRANKFURTER_API_CONFIG.timeout
        )
        try:
            return FrankfurterRate.model_validate(data).rate
        except ValidationError as exc:
            raise ApiResponseError(
                "Frankfurter API returned an invalid response"
            ) from exc


def create_frankfurter_api_client(
    frankfurter_api_settings: FrankfurterApiSettings,
    api_client: ApiClient,
) -> FrankfurterApiClient:
    return FrankfurterApiClient(
        api_client=api_client,
        frankfurter_api_settings=frankfurter_api_settings,
    )
