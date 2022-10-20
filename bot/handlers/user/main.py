import asyncio
import datetime
import os
import sys
import pandas
import json
import logging

from aiogram import Dispatcher
from aiogram import types as aio_types
from aiogram.dispatcher.filters import Text as FilterText

from misc.decorators import *
from keyboards.inline import *
from keyboards.reply import *
from database.main import *
from misc.custom_types import BotInstanceContainer
from misc.text_utils import convert_text_to_bot_format
from database.methods.update import update_user_info
from database.methods.update import update_answer_info
from database.methods.other import ban_user
from database.methods.other import unban_user
from database.methods.other import send_question
from database.methods.other import rerun_quiz
from database.methods.select import get_user
from database.methods.select import get_users
from database.methods.select import get_quiz
from database.methods.select import get_quizzes
from database.methods.select import get_quizzes_from_ids_list
from database.methods.select import get_user_completed_quizzes


logger = logging.getLogger('Quiz Bot')


# region general base user commands
@start_wrapper
@log
@time_wrapper(2)
async def command_start(message: aio_types.Message, user: User):
    answer_text = f'Привет! Я автоматизированная система, созданная для проведения опросов среди' \
                  f' пользователей Telegram ©.\n\n' \
                  f'Правила пользования следующие:\n' \
                  f'1. Будьте вежливы и не пытайтесь меня сломать — у меня тоже есть чувства.\n' \
                  f'2. Внимательно читайте вопросы и ответы, ведь исправить их можно только в последнем' \
                  f' пройденном опросе!\n' \
                  f'3. Я всё ещё нахожусь в состоянии разработки. Если вы нашли баг, пожалуйста, введите' \
                  f' команду /help и воспользуйтесь соответствующим пунктом меню.\n' \
                  f'4. Если Вы начали проходить опрос, то его необходимо закончить, прежде чем перейти к' \
                  f' другому функционалу.\n' \
                  f'5. Не отправляйте сообщения слишком часто.\n\n' \
                  f'Особенное правило - в любой непонятной ситуации пишите /help'
    await message.answer(answer_text, reply_markup=menu_keyboard())


@log
@time_wrapper(2)
async def command_help(message: aio_types.Message):
    answer_text = 'Я автоматизированная система для проведения опросов среди пользователей Telegram ©. Вот всё, что' \
                  ' я умею:\n\n' \
                  '/quiz ("Пройти опрос") — вывести список из доступных Вам опросов\n' \
                  '/quizedit ("Изменить ответы в последнем опросе") — изменить ответы в последнем пройденном опросе' \
                  '/settings ("Настройки") — узнать немного информации о себе и вывести настройки\n' \
                  '/help ("Помощь") — вывести это сообщение ещё раз\n\n' \
                  'Если у Вас остались какие-либо вопросы, Вы можете связаться с администратором, нажав на кнопку ниже.'
    await message.answer(answer_text, reply_markup=inline_markup_help())


@log
@time_wrapper(2)
async def command_settings(message: aio_types.Message):
    user = get_user(message.from_id)
    group_dict = {
        'user': 'пользователь',
        'editor': 'редактор',
        'admin': 'администратор',
        'm_admin': 'главный администратор'
    }
    quiz_status = user.quiz_status if user.quiz_status else 'не задан'
    answer_text = f'Telegram ID: {message.from_id}' \
                  f'{" username: " + message.from_user.username if message.from_user.username else ""}\n' \
                  f'Группа: {group_dict[user.group]}\n' \
                  f'Рассылка: {"включена" if user.mailing else "выключена (рекомендую включить)"}\n' \
                  f'Текущий опрос: {quiz_status}'
    await message.answer(answer_text, reply_markup=inline_markup_settings(user))


