"""Recite Coach Launcher — silent background server, opens browser.

Starts a local HTTP server, serves recite-player.html and cards.json.
Progress is stored in .recite-progress.json on disk so it survives
across EXE restarts (port is fixed).
"""

import atexit
import http.server
import socket
import sys
import time
import webbrowser
import os
import json
import threading

HOST = "127.0.0.1"
DATA_FILE = "cards.json"
PLAYER_FILE = "recite-player.html"
PROGRESS_FILE = ".recite-progress.json"
FIXED_PORTS = [18765, 18766, 18767]

_shutdown_event = threading.Event()


def find_port():
    for p in FIXED_PORTS:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((HOST, p))
            s.close()
            return p
        except OSError:
            s.close()
    # Fallback: random free port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, 0))
    port = s.getsockname()[1]
    s.close()
    return port


def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def read_progress(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def write_progress(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


class ReciteHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler: silent logging, /shutdown, /progress."""

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == '/progress':
            data = read_progress(os.path.join(get_base_dir(), PROGRESS_FILE))
            self._json_response(data)
            return
        if self.path == '/' or self.path == '/index.html':
            self.send_response(302)
            self.send_header('Location', f'/{PLAYER_FILE}?data={DATA_FILE}')
            self.end_headers()
            return
        super().do_GET()

    def do_POST(self):
        if self.path == '/shutdown':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'ok')
            _shutdown_event.set()
            return
        if self.path == '/progress':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length) if length else b'{}'
            try:
                data = json.loads(body)
            except Exception:
                data = {}
            write_progress(os.path.join(get_base_dir(), PROGRESS_FILE), data)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'ok')
            return
        self.send_response(404)
        self.end_headers()

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def _json_response(self, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)


def shutdown_watcher(httpd):
    _shutdown_event.wait()
    httpd.shutdown()


# Module-level refs for atexit cleanup
_devnull = None
_httpd = None


def _cleanup():
    """Release OS handles so PyInstaller can clean its temp dir."""
    if _httpd:
        try:
            _httpd.server_close()
        except Exception:
            pass
    if _devnull:
        try:
            _devnull.close()
        except Exception:
            pass
    time.sleep(0.3)


def main():
    global _devnull, _httpd
    atexit.register(_cleanup)

    base_dir = get_base_dir()
    os.chdir(base_dir)

    # Suppress output for silent background run
    _devnull = open(os.devnull, 'w')
    sys.stdout = _devnull
    sys.stderr = _devnull

    player_path = os.path.join(base_dir, PLAYER_FILE)
    if not os.path.exists(player_path):
        sys.exit(2)

    port = find_port()
    _httpd = http.server.HTTPServer((HOST, port), ReciteHandler)

    url = f"http://{HOST}:{port}/{PLAYER_FILE}?data={DATA_FILE}"
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    threading.Thread(target=shutdown_watcher, args=(_httpd,), daemon=True).start()

    _httpd.serve_forever()


if __name__ == "__main__":
    main()
