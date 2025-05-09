from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session
from database.database import get_session
from models.user import User
from models.prediction import PredictionStatus, Prediction
from schemas import PredictionResponse
from services.security import get_current_user
from services.crud.prediction import (
    get_predictions_by_user, get_next_prediction_id
)
from services.security import check_admin_role
from typing import Optional
from workers.publisher import publish_prediction_task



router = APIRouter(tags=['predictions'])


@router.post("/")
async def predict(photo: UploadFile = File(...),
        cost: float = 10,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    # Проверка баланса
    if current_user.balance < cost:
        raise HTTPException(400, f"Недостаточно средств. Текущий баланс: {current_user.balance}, стоимость предсказания: {cost}.")

    # Сохранение файла
    file_path = f"uploads/{photo.filename}"
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(photo.file.read())
    except Exception as e:
        raise HTTPException(500, f"File upload failed: {str(e)}")

    prediction_id = get_next_prediction_id(session)
    publish_prediction_task(current_user, file_path, "MushroomModel", cost, prediction_id, session)

    return {"message": "Задача отправлена в очередь",
            "prediction_id": prediction_id}



@router.patch("/{prediction_id}", response_model=PredictionResponse)
def update_prediction(
        prediction_id: int,
        new_status: PredictionStatus,
        result: Optional[str] = None,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    check_admin_role(current_user)

    prediction = session.get(Prediction, prediction_id)
    if not prediction:
        raise HTTPException(404, "Prediction not found")

    prediction.status = new_status
    prediction.result = result

    try:
        session.commit()
        session.refresh(prediction)
        return prediction
    except Exception as e:
        session.rollback()
        raise HTTPException(500, detail=str(e))


@router.get("/history/{user_id}")
def prediction_history(user_id: int, session: Session = Depends(get_session)):
    predictions = get_predictions_by_user(user_id, session)
    if not predictions:
        raise HTTPException(404, detail="История предсказаний пуста")
    return predictions