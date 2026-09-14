"""Frankfurter API client for retrieving and validating currency data.

This module provides a Pydantic-based client for fetching current currency
information from the Frankfurter API. It includes validation of currency
records with strict field constraints and a demonstration entry point for
retrieving supported currencies.
"""

from dataclasses import dataclass
from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, TypeAdapter

from cs2_storage_unit_tracker.api.client import ApiClient
from cs2_storage_unit_tracker.config import FRANKFURTER_API_CONFIG


class FrankfurterCurrency(BaseModel):
    """Validated representation of a currency supported by the Frankfurter API.

    This Pydantic model enforces strict validation of currency records,
    including format constraints on ISO codes and date range validation.
    The model is frozen and forbids extra fields to ensure data integrity.

    Attributes:
        iso_code: Three-character ISO 4217 currency code (e.g., "USD", "EUR").
        iso_numeric: ISO 4217 numeric code (max 3 characters, e.g., "840").
        name: Display name of the currency (max 50 characters, e.g., "US Dollar").
        symbol: Currency symbol for display (max 10 characters, e.g., "$").
        start_date: Date when the currency became available or active.
        end_date: Date when the currency ceased to be used or supported.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    iso_code: str = Field(min_length=3, max_length=3)
    iso_numeric: str = Field(max_length=3)
    name: str = Field(max_length=50)
    symbol: str = Field(max_length=10)
    start_date: date
    end_date: date


@dataclass(frozen=True)
class FrankfurterApiClient(ApiClient):
    """API client for the Frankfurter currency and exchange rate service.

    This client provides methods to retrieve and validate data from the
    Frankfurter API, including currency listings and historical exchange rates.
    Inherits core HTTP functionality from ApiClient with configurable response
    size and chunk size limits.
    """

    def get_currencies(self) -> list[FrankfurterCurrency]:
        """Fetch and validate a list of supported currencies from the API.

        Retrieves raw currency data from the API endpoint and validates each
        record against the FrankfurterCurrency schema using Pydantic's
        TypeAdapter. Ensures data integrity by enforcing field constraints
        and type requirements.

        Returns:
            A list of FrankfurterCurrency objects representing all currencies
            supported by the Frankfurter API.

        Raises:
            ValidationError: If any currency record fails Pydantic validation
                due to missing, malformed, or constraint-violating fields.
            ApiRequestError: If the HTTP request to the API fails (inherited
                from ApiClient).
            ApiResponseError: If the API returns an error response (inherited
                from ApiClient).
        """
        data: list[dict[str, Any]] = self.get()
        data_adapter = TypeAdapter(list[FrankfurterCurrency])
        return data_adapter.validate_python(data)


def main() -> None:
    """Fetch and display a set of currency ISO codes from the Frankfurter API.

    Initializes a FrankfurterApiClient instance, retrieves the list of
    supported currencies, and prints their ISO codes as a set.

    Raises:
        ValidationError: If currency data fails schema validation.
        ApiRequestError: If the HTTP request to the Frankfurter API fails.
        ApiResponseError: If the API returns an error response.
    """
    _currencies_url = HttpUrl(FRANKFURTER_API_CONFIG.domain + "/v2/currencies")
    FRANKFURTER_API_CLIENT = FrankfurterApiClient(
        url=_currencies_url, max_response_size=32 * 1024, chunk_size=8 * 1024
    )
    CURRENCIES: list[FrankfurterCurrency] = FRANKFURTER_API_CLIENT.get_currencies()

    print({CURRENCY.iso_code for CURRENCY in CURRENCIES})


if __name__ == "__main__":
    main()
