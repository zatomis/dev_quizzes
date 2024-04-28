import logging
import telegram
from environs import Env
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
import random


logger = logging.getLogger(__name__)
question = dict()
answer = dict()


def load_quizzes():
    quizzes = []
    directory = 'questions'
    question = dict()
    answer = dict()
    number = 0
    for file in os.listdir(directory):
        if file.endswith(".txt"):
            with open(os.path.join(directory, file), "r", encoding='KOI8-R') as sprite_file:
                quizzes.append(sprite_file.read())
    quizzes = random.choice(quizzes).split('\n\n')
    for i, question_answer in enumerate(quizzes):
        if "Вопрос" in question_answer:
            question[number] = question_answer
            answer[number] = quizzes[i+1]
            number += 1
    return question, answer


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
        question_now = question[random.randint(0,len(question))]
        update.message.reply_text(question_now)


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
    question, answer = load_quizzes()
    updater.start_polling()
    updater.idle()
