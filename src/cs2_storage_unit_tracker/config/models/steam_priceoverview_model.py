"""Steam API market price data models.

This module defines the structure for Steam Community Market API price overview
responses, including validation of required fields and API success status.
"""

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from cs2_storage_unit_tracker.config import STEAM_API_CONFIG


class SteamPriceoverview(BaseModel):
    """Steam Community Market price overview response.

    Represents the structured data returned by the Steam API priceoverview
    endpoint. Field names are mapped from the API response format via
    validation aliases. All price fields are strings as returned by the API.

    Attributes:
        success: Indicates whether the API request was successful. Validation
            ensures this is always True; False values raise ValueError.
        lowest_price: The lowest asking price for the item as a formatted
            string (e.g., "$1.23"). Optional; may be None if no listings exist.
            Maximum length is 30 characters.
        volume: The number of listings for the item as a formatted string.
            Optional; may be None if the API does not return this data.
            Maximum length is 30 characters.
        median_price: The median price for the item as a formatted string.
            Optional; may be None if insufficient data exists. Maximum length
            is 30 characters.

    Raises:
        ValueError: If success is False or if both lowest_price and
            median_price are None despite success=True.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    success: bool = Field(validation_alias=STEAM_API_CONFIG.expected_fields["success"])
    lowest_price: str | None = Field(
        default=None,
        max_length=30,
        validation_alias=STEAM_API_CONFIG.expected_fields["lowest_price"],
    )
    volume: str | None = Field(
        default=None,
        max_length=30,
        validation_alias=STEAM_API_CONFIG.expected_fields["volume"],
    )
    median_price: str | None = Field(
        default=None,
        max_length=30,
        validation_alias=STEAM_API_CONFIG.expected_fields["median_price"],
    )

    @model_validator(mode="after")
    def validate_response(self) -> Self:
        """Validate that the Steam API response contains required data.

        Ensures that the API returned a successful response and that at least
        one of the two primary price fields (lowest_price or median_price) is
        present. This prevents accepting incomplete or failed API responses.

        Returns:
            The validated SteamPriceoverview instance.

        Raises:
            ValueError: If success is False, indicating the API request failed.
            ValueError: If success is True but both lowest_price and median_price
                are None, indicating the API returned an incomplete response.
        """
        if not self.success:
            raise ValueError("Steam API returned success=false")

        if self.lowest_price is None and self.median_price is None:
            raise ValueError(
                "Steam API returned success=True but required data is missing"
            )
        return self
