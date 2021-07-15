import asyncio
from tkinter import messagebox

import configargparse

import gui


def get_argparser():
    parser = configargparse.ArgParser(default_config_files=["chat.ini"])
    parser.add_argument("--host", help="URL of chat hosting server")
    parser.add_argument("-i", "--inport", type=int, help="port to read from")
    parser.add_argument("-o", "--outport", type=int, help="port to write to")
    parser.add_argument("--history", help="file to save transcript to")
    parser.add_argument(
        "--blacklist", action="append", help="list of users to filter out"
    )
    return parser


def reconnect(*exceptions, retries=10, delay=1, backoff=1.2):
    def wrap(func):
        async def wrapped(*args):
            _retries, _delay = retries, delay
            while _retries > 0:
                try:
                    return await func(*args)
                except exceptions:
                    await asyncio.sleep(_delay)
                    _retries -= 1
                    _delay *= backoff

            messagebox.showerror("Ошибка", "Нет соединения с сервером")
            raise gui.TkAppClosed

        return wrapped

    return wrap
