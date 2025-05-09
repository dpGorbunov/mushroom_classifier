from typing import Optional
from .user import MushroomAppUser
from .ml_model import MushroomModel
from models.prediction import PredictionStatus
from .exceptions import InsufficientCreditsException, IdentificationFailedException

# --- ЗАДАЧА НА РАСПОЗНАВАНИЕ ---

class IdentificationTask:
    """
    Описывает одну задачу распознавания:
    содержит фото, выбранную модель и прочие данные.
    """

    def __init__(self, user: MushroomAppUser, task_id: str, photo, photo_path: str, model: MushroomModel, cost: float):
        self.__task_id = task_id
        self.__user = user
        self.__photo = photo
        self.__photo_path = photo_path
        self.__model = model
        self.__status = PredictionStatus.PENDING
        self.__result: Optional[str] = None
        self.__cost = cost

    @property
    def result(self) -> Optional[str]:
        """Геттер для получения результата."""
        return self.__result

    def run_identification(self) -> None:
        """
        Основной метод: пытается выполнить распознавание.
        При удаче списывает кредиты, сохраняет результат.
        При ошибке выбрасывает исключения.
        """
        try:
            self.__status = PredictionStatus.PROCESSING
            # Попытка распознать гриб
            result = self.__model.predict(self.__photo_path)
            # Если распознавание прошло успешно – списываем кредиты
            self.__user.get_credit_manager.spend_credits(self.__cost)
            self.__result = result
            self.__status = PredictionStatus.COMPLETED
            # Запишем в историю распознаваний
            self.__user.get_identification_history.add_entry(
                user=self.__user,  # Передаем объект пользователя
                photo_path=self.__photo_path,
                result=result,
                cost=self.__cost
            )
        except InsufficientCreditsException as e:
            # Недостаточно кредитов
            self.__status = PredictionStatus.FAILED
            raise e
        except Exception as e:
            # Любая другая ошибка, связанная с распознаванием
            self.__status = PredictionStatus.FAILED
            raise IdentificationFailedException(f"Сбой при распознавании: {str(e)}")

    @property
    def get_status(self) -> PredictionStatus:
        return self.__status