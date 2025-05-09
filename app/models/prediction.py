from __future__ import annotations
from datetime import datetime, UTC
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

class PredictionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Prediction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    photo_path: str
    result: Optional[str] = None
    status: PredictionStatus = Field(default=PredictionStatus.PENDING)
    cost: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


    def update_status(self, new_status: str):
        self.status = new_status
        self.timestamp = datetime.now(UTC)

    def update_result(self, new_result: str):
        self.result = new_result
        self.timestamp = datetime.now(UTC)

