import functools
from aiogram.types import ReplyKeyboardMarkup


@functools.cache
def menu_keyboard():
    """Create welcome greet menu"""

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Пройти опрос')
    keyboard.row('Изменить ответы в последнем опросе')
    keyboard.row('Настройки')
    keyboard.row('Помощь')

    return keyboard
