class TokenNotFoundError(Exception):
    """Исключение, возникающее в случае отсутствия токенов."""

    pass


class APINotFoundError(Exception):
    """Исключение, возникающее при сбое в API-запросе."""

    pass


class HomeworksNotFoundError(Exception):
    """Исключение, возникающее при отсутствии данных о заданиях."""

    pass


class StatusNotFoundError(Exception):
    """Исключение, возникающее в случае отсутствия статуса задания."""

    pass
