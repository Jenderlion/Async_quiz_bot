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
from database.methods.other import ban_user
from database.methods.other import unban_user
from database.methods.select import get_user
from database.methods.select import get_users


logger = logging.getLogger('Quiz Bot')


# # Decorator cannot be used because the user must be added first
# def welcome_handler(message: types.Message):
#     """Simple welcome-message handler
#
#     Adds a new user if it doesn't already exist
#     """
#     add_user(message.from_user.id, message.message_id, message.text, float(message.date.timestamp()))
#     msg = f'Привет! Я автоматизированная система, созданная для проведения опросов среди' \
#           f' пользователей Telegram ©.\n\n' \
#           f'Правила пользования следующие:\n' \
#           f'1. Будьте вежливы и не пытайтесь меня сломать — у меня тоже есть чувства.\n' \
#           f'2. Внимательно читайте вопросы и ответы, ведь исправить их можно только в последнем' \
#           f' пройденном опросе!\n' \
#           f'3. Я всё ещё нахожусь в состоянии разработки. Если вы нашли баг, пожалуйста, введите' \
#           f' команду /help и воспользуйтесь соответствующим пунктом меню.\n' \
#           f'4. Если Вы начали проходить опрос, то его необходимо закончить, прежде чем перейти к' \
#           f' другому функционалу.\n' \
#           f'5. Не отправляйте сообщения чаще, чем раз в {min_time_delta} секунд.\n\n' \
#           f'Особенное правило - в любой непонятной ситуации пишите /help'
#     simple_send_message(message.chat.id, msg, get_welcome_markup())
#
#
# @message_wrapper
# def help_handler(message: types.Message):
#     """/help handler"""
#     simple_send_message(message.chat.id, 'Что случилось?', get_help_inline_markup())
#
#
# @message_group_wrapper(('admin', 'm_admin'))
# @message_wrapper
# def set_role_handler(message: types.Message):
#     """/role handler"""
#     command_seq = message.text.split()
#     if len(command_seq) == 1:
#         msg_text = '/role - отправляет это сообщение с помощью\n' \
#                    '/role {id} - отправляет информацию о пользователе с {id}\n' \
#                    '/role {id} {group} - установить {group} для пользователя с {id}:' \
#                    ' group == (user, editor, admin)'
#         simple_send_message(message.chat.id, msg_text)
#     else:
#         target_user_id = int(command_seq[1])
#         if len(command_seq) == 2:
#             target_user = get_user_info(target_user_id)
#             group_dict = {
#                 'ban': 'забанен',
#                 'user': 'пользователь',
#                 'editor': 'редактор',
#                 'admin': 'администратор',
#                 'm_admin': 'главный администратор'
#             }
#             simple_send_message(
#                 message.chat.id,
#                 f'ID: {target_user.tg_user_id}\n'
#                 f'Внутренний ID: {target_user.internal_user_id}\n'
#                 f'Роль: {group_dict[target_user.group]}\n'
#                 f'Рассылка: {"включена" if target_user.mailing else "отключена"}'
#             )
#         elif command_seq[2] in ('user', 'editor', 'admin'):
#             target_user = get_user_info(target_user_id)
#             if target_user.group not in ('m_admin', 'ban'):
#                 update_user_group(message.from_user.id, target_user_id, command_seq[2])
#                 simple_send_message(
#                     message.chat.id,
#                     f'Новая группа "{command_seq[2]}" установлена для пользователя с'
#                     f' id {target_user_id}',
#                     get_welcome_markup()
#                 )
#             else:
#                 simple_send_message(
#                     message.chat.id,
#                     'Этому пользователю нельзя изменить группу!',
#                     get_welcome_markup()
#                 )
#         else:
#             simple_send_message(
#                 message.chat.id,
#                 'Ошибка в написании команды',
#                 get_welcome_markup()
#             )
#
#
# @message_group_wrapper(('admin', 'm_admin'))
# @message_wrapper
# def ban_handler(message: types.Message):
#     """/ban handler"""
#     command_seq = message.text.split()
#     if len(command_seq) == 1:
#         msg_text = '/ban - отправляет это сообщение с помощью\n' \
#                    '/ban {id} {term} {reason} - банит пользователя с {id} на срок {term} с' \
#                    ' причиной {reason}\n' \
#                    '/unban - вывод сообщения с помощью по разбану'
#         simple_send_message(message.chat.id, msg_text)
#     elif len(command_seq) >= 4:
#         if command_seq[1].isdigit():
#             if check_term(command_seq[2]):
#                 target_id = int(command_seq[1])
#                 ban_term = command_seq[2]
#                 ban_reason = ' '.join(command_seq[3:])
#                 try:
#                     if get_user_info(target_id).group != 'm_admin':
#                         ban_user(message.from_user.id, target_id, ban_reason, ban_term)
#                         simple_send_message(
#                             message.chat.id,
#                             f'Пользователь с ID {target_id} забанен на {ban_term} по причине'
#                             f' "{ban_reason}"'
#                         )
#                     else:
#                         simple_send_message(
#                             message.chat.id,
#                             f'Забанить главного администратора нельзя!'
#                         )
#                 except IndexError:
#                     simple_send_message(
#                         message.chat.id,
#                         f'Пользователя с таким ID не существует!'
#                     )
#             else:
#                 simple_send_message(message.chat.id, 'Некорректный срок бана!')
#         else:
#             simple_send_message(message.chat.id, 'ID должен быть числом!')
#     elif len(command_seq) == 2:
#         pass
#
#
# @message_group_wrapper(('admin', 'm_admin'))
# @message_wrapper
# def unban_handler(message: types.Message):
#     """/unban handler"""
#     command_seq = message.text.split()
#     if len(command_seq) == 1:
#         msg_text = '/unban - отправляет это сообщение с помощью\n' \
#                    '/unban {id} {optional: reason} - разбанивает пользователя с {id}' \
#                    '/ban - вывод сообщения с помощью по бану'
#         simple_send_message(message.chat.id, msg_text)
#     elif len(command_seq) >= 2:
#         if command_seq[1].isdigit():
#             reason = None
#             if len(command_seq) >= 3:
#                 reason = ' '.join(command_seq[3:])
#             unban_user(message.from_user.id, int(command_seq[1]), reason)
#             simple_send_message(message.chat.id, 'Пользователь успешно разбанен!')
#         else:
#             simple_send_message(message.chat.id, 'ID должен состоять только из цифр')
#
#
# @message_group_wrapper(('admin', 'm_admin'))
# @message_wrapper
# def broadcast_handler(message: types.Message):
#     """"/broadcast handler"""
#     command_seq = message.text.split()
#     if len(command_seq) > 1:
#         await send_broadcast(' '.join(command_seq[1:]))
#     await message.answer('/broadcast {text}')
#
#
# @message_group_wrapper(('editor', 'admin', 'm_admin'))
# @message_wrapper
# def editor_handler(message: types.Message):
#     """/quiz or /editor handler"""
#     message_tuple = tuple(message.text.split())
#     if len(message_tuple) == 1:
#         msg_text = '/quiz - отправляет меню редактора\n' \
#                    '/quiz {id} - отправляет результаты опроса\n' \
#                    '/quiz list - отправляет список 10 последних добавленных опросов\n' \
#                    '/quiz vis {id} {status} - установить {status} видимости для опроса с {id}'
#         simple_send_message(message.chat.id, msg_text, get_editor_inline_markup())
#     elif message_tuple[1] in ('list', ):
#         ans = quiz_list_prepare(message_tuple)
#         simple_send_message(message.chat.id, ans, get_welcome_markup())
#     elif message_tuple[1] in ('vis', ):
#         if message_tuple[2].isdigit():
#             if message_tuple[3] in ('True', 'False'):
#                 ans = update_quiz_status(
#                     message_tuple[2],
#                     message.chat.id,
#                     message_tuple[3]
#                 )
#             else:
#                 ans = 'Статус должен быть True или False!'
#         else:
#             ans = 'ID должен быть числом!'
#         simple_send_message(message.chat.id, ans)
#     elif message_tuple[1].isdigit():
#         # analytical message
#         analytical_message = get_analytical_message(int(message_tuple[1]))
#         file_name_a = 'temp_analytic.txt'
#         with open(file_name_a, 'w', encoding='utf-8') as opened_file:
#             opened_file.write(analytical_message)
#         with open(file_name_a, 'rb') as opened_file:
#             tg_bot = BotInstanceContainer().bot
#             await tg_bot.send_document(message.chat.id, opened_file)
#         # json
#         quiz_json = json.dumps(
#             get_quiz_answers(int(message_tuple[1])), ensure_ascii=False
#         )
#         file_name_j = 'temp_json.json'
#         with open(file_name_j, 'w', encoding='utf-8') as opened_file:
#             opened_file.write(quiz_json)
#         tg_bot.send_document(message.chat.id, open(file_name_j, 'rb'))
#         # xlsx-table
#         json_to_write = pandas.read_json(quiz_json)
#         file_name_t = 'temp_table.xlsx'
#         json_to_write.to_excel(file_name_t)
#         tg_bot.send_document(message.chat.id, open(file_name_t, 'rb'))
#
#
# @message_group_wrapper(('user', 'editor', 'admin', 'm_admin'))
# @message_wrapper
# def main_message_handler(message: types.Message):
#     """Message handler for all users"""
#     if message.text in ('Пройти опрос', 'пройти опрос', 'Ghjqnb jghjc', 'ghjqnb jghjc'):
#         available_quiz_list = get_quiz_list(visible=True)
#         completed_quizzes_id = get_completed_quizzes_id(message.from_user.id)
#         quizzes_menu = get_available_quiz_inline_markup(available_quiz_list, completed_quizzes_id)
#         if quizzes_menu.keyboard:
#             text_to_send = 'Вам доступны следующие опросы:'
#             menu_to_send = quizzes_menu
#         else:
#             text_to_send = 'Кажется, для Вас сейчас опросов нет!'
#             menu_to_send = get_welcome_markup()
#
#         simple_send_message(
#             message.chat.id,
#             text_to_send,
#             menu_to_send
#         )
#     elif message.text == 'Изменить ответы в последнем опросе':
#         completed_quizzes_id = get_completed_quizzes_id(message.from_user.id)
#         if completed_quizzes_id:
#             last_quiz_id = max(completed_quizzes_id)
#             quiz_r_menu = InlineKeyboardMarkup()
#             answers = get_list_of_questions_in_quiz(last_quiz_id)
#             for _ in answers:
#                 if _.quest_relation:
#                     quiz_r_menu.add(
#                         InlineKeyboardButton(
#                             text=f'Если на вопрос {_.quest_relation.split(" -> ")[0]} ответ'
#                                  f' "{_.quest_relation.split(" -> ")[1]}": {_.quest_text}',
#                             callback_data=f'quiz_rewrite {_.quiz_id} {_.quest_id}'
#                         )
#                     )
#                 else:
#                     quiz_r_menu.add(
#                         InlineKeyboardButton(
#                             text=f'{_.quest_text}',
#                             callback_data=f'quiz_rewrite {_.quiz_id} {_.quest_id}'
#                         )
#                     )
#             simple_send_message(
#                 message.chat.id,
#                 'Выберите вопрос, ответ на который вы хотели бы изменить\n\nИзменять ответы на'
#                 ' вопросы, зависящие от других вопросов, нужно в ручном режиме',
#                 quiz_r_menu
#             )
#         else:
#             simple_send_message(message.chat.id, 'У Вас ещё нет пройденных опросов!')
#     elif message.text == 'Настройки рассылки':
#         current_mailing_status = get_current_mailing_status(message.from_user.id)
#         mailing_menu = InlineKeyboardMarkup()
#         mailing_menu.add(InlineKeyboardButton(
#             'Изменить статус', callback_data=f'mailing {not current_mailing_status}')
#         )
#         simple_send_message(
#             message.chat.id,
#             f'Рассылка позволит вам получать уведомления о новых опросах и сообщения от'
#             f' администраторов.\n\nТекущий статус:'
#             f' {"разрешена" if current_mailing_status else "запрещена"}',
#             mailing_menu
#         )
#     elif message.text == 'Мой статус':
#         user = get_user_info(message.from_user.id)
#         group_dict = {
#             'ban': 'забанен',
#             'user': 'пользователь',
#             'editor': 'редактор',
#             'admin': 'администратор',
#             'm_admin': 'главный администратор'
#         }
#         simple_send_message(
#             message.chat.id,
#             f'ID: {user.tg_user_id}\n'
#             f'Внутренний ID: {user.internal_user_id}\n'
#             f'Роль: {group_dict[user.group]}\n'
#             f'Рассылка: {"включена" if user.mailing else "отключена"}'
#         )
#
#
# @callback_wrapper
# def callback_inline(call: types.CallbackQuery):
#     """Callback-data handler"""
#
#     if call.data == 'list':
#         ans = quiz_list_prepare((0, 0))
#         simple_send_message(call.message.chat.id, ans, None)
#     elif call.data == 'visible_list':
#         ans = quiz_list_prepare((0, 0, 0))
#         simple_send_message(call.message.chat.id, ans, None)
#     elif call.data == 'get_a_project':
#         simple_send_message(call.message.chat.id, 'Вы можете связаться с моим создателем через'
#                                                   ' его e-mail: vladchesyan@gmail.com\n\n'
#                                                   'Некоммерческое использование бесплатно!')
#     elif call.data in ('help', 'bug_find'):
#         subs_id = call.from_user.id
#         subs_name = call.from_user.username
#         admins_ids = get_users_id('m_admin') + get_users_id('admin')
#         if call.data == 'bug_find':
#             msg_txt = f'Пользователь @{subs_name} с ID {subs_id} нашёл баг!'
#         else:
#             msg_txt = f'Пользователь @{subs_name} с ID {subs_id} просит о помощи!'
#         # mailing(admins_ids, msg_txt)
#         simple_send_message(call.message.chat.id, 'Передал администраторам. С Вами скоро свяжутся!')
#     elif call.data.split()[0] == 'start_quiz':
#         update_user_quiz_status(call.from_user.id, f'{call.data.split()[1]} 1')
#         send_question(call.from_user.id, call.message.chat.id)
#     elif call.data.split()[0] == 'quiz_rewrite':
#         update_user_quiz_status(
#             call.from_user.id,
#             f'{call.data.split()[1]} {call.data.split()[2]} r'
#         )
#         send_question(call.from_user.id, call.message.chat.id)
#     elif call.data.split()[0] == 'mailing':
#         update_mailing_status(call.from_user.id, eval(call.data.split()[1]))
#         simple_send_message(
#             call.message.chat.id,
#             'Статус рассылки успешно изменён!',
#             get_welcome_markup()
#         )
#
#
# @document_wrapper
# @message_group_wrapper(('editor', 'admin', 'm_admin'))
# def document_handler(message: types.Message):
#     """Document handler (only for add-quiz functions)"""
#
#     file_extension = message.document.file_name.split('.')[-1]
#
#     if file_extension == 'txt':
#         file_name = message.document.file_name
#         file_id = message.document.file_id
#         dir_check()
#         tg_bot = BotInstanceContainer().bot
#         answer = download_new_raw_quiz(tg_bot, file_name, file_id)
#         simple_send_message(message.chat.id, answer[0], None)
#         if answer[1]:
#             answer_msg = new_quiz_handler(file_name, message.from_user.id)
#             simple_send_message(message.chat.id, answer_msg, None)


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