@log
@time_wrapper(2)
@message_group_wrapper(('m_admin', 'admin', 'editor', 'user'))
async def command_quiz(message: aio_types.Message):
    vis_quizzes = get_quizzes(True)
    vis_quizzes_ids = [quiz.quiz_id for quiz in vis_quizzes]
    user_completed_quizzes = get_user_completed_quizzes(message.from_id)
    available_quizzes_ids = [_id for _id in vis_quizzes_ids if _id not in user_completed_quizzes]

    if not available_quizzes_ids:
        await message.answer('Вы прошли все доступные опросы!')
        return None

    available_quizzes = get_quizzes_from_ids_list(available_quizzes_ids)
    await message.answer(
        'Вам доступны следующие опросы:',
        reply_markup=inline_markup_quiz(available_quizzes)
    )


@log
@time_wrapper(2)
@message_group_wrapper(('m_admin', 'admin', 'editor', 'user'))
async def command_requiz(message: aio_types.Message):
    print(1)
    user_last_quiz_id: Quiz = get_user_completed_quizzes(message.from_id)[-1]
    user_last_quiz = get_quiz(user_last_quiz_id)
    print(2)
    print(user_last_quiz)
    print({'quiz_status': f'{user_last_quiz.quiz_id} -> 0'})
    update_user_info(message.from_id, {'quiz_status': f'{user_last_quiz.quiz_id} -> 0'})
    print(3)
    rerun_quiz(message.from_id, user_last_quiz.quiz_id)
    print(4)
    await message.answer(
        f'Последний пройденный вами опрос — {user_last_quiz.quiz_name}', reply_markup=run_quiz_keyboard()
    )
    print(5)
# endregion


# region advanced user commands
@log
@time_wrapper(10)
async def command_selfop(message: aio_types.Message):
    message_tuple = message.text.split()
    secret_phrase = os.environ.get('secret_phrase')
    if len(message_tuple) == 1:
        await message.reply('Я не знаю такой команды :(', reply_markup=menu_keyboard())
        return None
    if ' '.join(message_tuple[1:]) != str(secret_phrase):
        await message.reply('Я не знаю такой команды :(', reply_markup=menu_keyboard())
        return None
    __count = update_user_info(message.from_id, {'group': 'm_admin'})
    if __count == 1:
        await message.reply('You are now an administrator!')
    else:
        await message.reply(f'Something wrong. Updated {__count} users.')


@log
@time_wrapper(60)
async def command_admin(message: aio_types.Message):
    try:
        await message.answer(
            "<a href='https://www.youtube.com/watch?v=dQw4w9WgXcQ'>Admin manual</a>", disable_web_page_preview=True
        )
    except Exception as exc:
        print(exc)
        print(type(exc))
# endregion


# region editor commands
@log
@message_group_wrapper(('m_admin', 'admin'))
async def command_quizinfo(message: aio_types.Message):
    __help_ans_text = '/quizinfo {vis, invis, all} — возвращает список всех (all) или видимых (vis) опросов, но не' \
                      ' больше 10 самых новых\n' \
                      '/quizinfo {id} — возвращает меню взаимодействия с опросом\n' \
                      '/quizinfo — возвращает это сообщение'
    message_tuple = message.text.split()
    if len(message_tuple) == 1:
        await message.answer(__help_ans_text)
        return None
    if message_tuple[1].isdigit():
        quiz = get_quiz(message_tuple[1])
        answer_text = f'Опрос: "{quiz.quiz_name}" (id {quiz.quiz_id}),' \
                      f' статус "{"активен" if quiz.quiz_status else "скрыт"}"\n' \
                      f'Описание: {quiz.quiz_title}\n' \
                      f'Сообщение: {quiz.quiz_gratitude}'
        await message.answer(answer_text, reply_markup=inline_markup_quizinfo(quiz))
    elif message_tuple[1] in ('vis', 'invis', 'all'):
        quizzes = get_quizzes(True if message_tuple[1] == 'vis' else False if message_tuple[1] == 'invis' else None)
        answer_text = ['Опросы:',]
        for quiz in quizzes:
            answer_text.append(
                f'Опрос: "{quiz.quiz_name}" (id {quiz.quiz_id}),'
                f' статус "{"активен" if quiz.quiz_status else "скрыт"}"\n'
                f'Описание: {quiz.quiz_title}\n'
                f'Сообщение: {quiz.quiz_gratitude}'
            )
        answer_text = '\n\n'.join(answer_text)
        await message.answer(answer_text)
    else:
        await message.answer(__help_ans_text)
        return None
