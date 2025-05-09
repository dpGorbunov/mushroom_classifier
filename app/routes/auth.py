from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from database.database import get_session
from models.user import User
from services.crud.user import create_user, get_user_by_username, get_all_users
from services.security import create_access_token
from schemas import UserCreate, UserResponse, Token

router = APIRouter(tags=['auth'])


@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, session: Session = Depends(get_session)):
    if get_user_by_username(user.username, session):
        raise HTTPException(status_code=400, detail="Грибник с таким именем уже существует, будь уникальнее!")

    db_user = User(
        username=user.username,
        role="user",
        balance=0.0
    )
    db_user.set_password(user.password)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.post("/signin", response_model=Token)
def signin(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not user.check_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}