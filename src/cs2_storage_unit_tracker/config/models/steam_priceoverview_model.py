from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from cs2_storage_unit_tracker.config import STEAM_API_CONFIG


class SteamPriceoverview(BaseModel):
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
        if not self.success:
            raise ValueError("Steam API returned success=false")

        if self.lowest_price is None and self.median_price is None:
            raise ValueError(
                "Steam API returned success=True but required data is missing"
            )
        return self
