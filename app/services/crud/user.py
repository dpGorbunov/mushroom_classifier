from sqlmodel import Session, select
from models.user import User
from typing import Optional


def get_all_users(session: Session) -> list[User]:
    return session.exec(select(User)).all()


def get_user_by_username(username: str, session: Session) -> Optional[User]:
    return session.exec(select(User).where(User.username == username)).first()

def get_user_by_id(user_id: int, session: Session) -> Optional[User]:
    return session.get(User, user_id)

def create_user(username: str, role: str, balance: float, session: Session) -> User:
    existing_user = session.exec(select(User).where(User.username == username)).first()
    if existing_user:
        raise ValueError(f"Пользователь '{username}' уже существует")
    user = User(username=username, role=role, balance=balance)
    user.set_password("default_password")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user_balance(user_id: int, amount: float, session: Session) -> Optional[User]:
    user = session.get(User, user_id)
    if user:
        user.balance += amount
        session.commit()
        return user
    return None
