"""Raventon Partners local web server: serves the static site and the accounts API.

Run:   python server.py            (http://localhost:8000)
       python server.py --port 9000
       python server.py dump       (print stored users and leads)

Uses SQLite at data/rvn.db by default; set DATABASE_URL to use Postgres (needs `pip install -r requirements.txt`).
The API logic lives in api/_core.py and is shared with the Vercel function in api/index.py.
"""
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "api"))

import _core  # noqa: E402

STATIC_EXT = {".html", ".css", ".js", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".ico", ".woff2", ".txt", ".xml"}
BLOCKED_DIRS = {"data", "api", "next-reference", "__pycache__"}


class Handler(_core.APIHandlerMixin, SimpleHTTPRequestHandler):
    server_version = "Raventon/1.0"

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        super().end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path.startswith("/api/"):
            return self.serve_api()
        if path == "/":
            path = "/index.html"
        parts = [p for p in path.split("/") if p]
        ext = os.path.splitext(path)[1].lower()
        # only public site assets: never source files, the database or dotfiles
        if any(p.startswith(".") or p in BLOCKED_DIRS for p in parts) or ext not in STATIC_EXT \
                or not os.path.isfile(os.path.join(ROOT, *parts)):
            return self.not_found()
        return super().do_GET()

    def do_HEAD(self):
        return self.do_GET()

    def do_POST(self):
        if urlparse(self.path).path.startswith("/api/"):
            return self.serve_api()
        self.not_found()

    def not_found(self):
        page = os.path.join(ROOT, "404.html")
        body = open(page, "rb").read() if os.path.isfile(page) else b"Not found"
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)


def main():
    args = sys.argv[1:]
    if args and args[0] == "dump":
        return _core.dump()
    port = int(args[args.index("--port") + 1]) if "--port" in args else 8000
    _core.init_db()
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    where = "Postgres (DATABASE_URL)" if _core.PG_URL else _core.SQLITE_PATH
    print(f"Raventon Partners running at http://localhost:{port}  (database: {where})")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
