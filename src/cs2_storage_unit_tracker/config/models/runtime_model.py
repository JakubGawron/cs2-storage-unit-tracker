"""Runtime state tracking for application execution.

This module defines the Runtime model, which tracks execution metadata including
the timestamp of the last successful run, source currency, cost/price totals,
API request counts, and completion status. It provides methods to check if a
recent run has occurred, reset request counts on new days, apply exchange rates,
and reset the entire runtime state.
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_serializer,
    model_validator,
)

from cs2_storage_unit_tracker.config import USER_DEFAULTS
from cs2_storage_unit_tracker.helpers.decimal import round_decimal
from cs2_storage_unit_tracker.helpers.pydantic import get_validated_context


class Runtime(BaseModel):
    """Application runtime state and execution metadata.

    Tracks the state of a single execution cycle, including the timestamp of
    the last run, the source currency used, cumulative totals (units, cost,
    price), API request counts, and completion status. Supports context-based
    defaults during validation and provides methods for checking recency,
    resetting, and applying currency exchange rates.

    Attributes:
        last_run: Timestamp of the last successful run in UTC. Defaults to the
            current UTC time.
        last_source_currency: ISO 4217 currency code used in the last run.
            Exactly 3 characters. Defaults to the source currency from
            validation context, or empty string if context is unavailable.
        reset_after_hours: Number of hours after which the runtime state is
            considered stale. Defaults to USER_DEFAULTS.general.reset_after_hours.
            Must be >= 6.
        total_units: Cumulative count of tracked units across all items.
            Defaults to 0. Must be non-negative.
        total_cost: Cumulative acquisition cost across all items as a Decimal.
            Defaults to 0.00. Must be non-negative. Serialized to string.
        total_price: Cumulative current market price across all items as a
            Decimal. Defaults to 0.00. Must be non-negative. Serialized to string.
        total_requests: Cumulative count of API requests made during execution.
            Defaults to 0. Must be non-negative.
        finished: Boolean flag indicating whether execution has completed.
            Defaults to False.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    last_run: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_source_currency: str = Field(default="", min_length=3, max_length=3)
    reset_after_hours: int = Field(default=USER_DEFAULTS.general.reset_after_hours)
    total_units: int = Field(default=0, ge=0)
    total_cost: Decimal = Field(Decimal(0), ge=Decimal(0))
    total_price: Decimal = Field(Decimal(0), ge=Decimal(0))
    total_requests: int = Field(default=0, ge=0)
    finished: bool = False

    @model_validator(mode="before")
    @classmethod
    def fill_context(cls, data: dict[str, Any], info: ValidationInfo) -> Any:
        """Fill missing runtime fields from validation context.

        Populates last_source_currency and reset_after_hours from the
        validation context if they are not already present in the input data.
        This allows these fields to be injected during model construction
        without requiring explicit arguments.

        Args:
            data: The input data dictionary being validated.
            info: Validation metadata, including the context dictionary.

        Returns:
            The updated data dictionary with context fields set as defaults
            if they were not already present.
        """
        if info.context is None:
            return data

        context: dict[str, Any] = get_validated_context(info)

        data.setdefault("last_source_currency", context["source_currency"])
        data.setdefault("reset_after_hours", context["reset_after_hours"])

        return data

    @field_serializer("total_cost", "total_price")
    def serialize_decimal(self, value: Decimal) -> str:
        """Serialize Decimal fields to strings.

        Converts total_cost and total_price from Decimal objects to their
        string representations for JSON serialization while preserving
        precision.

        Args:
            value: A Decimal value to serialize.

        Returns:
            The string representation of the Decimal value.
        """
        return str(value)

    def was_run_recently(self) -> bool:
        """Check if the last run occurred within the reset window.

        Determines whether the time elapsed since last_run is less than or
        equal to reset_after_hours. If True, the runtime state is considered
        current and valid for reuse.

        Returns:
            True if the last run occurred within reset_after_hours hours of
            the current UTC time; False otherwise.
        """
        return datetime.now(UTC) - self.last_run <= timedelta(
            hours=self.reset_after_hours
        )

    def reset_requests_if_new_day(self) -> None:
        """Reset request count if a new calendar day has started.

        Compares the date of last_run with the current UTC date. If they
        differ, total_requests is reset to 0, allowing per-day request limits
        to be enforced across multiple runs.

        Returns:
            None. Modifies total_requests in place.
        """
        if self.last_run.date() != datetime.now(UTC).date():
            self.total_requests = 0

    def exchange_money_values(self, exchange_rate: Decimal) -> None:
        """Apply an exchange rate to cost and price totals.

        Multiplies total_cost and total_price by the given exchange_rate and
        rounds the results to maintain decimal precision. Used when converting
        currency values to a different base currency.

        Args:
            exchange_rate: A Decimal multiplier representing the exchange rate.
                Must be non-negative.

        Returns:
            None. Modifies total_cost and total_price in place.
        """
        self.total_cost = round_decimal(self.total_cost * exchange_rate)
        self.total_price = round_decimal(self.total_price * exchange_rate)

    def reset(self) -> None:
        """Reset runtime state to defaults.

        Clears all cumulative totals and marks execution as incomplete. Sets
        last_run to the current UTC time, resets total_units, total_cost,
        total_price, and finished to their initial values. Does not affect
        last_source_currency, reset_after_hours, or total_requests.

        Returns:
            None. Modifies instance fields in place.
        """
        self.last_run = datetime.now(UTC)
        self.total_units = 0
        self.total_cost = Decimal(0)
        self.total_price = Decimal(0)
        self.finished = False
