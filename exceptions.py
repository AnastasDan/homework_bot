class TokenNotFoundError(Exception):
    """Исключение, возникающее в случае отсутствия токенов."""

    pass


class APINotFoundError(Exception):
    """Исключение, возникающее при сбое в API-запросе."""

    pass


class HomeworksNotFoundError(Exception):
    """Исключение, возникающее при отсутствии данных о заданиях."""

    pass


class CurrentDateNotFoundError(Exception):
    """Исключение, возникающее при отсутствии даты."""

    pass


class StatusNotFoundError(Exception):
    """Исключение, возникающее в случае отсутствия статуса задания."""

    pass


class NotForSend(Exception):
    """Базовый класс исключений, не требующих отправки сообщения в Телеграм."""

    pass


class TelegramError(NotForSend):
    """Исключение, возникающее при ошибке отправки сообщения в Telegram."""

    pass


class EmptyHomeworksError(NotForSend):
    """Исключение, возникающее при отсутствии домашних заданий."""
