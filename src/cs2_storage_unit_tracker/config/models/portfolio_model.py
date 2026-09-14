"""Portfolio item models and immutable portfolio container.

This module defines the structure for individual portfolio items and the
immutable Portfolio container that holds a mapping of named items. Portfolio
instances are validated to be non-empty and are frozen to prevent modification
after creation.
"""

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
    """A single portfolio item with pricing and quantity information.

    Represents an asset held in a portfolio, including its market link,
    quantity owned, and per-unit acquisition cost. Instances are frozen
    and immutable after creation.

    Attributes:
        link: A valid HTTP(S) URL pointing to the item's market listing or
            product page.
        quantity: The number of units of this item held in the portfolio.
            Must be a non-negative integer.
        purchase_price_per_item: The acquisition cost per unit as a Decimal
            value. Preserves decimal precision for accurate financial calculations.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    link: HttpUrl
    quantity: int
    purchase_price_per_item: Decimal


class Portfolio(RootModel[Mapping[str, Item]]):
    """An immutable collection of portfolio items keyed by identifier.

    A RootModel that wraps an immutable mapping of string identifiers to Item
    instances. Each portfolio must contain at least one item. The mapping is
    converted to a MappingProxyType internally to enforce immutability, and
    converted back to a dict during JSON serialization.

    The root attribute provides direct access to the underlying immutable
    mapping of items, where each key is a unique item identifier and each
    value is an Item instance.

    Raises:
        ValueError: If the portfolio is empty (contains no items).
    """

    model_config = ConfigDict(
        frozen=True,
    )

    @field_validator("root")
    @classmethod
    def make_immutable(cls, value: Mapping[str, Item]) -> Mapping[str, Item]:
        """Validate portfolio non-emptiness and convert to immutable mapping.

        Ensures that the portfolio contains at least one item and converts the
        input mapping to a MappingProxyType, which prevents any modifications
        to the underlying data structure. This provides runtime immutability
        guarantees beyond the model's frozen configuration.

        Args:
            value: A mapping of item identifiers to Item instances.

        Returns:
            A MappingProxyType wrapping the portfolio items, which is read-only.

        Raises:
            ValueError: If the mapping is empty or contains no items.
        """
        if not value:
            raise ValueError("portfolio must contain at least one item")
        return MappingProxyType(dict(value))

    @field_serializer("root")
    def serialize_root(self, value: Mapping[str, Item]) -> dict[str, Item]:
        """Convert immutable mapping to dict for JSON serialization.

        Transforms the internal MappingProxyType back into a standard dict
        to enable standard JSON serialization. This ensures the Portfolio can
        be serialized and deserialized without requiring special handling for
        read-only proxy objects.

        Args:
            value: The immutable MappingProxyType mapping of items.

        Returns:
            A dict[str, Item] representation of the portfolio items suitable
            for JSON output.
        """
        return dict(value)
