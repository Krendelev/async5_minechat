import json
import os
import socket
import tkinter as tk
from tkinter import messagebox

from dotenv import load_dotenv

from utils import get_argparser


def register(settings, username):
    if not username:
        messagebox.showerror("Ошибка", "Введите ваш никнейм")
        return
        
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((settings.host, settings.outport))
            conn = sock.makefile("rwb", 0)
            conn.readline()
            conn.write(b"\n")
            conn.readline()
            conn.write(f"{username}\n".encode())
            response = conn.readline()
        except OSError:
            messagebox.showerror("Ошибка", "Нет соединения с сервером")
            exit()

    creds = json.loads(response)

    with open(".env", "w") as fh:
        fh.write(f"TOKEN={creds['account_hash']}")

    messagebox.showinfo(
        "Пользователь зарегистрирован", f"Добро пожаловать {creds['nickname']}!"
    )
    print(creds['account_hash'])
    exit()


def draw(settings):
    root = tk.Tk()
    root.geometry("400x240+120+120")
    root.resizable(False, False)
    root.title("Регистрация нового пользователя")

    label1 = tk.Label(root, text="Добро пожаловать в чат майнкрафтера!")
    label1.pack(fill="x", expand=True)
    label2 = tk.Label(root, text="Введите ваш никнейм:")
    label2.pack(fill="x")

    nickname = tk.StringVar()
    entry = tk.Entry(root, textvariable=nickname)
    entry.pack(fill="x", padx=20)
    entry.focus()
    entry.bind("<Return>", lambda event: register(settings, nickname.get()))

    button = tk.Button(root, text="Зарегистрировать")
    button["command"] = lambda: register(settings, nickname.get())
    button.pack(expand=True)

    if settings.token:
        answer = messagebox.askokcancel(
            "Пользователь уже зарегистрирован", "Повторить регистрацию?"
        )
        if not answer:
            root.destroy()

    root.mainloop()


if __name__ == "__main__":
    load_dotenv()
    argparser = get_argparser()
    settings = argparser.parse_args()
    try:
        settings.token = os.environ["TOKEN"]
    except KeyError:
        settings.token = None

    draw(settings)
