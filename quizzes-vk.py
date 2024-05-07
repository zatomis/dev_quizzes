import os
from environs import Env
import random
import vk_api as vk
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType
import redis
import logging


question_answer_count = 0
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def clear_text(message):
    message = str(message.split('\n')[1])
    message = message.replace('.','')
    return message.lower().strip()

def load_quizzes():
    quizzes = []
    directory = 'questions'
    number = 0
    for file in os.listdir(directory):
        if file.endswith(".txt"):
            with open(os.path.join(directory, file), "r", encoding='KOI8-R') as sprite_file:
                quizzes.append(sprite_file.read())
    quizzes = random.choice(quizzes).split('\n\n')
    for i, question_answer in enumerate(quizzes):
        if "Вопрос" in question_answer:
            redis_question.set(number, question_answer)
            redis_answer.set(number, quizzes[i+1])
            number += 1
    return number

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

def send_question(event, vk_api):
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
    env: Env = Env()
    env.read_env()
    host = env('REDIS_HOST')
    port = env('REDIS_PORT')
    redis_answer = redis.Redis(host=host, port=port, db=0, protocol=3)
    redis_question = redis.Redis(host=host, port=port, db=1, protocol=3)
    user_question = redis.Redis(host=host, port=port, db=2, protocol=3)

    logger.setLevel(logging.INFO)
    logger.info('ВК Игра - викторина')
    question_answer_count = load_quizzes()

    vk_key_token = env('VK')
    vk_session = vk.VkApi(token=vk_key_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == "Начать":
                start_communication(event, vk_api)
            elif event.text == "Новый вопрос":
                send_question(event, vk_api)
            elif event.text == "Сдаться":
                send_answer(event, vk_api)
                send_question(event, vk_api)
            else:
                check_answer(event, vk_api)