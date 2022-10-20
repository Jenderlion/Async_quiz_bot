import logging
import pandas

from aiogram import Dispatcher
from misc.decorators import *
from misc.custom_types import BotInstanceContainer
from misc.custom_types import Path
from database.methods.select import get_users
from database.methods.select import get_analytical_message
from database.methods.select import get_users_answers_dict
from database.methods.update import update_user_info
from database.methods.update import update_quiz_info
from database.methods.other import run_quiz
from misc.text_utils import convert_text_to_bot_format
from keyboards.inline import inline_markup_credentials
from keyboards.reply import run_quiz_keyboard


logger = logging.getLogger('Quiz Bot')


@callback_wrapper
async def callback_settings(*args, **kwargs):
    callback: types.CallbackQuery = args[0]
    bot_message: types.Message = callback.message
    callback_tuple = callback.data.split()

    match callback_tuple[1]:
        case 'mailing':
            update_user_info(
                callback.from_user.id,
                {
                    'mailing': True if callback_tuple[2] == '1' else False,
                }
            )
        case 'quizend':
            update_user_info(
                callback.from_user.id,
                {
                    'quiz_status': None,
                }
            )
        case 'cancel':
            pass
        case _:
            await bot_message.answer('Если Вы пытаетесь подменить данные, пожалуйста, не делайте этого.')


@callback_wrapper
async def callback_help(*args, **kwargs):
    callback: types.CallbackQuery = args[0]
    bot_message: types.Message = callback.message
    callback_tuple = callback.data.split()
    tg_bot = BotInstanceContainer().bot

    match callback_tuple[1]:
        case 'request':
            admins = get_users(user_group='admin')
            main_admins = get_users(user_group='m_admin')
            for admin in admins + main_admins:
                try:
                    await tg_bot.send_message(
                        admin.tg_user_id,
                        f'User @{callback.from_user.username} ({callback.from_user.id}) asking for help',
                        reply_markup=inline_markup_credentials(callback.from_user.id)
                    )
                except Exception as exc:
                    logger.error(f'Error while admin mailing: {exc} \\ {type(exc)}')
        case 'credentials':
            __user = callback_tuple[2]
            admins = get_users(user_group='admin')
            main_admins = get_users(user_group='m_admin')
            try:
                await tg_bot.send_message(
                    __user, f'Администратор @{callback.from_user.username} просит Вас связаться с ним.'
                )
                for admin in admins + main_admins:
                    try:
                        await tg_bot.send_message(
                            admin.tg_user_id,
                            f'Admin @{callback.from_user.username} ({callback.from_user.id}) replied to {__user}',
                        )
                    except Exception as exc:
                        logger.error(f'Error while admin mailing: {exc} \\ {type(exc)}')
            except Exception as exc:
                answer_text = convert_text_to_bot_format(f'Unable to send message!\n{exc}\n{type(exc)}')
                await tg_bot.send_message(callback.from_user.id, answer_text)
        case 'bot':
            await tg_bot.send_message(449808966, f'User @{callback.from_user.username} ({callback.from_user.id})'
                                                 f' wants the same bot!')
        case _:
            await bot_message.answer('Если Вы пытаетесь подменить данные, пожалуйста, не делайте этого.')


