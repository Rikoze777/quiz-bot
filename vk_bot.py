import logging
import os
import random

import redis
import telegram
import vk_api as vk
from environs import Env
from logs_handler import TelegramLogsHandler
from quiz_utils import check_user_answer, update_questions
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll

logger = logging.getLogger(__name__)


def send_message(event, vk_api, messaage, keyboard):
    vk_api.messages.send(
        user_id=event.user_id,
        message=messaage,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard()
    )


def handle_quiz(event, vk_api, redis, quiz_tasks, keyboard):
    if event.text == "Новый вопрос":
        question = random.choice(list(quiz_tasks.keys()))
        redis.set(event.user_id, question)
        send_message(event, vk_api, question, keyboard)
    elif event.text == "Сдаться":
        question = redis.get(event.user_id)
        correct_answer = quiz_tasks.get(question)
        send_message(event, vk_api, correct_answer, keyboard)
    else:
        question = redis.get(event.user_id)
        user_answer = event.text
        correct_answer = quiz_tasks.get(question)

        if check_user_answer(user_answer, correct_answer):
            message = "Правильно! Поздравляю! "
            "Для следующего вопроса нажми «Новый вопрос»"
            send_message(event, vk_api, message, keyboard)
        else:
            message = "Неправильно… Попробуешь ещё раз?"
            send_message(event, vk_api, message, keyboard)


def main():
    env = Env()
    env.read_env()
    tg_token = env.str("TG_TOKEN")
    user_id = env.str("USER_ID")
    path = os.getenv('FILES_PATH', default='quiz-questions')
    redis_password = env.str('REPIS_PASSWORD')
    port = env.str('REDIS_PORT')
    host = env.str('REDIS_ADDRESS')
    vk_token = env.str("VK_TOKEN")
    redis_connection = redis.Redis(host=host, port=port,
                                   password=redis_password,
                                   db=0, charset='utf-8',
                                   decode_responses=True)
    quiz_tasks = update_questions(path)

    bot = telegram.Bot(token=tg_token)
    logger.setLevel(logging.ERROR)
    logger.addHandler(TelegramLogsHandler(bot, user_id))

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            try:
                handle_quiz(
                    event,
                    vk_api,
                    redis_connection,
                    quiz_tasks,
                    keyboard,
                )
            except Exception as error:
                logger.exception(error)


if __name__ == "__main__":
    main()
