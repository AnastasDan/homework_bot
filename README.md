# Telegram-бот ассистент

Telegram-бот - бот, взаимодействующий с API для получения статуса выполненных работ.

Бот умеет:

* раз в 10 минут опрашивать API сервиса и проверять статус выполненных работ;
* при обновлении статуса анализировать ответ API и отправлять вам соответствующее уведомление в Telegram;
* логировать свою работу и сообщать вам о важных проблемах сообщением в Telegram.

## Как запустить проект

Клонируем себе репозиторий:

```
git clone git@github.com:AnastasDan/homework_bot.git
```

Переходим в директорию:

```
cd homework_bot
```

Cоздаем и активируем виртуальное окружение:

* Если у вас Linux/MacOS:

    ```
    python3 -m venv venv
    ```

    ```
    source venv/bin/activate
    ```

* Если у вас Windows:

    ```
    python -m venv venv
    ```

    ```
    source venv/Scripts/activate
    ```

Устанавливаем зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Создаем файл .env и заполняем его. Список данных указан в файле .env.example.

Запускаем проект:

* Если у вас Linux/MacOS:

    ```
    python3 homework.py
    ```

* Если у вас Windows:

    ```
    python homework.py
    ```

## Автор проекта

[Anastas Danielian](https://github.com/AnastasDan)