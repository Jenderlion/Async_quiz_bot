"""
Database control module. Part "SELECT"
"""
import datetime

from database.main import *
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from sqlalchemy.orm.session import Session as ConnectedSession
from sqlalchemy.sql.selectable import Select as ConnectedSelect
from sqlalchemy.engine.result import ScalarResult


def get_user(__tg_id: str | int) -> User | None:
    """
    Select user.

    Return user with passed ID.

    :param __tg_id: user telegram id
    :return: user
    """

    __engine = DataBaseEngine().engine

    with Session(__engine) as __session:
        __session: ConnectedSession
        statement: ConnectedSelect = (select(User).where(User.tg_user_id == __tg_id))
        res: ScalarResult = __session.scalars(statement)
        result_list: list = res.all()
        __session.expunge_all()
        __session.commit()
    if len(result_list) == 1:
        return result_list[0]


def get_users(mailing_status: bool = None, user_group: str = None) -> list[User, ...]:
    """Return list with all data-lines"""

    __engine = DataBaseEngine().engine

    with Session(__engine) as __session:
        __session: ConnectedSession
        statement: ConnectedSelect = select(User)
        if mailing_status is not None:
            statement = statement.where(User.mailing == mailing_status)
        if user_group is not None:
            statement = statement.where(User.group == user_group)
        res: ScalarResult = __session.scalars(statement)
        __session.flush()
        result = res.all()
        __session.expunge_all()
        __session.commit()
    return result


def get_last_user_messages(__tg_id: str | int) -> MessageLog:

    __engine = DataBaseEngine().engine

    with Session(__engine) as __session:
        __session: ConnectedSession
        statement: ConnectedSelect = select(MessageLog).where(MessageLog.tg_user_id == __tg_id)
        res: ScalarResult = __session.scalars(statement)
        __session.flush()
        result = res.all()[-1]
        __session.expunge_all()
        __session.commit()
    return result


def get_quiz(__quiz_id: str | int) -> Quiz:

    __engine = DataBaseEngine().engine

    with Session(__engine) as __session:
        __session: ConnectedSession
        statement: ConnectedSelect = select(Quiz).where(Quiz.quiz_id == __quiz_id)
        res: ScalarResult = __session.scalars(statement)
        __session.flush()
        result = res.all()[0]
        __session.expunge_all()
        __session.commit()
    return result


def get_quiz_questions(__quiz_id: str | int) -> list[QuizQuestion]:

    __engine = DataBaseEngine().engine

    with Session(__engine) as __session:
        __session: ConnectedSession
        statement: ConnectedSelect = select(QuizQuestion).where(QuizQuestion.quiz_id == __quiz_id)
        res: ScalarResult = __session.scalars(statement)
        __session.flush()
        result = res.all()
        __session.expunge_all()
        __session.commit()
    return result


def get_bans(__tg_id: str | int) -> list[Ban]:

    __engine = DataBaseEngine().engine

    with Session(__engine) as __session:
        __session: ConnectedSession
        statement: ConnectedSelect = select(Ban).where(Ban.tg_id == __tg_id)
        res: ScalarResult = __session.scalars(statement)
        __session.flush()
        result = res.all()
        __session.expunge_all()
        __session.commit()
    return result


def get_expired_bans() -> list[Ban]:

    __engine = DataBaseEngine().engine

    with Session(__engine) as __session:
        __session: ConnectedSession
        statement: ConnectedSelect = select(Ban)\
            .where(Ban.current_status == True).where(Ban.unban_time <= datetime.datetime.now())
        res: ScalarResult = __session.scalars(statement)
        __session.flush()
        result = res.all()
        __session.expunge_all()
        __session.commit()
    return result
