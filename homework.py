import logging
import os
import sys
import time
from http import HTTPStatus
from typing import Any

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (APINotFoundError, CurrentDateNotFoundError,
                        HomeworksNotFoundError, StatusNotFoundError,
                        TokenNotFoundError)

load_dotenv()


PRACTICUM_TOKEN: str | None = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN: str | None = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID: str | None = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD: int = 600
ENDPOINT: str = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS: dict[str, str] = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS: dict[str, str] = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

base_dir: str = os.path.dirname(os.path.abspath(__file__))
log_dir: str = os.path.join(base_dir, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file: str = os.path.join(log_dir, 'telegram_bot.log')

logger: logging.Logger = logging.getLogger(__name__)
handler_stream: logging.StreamHandler = logging.StreamHandler(sys.stdout)
handler_file: logging.FileHandler = logging.FileHandler(
    log_file,
    encoding='utf-8'
)
formatter: logging.Formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(funcName)s:%(lineno)d - %(message)s'
)
handler_stream.setFormatter(formatter)
handler_file.setFormatter(formatter)
logger.addHandler(handler_stream)
logger.addHandler(handler_file)


def check_tokens() -> bool:
    """Проверка доступности переменных окружения."""
    return all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, PRACTICUM_TOKEN])


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправка сообщения в Telegram чат."""
    logger.debug(f'Начата отправка сообщения: {message}')

    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Отправлено сообщение: {message}')

    except telegram.error.TelegramError as error:
        logger.error(f'Ошибка при отправке сообщения: {error}')


def get_api_answer(timestamp: int) -> dict[str, Any]:
    """Запрос к единственному эндпоинту API-сервиса."""
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


def check_response(response: dict[str, Any]) -> dict[str, Any]:
    """Проверка ответа API на соответствие документации."""
    if not isinstance(response, dict):
        logger.error(f'Неверный тип данных ({type(response).__name__})')
        raise TypeError(f'Неверный тип данных ({type(response).__name__})')

    if 'homeworks' not in response:
        logger.error('Отсутствует ключ "homeworks"')
        raise HomeworksNotFoundError('Отсутствует ключ "homeworks"')

    homeworks: list[dict] = response.get('homeworks')

    if not isinstance(homeworks, list):
        logger.error(f'Неверный тип данных ({type(homeworks).__name__})')
        raise TypeError(f'Неверный тип данных ({type(homeworks).__name__})')

    if 'current_date' not in response:
        logger.error('Отсутствует ключ "current_date"')
        raise CurrentDateNotFoundError('Отсутствует ключ "current_date"')

    return response


def parse_status(homework: dict[str, Any]) -> str:
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
            homework: list[dict[str, Any]] = \
                check_response(response).get('homeworks')

            if not homework:
                status: str = 'Отсутствуют новые статусы'
                logger.debug(status)
                send_message(bot, status)

            else:
                send_message(bot, parse_status(homework[0]))

            timestamp: int = response.get('current_date')

        except Exception as error:
            message: str = f'Сбой в работе программы: {error}'
            last_status_message: str = ''

            if message != last_status_message:
                logger.error(message)
                send_message(bot, message)
                last_status_message = message

        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
    )

    main()
