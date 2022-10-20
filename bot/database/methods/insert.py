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
from misc.custom_types import PreparedQuiz
from misc.custom_types import PreparedQuestion

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


def __add_quiz(quiz: PreparedQuiz):

    __engine = DataBaseEngine().engine

    try:
        with Session(__engine) as __session:
            __session: ConnectedSession
            __new_quiz = Quiz(
                quiz_name=quiz.name,
                quiz_title=quiz.title,
                quiz_gratitude=quiz.gratitude,
            )
            __session.add(__new_quiz)
            __session.flush()
            __session.expunge_all()
            __session.commit()
        return __new_quiz
    except IntegrityError:
        pass


def __add_quiz_question(quiz_questions: list[PreparedQuestion], inserted_quiz: Quiz):

    __engine = DataBaseEngine().engine

    try:
        with Session(__engine) as __session:
            __session: ConnectedSession
            __result_list = []
            for question in quiz_questions:
                __new_question = QuizQuestion(
                    quiz_id=inserted_quiz.quiz_id,
                    quest_id=question.number,
                    quest_relation=question.relations,
                    quest_text=question.text,
                    quest_ans=' || '.join(question.answers)
                )
                __session.add(__new_question)
                __session.flush()
                __result_list.append(__new_question)
            __session.expunge_all()
            __session.commit()
        return __result_list
    except IntegrityError:
        pass


def add_quiz(quiz: PreparedQuiz) -> tuple[Quiz, list[QuizQuestion]]:
    new_quiz = __add_quiz(quiz)
    new_questions = __add_quiz_question(quiz.questions, new_quiz)
    return new_quiz, new_questions


def add_answer(quiz_id: int | str, question_id: int | str, internal_user_id: int | str, answer: str | None):

    __engine = DataBaseEngine().engine

    try:
        with Session(__engine) as __session:
            __session: ConnectedSession
            __answer = QuestionAnswer(
                quiz_id=quiz_id,
                quest_id=question_id,
                internal_user_id=internal_user_id,
                answer=answer
            )
            __session.add(__answer)
            __session.flush()
            __session.expunge_all()
            __session.commit()
        return __answer
    except IntegrityError:
        pass


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
