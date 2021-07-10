import asyncio
import json
import os
from contextlib import closing, suppress
from tkinter import messagebox

import anyio
from dotenv import load_dotenv

import gui
from errors import InvalidToken
from utils import get_argparser, reconnect


async def load_messages(filepath, queues):
    with suppress(FileNotFoundError):
        async with await anyio.open_file(filepath) as fh:
            async for line in fh:
                queues["messages"].put_nowait(line)


async def save_messages(filepath, queues):
    async with await anyio.open_file(filepath, "a") as fh:
        while True:
            text = await queues["transcript"].get()
            await fh.write(text)
            queues["transcript"].task_done()


async def send_messages(writer, queues):
    with closing(writer):
        while True:
            message = await queues["sending"].get()
            writer.write(f"{message}\n\n".encode())
            queues["sending"].task_done()
            await writer.drain()
            queues["watchdog"].put_nowait("Message sent")


async def read_messages(reader, writer, queues):
    with closing(writer):
        while True:
            message = await reader.readuntil()
            text = message.decode()
            queues["messages"].put_nowait(text)
            queues["transcript"].put_nowait(text)
            queues["watchdog"].put_nowait("New message in chat")


async def authorize(reader, writer, token, queues):
    await reader.readuntil()
    queues["watchdog"].put_nowait("Prompt before auth")
    writer.write(f"{token}\n".encode())
    response = await reader.readuntil()
    response_content = json.loads(response)
    if not response_content:
        raise InvalidToken("Неизвестный токен")

    event = gui.NicknameReceived(response_content["nickname"])
    queues["status"].put_nowait(event)
    queues["watchdog"].put_nowait("Authorization done")


async def ping_server(reader, writer, queues, delay=1):
    with closing(writer):
        while True:
            writer.write(b"\n")
            await reader.readuntil()
            queues["watchdog"].put_nowait("Connection alive")
            await asyncio.sleep(delay)


async def watch_for_connection(queues, timeout=2):
    while True:
        async with anyio.move_on_after(timeout) as scope:
            await queues["watchdog"].get()
            queues["watchdog"].task_done()

        if scope.cancel_called:
            queues["status"].put_nowait(gui.ReadConnectionStateChanged.CLOSED)
            queues["status"].put_nowait(gui.SendingConnectionStateChanged.CLOSED)
            raise ConnectionError


@reconnect((ConnectionError, OSError), retries=20)
async def handle_connection(settings, queues):
    queues["status"].put_nowait(gui.ReadConnectionStateChanged.INITIATED)
    queues["status"].put_nowait(gui.SendingConnectionStateChanged.INITIATED)

    rcv_reader, rcv_writer = await asyncio.open_connection(
        settings.host, settings.inport
    )
    queues["status"].put_nowait(gui.ReadConnectionStateChanged.ESTABLISHED)

    send_reader, send_writer = await asyncio.open_connection(
        settings.host, settings.outport
    )
    queues["status"].put_nowait(gui.SendingConnectionStateChanged.ESTABLISHED)

    try:
        await authorize(send_reader, send_writer, settings.token, queues)
    except InvalidToken as err:
        messagebox.showerror("Ошибка", err)
        raise gui.TkAppClosed

    async with anyio.create_task_group() as tg:
        tg.start_soon(read_messages, rcv_reader, rcv_writer, queues)
        tg.start_soon(send_messages, send_writer, queues)
        tg.start_soon(ping_server, send_reader, send_writer, queues)
        tg.start_soon(watch_for_connection, queues)


async def main():
    load_dotenv()
    argparser = get_argparser()
    settings = argparser.parse_args()
    try:
        settings.token = os.environ["TOKEN"]
    except KeyError:
        registration = await anyio.run_process("python3 register.py")
        settings.token = registration.stdout.decode()
        if not settings.token:
            raise gui.TkAppClosed

    queues_names = ["messages", "sending", "transcript", "status", "watchdog"]
    queues = {name: asyncio.Queue() for name in queues_names}

    async with anyio.create_task_group() as tg:
        tg.start_soon(load_messages, settings.history, queues)
        tg.start_soon(save_messages, settings.history, queues)
        tg.start_soon(handle_connection, settings, queues)
        tg.start_soon(gui.draw, queues["messages"], queues["sending"], queues["status"])


if __name__ == "__main__":
    try:
        anyio.run(main)
    except (KeyboardInterrupt, gui.TkAppClosed):
        exit()
