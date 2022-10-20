import functools
from aiogram.types import ReplyKeyboardMarkup
from database.main import QuizQuestion


@functools.cache
def menu_keyboard() -> ReplyKeyboardMarkup:
    """Create welcome greet menu"""

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Пройти опрос')
    keyboard.row('Изменить ответы в последнем опросе')
    keyboard.row('Настройки')
    keyboard.row('Помощь')

    return keyboard


def question_keyboard(question: QuizQuestion) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    answers_list = question.quest_ans.split(' || ')
    if len(answers_list) != 1 and answers_list[0] != 'MANUAL_INPUT':
        for answer in answers_list:
            keyboard.row(answer)

    keyboard.row('Завершить опрос сейчас')

    return keyboard


@functools.cache
def run_quiz_keyboard() -> ReplyKeyboardMarkup:

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Начать опрос')

    return keyboard
