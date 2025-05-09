from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models.prediction import PredictionStatus

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    balance: float
    role: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class PredictionResponse(BaseModel):
    id: int
    photo_path: str
    result: Optional[str]
    status: PredictionStatus  # Используем Enum
    cost: float
    timestamp: datetime

class TransactionCreate(BaseModel):
    amount: float

class TransactionResponse(BaseModel):
    id: int
    amount: float
    timestamp: datetime