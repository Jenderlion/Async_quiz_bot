from database.main import User
from database.methods.update import update_user_info
from database.methods.update import update_ban_info
from database.methods.insert import add_ban


def ban_user(initiator_id: int | str, user: User, term: int, reason: str) -> int:
    add_ban(initiator_id, user, term, reason)
    __count = update_user_info(user.tg_user_id, {'group': 'banned', 'is_ban': True})
    return __count


def unban_user(tg_id: int | str) -> int:
    __count = update_user_info(tg_id, {'group': 'user', 'is_ban': False})
    update_ban_info(tg_id, {'current_status': False})
    return __count
