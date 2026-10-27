import socket
import threading
import time
import webview
from waitress import serve

from app import app, initialize_database


def get_free_port():
    # Ask Windows for an available local port.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def start_server(port):
    serve(app, host="127.0.0.1", port=port, threads=8)


def main():
    initialize_database()
    port = get_free_port()

    server_thread = threading.Thread(
        target=start_server,
        args=(port,),
        daemon=True
    )
    server_thread.start()

    # Give the local Flask/Waitress server a moment to start.
    time.sleep(1)

    webview.create_window(
        "DarkWeb Threat Monitoring System",
        f"http://127.0.0.1:{port}/",
        width=1280,
        height=820,
        min_size=(900, 600),
        background_color="#080d18"
    )
    webview.start()


if __name__ == "__main__":
    main()