@callback_wrapper
@callback_group_wrapper(('m_admin', 'admin', 'editor'))
async def callback_quizinfo(*args, ** kwargs):
    callback: types.CallbackQuery = args[0]
    bot_message: types.Message = callback.message
    callback_tuple = callback.data.split()
    tg_bot = BotInstanceContainer().bot
    if len(callback_tuple) > 1:
        match callback_tuple[1]:

            case 'status':
                quiz_id = callback_tuple[2]
                new_quiz_status = True if callback_tuple[3] == '1' else False
                __count = update_quiz_info(quiz_id, {'quiz_status': new_quiz_status})
                if __count == 1:
                    await bot_message.answer(
                        f'Опрос с ID {quiz_id} успешно обновлён!'
                    )
                else:
                    await bot_message.answer(
                        f'Произошла ошибка во время обновления статуса. Число обновлённых опросов: {__count}'
                    )
                return None

            case 'analytics':
                analyst_id = callback.from_user.id
                quiz_id = callback_tuple[2]
                root_path = Path.get_root_path()
                if 'temp' not in os.listdir(str(root_path)):
                    os.mkdir(str(root_path + 'temp'))
                downloads_path = root_path + 'temp'
                txt_file_name = str(downloads_path + f'temp_{quiz_id}_{callback.from_user.id}.txt')
                json_file_name = str(downloads_path + f'temp_{quiz_id}_{callback.from_user.id}.json')
                xlsx_file_name = str(downloads_path + f'temp_{quiz_id}_{callback.from_user.id}.xlsx')

                analytical_message = get_analytical_message(quiz_id)
                if analytical_message is None:
                    await bot_message.answer('На этот опрос ещё никто не отвечал!')
                    return None

                # txt
                with open(txt_file_name, 'w', encoding='utf-8') as opened_file:
                    opened_file.write(analytical_message)

                # json
                quiz_json = json.dumps(
                    get_users_answers_dict(quiz_id), indent=4, ensure_ascii=False
                )

                with open(json_file_name, 'w', encoding='utf-8') as opened_file:
                    opened_file.write(quiz_json)

                # xlsx-table
                json_to_write = pandas.read_json(quiz_json)
                json_to_write.to_excel(xlsx_file_name)

                for file_name in (txt_file_name, json_file_name, xlsx_file_name):
                    with open(file_name, 'rb') as opened_file:
                        await tg_bot.send_document(analyst_id, opened_file)

                logger.debug(f'Send analytics to {callback.from_user.id}')
                return None
            case 'cancel':
                return None
    await bot_message.answer('Если Вы пытаетесь подменить данные, пожалуйста, не делайте этого.')


@callback_wrapper
@callback_group_wrapper(('m_admin', 'admin', 'editor', 'user'))
async def callback_quiz(*args, ** kwargs):
    callback: types.CallbackQuery = args[0]
    bot_message: types.Message = callback.message
    callback_tuple = callback.data.split()
    tg_bot = BotInstanceContainer().bot
    match callback_tuple[1]:
        case 'start':
            user_id = callback.from_user.id
            quiz_id = callback_tuple[2]
            answer = run_quiz(user_id, quiz_id)
            user = get_user(user_id)
            if user.quiz_status.split(' -> ')[1] == '0':
                markup = run_quiz_keyboard()
            else:
                markup = None
            await bot_message.answer(answer, reply_markup=markup)
            return None
        case 'cancel':
            return None
    await callback.answer('Если Вы пытаетесь подменить данные, пожалуйста, не делайте этого.')


@callback_wrapper
async def callback__(*args, ** kwargs):
    callback: types.CallbackQuery = args[0]
    tg_bot = BotInstanceContainer().bot
    message_text = f'Unknown Callback Query!\n{callback}'
    message_text = message_text.replace('<', '«').replace('>', '»')
    message_text = f'<code>{message_text}</code>'
    main_admins = get_users(user_group='m_admin')
    logger.error(
        f'Unknown callback from @{callback.from_user.username} ({callback.from_user.id}), data: {callback.data}'
    )
    for main_admin in main_admins:
        try:
            await tg_bot.send_message(chat_id=main_admin.tg_user_id, text=message_text)
        except Exception as exc:
            logger.error(f'Error while m_admin mailing: {exc} \\ {type(exc)}')


def register_callback_handlers(dp: Dispatcher) -> None:

    dp.register_callback_query_handler(callback_settings, lambda c: c.data.split()[0] == 'settings')
    dp.register_callback_query_handler(callback_help, lambda c: c.data.split()[0] == 'help')
    dp.register_callback_query_handler(callback_quizinfo, lambda c: c.data.split()[0] == 'quizinfo')
    dp.register_callback_query_handler(callback_quiz, lambda c: c.data.split()[0] == 'quiz')

    dp.register_callback_query_handler(callback__, lambda c: True)
