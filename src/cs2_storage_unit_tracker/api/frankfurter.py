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
    """Client for retrieving currency exchange rates from the Frankfurter API.

    This class provides a wrapper around the Frankfurter API for fetching current
    exchange rates between currencies. It handles URL construction, API communication,
    response validation, and rate extraction.

    Attributes:
        api_client: The HTTP client used to communicate with the Frankfurter API.
        frankfurter_api_settings: Configuration settings for Frankfurter API requests,
            including the default target currency.
    """

    api_client: ApiClient
    frankfurter_api_settings: FrankfurterApiSettings

    def get_rate(
        self,
        source_currency: str,
        target_currency: str | None = None,
    ) -> Decimal:
        """Retrieve the exchange rate between two currencies.

        Queries the Frankfurter API for the current exchange rate from a source
        currency to a target currency. If no target currency is specified, defaults
        to the configured currency in frankfurter_api_settings.

        Args:
            source_currency: The ISO 4217 currency code to convert from (e.g., "USD").
            target_currency: The ISO 4217 currency code to convert to (e.g., "EUR").
                If not provided, defaults to the value in frankfurter_api_settings.to_currency.

        Returns:
            The exchange rate as a Decimal value, representing the amount of target
            currency per unit of source currency.

        Raises:
            ValueError: If neither the target_currency parameter nor the configured
                default target currency is provided.
            ApiResponseError: If the API response is invalid or fails validation against
                the expected schema.
        """
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
    """Factory function to create a Frankfurter API client.

    Creates a new FrankfurterApiClient instance with the provided configuration
    and HTTP client.

    Args:
        frankfurter_api_settings: Configuration for Frankfurter API interactions,
            including the default target currency for exchange rate queries.
        api_client: The HTTP client to be used for API communication.

    Returns:
        A fully configured FrankfurterApiClient instance ready for making
        Frankfurter API requests.
    """
    return FrankfurterApiClient(
        api_client=api_client,
        frankfurter_api_settings=frankfurter_api_settings,
    )
