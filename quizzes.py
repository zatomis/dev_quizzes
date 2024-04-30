import logging
import telegram
from environs import Env
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
import random
import redis

redis_answer = redis.Redis()
redis_question = redis.Redis()
question_answer_count = 0
logger = logging.getLogger(__name__)


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
            redis_answer.set(number,quizzes[i+1])
            number += 1
    return number


def start(update: Update, context: CallbackContext) -> None:
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Здравствуйте {user.mention_markdown_v2()}\!',
        reply_markup=reply_markup,
    )


def echo(update: Update, context: CallbackContext) -> None:
    if update.message.text == 'Новый вопрос':
        question_now = redis_question.get(random.randint(0, question_answer_count))
        update.message.reply_text(question_now.decode("utf-8"))


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    env: Env = Env()
    env.read_env()
    token_bot = env('BOT_TOKEN')
    updater = Updater(token_bot)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    logger.setLevel(logging.INFO)
    logger.info('Бот Игра - викторина')
    question_answer_count = load_quizzes()
    print(question_answer_count)
    updater.start_polling()
    updater.idle()
