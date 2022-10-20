from aiogram import Dispatcher

from handlers.admin import register_admin_handlers
from handlers.user import register_user_handlers
from handlers.other import register_other_handlers
from handlers.documents import register_documents_handlers
from handlers.callback import register_callback_handlers


def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_user_handlers,
        register_admin_handlers,
        register_other_handlers,
        register_documents_handlers,
        register_callback_handlers,
    )
    for handler in handlers:
        handler(dp)
