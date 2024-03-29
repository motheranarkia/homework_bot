import time
import logging
import os
import sys
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import exceptions

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info('Сообщение отправлено в Telegram')
    except Exception as error:
        message = f'Сбой при отправке сообщения: {error}'
        logging.error(message)
        raise exceptions.SendMessageException(message)


def get_api_answer(current_timestamp):
    """Выполняет запрос к API."""
    try:
        timestamp = current_timestamp or int(time.time())
        params = {'from_date': timestamp}
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=params
        )
    except Exception:
        raise exceptions.ApiAnswerNotOK('Сбой при запросе к API')
    else:
        if homework_statuses.status_code != HTTPStatus.OK:
            raise exceptions.ApiAnswerNotOK('Ошибка соединения')
        return homework_statuses.json()


def check_response(response):
    """проверяет API на корректность, возвращает список домашних работ."""
    if not isinstance(response, dict):
        raise TypeError('Некорректные данные')
    if 'homeworks' not in response:
        raise KeyError('Нет ключа homeworks в ответе от сервиса API')
    homeworks = response['homeworks']
    if not isinstance(response['homeworks'], list):
        raise TypeError('homeworks пришел не списком.')
    return homeworks


def parse_status(homework):
    """Извлекает статус домашней работы."""
    homework_name = homework.get('homework_name')
    if 'homework_name' not in homework:
        message_homework_name = 'Такого имени не существует'
        raise KeyError(message_homework_name)
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_STATUSES:
        message_homework_status = 'Такого статуса не существует'
        raise KeyError(message_homework_status)
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных."""
    return all(([TELEGRAM_TOKEN, PRACTICUM_TOKEN, TELEGRAM_CHAT_ID]))


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('Отсутствуют переменные окружения!')
        sys.exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            message = parse_status(homeworks)
            if not homeworks:
                logging.info('Новые статусы отсутствуют.')
            else:
                send_message(bot, message)

            current_timestamp = response.get(
                'current_date', current_timestamp
            )

        except Exception as error:
            message = f'Сбой в работе программы: {error}',
            logging.error(message)
        else:
            message = 'Программа отработана без ошибок'
            logging.info(message)

        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.Formatter(
        '%(asctime)s : [%(levelname)s] [%(lineno)d] : %(message)s'
    )
    main()
