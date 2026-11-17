"""Raventon Partners web server: serves the static site and a small JSON API backed by SQLite.

Run:   python server.py            (http://localhost:8000)
       python server.py --port 9000
       python server.py dump       (print stored users and leads)

Data is stored in data/rvn.db (created automatically). Python standard library only.
"""
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import sys
import threading
import time
from http import cookies
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT, "data", "rvn.db")
SESSION_DAYS = 30
PBKDF2_ITERATIONS = 240_000
MAX_BODY = 32 * 1024
ROLES = ("advertiser", "publisher")
STATIC_EXT = {".html", ".css", ".js", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".ico", ".woff2", ".txt", ".xml"}
EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,190}\.[^@\s]{2,24}$")

_lock = threading.Lock()
_attempts = {}  # ip -> [timestamps] for simple login throttling


# ---------- database ----------
def db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL CHECK (role IN ('advertiser','publisher')),
            full_name TEXT NOT NULL,
            company TEXT,
            email TEXT NOT NULL,
            phone TEXT,
            website TEXT,
            details TEXT,
            account_type TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            country TEXT,
            marketing_opt_in INTEGER NOT NULL DEFAULT 0,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            last_login TEXT,
            UNIQUE (role, email)
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token_hash TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            expires_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            service TEXT,
            website TEXT,
            budget TEXT,
            goals TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """)
        # migrate databases created before the address/account-type columns existed
        have = {r[1] for r in c.execute("PRAGMA table_info(users)")}
        for col, typ in (("account_type", "TEXT"), ("address", "TEXT"), ("city", "TEXT"), ("state", "TEXT"),
                         ("country", "TEXT"), ("marketing_opt_in", "INTEGER NOT NULL DEFAULT 0")):
            if col not in have:
                c.execute(f"ALTER TABLE users ADD COLUMN {col} {typ}")


def hash_password(pw):
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${dk.hex()}"


def check_password(pw, stored):
    try:
        _, iters, salt, digest = stored.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), int(iters))
        return hmac.compare_digest(dk.hex(), digest)
    except (ValueError, TypeError):
        return False


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


def clean(data, key, limit=200):
    v = data.get(key, "")
    if not isinstance(v, str):
        return ""
    return v.strip()[:limit]


# ---------- request handler ----------
class Handler(SimpleHTTPRequestHandler):
    server_version = "Raventon/1.0"

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    # static files: only public site assets, never source, data or dotfiles
    def do_GET(self):
        path = urlparse(self.path).path
        if path.startswith("/api/"):
            return self.api_get(path)
        if path == "/":
            path = "/index.html"
        parts = [p for p in path.split("/") if p]
        ext = os.path.splitext(path)[1].lower()
        if (any(p.startswith(".") or p in ("data", "next-reference", "__pycache__") for p in parts)
                or ext not in STATIC_EXT):
            return self.not_found()
        full = os.path.join(ROOT, *parts)
        if not os.path.isfile(full):
            return self.not_found()
        return super().do_GET()

    def do_HEAD(self):
        return self.do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        routes = {"/api/register": self.api_register, "/api/login": self.api_login,
                  "/api/logout": self.api_logout, "/api/contact": self.api_contact}
        if path not in routes:
            return self.json(404, {"error": "Not found"})
        # same-origin check for state-changing requests
        origin = self.headers.get("Origin")
        if origin and urlparse(origin).netloc != self.headers.get("Host"):
            return self.json(403, {"error": "Cross-origin request blocked"})
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            n = 0
        if n > MAX_BODY:
            return self.json(413, {"error": "Request too large"})
        try:
            data = json.loads(self.rfile.read(n) or b"{}")
            if not isinstance(data, dict):
                raise ValueError
        except ValueError:
            return self.json(400, {"error": "Invalid request"})
        return routes[path](data)

    def not_found(self):
        page = os.path.join(ROOT, "404.html")
        body = open(page, "rb").read() if os.path.isfile(page) else b"Not found"
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def json(self, code, obj, cookie=None):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    # ---- sessions ----
    def current_user(self):
        jar = cookies.SimpleCookie(self.headers.get("Cookie", ""))
        if "rvn_session" not in jar:
            return None
        with db() as c:
            row = c.execute(
                "SELECT u.* FROM sessions s JOIN users u ON u.id = s.user_id "
                "WHERE s.token_hash = ? AND s.expires_at > ?",
                (token_hash(jar["rvn_session"].value), int(time.time()))).fetchone()
        return row

    def session_cookie(self, token, max_age):
        return f"rvn_session={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age}"

    # ---- API ----
    def api_get(self, path):
        if path == "/api/me":
            u = self.current_user()
            if not u:
                return self.json(401, {"error": "Not signed in"})
            return self.json(200, {"user": {k: u[k] for k in (
                "id", "role", "full_name", "company", "email", "phone", "website", "details", "account_type",
                "address", "city", "state", "country", "created_at", "last_login")}})
        if path == "/api/health":
            return self.json(200, {"ok": True})
        return self.json(404, {"error": "Not found"})

    def api_register(self, d):
        role = clean(d, "role", 20)
        name = clean(d, "full_name", 120) or " ".join(
            x for x in (clean(d, "first_name", 60), clean(d, "last_name", 60)) if x)
        email = clean(d, "email", 254).lower()
        pw = d.get("password") if isinstance(d.get("password"), str) else ""
        acct = clean(d, "account_type", 30)
        phone = " ".join(x for x in (clean(d, "phone_code", 6), clean(d, "phone", 30)) if x) if clean(d, "phone", 30) else ""
        if role not in ROLES:
            return self.json(400, {"error": "Choose advertiser or publisher."})
        if not name:
            return self.json(400, {"error": "Please enter your name."})
        if not EMAIL_RE.match(email):
            return self.json(400, {"error": "Please enter a valid email address."})
        if len(pw) < 8 or len(pw) > 200:
            return self.json(400, {"error": "Password must be at least 8 characters."})
        if acct and acct not in ("Individual", "Business Entity"):
            return self.json(400, {"error": "Choose an account type."})
        try:
            with db() as c:
                cur = c.execute(
                    "INSERT INTO users (role, full_name, company, email, phone, website, details, account_type, "
                    "address, city, state, country, marketing_opt_in, password_hash) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (role, name, clean(d, "company", 160), email, phone, clean(d, "website", 200),
                     clean(d, "details", 120), acct or None, clean(d, "address", 200), clean(d, "city", 100),
                     clean(d, "state", 100), clean(d, "country", 100), 1 if d.get("marketing") is True else 0,
                     hash_password(pw)))
                uid = cur.lastrowid
        except sqlite3.IntegrityError:
            return self.json(409, {"error": f"An {role} account with this email already exists."})
        return self.start_session(uid, 201)

    def api_login(self, d):
        ip = self.client_address[0]
        now = time.time()
        with _lock:
            recent = [t for t in _attempts.get(ip, []) if now - t < 600]
            _attempts[ip] = recent
            if len(recent) >= 10:
                return self.json(429, {"error": "Too many attempts. Please wait a few minutes."})
        role, email = clean(d, "role", 20), clean(d, "email", 254).lower()
        pw = d.get("password") if isinstance(d.get("password"), str) else ""
        with db() as c:
            u = c.execute("SELECT id, password_hash FROM users WHERE role = ? AND email = ?", (role, email)).fetchone()
        if not u or not check_password(pw, u["password_hash"]):
            with _lock:
                _attempts.setdefault(ip, []).append(now)
            return self.json(401, {"error": "Email or password is incorrect."})
        with db() as c:
            c.execute("UPDATE users SET last_login = datetime('now') WHERE id = ?", (u["id"],))
        return self.start_session(u["id"], 200, remember=bool(d.get("remember")))

    def start_session(self, uid, code, remember=True):
        token = secrets.token_urlsafe(32)
        days = SESSION_DAYS if remember else 1
        with db() as c:
            c.execute("DELETE FROM sessions WHERE expires_at < ?", (int(time.time()),))
            c.execute("INSERT INTO sessions VALUES (?,?,?)", (token_hash(token), uid, int(time.time()) + days * 86400))
        return self.json(code, {"ok": True, "redirect": "dashboard.html"},
                         cookie=self.session_cookie(token, days * 86400))

    def api_logout(self, d):
        jar = cookies.SimpleCookie(self.headers.get("Cookie", ""))
        if "rvn_session" in jar:
            with db() as c:
                c.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash(jar["rvn_session"].value),))
        return self.json(200, {"ok": True}, cookie=self.session_cookie("", 0))

    def api_contact(self, d):
        name, email = clean(d, "full_name", 120), clean(d, "email", 254).lower()
        if not name or not EMAIL_RE.match(email):
            return self.json(400, {"error": "Please enter your name and a valid email."})
        with db() as c:
            c.execute("INSERT INTO leads (full_name, email, phone, service, website, budget, goals) VALUES (?,?,?,?,?,?,?)",
                      (name, email, clean(d, "phone", 40), clean(d, "service", 120), clean(d, "website", 200),
                       clean(d, "budget", 60), clean(d, "goals", 4000)))
        return self.json(201, {"ok": True})


def dump():
    init_db()
    with db() as c:
        for table, cols in (("users", "id, role, account_type, full_name, company, email, phone, country, created_at, last_login"),
                            ("leads", "id, full_name, email, service, budget, created_at")):
            rows = c.execute(f"SELECT {cols} FROM {table} ORDER BY id DESC").fetchall()
            print(f"\n== {table} ({len(rows)})")
            for r in rows:
                print(" | ".join("" if v is None else str(v) for v in r))


def main():
    args = sys.argv[1:]
    if args and args[0] == "dump":
        return dump()
    port = int(args[args.index("--port") + 1]) if "--port" in args else 8000
    init_db()
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Raventon Partners running at http://localhost:{port}  (database: {DB_PATH})")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
