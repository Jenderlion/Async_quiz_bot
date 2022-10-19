"""
Database control module. Part "INSERT"
"""
import datetime
import logging

from database.main import *
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import Session as ConnectedSession
from sqlalchemy.exc import IntegrityError
from aiogram.types import Message

logger = logging.getLogger('Quiz Bot')


def add_user(message: Message) -> User:
    """
    Use to insert new user.

    The data is retrieved from the message.

    :param message: message from user
    :return: user
    """

    __engine = DataBaseEngine().engine

    try:
        with Session(__engine) as __session:
            __session: ConnectedSession
            __id = message.from_id
            __new_user = User(
                tg_user_id=__id
            )
            __session.add(__new_user)
            __session.flush()
            __session.expunge_all()
            __session.commit()
        return __new_user
    except IntegrityError:
        pass


def add_message_log(message: Message) -> MessageLog:

    __engine = DataBaseEngine().engine

    try:
        with Session(__engine) as __session:
            __session: ConnectedSession
            __id = message.from_id
            __new_message_log = MessageLog(
                tg_user_id=message.from_id,
                msg_tg_id=message.message_id,
                msg_text=message.text,
                msg_timestamp=message.date.timestamp()
            )
            __session.add(__new_message_log)
            __session.flush()
            __session.expunge_all()
            __session.commit()
        return __new_message_log
    except IntegrityError:
        pass


def __add_quiz(): ...


def __add_quiz_question(): ...


def add_quiz(): ...


def add_answer(): ...


def add_log(): ...


def add_ban(initiator_id: int | str, user: User, term: int, reason: str) -> Ban:

    __engine = DataBaseEngine().engine

    try:
        with Session(__engine) as __session:
            __session: ConnectedSession
            __ban = Ban(
                initiator_tg_id=initiator_id,
                tg_id=user.tg_user_id,
                reason=reason,
                ban_time=datetime.datetime.now(),
                unban_time=datetime.datetime.now() + datetime.timedelta(seconds=term)
            )
            __session.add(__ban)
            __session.flush()
            __session.expunge_all()
            __session.commit()
        return __ban
    except IntegrityError:
        pass
