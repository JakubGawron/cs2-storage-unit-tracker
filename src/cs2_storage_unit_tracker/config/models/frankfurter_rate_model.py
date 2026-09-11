from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from cs2_storage_unit_tracker.config import FRANKFURTER_API_CONFIG


class FrankfurterRate(BaseModel):
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
        if value not in FRANKFURTER_API_CONFIG.currencies:
            raise ValueError(f"Unsupported currency: {value}")
        return value
