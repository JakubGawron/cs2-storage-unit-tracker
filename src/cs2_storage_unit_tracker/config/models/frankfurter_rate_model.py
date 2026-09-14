"""Exchange rate data models for the Frankfurter API.

This module defines the Pydantic model for parsing and validating exchange rate
responses from the Frankfurter currency conversion API. Data is mapped from API
field names and validated against supported currency codes.
"""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from cs2_storage_unit_tracker.config import FRANKFURTER_API_CONFIG


class FrankfurterRate(BaseModel):
    """An exchange rate between two currencies from the Frankfurter API.

    Represents a single exchange rate response from the Frankfurter API,
    including the date of the rate, the base and quote currencies, and the
    exchange rate value. Field names are mapped from the API response using
    validation aliases, and currency codes are validated against the set of
    supported ISO 4217 currencies.

    Instances are frozen and immutable after creation, and do not permit extra
    fields beyond those explicitly defined.

    Attributes:
        update_date: The date on which the exchange rate is effective.
        base: A 3-character ISO 4217 currency code for the base currency.
            Must be a supported currency in the Frankfurter API.
        quote: A 3-character ISO 4217 currency code for the quote (target)
            currency. Must be a supported currency in the Frankfurter API.
        rate: The exchange rate as a Decimal, representing how many units of
            the quote currency equal one unit of the base currency. Always
            greater than zero.

    Raises:
        ValueError: If base or quote is not a supported currency code.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    update_date: date = Field(
        validation_alias=FRANKFURTER_API_CONFIG.expected_fields["date"]
    )
    base: str = Field(
        min_length=3,
        max_length=3,
        validation_alias=FRANKFURTER_API_CONFIG.expected_fields["base"],
    )
    quote: str = Field(
        min_length=3,
        max_length=3,
        validation_alias=FRANKFURTER_API_CONFIG.expected_fields["quote"],
    )
    rate: Decimal = Field(
        gt=Decimal(0), validation_alias=FRANKFURTER_API_CONFIG.expected_fields["rate"]
    )

    @field_validator("base", "quote")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        """Validate that a currency code is supported by the Frankfurter API.

        Checks the provided currency code against the set of supported ISO 4217
        currencies available from the Frankfurter API. This ensures that both
        the base and quote currencies are valid before the model is instantiated.

        Args:
            value: A 3-character currency code to validate.

        Returns:
            The input currency code if it is valid and supported.

        Raises:
            ValueError: If the currency code is not in the Frankfurter API's
                supported currencies set.
        """
        if value not in FRANKFURTER_API_CONFIG.currencies:
            raise ValueError(f"Unsupported currency: {value}")
        return value
