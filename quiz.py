import pprint


def get_quiz_tasks():
    with open('quiz-questions/1vs1200.txt', 'r', encoding='KOI8-R') as questions_file:
        quiz_questions = questions_file.read()
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
                quiz.get(f'Вопрос - {question_number}')['answer'] = answer
        pprint.pprint(quiz)
        return quiz


if __name__ == "__main__":
    get_quiz_tasks()
