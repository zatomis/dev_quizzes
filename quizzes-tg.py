import logging
import telegram
from environs import Env
from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackContext)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
import redis
import random
from quizzes_api import clear_text, load_quizzes
import argparse
from functools import partial


logger = logging.getLogger(__name__)
ANSWER = 0


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


def start(update: Update, context: CallbackContext) -> None:
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Здравствуйте {user.mention_markdown_v2()}\!',
        reply_markup=reply_markup,
    )


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def send_question(update: Update, context: CallbackContext, question_answer_count):
    number = random.randint(0, int(question_answer_count))
    question_now = redis_question.get(number)
    user_question.set(update.message.from_user.id, number)
    update.message.reply_text(question_now.decode("utf-8"))
    return ANSWER


def give_up(update: Update, context: CallbackContext, question_answer_count):
    user_number_answer = user_question.get(update.message.from_user.id)
    correct_answer = clear_text(redis_answer.get(user_number_answer).decode("utf-8"))
    update.message.reply_text(f"Правильный ответ: {correct_answer}")
    # return partial(send_question,(update, context, int(question_answer_count))
    return partial(send_question, question_answer_count=question_answer_count)


def check_answer(update: Update, context: CallbackContext):
    user_number_answer = user_question.get(update.message.from_user.id)
    correct_answer = clear_text(redis_answer.get(user_number_answer).decode("utf-8"))
    if correct_answer == update.message.text.strip():
        update.message.reply_text("Правильно!\n Поздравляю!\n Для следующего вопроса нажми «Новый вопрос»")
        return ConversationHandler.END
    else:
        update.message.reply_text(f"Нет 😭 !!!\nПравильный ответ\n\n{correct_answer}\n\nПопробуешь ещё раз ?")
        return ConversationHandler.END


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    env: Env = Env()
    env.read_env()
    token_bot = env('BOT_TOKEN')
    host = env('REDIS_HOST')
    port = env('REDIS_PORT')
    redis_answer = redis.Redis(host=host, port=port, db=0, protocol=3)
    redis_question = redis.Redis(host=host, port=port, db=1, protocol=3)
    user_question = redis.Redis(host=host, port=port, db=2, protocol=3)
    updater = Updater(token_bot)
    dispatcher = updater.dispatcher
    question_answer_count = load_quizzes(redis_question,
                                         redis_answer,
                                         parse_arguments().folder,
                                         parse_arguments().createquizzes)
    if (question_answer_count):
        conv_handler = ConversationHandler(
            entry_points=[MessageHandler(Filters.regex(r"^Новый вопрос$"), partial(send_question, question_answer_count=question_answer_count))],
            states={
                ANSWER: [
                    MessageHandler(Filters.regex(r"^Сдаться$"), partial(give_up, question_answer_count=question_answer_count)),
                    MessageHandler(Filters.text & ~Filters.command, check_answer),
                ]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(conv_handler)
        logger.setLevel(logging.INFO)
        logger.info('Бот Игра - викторина')

        updater.start_polling()
        updater.idle()
    else:
        print("Необходимо создать БД Викторины, воспользуйтесь инструкцией --help")
