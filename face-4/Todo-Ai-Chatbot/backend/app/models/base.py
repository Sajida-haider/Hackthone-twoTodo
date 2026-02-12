"""Base model with automatic timestamp handling."""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class TimestampModel(SQLModel):
    """Base model with automatic timestamp fields."""

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp in UTC"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        nullable=False,
        description="Last modification timestamp in UTC"
    )
