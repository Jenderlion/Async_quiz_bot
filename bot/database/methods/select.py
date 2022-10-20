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


def get_quizzes(status: bool = None) -> list[Quiz]:

    __engine = DataBaseEngine().engine

    with Session(__engine) as __session:
        __session: ConnectedSession
        statement: ConnectedSelect = select(Quiz)
        if status is not None:
            statement = statement.where(Quiz.quiz_status == status)
        res: ScalarResult = __session.scalars(statement)
        __session.flush()
        result = res.all()
        if len(result) > 10:
            result = result[-10:]
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


def get_user_answers(__quiz_id) -> list[QuestionAnswer]:

    __engine = DataBaseEngine().engine

    with Session(__engine) as __session:
        __session: ConnectedSession
        statement: ConnectedSelect = select(QuestionAnswer).where(
            QuestionAnswer.quiz_id == __quiz_id,
        )
        __session.flush()
        result = __session.scalars(statement).all()
        __session.expunge_all()
        __session.commit()
    return result


def get_analytical_message(quiz_id) -> str | None:

    __engine = DataBaseEngine().engine

    with Session(__engine) as __session:
        __session: ConnectedSession
        statement: ConnectedSelect = select(QuizQuestion).where(QuizQuestion.quiz_id == quiz_id)
        res: ScalarResult = __session.scalars(statement).all()
        __session.flush()
        __session.expunge_all()
        __session.commit()
    quests_id = frozenset([question.quest_id for question in res])
    questions_info: list[QuizQuestion] = [question for question in res]
    all_answers: list[QuestionAnswer] = get_user_answers(quiz_id)
    analytical_dict = dict()

    for quest_id in quests_id:
        try:
            answers = [answer for answer in all_answers if answer.quest_id == quest_id]
            for answer in answers:
                print(answer.internal_user_id)
                print(analytical_dict)
                if answer.internal_user_id not in analytical_dict:
                    analytical_dict[answer.internal_user_id] = dict()
                analytical_dict[answer.internal_user_id][answer.quest_id] = answer.answer
        except IndexError:
            pass

    if analytical_dict:
        return __dict_analytic(analytical_dict, questions_info)
    return None


def get_user_completed_quizzes(__tg_id) -> list:

    __engine = DataBaseEngine().engine

    user = get_user(__tg_id)

    with Session(__engine) as __session:
        __session: ConnectedSession
        statement: ConnectedSelect = select(QuestionAnswer.quiz_id)\
            .where(QuestionAnswer.internal_user_id == user.internal_user_id)
        res: list = __session.scalars(statement).all()
        __session.flush()
        __session.expunge_all()
        __session.commit()

    result = []
    for _ in res:
        if _ not in result:
            result.append(_)

    return result


def get_quizzes_from_ids_list(ids: list) -> list[Quiz]:

    __engine = DataBaseEngine().engine

    with Session(__engine) as __session:
        __session: ConnectedSession
        result = []
        for _id in ids:
            statement: ConnectedSelect = select(Quiz).where(Quiz.quiz_id == _id)
            res: Quiz = __session.scalars(statement).first()
            __session.flush()
            __session.expunge_all()
            result.append(res)
        __session.commit()

    return result


def __dict_analytic(input_dict: dict, questions_info: list[QuizQuestion]):
    """Prepare analytical message"""
    general_answers_seq = []
    for answers_dict in input_dict.values():
        answer_seq = []
        for answer in answers_dict.values():
            answer_seq.append(answer)
        while len(answer_seq) < len(questions_info):
            answer_seq.append(None)
        general_answers_seq.append(answer_seq)
    analytical_list = __seq_analytic(general_answers_seq)
    info_analytical_list = []
    for index in range(len(analytical_list)):
        info_string = f'{questions_info[index].quest_text}\nСамый популярный ответ' \
                      f' ({analytical_list[index][1]}%): {analytical_list[index][0]}'
        info_analytical_list.append(info_string)
    return '\n'.join(info_analytical_list)


def __seq_analytic(input_seq: list[list], output_seq: list or None = None) -> list:
    """Recursive sequence traversal"""
    if output_seq is None:
        output_seq = list()
    temp_dict = dict()
    second_seq = list()
    for user_answers in input_seq:
        if user_answers[0] not in temp_dict:
            temp_dict[user_answers[0]] = 1
        else:
            temp_dict[user_answers[0]] += 1

    frequent_answer = max(temp_dict, key=temp_dict.get)
    output_seq.append(
        (frequent_answer, round(temp_dict[frequent_answer] / len(input_seq) * 100, 2))
    )

    for user_answers in input_seq:
        if len(user_answers) > 0 and user_answers[0] == frequent_answer:
            second_seq.append(user_answers[1:])

    if len(second_seq[0]) > 0:
        seq = __seq_analytic(second_seq, output_seq)
    else:
        seq = output_seq

    return seq
