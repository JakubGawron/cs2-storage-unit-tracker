import json
from dataclasses import dataclass, field
from typing import Any, Literal

import requests
from pydantic import HttpUrl

from cs2_storage_unit_tracker.config import API_DEFAULTS
from cs2_storage_unit_tracker.helpers.errors import (
    ApiRequestError,
    ApiResponseError,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class ApiClient:
    """HTTP client for making API requests with validation and size limits.

    This class provides a wrapper around the requests library with built-in safeguards
    for response validation, size limits, and JSON parsing. It supports request scoping
    to different URLs while maintaining session state across requests.

    Attributes:
        url: The base URL for API requests. If None, must be provided per request.
        max_response_size: Maximum allowed response size in bytes. Responses exceeding
            this limit will raise ApiResponseError. Defaults to API_DEFAULTS.max_response_size.
        chunk_size: Size of chunks when streaming response content in bytes.
            Defaults to API_DEFAULTS.chunk_size.
        session: The requests.Session object used for all HTTP communication.
            Not included in repr. Defaults to a new Session instance.
    """

    url: HttpUrl | None = None
    max_response_size: int = API_DEFAULTS.max_response_size
    chunk_size: int = API_DEFAULTS.chunk_size
    session: requests.Session = field(default_factory=requests.Session, repr=False)

    def __post_init__(self) -> None:
        """Initialize the session with default headers."""
        self.session.headers.update(API_DEFAULTS.headers)

    def close(self) -> None:
        """Close the underlying requests session and cleanup resources."""
        self.session.close()

    def request(self, method: Literal["GET"], **kwargs: Any) -> Any:
        """Make an HTTP request with response validation and size enforcement.

        Performs an HTTP request to the configured URL with automatic timeout defaults,
        response validation, and size limiting. Validates that the response is JSON,
        enforces maximum response size limits, and properly streams large responses
        to prevent memory exhaustion.

        Args:
            method: The HTTP method to use. Currently only "GET" is supported.
            **kwargs: Additional arguments passed to requests.Session.request(), including:
                timeout: Request timeout in seconds. Defaults to API_DEFAULTS.timeout
                    if not provided.
                params: Query string parameters.
                headers: Custom headers (merged with session headers).

        Returns:
            Parsed JSON response data as a Python object (dict, list, etc.).

        Raises:
            ApiResponseError: If the response Content-Type is not JSON, the response
                exceeds max_response_size, or the response body contains invalid JSON.
            ApiRequestError: If the HTTP request fails (network error, timeout, status
                code error, or other request exceptions).
        """
        kwargs.setdefault("timeout", API_DEFAULTS.timeout)
        try:
            with self.session.request(
                method=method, stream=True, url=str(self.url), **kwargs
            ) as response:
                response.raise_for_status()

                content_type: str = response.headers.get("Content-Type", "")
                if "application/json" not in content_type:
                    raise ApiResponseError(
                        "Expected a JSON response with Content-Type: 'application/json'"
                    )

                response_size_error: str = (
                    f"Response too large (bigger than {self.max_response_size} B)"
                )
                content_length: str = response.headers.get("Content-Length", "")

                if (
                    content_length.isdigit()
                    and int(content_length) > self.max_response_size
                ):
                    raise ApiResponseError(response_size_error)

                chunks = bytearray()
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    chunks.extend(chunk)

                    if len(chunks) > self.max_response_size:
                        raise ApiResponseError(response_size_error)

                data: Any = json.loads(chunks)
                return data

        except json.JSONDecodeError as exc:
            raise ApiResponseError("API returned invalid JSON") from exc

        except requests.exceptions.RequestException as exc:
            raise ApiRequestError("API request failed") from exc

    def get(self, **kwargs: Any) -> Any:
        """Make a GET request to the configured URL.

        Convenience method that calls request() with method="GET".

        Args:
            **kwargs: Additional arguments passed to request(), including timeout,
                params, and headers.

        Returns:
            Parsed JSON response data as a Python object.

        Raises:
            ApiResponseError: If the response is invalid or exceeds size limits.
            ApiRequestError: If the HTTP request fails.
        """
        return self.request("GET", **kwargs)

    def scoped(self, url: HttpUrl, **kwargs: Any) -> ApiClient:
        """Create a new client scoped to a different URL with shared session state.

        Returns a new ApiClient instance targeting a different URL while reusing the
        same underlying requests.Session. This allows multiple API endpoints to share
        connection pooling and session data (cookies, etc.) without duplicating resources.

        Args:
            url: The new base URL for the scoped client.
            **kwargs: Optional client configuration overrides:
                max_response_size: Override maximum response size. Defaults to current
                    client's max_response_size.
                chunk_size: Override chunk size for streaming. Defaults to current
                    client's chunk_size.

        Returns:
            A new ApiClient instance scoped to the provided URL with inherited or
            overridden configuration.
        """
        return ApiClient(
            url=url,
            session=self.session,
            max_response_size=kwargs.get("max_response_size", self.max_response_size),
            chunk_size=kwargs.get("chunk_size", self.chunk_size),
        )
