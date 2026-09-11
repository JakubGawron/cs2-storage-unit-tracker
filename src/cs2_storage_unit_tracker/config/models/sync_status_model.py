from pydantic import BaseModel, ConfigDict, Field


class SyncStatus(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    synced_items: set[str] = Field(default_factory=set)
