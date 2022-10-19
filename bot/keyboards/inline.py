import requests
from lxml import html
from functools import cache

from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from database.main import User


def inline_markup_settings(user: User) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.row(InlineKeyboardButton(
        f'Изменить статус рассылки',
        callback_data=f'settings mailing {"0" if user.mailing else "1"}')
    )
    keyboard.row(InlineKeyboardButton(
        f'Ничего не делать',
        callback_data='settings cancel')
    )

    return keyboard


def inline_markup_user(user: User) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton('Cancel', callback_data='user cancel'))

    if user.quiz_status:
        keyboard.row(InlineKeyboardButton('Refresh quiz', callback_data='user quiz'))
    if user.group == 'banned':
        keyboard.row(InlineKeyboardButton('Unban user', callback_data='user unban'))
        return keyboard
    if user.group in ('admin', 'm_admin'):
        return keyboard
    if user.group == 'user':
        keyboard.row(InlineKeyboardButton('Make Editor', callback_data='user editor'))
        return keyboard
    if user.group == 'editor':
        keyboard.row(InlineKeyboardButton('Make User', callback_data='user user'))
    return keyboard


@cache
def inline_markup_help() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton('Связаться с администратором', callback_data='help request'))
    keyboard.row(InlineKeyboardButton('Хочу такого бота', callback_data='help bot'))
    return keyboard


def inline_markup_credentials(__target_id: int | str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton('Send contact information', callback_data=f'help credentials {__target_id}'))
    return keyboard


def base_markup() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('base button', callback_data='base callback'))
    return keyboard
