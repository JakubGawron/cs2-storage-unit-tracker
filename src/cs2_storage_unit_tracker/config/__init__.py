"""Application configuration defaults and path management.

This module provides the public interface for application configuration defaults
and filesystem path management. It re-exports static configuration constants
containing immutable default values for API endpoints, credentials, and user
settings, along with the Paths utility for centralized configuration directory
management.

Configuration Constants:
    API_DEFAULTS: Default configuration values shared across all API clients
        (base URLs, timeout settings, retry policies).
    FRANKFURTER_API_CONFIG: Frankfurter API-specific defaults (endpoint URL,
        API key defaults, exchange rate parameters).
    STEAM_API_CONFIG: Steam API-specific defaults (market endpoint URL,
        API key defaults, price query parameters).
    USER_DEFAULTS: Default user preferences (formatting settings, locale,
        display options, synchronization intervals).

Path Management:
    Paths: Utility class for generating and managing paths to configuration,
        cache, and report directories. Ensures consistent path resolution
        across the application.
"""

from cs2_storage_unit_tracker.config.api_defaults import API_DEFAULTS
from cs2_storage_unit_tracker.config.frankfurter_api import FRANKFURTER_API_CONFIG
from cs2_storage_unit_tracker.config.paths import Paths
from cs2_storage_unit_tracker.config.steam_api import STEAM_API_CONFIG
from cs2_storage_unit_tracker.config.user_defaults import USER_DEFAULTS

__all__: list[str] = [
    "API_DEFAULTS",
    "FRANKFURTER_API_CONFIG",
    "STEAM_API_CONFIG",
    "USER_DEFAULTS",
    "Paths",
]
