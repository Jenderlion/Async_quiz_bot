import json
import datetime
import logging
import traceback

from aiogram import Bot


logger = logging.getLogger('BSEU Schedule')


class Path:
    """Focused class for save path to script"""

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
