class ApiAnswerNotOK(ConnectionError):
    pass


class SendMessageException(Exception):
    """Сбой при отправке сообщения в Telegram чат."""
    pass
