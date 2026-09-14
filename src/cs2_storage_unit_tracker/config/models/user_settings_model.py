"""User configuration settings for APIs, formatting, and application behavior.

This module provides Pydantic models for managing user-configurable settings
across Steam API, Frankfurter API, currency formatting, and general application
behavior. All settings are frozen (immutable) and validated against allowed
values from context.
"""

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
    """Configuration for Steam API requests.

    Attributes:
        app_id: Steam application ID for market queries. Defaults to
            Counter-Strike 2 (730). Must be greater than 0.
        currency: ISO 4217 currency code for Steam market prices. Must be
            exactly 3 characters and present in the Steam API allowed
            currencies list.
    """

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
        """Validate and normalize the Steam currency code.

        Converts the currency code to uppercase and checks that it is
        supported by the Steam API.

        Args:
            value: The currency code to validate.
            info: Pydantic validation context containing allowed currency set.

        Returns:
            The normalized (uppercase) currency code.

        Raises:
            ValueError: If the uppercase currency code is not in the Steam API
                allowed currencies list.
        """
        context: dict[str, Any] = get_validated_context(info)

        value_upper: str = value.upper()

        if value_upper not in context["steam_api_allowed_currencies"]:
            raise ValueError(f"'{value_upper}' is not allowed currency")

        return value_upper


class FrankfurterApiSettings(BaseModel):
    """Configuration for Frankfurter API currency conversion.

    Attributes:
        to_currency: ISO 4217 currency code to convert amounts into. If None,
            no currency conversion is performed. Must be exactly 3 characters
            when provided and present in the Frankfurter API allowed currencies
            list.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    to_currency: str | None = Field(
        default=USER_DEFAULTS.frankfurter_api.to_currency, max_length=3
    )

    @field_validator("to_currency")
    @classmethod
    def validate_currency(cls, value: str | None, info: ValidationInfo) -> str | None:
        """Validate and normalize the Frankfurter currency code.

        Converts a non-None currency code to uppercase and checks that it is
        supported by the Frankfurter API. Passes through None values without
        validation.

        Args:
            value: The currency code to validate, or None to disable conversion.
            info: Pydantic validation context containing allowed currency set.

        Returns:
            The normalized (uppercase) currency code, or None if input is None.

        Raises:
            ValueError: If the uppercase currency code is not in the Frankfurter
                API allowed currencies list.
        """
        if not value:
            return None

        context: dict[str, Any] = get_validated_context(info)

        value_upper: str = value.upper()

        if value_upper not in context["frankfurter_api_allowed_currencies"]:
            raise ValueError(f"'{value_upper}' is not allowed currency")

        return value_upper


class FormattingSettings(BaseModel):
    """Configuration for currency formatting and localization.

    Controls whether locale-aware formatting rules are applied to source and
    exchanged currency amounts during display.

    Attributes:
        source_currency_use_locale: If True, apply locale-specific formatting
            rules to the source currency amount. If False, use fallback format
            pattern.
        exchanged_currency_use_locale: If True, apply locale-specific formatting
            rules to the exchanged currency amount. If False, use fallback format
            pattern.
    """

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
    """General application configuration.

    Attributes:
        reset_after_hours: Number of hours after which request limits reset.
            Must be at least 6 hours.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    reset_after_hours: int = Field(
        default=USER_DEFAULTS.general.reset_after_hours, ge=6
    )


class UserSettings(BaseModel):
    """Aggregated user configuration across all application domains.

    Combines Steam API, Frankfurter API, formatting, and general settings into
    a single frozen configuration object. Enforces cross-field validation to
    ensure that source and exchanged currencies are distinct.

    Attributes:
        steam_api: Configuration for Steam API requests.
        frankfurter_api: Configuration for Frankfurter API currency conversion.
        formatting: Configuration for currency formatting and localization.
        general: General application settings.
    """

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
        """Validate that source and exchanged currencies are different.

        Ensures that the source currency (from Steam API) differs from the
        target conversion currency (from Frankfurter API) when currency
        conversion is enabled.

        Returns:
            The validated UserSettings instance.

        Raises:
            ValueError: If the Frankfurter target currency matches the Steam
                source currency.
        """
        if (
            self.frankfurter_api.to_currency is not None
            and self.frankfurter_api.to_currency == self.steam_api.currency
        ):
            raise ValueError("Exchanged currency must differ from source currency")

        return self