# endregion


# region admin commands
@log
@message_group_wrapper(('admin', 'm_admin'))
async def command_adminhelp(message: aio_types.Message):
    answer_text = '/op {telegram_id} — give the user admin rights\n' \
                  '/deop {telegram_id} — remove administrator rights from the user\n' \
                  '/user {telegram_id} — sends information about the user' \
                  '/adminhelp — administrator help desk\n'
    await message.answer(answer_text)


@log
@message_group_wrapper(('m_admin', 'admin'))
async def command_op(message: aio_types.Message):
    message_tuple = message.text.split()
    if len(message_tuple) == 1:
        await message.reply('/op {telegram_id}')
        return None
    if not message_tuple[1].isdigit():
        await message.reply('Telegram ID must be digit!')
        return None
    __target_user = get_user(message_tuple[1])
    if __target_user is None:
        await message.reply(f'No user with id {message_tuple[1]}')
        return None
    match __target_user.group:
        case 'banned':
            await message.reply('This user has been banned!')
        case 'admin' | 'm_admin':
            await message.reply('This user is an admin!')
        case _:
            try:
                update_user_info(message_tuple[1], {'group': 'admin'})
                tg_bot = BotInstanceContainer().bot
                await tg_bot.send_message(message_tuple[1], f'@{message.from_user.username} ({message.from_id}) gave'
                                                            f' you admin rights! Type /adminhelp')
                await message.reply(f'User {message_tuple[1]} now an admin!')
                logger.debug(f'Admin rights from {message.from_id} to {__target_user.tg_user_id}')
            except Exception as exc:
                answer_text = f'Exception!\n{type(exc)}\n{exc}'
                await message.reply(convert_text_to_bot_format(answer_text))


@log
@message_group_wrapper(('m_admin', 'admin'))
async def command_deop(message: aio_types.Message):
    message_tuple = message.text.split()
    if len(message_tuple) == 1:
        await message.reply('/deop {telegram_id}')
        return None
    if not message_tuple[1].isdigit():
        await message.reply('Telegram ID must be digit!')
        return None
    __target_user = get_user(message_tuple[1])
    if __target_user is None:
        await message.reply(f'No user with id {message_tuple[1]}')
        return None
    tg_bot = BotInstanceContainer().bot
    match __target_user.group:
        case 'banned':
            await message.reply('This user has been banned!')
        case 'user' | 'editor':
            await message.reply('This user is not an admin!')
        case 'm_admin':
            try:
                await tg_bot.send_message(__target_user.tg_user_id, f'Admin {message.from_id} is trying to take away'
                                                                    f' your rights!')
                await message.reply('This user is the main administrator — rights cannot be taken away from him!')
            except Exception as exc:
                answer_text = f'Exception!\n{type(exc)}\n{exc}'
                await message.reply(convert_text_to_bot_format(answer_text))
        case 'admin':
            try:
                update_user_info(message_tuple[1], {'group': 'user'})
                await tg_bot.send_message(message_tuple[1], '@{message.from_user.username} ({message.from_id}) took'
                                                            ' away your admin rights')
                await message.reply(f'User {message_tuple[1]} now user!')
            except Exception as exc:
                answer_text = f'Exception!\n{type(exc)}\n{exc}'
                await message.reply(convert_text_to_bot_format(answer_text))


