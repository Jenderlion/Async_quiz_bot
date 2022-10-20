from database.main import User
from database.main import QuizQuestion
from database.methods.select import get_user
from database.methods.select import get_user_answers
from database.methods.select import get_quiz
from database.methods.select import get_quiz_questions
from database.methods.update import update_user_info
from database.methods.update import update_ban_info
from database.methods.update import update_answer_info
from database.methods.insert import add_ban
from database.methods.insert import add_answer
from keyboards.reply import menu_keyboard
from keyboards.reply import question_keyboard


def ban_user(initiator_id: int | str, user: User, term: int, reason: str) -> int:
    add_ban(initiator_id, user, term, reason)
    __count = update_user_info(user.tg_user_id, {'group': 'banned', 'is_ban': True})
    return __count


def unban_user(tg_id: int | str) -> int:
    __count = update_user_info(tg_id, {'group': 'user', 'is_ban': False})
    update_ban_info(tg_id, {'current_status': False})
    return __count


def run_quiz(user_id: str | int, quiz_id: str | int) -> str:
    user = get_user(user_id)
    quiz = get_quiz(quiz_id)
    if user.quiz_status is not None:
        return 'У вас уже запущен один опрос. Пожалуйста, пройдите или завершите его прежде, чем начинать новый.'
    user_answers = get_user_answers(user.tg_user_id)
    user_answers_quizzes_ids = set([answer.quiz_id for answer in user_answers])
    if quiz.quiz_id in user_answers_quizzes_ids:
        return 'Вы уже проходили этот опрос. Если Вы хотите изменить ответы, выбери соответствующий пункт в меню.'
    questions = get_quiz_questions(quiz.quiz_id)
    update_user_info(user.tg_user_id, {'quiz_status': f'{quiz.quiz_id} -> 0'})

    for question in questions:
        add_answer(question.quiz_id, question.quest_id, user.internal_user_id, None)

    answer = f'Запущен опрос "{quiz.quiz_name}": {quiz.quiz_title}.\n' \
             f'Всего вопросов, с учётом ветвления: {len(questions)}\n\n' \
             f'Предполагаемые ответы будут на клавиатуре. Если там есть только "завершить опрос", то вопрос' \
             f' предполагает рукописный ввод.'

    return answer


def rerun_quiz(tg_id, quiz_id):
    questions = get_quiz_questions(quiz_id)
    user = get_user(tg_id)
    for question in questions:
        update_answer_info(user, quiz_id, question.quest_id, {'answer': None})


async def send_question(user: User, bot):
    quiz_id, question_id = user.quiz_status.split(' -> ')
    questions = get_quiz_questions(quiz_id)
    if int(question_id) > len(questions):
        update_user_info(user.tg_user_id, {'quiz_status': None})
        quiz = get_quiz(quiz_id)
        await bot.send_message(
            user.tg_user_id, f'Опрос завершён!\n\n{quiz.quiz_gratitude}', reply_markup=menu_keyboard()
        )
        return None
    questions_dict = {question.quest_id: question for question in questions}
    question_to_send: QuizQuestion = questions_dict[int(question_id)]
    if question_to_send.quest_relation is not None:
        relation_question_id, relation_answer = question_to_send.quest_relation.split(' -> ')
        user_answers = get_user_answers(quiz_id)
        answers_dict = {answer.quest_id: answer.answer for answer in user_answers}
        user_answer_to_relation_question = answers_dict[int(relation_question_id)]

        if user_answer_to_relation_question != relation_answer:
            update_user_info(user.tg_user_id, {'quiz_status': f'{quiz_id} -> {int(question_id) + 1}'})
            user = get_user(user.tg_user_id)
            await send_question(user, bot)
        else:
            await bot.send_message(
                user.tg_user_id, question_to_send.quest_text, reply_markup=question_keyboard(question_to_send)
            )
    else:
        await bot.send_message(
            user.tg_user_id, question_to_send.quest_text, reply_markup=question_keyboard(question_to_send)
        )
