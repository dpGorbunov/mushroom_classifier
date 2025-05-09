import os
from fastapi import (
    APIRouter, Depends, File, Form, HTTPException, Request,
    UploadFile, status
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from jose import JWTError, jwt
from sqlmodel import Session
from database.database import get_session
from models.user import User
from services.crud.prediction import get_next_prediction_id, get_predictions_by_user
from services.crud.transaction import create_transaction, get_transactions_by_user
from services.crud.user import (
    get_user_by_username,
)
from services.security import Settings, create_access_token, ALGORITHM
from workers.publisher import publish_prediction_task

web_router = APIRouter(tags=["Web"])
templates = Jinja2Templates(directory="templates")

settings = Settings()


def format_datetime(value, format="%Y-%m-%d %H:%M:%S"):
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime(format)

templates.env.filters["datetime"] = format_datetime

# Аутентификация через куки
async def get_current_user_web(
        request: Request,
        session: Session = Depends(get_session)
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        token = token.split("Bearer ")[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = get_user_by_username(username, session)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@web_router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@web_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
        request: Request,
        user: User = Depends(get_current_user_web),
        session: Session = Depends(get_session)
):
    predictions = get_predictions_by_user(user.id, session)
    transactions = get_transactions_by_user(user.id, session)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "predictions": predictions[::-1],
        "transactions": transactions[::-1],
        "balance": user.balance,
        "selected_model": "Mashroom-model"
    })


@web_router.post("/balance")
async def deposit_balance_web(
        amount: int = Form(...),
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user_web)
):
    create_transaction(user.id, amount, session)
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@web_router.post("/predict")
async def predict_image(
        file: UploadFile = File(...),
        session: Session = Depends(get_session),
        user: User = Depends(get_current_user_web)
):

    # Сохранение временного файла
    temp_dir = "app/temp_images"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)

    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Создание задачи предсказания
    prediction_id = get_next_prediction_id(session)
    publish_prediction_task(user, file_path, "Mashroom-model", 10, prediction_id, session)

    return RedirectResponse(url="/dashboard", status_code=303)


@web_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@web_router.post("/login")
async def login_user(
        request: Request,
        session: Session = Depends(get_session)
):
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")

    user = get_user_by_username(username, session)
    if not user or not user.check_password(password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid username or password"
        })

    access_token = create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=3600
    )
    return response


@web_router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@web_router.post("/register")
async def register_user(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        session: Session = Depends(get_session)
):
    try:
        if get_user_by_username(username, session):
            raise HTTPException(status_code=400, detail="Грибник с таким именем уже существует, будь уникальнее!")

        user = User(username=username, role="user", balance=0.0)
        user.set_password(password)
        session.add(user)
        session.commit()
        return RedirectResponse(url="/login", status_code=303)
    except Exception as e:
        session.rollback()
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": str(e)
        })


@web_router.post("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response