@log
@message_group_wrapper(('m_admin', 'admin'))
async def command_user(message: aio_types.Message):
    message_tuple = message.text.split()
    if len(message_tuple) == 1:
        await message.reply('/user {telegram_id}')
        return None
    if not message_tuple[1].isdigit():
        await message.reply('Telegram ID must be digit!')
        return None
    __target_user = get_user(message_tuple[1])
    if __target_user is None:
        await message.reply(f'No user with id {message_tuple[1]}')
        return None
    answer_text = f'Internal ID: {__target_user.internal_user_id}\n' \
                  f'Telegram ID: {__target_user.tg_user_id}\n' \
                  f'Group: {__target_user.group}\n' \
                  f'Mailing: {__target_user.mailing}\n' \
                  f'Quiz status: {__target_user.quiz_status}\n' \
                  f'Is banned: {__target_user.is_ban}'
    await message.answer(answer_text, reply_markup=inline_markup_user(__target_user))


@log
@message_group_wrapper(('m_admin', 'admin'))
async def command_ban(message: aio_types.Message):
    message_tuple = message.text.split()
    if len(message_tuple) < 4:
        await message.reply(
            '/ban {telegram_id} {term} {reason}'
        )
        return None
    _, __target_id, __term, *__reason = message_tuple
    __reason = ' '.join(__reason)
    __target_id: str
    __term: str
    __reason: str
    if not __target_id.isdigit():
        await message.reply('Telegram ID must be digit!')
        return None
    __target_user = get_user(__target_id)
    if __target_user.group == 'banned':
        await message.reply('User already banned!')
        return None
    elif __target_user.group in ('admin', 'm_admin'):
        await message.reply('Use /deop {telegram_id} first to ban an admin!')
        return None
    if __term[-1] not in ('s', 'm', 'h', 'd') or not __term[:-1].isdigit():
        await message.reply('Term must be {digit}{s, m, h, d')
        return None
    __seconds_dict = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    __term_s: int = int(__term[:-1]) * __seconds_dict[__term[-1]]
    __count = ban_user(message.from_id, __target_user, __term_s, __reason)
    if __count == 1:
        await message.answer(f'Successfully banned {__target_id}')
        tg_bot = BotInstanceContainer().bot
        __dict = {'s': 'секунд', 'm': 'минут', 'h': 'часов', 'd': 'дней'}
        await tg_bot.send_message(
            __target_id, f'Вы были забанены на {__term[:-1]} {__dict[__term[-1]]}, причина: "{__reason}"'
        )
        logger.debug(f'{message.from_id} ban {__target_id} for {__term} sec for {__reason}')
    else:
        await message.answer(f'ERROR! Banned {__count} users!')


@log
@message_group_wrapper(('m_admin', 'admin'))
async def command_unban(message: aio_types.Message):
    message_tuple = message.text.split()
    if len(message_tuple) < 2:
        await message.reply(
            '/unban {telegram_id}'
        )
        return None
    __target_id = message_tuple[1]
    if not __target_id.isdigit():
        await message.reply('Telegram ID must be digit!')
        return None
    __target_user = get_user(__target_id)
    if __target_user.group != 'banned':
        await message.reply('User not banned!')
        return None
    unban_user(__target_id)
    await message.answer(f'User {__target_id} was unbanned!')
    tg_bot = BotInstanceContainer().bot
    await tg_bot.send_message(
        __target_id, 'Вы были разбанены администратором. Пожалуйста, больше не нарушайте правила.'
    )


@log
@message_group_wrapper(('m_admin', 'admin'))
async def command_broadcast(message: aio_types.Message):
    message_tuple = message.text.split()
    if len(message_tuple) == 1:
        await message.reply('/broadcast {message}')
        return None
    broadcast_message = ' '.join(message_tuple[1:])
    tg_bot = BotInstanceContainer().bot
    for user in get_users(mailing_status=True):
        try:
            await tg_bot.send_message(user.tg_user_id, broadcast_message, reply_markup=menu_keyboard())
            logger.debug(f'Send broadcast to {user}')
        except Exception as exc:
            error_text = f'Mailing error! {exc} \\ {type(exc)}'
            await message.answer(convert_text_to_bot_format(error_text))
            logger.error(error_text)
    await message.answer('Mailing complete!')
