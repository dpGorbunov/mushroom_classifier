from fastapi import APIRouter, Depends
from sqlmodel import Session
from database.database import get_session
from schemas import UserResponse
from services.security import get_current_user
from models.user import User

router = APIRouter(tags=['users'])

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return current_user