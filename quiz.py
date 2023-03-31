import os
import pprint
import re
from string import punctuation


def get_quiz_tasks(file_path):
    with open(f"quiz-questions/{file_path}", 'r', encoding='KOI8-R') as file:
        quiz_questions = file.read()

    splited_file = quiz_questions.split('\n\n')
    question_number = 0
    quiz = {}
    for chunk in splited_file:
        if 'Вопрос' in chunk:
            question_number += 1
            question = chunk.partition(':\n')[2]
            quiz[f'Вопрос - {question_number}'] = {'question': question}
        elif 'Ответ' in chunk:
            answer = chunk.partition(':\n')[2]
            try:
                quiz.get(f'Вопрос - {question_number}')['answer'] = answer
            except TypeError:
                quiz[f'Вопрос - {question_number}'] = 'No answer'
    return quiz


def update_questions(path):
    questions = {}

    for file in os.listdir(path):
        questions.update(get_quiz_tasks(file))
    pprint.pprint(questions)
    return questions


def fix_answer(text):
    string = ''.join([char for char in text if char not in punctuation])
    string = ' '.join(string.split())
    return string


def check_user_answer(user_answer, correct_answer):
    matches = re.search(r"^[^.()]+", correct_answer)
    return fix_answer(user_answer.lower()) ==\
        fix_answer(matches.group().lower())
