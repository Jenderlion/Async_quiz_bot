from database.main import User
from database.main import Ban
from database.main import DataBaseEngine
from sqlalchemy.orm import Session
from sqlalchemy.engine.base import Engine as ConnectedEngine
from sqlalchemy.orm.session import Session as ConnectedSession
from sqlalchemy.orm.query import Query as ConnectedQuery


def update_user_info(__tg_id: str | int, __update_dict: dict) -> int:
    """
    Update user info

    Only for related use

    :param engine: instance of sqlalchemy.engine.base.Engine
    :param __tg_id: user telegram id
    :param __update_dict: values to update
    :return: count of updated users (normal value is 1)
    """

    __engine = DataBaseEngine().engine

    with Session(__engine) as __session:
        __session: ConnectedSession
        __query: ConnectedQuery = __session.query(User).filter(User.tg_user_id == __tg_id)
        __update_count = __query.update(__update_dict)
        __session.commit()
    return __update_count


def update_ban_info(__tg_id: str | int, __update_dict: dict) -> int:
    """
    Update user info

    Only for related use

    :param engine: instance of sqlalchemy.engine.base.Engine
    :param __tg_id: user telegram id
    :param __update_dict: values to update
    :return: count of updated users (normal value is 1)
    """

    __engine = DataBaseEngine().engine

    with Session(__engine) as __session:
        __session: ConnectedSession
        __query: ConnectedQuery = __session.query(Ban).filter(Ban.tg_id == __tg_id)
        __update_count = __query.update(__update_dict)
        __session.commit()
    return __update_count
