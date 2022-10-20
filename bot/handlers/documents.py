import logging

from aiogram import Dispatcher
from aiogram import types as aio_types
from misc.decorators import *
from misc.text_utils import convert_text_to_bot_format
from database.methods.insert import add_quiz
from misc.custom_types import Path
from misc.custom_types import BotInstanceContainer
from misc.custom_types import PreparedQuiz


logger = logging.getLogger('Quiz Bot')


@documents_group_wrapper(('m_admin', 'admin', 'editor'))
async def documents_editor(*args, ** kwargs):
    message: aio_types.Message = args[0]
    document: aio_types.document.Document = message.document
    if document.file_name.split('.')[-1] != 'txt':
        await message.reply('Файл для составления опроса должен быть в формате .txt')
        return None
    root_path = Path.get_root_path()
    if 'downloads' not in os.listdir(str(root_path)):
        os.mkdir(str(root_path + 'downloads'))
    downloads_path = root_path + 'downloads'
    file_path = downloads_path + document.file_name
    tg_bot = BotInstanceContainer().bot
    file_size_limit = 128
    if document.file_name in os.listdir(str(downloads_path)):
        await message.reply(f'Файл с таким названием уже существует. Переименуйте его и повторите попытку')
        return None
    if document.file_size / 1024 <= file_size_limit:
        await tg_bot.download_file_by_id(document.file_id, str(file_path))
    else:
        await message.reply(
            f'Файл слишком большой. Его вес составляет {document.file_size / 1024} КБ (лимит {file_size_limit} КБ)'
        )
        return None
    await message.answer('Начинаю составление опроса...')
    try:
        __quiz = PreparedQuiz(file_path)
    except UnicodeEncodeError:
        await message.reply('Ошибка кодировки! Файл должен быть в кодировке UTF-8 или CP1251!')
        return None
    except ValueError as exc:
        await message.reply(f'При обработке возникла ошибка:\n\n{exc}')
        return None
    except Exception as exc:
        print(traceback.format_exc())
        answer_text = f'Exception!\n{type(exc)}\n{exc}'
        await message.reply(convert_text_to_bot_format(answer_text))
        return None

    await message.answer('Опрос прошёл проверку и первичную обработку, добавляю его в базу данных...')

    _quiz, _questions = add_quiz(__quiz)
    answer_text = [
        f'Добавлен опрос "{_quiz.quiz_name}" (id {_quiz.quiz_id})'
        f' (статус: {"видимый" if _quiz.quiz_status == 1 else "скрыт"})\n'
        f'Всего вопросов: {len(_questions)}'
    ]
    for _question in _questions:
        answer_text.append(f'Вопрос {_question.quest_id}: {_question.quest_text}\nОтветы: {_question.quest_ans}')

    answer_text = '\n\n'.join(answer_text)
    logger.debug(f'Add new Quiz "{_quiz.quiz_name}" from {message.from_id}')
    await message.answer(answer_text)


def register_documents_handlers(dp: Dispatcher) -> None:

    dp.register_message_handler(documents_editor, content_types=('document',))
