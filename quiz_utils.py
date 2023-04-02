import os
import re
from string import punctuation


def get_quiz_tasks(file_path):
    with open(f"quiz-questions/{file_path}", 'r', encoding='KOI8-R') as file:
        quiz_questions = file.read()

    splited_file = quiz_questions.split('\n\n')
    questions = []
    answers = []
    for chunk in splited_file:
        if 'Вопрос' in chunk:
            question = chunk.partition(':\n')[2]
            questions.append(question)
        elif 'Ответ' in chunk:
            answer = chunk.partition(':\n')[2]
            answers.append(answer)
    return dict(zip(questions, answers))


def update_questions(path):
    questions = {}
    for file in os.listdir(path):
        questions.update(get_quiz_tasks(file))
    return questions


def fix_answer(text):
    string = ''.join([char for char in text if char not in punctuation])
    string = ' '.join(string.split())
    return string


def check_user_answer(user_answer, correct_answer):
    matches = re.search(r"^[^.()]+", correct_answer)
    return fix_answer(user_answer.lower()) ==\
        fix_answer(matches.group().lower())