@log
async def command__(message: aio_types.Message):
    logger.debug(
        f'Unknown message from user @{message.from_user.username}, chat {message.chat.id}, text: {message.text}'
    )
    await message.reply('Я не знаю такой команды :(', reply_markup=menu_keyboard())


def register_user_handlers(dp: Dispatcher):

    # general users commands
    dp.register_message_handler(command_help, commands=('help', 'h'))
    dp.register_message_handler(command_help, FilterText(('Помощь', 'помощь')))
    dp.register_message_handler(command_settings, commands=('settings',))
    dp.register_message_handler(command_settings, FilterText(('Настройки', 'настройки')))

    dp.register_message_handler(command_start, commands=('start',))

    # advanced users commands
    dp.register_message_handler(command_selfop, commands=('selfop',))
    dp.register_message_handler(command_admin, commands=('admin',))

    # m_admin commands
    dp.register_message_handler(command_check, commands=('check',))
    dp.register_message_handler(command_reboot, commands=('reboot',))

    # admin commands
    dp.register_message_handler(command_adminhelp, commands=('adminhelp',))
    dp.register_message_handler(command_op, commands=('op',))
    dp.register_message_handler(command_deop, commands=('deop',))
    dp.register_message_handler(command_user, commands=('user',))
    dp.register_message_handler(command_ban, commands=('ban',))
    dp.register_message_handler(command_unban, commands=('unban',))
    dp.register_message_handler(command_broadcast, commands=('broadcast',))

    # other
    dp.register_message_handler(command__)
