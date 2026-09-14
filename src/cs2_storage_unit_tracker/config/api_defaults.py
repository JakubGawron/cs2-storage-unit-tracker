"""API client configuration and default settings.

This module provides default configuration values for API requests, including
headers, timeouts, and response size limits.
"""

from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True, slots=True, kw_only=True)
class ApiDefaults:
    """Default configuration for API requests.

    This immutable dataclass defines standard settings for all API client
    requests, including HTTP headers, timeouts, and size constraints.

    Attributes:
        headers: Default HTTP headers sent with every request. Includes Accept
            and User-Agent headers. Immutable mapping.
        timeout: Request timeout in seconds. Default is 10 seconds.
        max_response_size: Maximum allowed response body size in bytes. Larger
            responses will be rejected. Default is 1024 bytes.
        chunk_size: Size of chunks in bytes when streaming response bodies.
            Default is 256 bytes.
    """

    headers: MappingProxyType[str, str] = MappingProxyType(
        {
            "Accept": "application/json",
            "User-Agent": "curl/8.21.0",
        }
    )
    timeout: int = 10
    max_response_size: int = 1024
    chunk_size: int = 256


#: Global instance of default API configuration used across all API clients.
API_DEFAULTS = ApiDefaults()
