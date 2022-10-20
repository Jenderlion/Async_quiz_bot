import json
import datetime
import logging
import os
import traceback

from aiogram import Bot


logger = logging.getLogger('BSEU Schedule')


class Path:
    """Focused class for save path to script"""
    root_path = None

    def __init__(self, raw_path: str):
        self.os = 'Linux' if raw_path[0] == '/' else 'Windows' if raw_path[0].isalpha() else 'Unknown OS'

        # OS type
        match self.os:
            case 'Linux':
                self.__sep = '/'
                self.__first = '/'
                self.__last = ''
                self.__path_list = raw_path[1:].split(self.__sep)
            case 'Windows':
                self.__sep = '\\'
                self.__first = ''
                self.__last = ''
                self.__path_list = raw_path.split(self.__sep)
            case _:
                self.__sep = '|'
                self.__first = '<<'
                self.__last = '>>'
                self.__path_list = [raw_path, ]

        self.root = self.__path_list[0]

    def __repr__(self):
        return f'{self.__first}{self.__sep.join(self.__path_list)}{self.__last}'

    def __str__(self):
        return f'{self.__first}{self.__sep.join(self.__path_list)}{self.__last}'

    def __add__(self, other):
        if isinstance(other, str):
            if other.find('\\') != -1:
                other = other.split('\\')
            else:
                other = other.split('/')
        elif isinstance(other, (list, tuple)):
            other = [str(_) for _ in other]
        else:
            raise ValueError('Added part of the path must be <str>, <list> or <tuple>')
        return Path(f'{self}{self.__sep}{self.__sep.join(other)}')

    def __sub__(self, other):
        if isinstance(other, int):
            if other < len(self.__path_list):
                return Path(f'{self.__first}{self.__sep.join(self.__path_list[:-1 * other])}{self.__last}')
            else:
                raise ValueError('You are about to return to more directories than the path specified')
        else:
            raise ValueError('You can only take <int> number of directories and files')

    @classmethod
    def get_root_path(cls):
        if cls.root_path is None:
            abs_file_path = os.path.abspath(__file__)
            current_file_path, filename = os.path.split(abs_file_path)
            cls.root_path = Path(current_file_path) - 1
        return cls.root_path


class BotTimer:
    """Time filter to blocked spamming"""

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if 'create_date' not in self.__dict__:
            self.create_date = datetime.datetime.now()
            self.message_time_dict = {}

    def __repr__(self):
        return f'<Bot Timer>, create at {self.create_date}\n{json.dumps(self.message_time_dict, indent=4)}'

    def add_user_timestamp(self, user_id: int, message_timestamp: int):
        self.message_time_dict[user_id] = message_timestamp


class BotInstanceContainer:
    """Saves bot instance"""

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, bot: Bot = None):
        if 'bot' not in self.__dict__:
            self.bot = bot


class PreparedQuestion:

    def __init__(self, input_string: str):
        __tuple = input_string.split('//\\\\')
        if len(__tuple) != 2:
            raise ValueError(
                f'Нет номера вопроса, текста или вариантов ответа! Строка, вызвавшая ошибку: {input_string}'
            )
        __info, __answers = __tuple
        self.answers = __answers.split('/\\')
        __relations_number, __text, *trash = __info.split('. ')
        if trash:
            raise ValueError(
                f'В описании вопроса (слева от //\\\\) несколько точек (точка должна быть только после номера)!'
                f' Строка, вызвавшая ошибку: {input_string}'
            )
        self.text = __text
        if __relations_number.isdigit():
            self.relations = None
            self.number = __relations_number
        else:
            __start = input_string.find('[{')
            __end = input_string.find('}]')
            if __start == -1 or __end == -1:
                raise ValueError(
                    f'Некорректно указана зависимость!'
                    f' Строка, вызвавшая ошибку: {input_string}'
                )
            __relations = __relations_number[__start + 2:__end]
            __number = __relations_number[__end + 2:]
            if not __number.isdigit():
                raise ValueError(
                    f'Номер должен быть числом!'
                    f' Строка, вызвавшая ошибку: {input_string}'
                )
            self.number = __number
            __relations_tuple = __relations.split(' -> ')
            if len(__relations_tuple) != 2:
                raise ValueError(
                    f'Некорректно указана зависимость!'
                    f' Строка, вызвавшая ошибку: {input_string}'
                )
            __rel_num, __rel_answer = __relations_tuple
            if not __rel_num.isdigit():
                raise ValueError(
                    f'Некорректно указана зависимость: номер вопроса должен быть числом!'
                    f' Строка, вызвавшая ошибку: {input_string}'
                )
            self.relations = __relations

    def __repr__(self):
        return f'<PreparedQuiz> {self.number}: {self.text} ({", ".join(self.answers)}); {self.relations}'


class PreparedQuiz:
    allowed_encodings = ['cp1251', 'utf-8']

    def __init__(self, quiz_path: Path):
        with open(str(quiz_path), 'r', encoding='utf-8') as opened_quiz:
            if opened_quiz.encoding not in self.allowed_encodings:
                raise UnicodeEncodeError
            quiz_content = opened_quiz.read().split('\n')
        if quiz_content[-1] == '':
            quiz_content.pop(-1)

        if not quiz_content[0][0].isalpha():
            raise ValueError(
                f'Имя опроса должно начинаться я буквы! Строка, вызвавшая ошибку: {quiz_content[0]}'
            )
        self.name = quiz_content.pop(0)

        if not quiz_content[0][0].isalpha():
            raise ValueError(
                f'Описание опроса должно начинаться с буквы! Строка, вызвавшая ошибку: {quiz_content[0]}'
            )
        self.title = quiz_content.pop(0)

        if not quiz_content[-1][0].isalpha():
            raise ValueError(
                f'Финальное сообщение должно начинаться с буквы! Строка, вызвавшая ошибку: {quiz_content[-1]}'
            )
        self.gratitude = quiz_content.pop(-1)

        self.questions = [PreparedQuestion(question) for question in quiz_content]

    def __repr__(self):
        return f'<PreparedQuiz> Name: {self.name}, title: {self.title}, gratitude: {self.gratitude},' \
               f' questions amount: {len(self.questions)}'
