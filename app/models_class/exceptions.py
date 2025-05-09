# --- БАЗОВЫЕ ИСКЛЮЧЕНИЯ ---


class MushroomAppException(Exception):
    """Базовое исключение для всего приложения."""
    pass


class InsufficientCreditsException(MushroomAppException):
    """Недостаточно кредитов у пользователя для совершения операции."""
    pass


class IdentificationFailedException(MushroomAppException):
    """Ошибка при попытке распознать гриб (например, модель не смогла обработать изображение)."""
    pass


class IdentificationTaskFailedException(MushroomAppException):
    """Ошибка при выполнении задачи на распознавание (общий сбой)."""
    pass
