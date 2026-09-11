from typing import Any, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)

from cs2_storage_unit_tracker.config import USER_DEFAULTS
from cs2_storage_unit_tracker.helpers.pydantic import get_validated_context


class SteamApiSettings(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    app_id: int = Field(default=USER_DEFAULTS.steam_api.app_id, gt=0)
    currency: str = Field(
        default=USER_DEFAULTS.steam_api.currency, min_length=3, max_length=3
    )

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str, info: ValidationInfo) -> str:
        context: dict[str, Any] = get_validated_context(info)

        value_upper: str = value.upper()

        if value_upper not in context["steam_api_allowed_currencies"]:
            raise ValueError(f"'{value_upper}' is not allowed currency")

        return value_upper


class FrankfurterApiSettings(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    to_currency: str | None = Field(
        default=USER_DEFAULTS.frankfurter_api.to_currency, min_length=3, max_length=3
    )

    @field_validator("to_currency")
    @classmethod
    def validate_currency(cls, value: str | None, info: ValidationInfo) -> str | None:
        if not value:
            return None

        context: dict[str, Any] = get_validated_context(info)

        value_upper: str = value.upper()

        if value_upper not in context["frankfurter_api_allowed_currencies"]:
            raise ValueError(f"'{value_upper}' is not allowed currency")

        return value_upper


class FormattingSettings(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    source_currency_use_locale: bool = Field(
        default=USER_DEFAULTS.formatting.source_currency_use_locale
    )
    exchanged_currency_use_locale: bool = Field(
        default=USER_DEFAULTS.formatting.exchanged_currency_use_locale
    )


class GeneralSettings(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    reset_after_hours: int = Field(
        default=USER_DEFAULTS.general.reset_after_hours, ge=6
    )


class UserSettings(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    steam_api: SteamApiSettings = SteamApiSettings()
    frankfurter_api: FrankfurterApiSettings = FrankfurterApiSettings()
    formatting: FormattingSettings = FormattingSettings()
    general: GeneralSettings = GeneralSettings()

    @model_validator(mode="after")
    def validate_currencies(self) -> Self:
        if (
            self.frankfurter_api.to_currency is not None
            and self.frankfurter_api.to_currency == self.steam_api.currency
        ):
            raise ValueError("Exchanged currency must differ from source currency")

        return self
