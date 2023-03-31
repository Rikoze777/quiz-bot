# quiz-bot


## Установка

1) Клонировать проект:
```
git clone https://github.com/Rikoze777/quiz-bot
```

2) Установить зависимости:
```
pip install -r requiremenets.txt
```

3) Создать .env файл для ваших секретных ключей:
```
touch .env
```

4) Записать в .env следующие переменные:
* TG_TOKEN='Ваш телеграм токен'  [Получают при создании у отца ботов](https://t.me/botfather)
* USER_ID='ID вашей личной страницы Telegram' [узнать можно тут](https://t.me/username_to_id_bot)
* VK_TOKEN='Токен вашей группы ВК' Не забудьте также разрешить отправление сообщений группе
* FILES_PATH='Путь к файлам вопросов'
* REDIS_ADDRESS='Your redis address' [Можно получить после регистации на redis](https://www.redislabs.com/)
* REDIS_PORT='Your redis port'
* REPIS_PASSWORD='Your redis password'