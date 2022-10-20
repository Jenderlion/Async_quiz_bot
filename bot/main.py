"""
Wunder Digital Bot.
Implemented functionality:
- updating invalid tokens

Webhook-server in development!!!
Start this script only through start.sh or start.cmd
"""


import logging
import os

from aiogram.utils import executor
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.executor import start_webhook

from filters import register_all_filters
from handlers import register_all_handlers
from database import create_engine

from misc.util import load_local_vars
from misc.util import create_logger
from misc.util import get_console_args
from misc.custom_types import Path
from misc.custom_types import BotInstanceContainer
from database.methods.select import get_expired_bans
from database.methods.other import unban_user

from apscheduler.schedulers.asyncio import AsyncIOScheduler


# globals
manual_debug = False

console_args = get_console_args()
if console_args.verbose:
    logger_level = 0
else:
    logger_level = 30
if manual_debug:
    logger_level = 0
    pass

logger, path = create_logger(__file__, logger_name='Quiz Bot', logger_level=logger_level)
logger: logging.Logger
path: Path

load_local_vars(path)
tg_bot = Bot(token=os.environ.get("bot_token"), parse_mode='HTML')
BotInstanceContainer(tg_bot)  # save Bot instance in data-class
dp = Dispatcher(tg_bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
__host = os.environ['local_bot_host']  # for webhook
__port = os.environ['local_bot_port']  # for webhook


# bot funcs
async def __on_start_up(disp: Dispatcher) -> None:
    register_all_filters(dp)
    register_all_handlers(dp)

    create_engine()
    schedule()


async def __on_shut_down(disp: Dispatcher) -> None:
    pass


async def auto_unban():
    """Separate thread for automated user unbanning"""
    active_ban_list = get_expired_bans()
    for ban in active_ban_list:
        __count = unban_user(ban.tg_id)
        if __count == 1:
            await tg_bot.send_message(
                ban.tg_id,
                'Срок Вашего бана истёк, вы можете продолжить пользоваться ботом. Пожалуйста, больше не нарушайте'
                ' правила.'
            )
            logger.debug(f'User {ban.tg_id} was automatically unbanned!')
        else:
            logger.error(f'Error while unbanning {ban}')


def schedule() -> None:
    """Schedule create"""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(auto_unban, 'interval', seconds=60, )
    scheduler.start()


if __name__ == '__main__':

    if console_args.webhook:
        print('IN DEVELOPMENT!!!')
        start_webhook(
            dispatcher=dp,
            webhook_path='/bot/gum',
            on_startup=__on_start_up,
            on_shutdown=__on_shut_down,
            skip_updates=True,
            host=__host,
            port=__port,
        )
    else:
        logger.warning('Bot start in Long polling mode.')
        executor.start_polling(dp, skip_updates=True, on_startup=__on_start_up, on_shutdown=__on_shut_down)
