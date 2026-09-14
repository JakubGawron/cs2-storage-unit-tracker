"""API client interfaces and factories for external service integration.

This module provides abstracted API clients for currency conversion and Steam
platform integration, supporting the CS2 storage unit tracker application.

Exports:
    ApiClient: Base class defining the standard API client interface.
    create_frankfurter_api_client: Factory function for Frankfurter currency API.
    create_steam_api_client: Factory function for Steam Web API.
"""

from cs2_storage_unit_tracker.api.client import ApiClient
from cs2_storage_unit_tracker.api.frankfurter import create_frankfurter_api_client
from cs2_storage_unit_tracker.api.steam import create_steam_api_client

__all__: list[str] = [
    "ApiClient",
    "create_frankfurter_api_client",
    "create_steam_api_client",
]
