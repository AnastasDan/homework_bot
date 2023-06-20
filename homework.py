import logging
import os
import sys
import time
from http import HTTPStatus
from typing import Any, Optional

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (APINotFoundError, HomeworksNotFoundError,
                        StatusNotFoundError, TokenNotFoundError)

load_dotenv()


PRACTICUM_TOKEN: Optional[str] = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN: Optional[str] = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID: Optional[str] = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD: int = 600
ENDPOINT: str = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS: dict[str, str] = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS: dict[str, str] = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.DEBUG,
)

logger: logging.Logger = logging.getLogger(__name__)
handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


def check_tokens() -> bool:
    """Проверка доступности переменных окружения."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    return False


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправка сообщения в Telegram чат."""
    bot.send_message(TELEGRAM_CHAT_ID, message)
    logger.debug('Отправлено сообщение')


def get_api_answer(timestamp: int) -> dict[str, Any]:
    """Запрос к единственному API-сервиса."""
    payload: dict[str, int] = {'from_date': timestamp}
    try:
        response: requests.Response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=payload
        )
    except requests.RequestException:
        logger.error('Сбой при запросе к эндпоинту')
        raise APINotFoundError('Сбой при запросе к эндпоинту')
    if response.status_code != HTTPStatus.OK:
        logger.error('Сбой при запросе к эндпоинту')
        raise APINotFoundError('Сбой при запросе к эндпоинту')
    return response.json()


def check_response(response: dict[str, Any]) -> list[dict[str, Any]]:
    """Проверка ответа API на соответствие документации."""
    if not isinstance(response, dict):
        logger.error('Неверный тип данных')
        raise TypeError('Неверный тип данных')
    if 'homeworks' not in response:
        logger.error('Отсутствует ключ "homeworks"')
        raise HomeworksNotFoundError('Отсутствует ключ "homeworks"')
    homeworks: list[dict] = response.get('homeworks')
    if not isinstance(homeworks, list):
        logger.error('Неверный тип данных')
        raise TypeError('Неверный тип данных')
    return homeworks


def parse_status(homework: list[dict[str, Any]]) -> str:
    """Извлечение из информации статуса домашней работы."""
    if 'homework_name' not in homework:
        logger.error('Отсутствует переменная "homework_name"')
        raise HomeworksNotFoundError('Отсутствует переменная "homework_name"')
    homework_name: str = homework.get('homework_name')
    status: str = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        logger.error('Неожиданный статус домашней работы')
        raise StatusNotFoundError('Неожиданный статус домашней работы')
    verdict: str = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main() -> None:
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствуют обязательные переменные')
        raise TokenNotFoundError('Отсутствуют обязательные переменные')
    bot: telegram.Bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp: int = int(time.time())
    while True:
        try:
            response: dict[str, Any] = get_api_answer(timestamp)
            homework: list[dict[str, Any]] = check_response(response)
            logger.debug('Сообщение отправлено успешно')
            if not homework:
                status: str = 'Отсутствуют новые статусы'
                logger.debug(status)
                send_message(bot, status)
            else:
                send_message(bot, parse_status(homework[0]))
        except Exception as error:
            message: str = f'Сбой в работе программы: {error}'
            try:
                logger.error(message)
                send_message(bot, message)
            except Exception as error:
                logger.error(
                    f'Ошибка при отправке сообщения в Telegram: {error}'
                )
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
