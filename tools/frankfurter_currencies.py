from dataclasses import dataclass
from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, TypeAdapter

from cs2_storage_unit_tracker.api.client import ApiClient
from cs2_storage_unit_tracker.config.config import FrankfurterAPIConfig

FRANKFURTER_API_CONFIG = FrankfurterAPIConfig()


class FrankfurterCurrency(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    iso_code: str = Field(min_length=3, max_length=3)
    iso_numeric: str = Field(max_length=3)
    name: str = Field(max_length=50)
    symbol: str = Field(max_length=10)
    start_date: date
    end_date: date


@dataclass(frozen=True)
class FrankfurterApiClient(ApiClient):
    def get_currencies(self) -> list[FrankfurterCurrency]:
        data: list[dict[str, Any]] = self.get()
        data_adapter = TypeAdapter(list[FrankfurterCurrency])
        return data_adapter.validate_python(data)


def main() -> None:
    _currencies_url = HttpUrl(FRANKFURTER_API_CONFIG.domain + "/v2/currencies")
    FRANKFURTER_API_CLIENT = FrankfurterApiClient(
        url=_currencies_url, max_response_size=32 * 1024, chunk_size=8 * 1024
    )
    CURRENCIES: list[FrankfurterCurrency] = FRANKFURTER_API_CLIENT.get_currencies()

    print({CURRENCY.iso_code for CURRENCY in CURRENCIES})


if __name__ == "__main__":
    main()
