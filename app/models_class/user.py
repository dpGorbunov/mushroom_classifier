from .credit import CreditManager
from .history import TransactionHistory, IdentificationHistory


class MushroomAppUser:
    def __init__(self, user_id: int, username: str, initial_credits: float = 0.0):
        self.__user_id = user_id
        self.__username = username
        self.__credit_manager = CreditManager(initial_credits)
        self.__transaction_history = TransactionHistory()
        self.__identification_history = IdentificationHistory()

    @property
    def get_id(self) -> int:
        return self.__user_id

    @property
    def get_username(self) -> str:
        return self.__username

    @property
    def get_credit_manager(self) -> CreditManager:
        return self.__credit_manager

    @property
    def get_transaction_history(self) -> TransactionHistory:
        return self.__transaction_history

    @property
    def get_identification_history(self) -> IdentificationHistory:
        return self.__identification_history