"""
Launcher silencioso para IMPRESSAO ALMOX.
- Se o servidor já estiver rodando: só abre o browser.
- Se não estiver: inicia o servidor e depois abre o browser.
- Com --no-browser: inicia só o servidor (uso no auto-start do Windows).
"""
import os
import socket
import subprocess
import sys
import time
import webbrowser

PORT = 5000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def is_running() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect(("127.0.0.1", PORT))
            return True
        except OSError:
            return False


def start_server() -> None:
    subprocess.Popen(
        [sys.executable, os.path.join(BASE_DIR, "app.py")],
        cwd=BASE_DIR,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def open_browser() -> None:
    hostname = socket.gethostname()
    webbrowser.open(f"http://{hostname}:{PORT}/")


if __name__ == "__main__":
    no_browser = "--no-browser" in sys.argv

    if not is_running():
        start_server()
        if not no_browser:
            time.sleep(2.5)

    if not no_browser:
        open_browser()
