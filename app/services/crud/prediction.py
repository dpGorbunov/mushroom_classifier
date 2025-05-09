from sqlmodel import Session, select, func
from models.prediction import Prediction
from typing import Optional
from models.prediction import PredictionStatus


def create_prediction(user_id: int, photo_path: str, cost: float, session: Session) -> Prediction:
    new_prediction = Prediction(user_id=user_id, photo_path=photo_path, cost=cost)
    session.add(new_prediction)
    session.commit()
    session.refresh(new_prediction)
    return new_prediction


def get_predictions_by_user(user_id: int, session: Session) -> list[Prediction]:
    return session.exec(select(Prediction).where(Prediction.user_id == user_id)).all()


def update_prediction_status(prediction_id: int, new_status: PredictionStatus, session: Session) -> Optional[Prediction]:
    prediction = session.get(Prediction, prediction_id)
    if prediction:
        prediction.update_status(new_status)
        session.commit()
        return prediction
    return None


def get_all_predictions(session: Session) -> list[Prediction]:
    return session.exec(select(Prediction)).all()


def update_prediction_result(prediction_id: int, new_result: str, session: Session) -> Optional[Prediction]:
    prediction = session.get(Prediction, prediction_id)
    if prediction:
        prediction.update_result(new_result)
        session.commit()
        return prediction
    return None

def get_next_prediction_id(session: Session) -> int:
    max_id = session.exec(select(func.max(Prediction.id))).one_or_none()
    return (max_id or 0) + 1