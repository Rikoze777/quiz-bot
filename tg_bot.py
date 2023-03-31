import logging
from environs import Env
import random
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackContext, ConversationHandler)
from quiz import update_questions
from functools import partial
import redis


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CUSTOM_KEYBOARD = [['Новый вопрос', 'Сдаться'],
                   ['Мой счет', 'Закончить игру']]


def start(update: Update, context: CallbackContext) -> None:
    reply_markup = ReplyKeyboardMarkup(CUSTOM_KEYBOARD,
                                       resize_keyboard=True,
                                       one_time_keyboard=True)
    update.message.reply_text(
        'Привет! Для начала игры нажми на "Новый вопрос"!',
        reply_markup=reply_markup,
    )


def new_question(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user["id"]
    redis = context.bot_data["redis_connection"]
    quiz_questions = context.bot_data["quiz_tasks"]
    question_number = random.choice(list(quiz_questions))
    question = quiz_questions.get(question_number)['question']
    context.user_data[update.effective_user.id] = question
    # reply_markup = ReplyKeyboardMarkup(CUSTOM_KEYBOARD, resize_keyboard=True)
    redis.set(user_id, question)
    update.message.reply_text(question)
    # return 'user_answer'


def end(update: Update, context: CallbackContext):
    update.message.reply_text(
        'До встречи!',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main() -> None:
    env = Env()
    env.read_env()
    tg_token = env.str("TG_TOKEN")
    path = env.str('FILES_PATH')
    redis_password = env.str('REPIS_PASSWORD')
    port = env.str('REDIS_PORT')
    host = env.str('REDIS_ADDRESS')
    redis_connection = redis.Redis(host=host, port=port,
                                   password=redis_password,
                                   db=0, charset='utf-8',
                                   decode_responses=True)
    quiz_tasks = update_questions(path)

    updater = Updater(tg_token)

    dispatcher = updater.dispatcher

    dispatcher.bot_data["redis_connection"] = redis_connection
    dispatcher.bot_data["quiz_tasks"] = quiz_tasks

    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(
        MessageHandler(
            Filters.regex("^Новый вопрос"),
            new_question
        ),
    )
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command,
    #                                       new_question))

    # dispatcher.add_handler(
    #     MessageHandler(Filters.regex("^Сдаться"), send_correct_answer),
    # )

    dispatcher.add_handler(CommandHandler("end", end))

    updater.start_polling()
    updater.idle()
    redis_connection.close()


if __name__ == '__main__':
    main()
