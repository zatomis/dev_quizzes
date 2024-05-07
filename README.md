# Quiz бот

Телеграм и vk бот мини-игра - викторина.

## Установка

```commandline
git clone git@github.com:zatomis/dev_quizzes.git
```

## Установка зависимостей
Переход в директорию с исполняемым файлом

```commandline
cd dev_quizzes
```

Установка
```commandline
pip install -r requirements.txt
```

## Предварительная подготовка

### Подготовка vk

Создайте группу в [vk](vk.com), получите [API для сообщений сообществ](https://dev.vk.com/ru/api/community-messages/getting-started?ref=old_portal), установите права доступа для сообщений 
сообщества. Включите сообщения сообщества в настройках группы. Также в настройках сообщения включиите возможности ботов.  

### Подготовка telegram

Создайте бота в [botfather](https://t.me/BotFather). Получите его токен.

### Подготовка Redis
[Установите](https://timeweb.cloud/tutorials/redis/ustanovka-i-nastrojka-redis-dlya-raznyh-os) Redis, 
либо воспользуйтесь [облачным сервисом](https://redis.com). Получите адрес, порт и пароль.

## Создание и настройка .env

Создайте в корне папки `dev_quizzes` файл `.env`. Откройте его для редактирования любым текстовым редактором
и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.
Доступны следующие переменные:
- BOT_TOKEN - ваш телеграм бот API ключ(бот, который отвечает на вопросы).
- REDIS_HOST - ваш Redis адрес
- REDIS_PORT - ваш Redis порт 
- VK - Ваш vk API ключ(для бота, который отвечает на вопросы).

## Папка с вопросами
В папке `dev_quizzes` создайте папку `questions` и поместите туда вопросы
[вопросы](https://dvmn.org/media/modules_dist/quiz-questions.zip)

## Запуск телеграм бота

```commandline
python3 quizzes-tg.py 
```

Пример работы телеграм бота:  
![telegram example](https://dvmn.org/filer/canonical/1569215494/324/)


## Запуск бота в vk

```commandline
python3 quizzes-vk.py
```

![vk example](https://dvmn.org/filer/canonical/1569215498/325/)
