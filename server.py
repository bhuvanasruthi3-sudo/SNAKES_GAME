"""Web server for browser-based Snake (Render / Docker deploy)."""
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parent / "web"


class GameHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            self.path = "/index.html"
        return super().do_GET()

    def end_headers(self):
        if self.path.endswith(".html") or self.path == "/index.html":
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
        super().end_headers()

    def log_message(self, fmt, *args):
        if args and args[1] != "200":
            super().log_message(fmt, *args)


def main():
    if not (WEB_DIR / "index.html").is_file():
        raise SystemExit(f"Missing game files: {WEB_DIR / 'index.html'}")

    port = int(os.environ.get("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), GameHandler)
    print(f"Snake game running at http://0.0.0.0:{port}")
    print(f"Serving from {WEB_DIR}")
    server.serve_forever()


if __name__ == "__main__":
    main()
