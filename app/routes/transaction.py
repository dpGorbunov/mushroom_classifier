from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from database.database import get_session
from schemas import TransactionCreate, TransactionResponse
from services.security import get_current_user
from services.crud.transaction import (
    create_transaction,
    get_transactions_by_user
)
from models.user import User


router = APIRouter(tags=['transactions'])


@router.post("/deposit", response_model=TransactionResponse)
def deposit(
        transaction: TransactionCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    if transaction.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    # Создаём транзакцию (баланс обновится внутри create_transaction)
    return create_transaction(
        user_id=current_user.id,
        amount=transaction.amount,
        session=session
    )


@router.get("/", response_model=list[TransactionResponse])
def get_user_transactions(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    return get_transactions_by_user(
        user_id=current_user.id,
        session=session,
        skip=skip,
        limit=limit
    )