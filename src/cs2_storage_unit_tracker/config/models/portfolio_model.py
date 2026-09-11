from collections.abc import Mapping
from decimal import Decimal
from types import MappingProxyType

from pydantic import (
    BaseModel,
    ConfigDict,
    HttpUrl,
    RootModel,
    field_serializer,
    field_validator,
)


class Item(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    link: HttpUrl
    quantity: int
    purchase_price_per_item: Decimal


class Portfolio(RootModel[Mapping[str, Item]]):
    model_config = ConfigDict(
        frozen=True,
    )

    @field_validator("root")
    @classmethod
    def make_immutable(cls, value: Mapping[str, Item]) -> Mapping[str, Item]:
        if not value:
            raise ValueError("portfolio must contain at least one item")
        return MappingProxyType(dict(value))

    @field_serializer("root")
    def serialize_root(self, value: Mapping[str, Item]) -> dict[str, Item]:
        return dict(value)
