"""Error handling and custom exception types for the application.

This module defines application-specific exceptions for configuration and
API-related errors, along with handlers for presenting these errors to users.
All exceptions provide structured error information and integrate with the
rich-based messaging system for consistent error reporting.
"""

from dataclasses import dataclass
from pathlib import Path

from cs2_storage_unit_tracker.cli.content.rich import messages_key
from cs2_storage_unit_tracker.cli.renderers.rich import RichMessageRenderer


@dataclass(frozen=True, slots=True)
class ConfigError(Exception):
    """Exception raised when configuration loading or validation fails.

    This exception encapsulates configuration errors with details about the
    failure message and the path to the problematic configuration file.
    The dataclass is frozen to ensure immutability after creation.

    Attributes:
        message: Human-readable description of the configuration error.
        path: Filesystem path to the configuration file that caused the error.
    """

    message: str
    path: Path

    def __post_init__(self) -> None:
        """Initialize the parent Exception with the error message.

        Called automatically after dataclass initialization to populate the
        base Exception class with the error message, enabling standard
        exception formatting and traceback display.
        """
        super().__init__(self.message)


def handle_config_error(exc: ConfigError) -> None:
    """Render a configuration error message to the user.

    Displays a formatted error message using the rich renderer with the
    error details (message and path) substituted into the CONFIG_ERROR
    message template. This provides a consistent, visually formatted
    representation of configuration errors.

    Args:
        exc: The ConfigError instance containing the error details.

    Raises:
        ValueError: If the CONFIG_ERROR message template is not found in
            the message registry or if variable substitution fails.
    """
    RichMessageRenderer().print(
        key=messages_key.CONFIG_ERROR,
        variables={
            "message": exc.message,
            "path": exc.path,
        },
    )


@dataclass(frozen=True, slots=True)
class ApiError(Exception):
    """Base exception for API-related errors.

    This exception serves as the base class for all API client errors,
    providing a consistent structure for API error handling. The dataclass
    is frozen to ensure immutability after creation.

    Attributes:
        message: Human-readable description of the API error.
    """

    message: str

    def __post_init__(self) -> None:
        """Initialize the parent Exception with the error message.

        Called automatically after dataclass initialization to populate the
        base Exception class with the error message, enabling standard
        exception formatting and traceback display.
        """
        super().__init__(self.message)


class ApiRequestError(ApiError):
    """Exception raised when an API request fails.

    Indicates that the API request could not be sent or was rejected by the
    server due to network issues, authentication failures, or request format
    problems. Inherits message field and behavior from ApiError.
    """


class ApiResponseError(ApiError):
    """Exception raised when an API response is invalid or unexpected.

    Indicates that an API response was received but could not be processed,
    such as when the server returns an error status code or an unexpected
    response format. Inherits message field and behavior from ApiError.
    """


class SteamApiParseError(ApiError):
    """Exception raised when Steam API response parsing fails.

    Indicates that a response from the Steam API was received but could not
    be parsed into the expected data structure, such as when required fields
    are missing or data types are incorrect. Inherits message field and
    behavior from ApiError.
    """
