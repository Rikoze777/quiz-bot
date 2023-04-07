import logging
import os
import random

import redis
import telegram
from environs import Env
from logs_handler import TelegramLogsHandler
from quiz_utils import check_user_answer, update_questions
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)


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


def handle_new_question_request(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user["id"]
    redis = context.bot_data["redis_connection"]
    quiz_questions = context.bot_data["quiz_tasks"]
    question = random.choice(list(quiz_questions.keys()))
    context.user_data[update.effective_user.id] = question
    redis.set(user_id, question)
    update.message.reply_text(question)


def handle_solution_attempt(update: Update, context: CallbackContext):
    redis_connection = context.bot_data["redis_connection"]
    question = redis_connection.get(update.message.chat_id)
    correct_answer = context.bot_data["quiz_tasks"].get(question)
    user_answer = update.message.text
    keyboard = CUSTOM_KEYBOARD
    markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    if check_user_answer(user_answer, correct_answer):
        update.message.reply_text(
            "Поздравляю! Верно!"
            "Нажми «Новый вопрос» для продолжения",
            reply_markup=markup
        )
    else:
        update.message.reply_text(
            "Неправильно… Попробуешь ещё раз?",
            reply_markup=markup
        )


def send_answer(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user["id"]
    question = context.bot_data["redis_connection"].get(user_id)
    correct_answer = context.bot_data["quiz_tasks"].get(question)
    update.message.reply_text(correct_answer)
    return handle_new_question_request(update, context)


def handle_error(update: Update, context: CallbackContext):
    logger.exception(context.error)


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
    user_id = env.str("USER_ID")
    path = os.getenv('FILES_PATH', default='quiz-questions')
    redis_password = env.str('REPIS_PASSWORD')
    port = env.str('REDIS_PORT')
    host = env.str('REDIS_ADDRESS')
    redis_connection = redis.Redis(host=host, port=port,
                                   password=redis_password,
                                   db=0, charset='utf-8',
                                   decode_responses=True)
    quiz_tasks = update_questions(path)

    bot = telegram.Bot(token=tg_token)
    logger.setLevel(logging.ERROR)
    logger.addHandler(TelegramLogsHandler(bot, user_id))

    updater = Updater(tg_token)

    dispatcher = updater.dispatcher

    dispatcher.bot_data["redis_connection"] = redis_connection
    dispatcher.bot_data["quiz_tasks"] = quiz_tasks
    dispatcher.add_error_handler(handle_error)

    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(
        MessageHandler(
            Filters.regex("^Новый вопрос"),
            handle_new_question_request
        ),
    )
    dispatcher.add_handler(
        MessageHandler(Filters.regex("^Сдаться"), send_answer),
    )

    dispatcher.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command,
            handle_solution_attempt
        )
    )
    dispatcher.add_handler(CommandHandler('end', end))

    updater.start_polling()
    updater.idle()
    redis_connection.close()


if __name__ == '__main__':
    main()
