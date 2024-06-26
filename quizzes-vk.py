from environs import Env
import random
import vk_api as vk
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType
import redis
import logging
from quizzes_api import clear_text, load_quizzes
import argparse


logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Бот Викторина"
    )
    parser.add_argument(
        '--folder',
        default='questions',
        type=str,
        help='Указать новый путь к данным викторины',
    )
    parser.add_argument(
        '--createquizzes',
        action='store_true',
        help='Создать БД Викторины'
    )
    args = parser.parse_args()
    return args


def check_answer(event, vk_api):
    user_number_answer = user_question.get(event.user_id)
    correct_answer = clear_text(redis_answer.get(user_number_answer).decode("utf-8"))
    if correct_answer == event.text.strip():
        answer = "Правильно! Для следующего вопроса нажми «Новый вопрос»"
    else:
        answer = f"Нет 😭 !!!\nПопробуешь ещё раз ?"

    vk_api.messages.send(
        user_id=event.user_id,
        message=answer,
        random_id=random.randint(1, 1000),
    )


def send_question(event, vk_api, question_answer_count):
    number = random.randint(0, question_answer_count)
    question_now = redis_question.get(number)
    user_question.set(event.user_id, number)
    vk_api.messages.send(
        user_id=event.user_id,
        message=question_now.decode("utf-8"),
        random_id=random.randint(1, 1000),
    )


def send_answer(event, vk_api):
    user_number_answer = user_question.get(event.user_id)
    correct_answer = clear_text(redis_answer.get(user_number_answer).decode("utf-8"))
    answer = f"Правильный ответ\n\n{correct_answer}"

    vk_api.messages.send(
        user_id=event.user_id,
        message=answer,
        random_id=random.randint(1, 1000),
    )


def start_communication(event, vk_api):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Новый вопрос")
    keyboard.add_button("Сдаться")
    keyboard.add_line()
    keyboard.add_button("Мой счёт")
    vk_api.messages.send(
        user_id=event.user_id,
        message="Привет! Я викторинный бот ️!",
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    env: Env = Env()
    env.read_env()
    host = env('REDIS_HOST')
    port = env('REDIS_PORT')
    redis_answer = redis.Redis(host=host, port=port, db=0, protocol=3)
    redis_question = redis.Redis(host=host, port=port, db=1, protocol=3)
    user_question = redis.Redis(host=host, port=port, db=2, protocol=3)
    logger.setLevel(logging.INFO)
    logger.info('ВК Игра - викторина')

    question_answer_count = load_quizzes(redis_question,
                                         redis_answer,
                                         parse_arguments().folder,
                                         parse_arguments().createquizzes)
    if question_answer_count:
        vk_key_token = env('VK')
        vk_session = vk.VkApi(token=vk_key_token)
        vk_api = vk_session.get_api()
        longpoll = VkLongPoll(vk_session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text == "Начать":
                    start_communication(event, vk_api)
                elif event.text == "Новый вопрос":
                    send_question(event, vk_api, question_answer_count)
                elif event.text == "Сдаться":
                    send_answer(event, vk_api)
                    send_question(event, vk_api, question_answer_count)
                else:
                    check_answer(event, vk_api)
    else:
        print("Необходимо создать БД Викторины, воспользуйтесь инструкцией --help")
