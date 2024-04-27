import os
import random


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

if __name__ == '__main__':
    question, answer = load_quizzes()
    print(question)
    print(answer)
