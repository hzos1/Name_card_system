"""PyInstaller 與一般啟動入口。"""

from __future__ import annotations

import os
import socket
import threading
import webbrowser

from app import app
from paths import ensure_runtime_files, is_frozen


def _local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def main() -> None:
    ensure_runtime_files()

    host = os.environ.get("NAMECARD_HOST", "127.0.0.1")
    port = int(os.environ.get("NAMECARD_PORT", "5000"))

    def _open_browser() -> None:
        webbrowser.open(f"http://127.0.0.1:{port}")

    if not is_frozen():
        if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
            threading.Timer(1.0, _open_browser).start()
    else:
        threading.Timer(1.5, _open_browser).start()

    print("======================================")
    print("Name Card System")
    print("======================================")
    print(f"本機網址：http://127.0.0.1:{port}")
    if host == "0.0.0.0":
        print(f"區域網路網址：http://{_local_ip()}:{port}")
    print("請保持此視窗開啟。關閉視窗即停止系統。")
    print("======================================")

    app.run(
        debug=not is_frozen(),
        use_reloader=not is_frozen(),
        host=host,
        port=port,
    )


if __name__ == "__main__":
    main()
