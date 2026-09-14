"""Application configuration and data models.

This module provides the public interface for all application configuration and
external data models. It re-exports Pydantic dataclasses that handle validation,
serialization, and type safety across multiple configuration domains: user
settings (API credentials, formatting preferences), runtime state (portfolio
tracking, sync status), and external API responses (Frankfurter exchange rates,
Steam pricing data).

All exported classes are Pydantic models with automatic field validation,
JSON/TOML serialization support, and runtime type checking.

Exported Models:
    User Settings:
        UserSettings: Complete user preferences combining API credentials and
            formatting options.
        FrankfurterApiSettings: Frankfurter API configuration (base URL, API key).
        SteamApiSettings: Steam API configuration (base URL, API key).
        FormattingSettings: Display formatting preferences (decimal places, units).

    Application State:
        Portfolio: Portfolio configuration and tracked inventory.
        Runtime: Runtime state and application-level settings.
        SyncStatus: Synchronization status for external data sources.

    External Data:
        FrankfurterRate: Exchange rate data from Frankfurter API.
        SteamPriceoverview: Price and currency data from Steam API.
"""

from cs2_storage_unit_tracker.config.models.frankfurter_rate_model import (
    FrankfurterRate,
)
from cs2_storage_unit_tracker.config.models.portfolio_model import Portfolio
from cs2_storage_unit_tracker.config.models.runtime_model import Runtime
from cs2_storage_unit_tracker.config.models.steam_priceoverview_model import (
    SteamPriceoverview,
)
from cs2_storage_unit_tracker.config.models.sync_status_model import SyncStatus
from cs2_storage_unit_tracker.config.models.user_settings_model import (
    FormattingSettings,
    FrankfurterApiSettings,
    SteamApiSettings,
    UserSettings,
)

__all__: list[str] = [
    "FormattingSettings",
    "FrankfurterApiSettings",
    "FrankfurterRate",
    "Portfolio",
    "Runtime",
    "SteamApiSettings",
    "SteamPriceoverview",
    "SyncStatus",
    "UserSettings",
]
