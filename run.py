import threading
import webview
from app import app


def run_flask():
    app.run(port=5000)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    webview.create_window("Email Sender", "http://127.0.0.1:5000")