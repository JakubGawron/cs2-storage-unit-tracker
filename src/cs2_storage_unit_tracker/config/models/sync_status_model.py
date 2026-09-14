"""Synchronization status tracking for user data items.

This module provides a data model for maintaining the state of synchronized
items in the application.
"""

from pydantic import BaseModel, ConfigDict, Field


class SyncStatus(BaseModel):
    """Tracks items that have been synchronized.

    A frozen configuration model that maintains a set of synchronized item
    identifiers. Field assignment validation is enabled to ensure data
    integrity when the state is updated.

    Attributes:
        synced_items: A set of item identifiers (strings) that have been
            successfully synchronized. Defaults to an empty set.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    synced_items: set[str] = Field(default_factory=set)
