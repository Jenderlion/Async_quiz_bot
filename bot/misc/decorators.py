import datetime
import traceback
import logging
import os
import json

from .custom_types import BotTimer
from .custom_types import BotInstanceContainer
from aiogram import types
from database.methods.select import get_user
from database.methods.select import get_bans
from database.methods.insert import add_user
from keyboards.reply import menu_keyboard


logger = logging.getLogger('Quiz Bot')


def message_group_wrapper(rules: tuple):
    """Enables or disables the execution of the function depending on the rules passed."""

    def decorator(func):

        async def wrapper(*args):
            message: types.Message = args[0]
            user_group = get_user(message.from_id).group
            if user_group == 'banned':
                ban_time = get_bans(message.from_id)[-1].unban_time
                await message.reply(f'Кажется, вы забанены до {ban_time}')
            elif user_group in rules:
                await func(message)
            else:
                logger.warning(
                    f'GROUP EROOR: Message {message.text} from @{message.from_user.username} ({message.from_id})'
                )
                await message.reply('Я не знаю такой команды :(', reply_markup=menu_keyboard())

        return wrapper

    return decorator


def callback_group_wrapper(rules: tuple):
    """Enables or disables the execution of the function depending on the rules passed."""

    def decorator(func):

        async def wrapper(*args):
            callback: types.CallbackQuery = args[0]
            bot_message: types.Message = callback.message
            tg_bot = BotInstanceContainer().bot
            user_group = get_user(callback.from_user.id).group
            if user_group == 'banned':
                ban_time = get_bans(callback.from_user.id)[-1].unban_time
                await tg_bot.send_message(callback.from_user.id, f'Кажется, Вы забанены до {ban_time}')
            elif user_group in rules:
                await func(callback)
            else:
                await tg_bot.send_message(
                    callback.from_user.id, 'Вам нельзя пользоваться этим функционалом!', reply_markup=menu_keyboard()
                )

        return wrapper

    return decorator


def time_wrapper(timeout: int = 5):
    """Enables (or disables) the execution of the function depending on the time passed.
    Also adds a timestamp for user"""

    def decorator(func):

        async def wrapper(*args, **kwargs):
            message: types.Message = args[0]
            bot_timer = BotTimer()
            __now = datetime.datetime.now().timestamp()
            __last_message_in = bot_timer.message_time_dict.get(message.from_id, 0)

            if __now > __last_message_in + timeout:
                await func(*args)
                bot_timer.message_time_dict[message.from_id] = __now
            else:
                __word = \
                    "секунд" if timeout in (0, 5, 6, 7, 8, 9, 10) else "секунды" if timeout in (2, 3, 4) else "секунда"
                await message.reply(f'С последнего сообщения должно пройти как минимум {timeout} {__word},'
                                    f' чтобы выполнить эту команду')

        return wrapper

    if isinstance(timeout, int):
        timeout = 10 if timeout > 10 else timeout
        return decorator
    else:
        function = timeout
        timeout = 0
        return decorator(function)


def start_wrapper(func):
    """/start wrapper"""

    async def wrapper(*args, **kwargs):
        message: types.Message = args[0]
        user = get_user(message.from_id)
        if user is None:
            user = add_user(message)
            logger.debug(f'Add new user {user}')
        await func(*args, user)

    return wrapper


def callback_wrapper(func):
    """Remove Inline Markup in message"""

    async def wrapper(*args, **kwargs):
        callback_query: types.CallbackQuery = args[0]
        try:
            message: types.Message = callback_query.message
            __inline_dict = {}
            __inline_general_list = callback_query.message.reply_markup.inline_keyboard
            for __inline_list in __inline_general_list:
                for __item in __inline_list:
                    __inline_dict[__item['callback_data']] = __item['text']
            __action = __inline_dict.get(callback_query.data, 'Не установлено')
            await message.edit_text(
                text=f'{message.text}\n\nВыбран вариант "{__action}"', reply_markup=None
            )
            logger.debug(
                f'Callback {callback_query} from @{callback_query.from_user.username} {callback_query.from_user.id}'
            )
        except Exception as exc:
            logger.error(f'Callback processing error: {exc} \\ {type(exc)}')
        await func(callback_query)

    return wrapper


def log(func):
    """Message logger decorator"""

    async def wrapper(*args, **kwargs):
        message: types.Message = args[0]
        await func(*args)
        logger.debug(f'Message {message.text} from @{message.from_user.username} in chat {message.chat.id}')

    return wrapper


def error_log(func):
    """Error logger decorator"""

    async def wrapper(*args, **kwargs):

        __update: types.update.Update = args[0]
        __exception = args[1]
        __message: types.Message = __update['message']
        logger.error(f'Error when trying to send a message to @{__message.from_user.username}!\n'
                     f'User message text: {__message.text}\nError text: {__exception}\n'
                     f'Traceback:\n{traceback.format_exc()}')
        await func(*args, **kwargs)

    return wrapper
