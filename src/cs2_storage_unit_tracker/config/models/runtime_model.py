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
        if info.context is None:
            return data

        context: dict[str, Any] = get_validated_context(info)

        data.setdefault("last_source_currency", context["source_currency"])
        data.setdefault("reset_after_hours", context["reset_after_hours"])

        return data

    @field_serializer("total_cost", "total_price")
    def serialize_decimal(self, value: Decimal) -> str:
        return str(value)

    def was_run_recently(self) -> bool:
        return datetime.now(UTC) - self.last_run <= timedelta(
            hours=self.reset_after_hours
        )

    def reset_requests_if_new_day(self) -> None:
        if self.last_run.date() != datetime.now(UTC).date():
            self.total_requests = 0

    def exchange_money_values(self, exchange_rate: Decimal) -> None:
        self.total_cost = round_decimal(self.total_cost * exchange_rate)
        self.total_price = round_decimal(self.total_price * exchange_rate)

    def reset(self) -> None:
        self.last_run = datetime.now(UTC)
        self.total_units = 0
        self.total_cost = Decimal(0)
        self.total_price = Decimal(0)
        self.finished = False