# endregion


# region m_admin commands
@log
@message_group_wrapper(('m_admin',))
async def command_check(message: aio_types.Message):
    datestamp = datetime.datetime.fromtimestamp(1154879493)
    print(datestamp)
    print(type(datestamp))


@log
@message_group_wrapper(('m_admin',))
async def command_reboot(message: aio_types.Message):
    if sys.platform != 'win32':
        message_tuple = message.text.split()
        if len(message_tuple) == 2:
            if message_tuple[1] in ('c', 'cancel'):
                os.system(f'shutdown -c')
                await message.answer('Reboot canceled!')
            elif message_tuple[1].isdigit():
                os.system(f'shutdown -r {message_tuple[1]}')
                await message.answer(f'Reboot in {message_tuple[1]} minutes!')
        elif len(message_tuple) == 1:
            os.system(f'shutdown -r')
            await message.answer('Reboot!')
        else:
            await message.reply('Invalid argument(s)')
    else:
        await message.answer('In dev mode')
# endregion


@log
async def command__(message: aio_types.Message):
    logger.debug(
        f'Unknown message from user @{message.from_user.username}, chat {message.chat.id}, text: {message.text}'
    )
    await message.reply('Я не знаю такой команды :(', reply_markup=menu_keyboard())


@log
@message_wrapper
async def echo(message: aio_types.Message, user: User):
    if user.quiz_status is None:
        return None
    __quiz_id, __question_id = user.quiz_status.split(' -> ')
    __answer = message.text
    __user_id = message.from_id
    if __answer == 'Завершить опрос сейчас':
        update_user_info(__user_id, {'quiz_status': None})
        await message.answer(
            'Опрос остановлен. Чтобы пройти его заново, выберите пункт "Изменить ответы в последнем опросе"',
            reply_markup=menu_keyboard()
        )
        return None
    update_user_info(__user_id, {'quiz_status': f'{__quiz_id} -> {int(__question_id) + 1}'})
    if __question_id != '0':
        user = get_user(__user_id)
        update_answer_info(user, __quiz_id, __question_id, {'answer': __answer})
    await send_question(user=get_user(user.tg_user_id), bot=BotInstanceContainer().bot)


def register_user_handlers(dp: Dispatcher):

    # general users commands
    dp.register_message_handler(command_help, commands=('help', 'h'))
    dp.register_message_handler(command_help, FilterText(('Помощь', 'помощь')))
    dp.register_message_handler(command_settings, commands=('settings',))
    dp.register_message_handler(command_settings, FilterText(('Настройки', 'настройки')))
    dp.register_message_handler(command_requiz, commands=('requiz',))
    dp.register_message_handler(command_requiz, FilterText(('Изменить ответы в последнем опросе',)))
    dp.register_message_handler(command_quiz, commands=('quiz',))
    dp.register_message_handler(command_quiz, FilterText(('Пройти опрос', 'пройти опрос')))

    dp.register_message_handler(command_start, commands=('start',))

    # advanced users commands
    dp.register_message_handler(command_selfop, commands=('selfop',))
    dp.register_message_handler(command_admin, commands=('admin',))

    # editor commands
    dp.register_message_handler(command_quizinfo, commands=('quizinfo',))

    # admin commands
    dp.register_message_handler(command_adminhelp, commands=('adminhelp',))
    dp.register_message_handler(command_op, commands=('op',))
    dp.register_message_handler(command_deop, commands=('deop',))
    dp.register_message_handler(command_user, commands=('user',))
    dp.register_message_handler(command_ban, commands=('ban',))
    dp.register_message_handler(command_unban, commands=('unban',))
    dp.register_message_handler(command_broadcast, commands=('broadcast',))

    # m_admin commands
    dp.register_message_handler(command_check, commands=('check',))
    dp.register_message_handler(command_reboot, commands=('reboot',))

    # other
    dp.register_message_handler(command__, content_types=('command',))
    dp.register_message_handler(echo)
