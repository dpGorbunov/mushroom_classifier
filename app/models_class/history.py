from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

# --- ИСТОРИЯ (АБСТРАКТНЫЙ КЛАСС) ---
class AbstractHistory(ABC):
    """
    Базовый абстрактный класс для ведения истории (транзакций, распознаваний и т.д.).
    """
    def __init__(self):
        self._history: list[dict] = []

    @abstractmethod
    def add_entry(self, *args, **kwargs):
        pass

    @property
    def get_history(self) -> list[dict]:
        return self._history

# --- ИСТОРИЯ ТРАНЗАКЦИЙ ---
class TransactionHistory(AbstractHistory):
    """
    Хранит информацию о пополнениях и списаниях кредитов.
    """
    def add_entry(self, user, amount: float, timestamp: Optional[datetime] = None):
        self._history.append({
            "user_id": user.get_username,  # Используем геттер get_username
            "amount": amount,
            "timestamp": timestamp or datetime.now()
        })

# --- ИСТОРИЯ РАСПОЗНАВАНИЙ ---
class IdentificationHistory(AbstractHistory):
    """
    Хранит информацию о выполненных распознаваниях (изображение, результат, стоимость).
    """
    def add_entry(self, user, photo_path: str, result: str, cost: float,
                  timestamp: Optional[datetime] = None):
        self._history.append({
            "user_id": user.get_username,  # Используем геттер get_username
            "photo_path": photo_path,
            "result": result,
            "cost": cost,
            "timestamp": timestamp or datetime.now()
        })