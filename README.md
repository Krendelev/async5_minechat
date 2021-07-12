# Секретный чат

Клиент для "секретного" чата. Позволяет читать и писать сообщения, сохраняет историю переписки.

## Запуск

Скачайте код и установите зависимости.

```bash
$ python3 -m pip install -r requirements.txt
```
Запустите программу:
```bash
$ python3 main.py [--host] [--port] [--history] [--blacklist]
```

Если вы не зарегистрированы на сервере, при первом запуске программа предложит вам зарегистрироваться. Вы также можете зарегистрироваться (или изменить никнейм) не запуская клиента:

```bash
$ python3 register.py [--host] [--port]
```

## Настройки и переменные окружения

Настройки клиента включают в себя адрес сервера, порты, имя файла для сохранения переписки, а также список заблокированных пользователей. Они хранятся в файле `chat.ini`. При желании их можно переопределить из командной строки. Токен для подключения к чату создаётся при первом запуске и сохраняется в файл `.env`.

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
