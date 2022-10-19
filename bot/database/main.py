import logging
import os
import sqlalchemy

from sqlalchemy import *
from sqlalchemy.orm import declarative_base


# create base table
Base = declarative_base()


# database engine class
class DataBaseEngine:
    """Saves engine"""
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        if 'engine' not in self.__dict__:
            self.engine, self.meta = connect_db()

    def __repr__(self):
        return f'<DB Engine>, {self.engine}'

    def create_tables(self):
        self.meta.create_all(self.engine)


# tables
class User(Base):
    """Create table 'user'"""
    __tablename__ = 'user'
    internal_user_id = Column(INTEGER, primary_key=True)  # only internal user_id
    tg_user_id = Column(INTEGER, unique=True)  # tg id
    quiz_status = Column(VARCHAR(12), nullable=True)  # current quiz id (0 - no current quiz)
    is_ban = Column(BOOLEAN, default=0)  # ban status where 0 - unbanned and 1 - banned
    group = Column(VARCHAR(30), default='user')  # group in (m_admin, admin, editor or user)
    mailing = Column(BOOLEAN, default=1)  # mailing status where 0 - disable and 1 - enable

    def __repr__(self):
        return f'<User> Internal ID: {self.internal_user_id}, Telegram ID: {self.tg_user_id}, Is ban: {self.is_ban},' \
               f' Group: {self.group}, Mailing: {self.mailing}'


class MessageLog(Base):
    """Create table 'message_log'"""
    __tablename__ = 'message_log'
    internal_msg_id = Column(INTEGER, primary_key=True)  # only internal msg_id
    tg_user_id = Column(INTEGER, ForeignKey('user.tg_user_id'))  # tg sender id
    msg_tg_id = Column(INTEGER)  # message id in chat
    msg_text = Column(TEXT)  # text from message
    msg_timestamp = Column(TIMESTAMP)  # seconds since the epoch

    def __repr__(self):
        return f'<MessageLog> Internal ID: {self.internal_msg_id} from {self.tg_user_id} in {self.msg_timestamp}'


class Quiz(Base):
    """Create table 'quiz_list'"""
    __tablename__ = 'quiz_list'
    quiz_id = Column(INTEGER, primary_key=True)  # quiz_id
    quiz_name = Column(VARCHAR(128))  # full quiz name
    quiz_title = Column(TEXT)  # quiz title
    quiz_status = Column(BOOLEAN, default=0)  # current status in 0 - hide, 1 - show
    quiz_gratitude = Column(VARCHAR(512))

    def __repr__(self):
        return f'<Quiz> {self.quiz_id} {self.quiz_title}, status {self.quiz_status}'


class QuizQuestion(Base):
    """Create table 'quiz_questions'"""
    __tablename__ = 'quiz_questions'
    quiz_id = Column(INTEGER, ForeignKey('quiz_list.quiz_id'))  # quiz_id
    quest_id = Column(INTEGER)  # quest_id (unique only within the quiz)
    internal_quest_id = Column(INTEGER, primary_key=True)  # fully unique id
    quest_relation = Column(VARCHAR(50), nullable=True)  # This question will only be asked if the
    # correct answer to another question has been received
    quest_text = Column(TEXT)  # question text
    quest_ans = Column(TEXT)  # answer options or marker for self-written input

    def __repr__(self):
        return f'<QuizQuestion> {self.quest_id} in {self.quiz_id}, unique {self.internal_quest_id}'


class QuestionAnswer(Base):
    """Create table 'questions_answers'"""
    __tablename__ = 'questions_answers'
    quiz_id = Column(INTEGER, ForeignKey('quiz_list.quiz_id'))  # quiz_id
    quest_id = Column(INTEGER)  # quest_id
    internal_user_id = Column(INTEGER, ForeignKey('user.internal_user_id'))  # internal user id
    answer = Column(TEXT)  # text of user answer
    internal_ans_id = Column(INTEGER, primary_key=True)  # internal unique answer id


class Log(Base):
    """Create table 'logs'"""
    __tablename__ = 'logs'
    event_id = Column(INTEGER, primary_key=True)  # internal event id
    event_msg = Column(TEXT)  # info-message such as "added new user with {params}"
    event_initiator = Column(VARCHAR(20))  # initiator such as {internal_user_id} or 'system'
    event_timestamp = Column(TIMESTAMP)  # seconds since the epoch


class Ban(Base):
    """Create table 'ban_list'"""
    __tablename__ = 'ban_list'
    internal_ban_id = Column(INTEGER, primary_key=True)  # internal ban id
    initiator_tg_id = Column(INTEGER, ForeignKey('user.tg_user_id'))  # user-initiator id
    tg_id = Column(INTEGER, ForeignKey('user.tg_user_id'))  # tg user id
    reason = Column(VARCHAR(128))  # ban reason
    ban_time = Column(TIMESTAMP)  # ban time in seconds since the epoch
    unban_time = Column(TIMESTAMP)  # unban time in seconds since the epoch
    current_status = Column(BOOLEAN, default=True)

    def __repr__(self):
        return f'<Ban> {self.internal_ban_id}: from {self.ban_time} to {self.unban_time}, from {self.initiator_tg_id}' \
               f' to {self.tg_id}, reason "{self.reason}"'


def connect_db(logger: logging.Logger = None):

    # get base logger
    if logger is None:
        logger = logging.getLogger('Digital Bot')
        if len(logger.handlers) == 0:  # if std handler not added
            std_out_handler = logging.StreamHandler()
            std_out_handler.setLevel(30)  # set stdout-handler level
            logger.addHandler(std_out_handler)

    echo_mode = os.environ.get('echo_mode')
    if echo_mode is None:
        echo_mode = False

    # create DB
    logger.debug('Creating DB engine...')
    connect_string = "sqlite:///quiz_db.sqlite"
    db_engine = sqlalchemy.create_engine(connect_string, echo=eval(echo_mode))
    meta = sqlalchemy.MetaData()
    Base.metadata.create_all(db_engine)
    logger.debug('Connected to DB.')
    return db_engine, meta


def create_engine():
    # saves engine
    DataBaseEngine()
