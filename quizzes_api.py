import os
import random


def clear_text(message):
    message = str(message.split('\n')[1])
    message = message.replace('.', '')
    return message.lower().strip()


def load_quizzes(redis_question, redis_answer, directory, createquizzes):
    quizzes = []
    number = 0
    if createquizzes:
        for file in os.listdir(directory):
            if file.endswith(".txt"):
                with open(os.path.join(directory, file), "r", encoding='KOI8-R') as sprite_file:
                    quizzes.append(sprite_file.read())
        quizzes = random.choice(quizzes).split('\n\n')
        for i, question_answer in enumerate(quizzes):
            if "Вопрос" in question_answer:
                redis_question.set(number, question_answer)
                redis_answer.set(number, quizzes[i+1])
                number += 1
        return number
    else:
        return redis_question.dbsize()
