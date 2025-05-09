from .exceptions import InsufficientCreditsException


# --- МЕНЕДЖЕР КРЕДИТОВ ---

class CreditManager:
    """
    Отвечает за учёт «кредитов» пользователя.
    Можно считать, что это условная «валюта» приложения,
    которая расходуется на запросы к системе распознавания.
    """

    def __init__(self, initial_credits: float = 0.0):
        self.__credits = initial_credits

    @property
    def get_credits(self) -> float:
        return self.__credits

    def add_credits(self, amount: float) -> None:
        self.__credits += amount

    def spend_credits(self, amount: float) -> None:
        """Списывает указанную сумму кредитов; бросает исключение, если их недостаточно."""
        if self.__credits < amount:
            raise InsufficientCreditsException("Недостаточно кредитов для распознавания.")
        self.__credits -= amount