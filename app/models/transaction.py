from __future__ import annotations
from sqlmodel import SQLModel, Field
from datetime import UTC, datetime
from typing import Optional

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    amount: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # user: Optional["User"] = Relationship(back_populates="transactions")