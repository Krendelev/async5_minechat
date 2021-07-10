# Секретный чат

Клиент для "секретного" чата. Позволяют читать и писать сообщения, а также сохранять историю переписки.

## Запуск

Скачайте код и установите зависимости.

```bash
$ python3 -m pip install -r requirements.txt
```
Запустите программу:
```bash
$ python3 main.py [--host] [--port] [--history]
```

Если вы не зарегистрированы на сервере, при первом запуске программа предложит вам зарегистрироваться. Вы также можете зарегистрироваться (или изменить никнейм) не запуская клиента:

```bash
$ python3 register.py [--host] [--port]
```

## Настройки и переменные окружения

Настройки (адрес сервера, порты, файл истории) хранятся в файле `chat.ini`. При желании их можно переопределить из командной строки. Токен для подключения к чату создаётся при первом запуске и сохраняется в файл `.env`.

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
