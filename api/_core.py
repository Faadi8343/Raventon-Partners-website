"""Shared account/lead API for Raventon Partners.

Used by both the local server (server.py, SQLite) and the Vercel function (api/index.py).
Storage: Postgres when DATABASE_URL or POSTGRES_URL is set, otherwise SQLite at data/rvn.db.
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
from datetime import datetime, timezone
from http import cookies
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_PATH = os.environ.get("RVN_SQLITE_PATH") or os.path.join(ROOT, "data", "rvn.db")


def _find_pg_url():
    """DATABASE_URL / POSTGRES_URL, also when the Vercel integration added a custom prefix (e.g. STORAGE_DATABASE_URL)."""
    for key in ("DATABASE_URL", "POSTGRES_URL"):
        if os.environ.get(key):
            return os.environ[key]
    for suffix in ("DATABASE_URL", "POSTGRES_URL"):
        for key, val in sorted(os.environ.items()):
            if key.upper().endswith(suffix) and val.startswith(("postgres://", "postgresql://")):
                return val
    return None


PG_URL = _find_pg_url()

SESSION_DAYS = 30
PBKDF2_ITERATIONS = 240_000
MAX_BODY = 32 * 1024
ROLES = ("advertiser", "publisher")
ACCOUNT_TYPES = ("Individual", "Business Entity")
EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,190}\.[^@\s]{2,24}$")
USER_FIELDS = ("id", "role", "full_name", "company", "email", "phone", "website", "details", "account_type",
               "address", "city", "state", "country", "created_at", "last_login")

_lock = threading.Lock()
_attempts = {}  # ip -> [timestamps]; best-effort login throttling per process
_ready = False


# ---------- storage ----------
class DB:
    """Tiny adapter so the same SQL ("?" placeholders) runs on SQLite and Postgres."""

    def __init__(self):
        self.pg = bool(PG_URL)
        if self.pg:
            import psycopg
            from psycopg.rows import dict_row
            self.conn = psycopg.connect(PG_URL, row_factory=dict_row, connect_timeout=10)
        else:
            os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
            self.conn = sqlite3.connect(SQLITE_PATH, timeout=10)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, *_):
        try:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
        finally:
            self.conn.close()

    def run(self, sql, args=()):
        return self.conn.execute(sql.replace("?", "%s") if self.pg else sql, args)

    def one(self, sql, args=()):
        row = self.run(sql, args).fetchone()
        return dict(row) if row else None

    def all(self, sql, args=()):
        return [dict(r) for r in self.run(sql, args).fetchall()]


def integrity_errors():
    errs = [sqlite3.IntegrityError]
    if PG_URL:
        import psycopg
        errs.append(psycopg.IntegrityError)
    return tuple(errs)


def init_db():
    global _ready
    if _ready:
        return
    with DB() as db:
        idcol = "BIGSERIAL PRIMARY KEY" if db.pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
        for stmt in (
            f"""CREATE TABLE IF NOT EXISTS users (
                id {idcol},
                role TEXT NOT NULL CHECK (role IN ('advertiser','publisher')),
                full_name TEXT NOT NULL, company TEXT, email TEXT NOT NULL, phone TEXT, website TEXT,
                details TEXT, account_type TEXT, address TEXT, city TEXT, state TEXT, country TEXT,
                marketing_opt_in INTEGER NOT NULL DEFAULT 0,
                password_hash TEXT NOT NULL, created_at TEXT NOT NULL, last_login TEXT,
                UNIQUE (role, email))""",
            """CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at BIGINT NOT NULL)""",
            f"""CREATE TABLE IF NOT EXISTS leads (
                id {idcol},
                full_name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT, service TEXT, website TEXT,
                budget TEXT, goals TEXT, created_at TEXT NOT NULL)""",
        ):
            db.run(stmt)
        # bring older databases up to the current columns
        cols = (("account_type", "TEXT"), ("address", "TEXT"), ("city", "TEXT"), ("state", "TEXT"),
                ("country", "TEXT"), ("marketing_opt_in", "INTEGER NOT NULL DEFAULT 0"))
        if db.pg:
            for col, typ in cols:
                db.run(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col} {typ}")
        else:
            have = {r["name"] for r in db.all("PRAGMA table_info(users)")}
            for col, typ in cols:
                if col not in have:
                    db.run(f"ALTER TABLE users ADD COLUMN {col} {typ}")
    _ready = True


# ---------- helpers ----------
def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


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


def clean(d, key, limit=200):
    v = d.get(key, "")
    return v.strip()[:limit] if isinstance(v, str) else ""


class Request:
    def __init__(self, method, path, headers, body, ip):
        self.method, self.headers, self.body, self.ip = method, headers, body, ip
        u = urlparse(path)
        route = parse_qs(u.query).get("route", [""])[0]  # set by the Vercel rewrite
        self.route = "/" + (route.strip("/") if route else u.path.split("/api/", 1)[-1].strip("/"))

    @property
    def https(self):
        return (self.headers.get("X-Forwarded-Proto") or "").lower() == "https"

    def cookie(self, name):
        jar = cookies.SimpleCookie(self.headers.get("Cookie", ""))
        return jar[name].value if name in jar else None


def session_cookie(req, token, max_age):
    c = f"rvn_session={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age}"
    return c + "; Secure" if req.https else c


# ---------- API ----------
def handle(req):
    """Returns (status, payload_dict, set_cookie_or_None)."""
    try:
        init_db()
    except Exception as exc:
        # log the cause (and which database-like env var NAMES exist, never values) for the runtime logs
        names = sorted(k for k in os.environ if "DATABASE" in k.upper() or "POSTGRES" in k.upper() or "PG" in k.upper())
        print(f"[raventon] database unavailable: {type(exc).__name__}: {exc}; pg={bool(PG_URL)}; env names={names}",
              file=sys.stderr)
        return 503, {"error": "Database is not available. Please try again shortly."}, None
    if req.method == "GET":
        if req.route == "/me":
            return me(req)
        if req.route == "/health":
            return 200, {"ok": True, "db": "postgres" if PG_URL else "sqlite"}, None
        return 404, {"error": "Not found"}, None
    if req.method != "POST":
        return 405, {"error": "Method not allowed"}, None
    origin = req.headers.get("Origin")
    host = req.headers.get("X-Forwarded-Host") or req.headers.get("Host")
    if origin and urlparse(origin).netloc != host:
        return 403, {"error": "Cross-origin request blocked"}, None
    if len(req.body) > MAX_BODY:
        return 413, {"error": "Request too large"}, None
    try:
        data = json.loads(req.body or b"{}")
        if not isinstance(data, dict):
            raise ValueError
    except ValueError:
        return 400, {"error": "Invalid request"}, None
    routes = {"/register": register, "/login": login, "/logout": logout, "/contact": contact}
    if req.route not in routes:
        return 404, {"error": "Not found"}, None
    return routes[req.route](req, data)


def current_user(req):
    tok = req.cookie("rvn_session")
    if not tok:
        return None
    with DB() as db:
        return db.one("SELECT u.* FROM sessions s JOIN users u ON u.id = s.user_id "
                      "WHERE s.token_hash = ? AND s.expires_at > ?", (token_hash(tok), int(time.time())))


def me(req):
    u = current_user(req)
    if not u:
        return 401, {"error": "Not signed in"}, None
    return 200, {"user": {k: u.get(k) for k in USER_FIELDS}}, None


def start_session(req, uid, code, remember=True):
    token = secrets.token_urlsafe(32)
    days = SESSION_DAYS if remember else 1
    with DB() as db:
        db.run("DELETE FROM sessions WHERE expires_at < ?", (int(time.time()),))
        db.run("INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?,?,?)",
               (token_hash(token), uid, int(time.time()) + days * 86400))
    return code, {"ok": True, "redirect": "dashboard.html"}, session_cookie(req, token, days * 86400)


def register(req, d):
    role = clean(d, "role", 20)
    name = clean(d, "full_name", 120) or " ".join(x for x in (clean(d, "first_name", 60), clean(d, "last_name", 60)) if x)
    email = clean(d, "email", 254).lower()
    pw = d.get("password") if isinstance(d.get("password"), str) else ""
    acct = clean(d, "account_type", 30)
    phone = " ".join(x for x in (clean(d, "phone_code", 6), clean(d, "phone", 30)) if x) if clean(d, "phone", 30) else ""
    if role not in ROLES:
        return 400, {"error": "Choose advertiser or publisher."}, None
    if not name:
        return 400, {"error": "Please enter your name."}, None
    if not EMAIL_RE.match(email):
        return 400, {"error": "Please enter a valid email address."}, None
    if len(pw) < 8 or len(pw) > 200:
        return 400, {"error": "Password must be at least 8 characters."}, None
    if acct and acct not in ACCOUNT_TYPES:
        return 400, {"error": "Choose an account type."}, None
    try:
        with DB() as db:
            row = db.one(
                "INSERT INTO users (role, full_name, company, email, phone, website, details, account_type, address, "
                "city, state, country, marketing_opt_in, password_hash, created_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) RETURNING id",
                (role, name, clean(d, "company", 160), email, phone, clean(d, "website", 200), clean(d, "details", 120),
                 acct or None, clean(d, "address", 200), clean(d, "city", 100), clean(d, "state", 100),
                 clean(d, "country", 100), 1 if d.get("marketing") is True else 0, hash_password(pw), now_iso()))
    except integrity_errors():
        return 409, {"error": f"An {role} account with this email already exists."}, None
    return start_session(req, row["id"], 201)


def login(req, d):
    now = time.time()
    with _lock:
        recent = [t for t in _attempts.get(req.ip, []) if now - t < 600]
        _attempts[req.ip] = recent
        if len(recent) >= 10:
            return 429, {"error": "Too many attempts. Please wait a few minutes."}, None
    role, email = clean(d, "role", 20), clean(d, "email", 254).lower()
    pw = d.get("password") if isinstance(d.get("password"), str) else ""
    with DB() as db:
        u = db.one("SELECT id, password_hash FROM users WHERE role = ? AND email = ?", (role, email))
    if not u or not check_password(pw, u["password_hash"]):
        with _lock:
            _attempts.setdefault(req.ip, []).append(now)
        return 401, {"error": "Email or password is incorrect."}, None
    with DB() as db:
        db.run("UPDATE users SET last_login = ? WHERE id = ?", (now_iso(), u["id"]))
    return start_session(req, u["id"], 200, remember=d.get("remember") is True)


def logout(req, d):
    tok = req.cookie("rvn_session")
    if tok:
        with DB() as db:
            db.run("DELETE FROM sessions WHERE token_hash = ?", (token_hash(tok),))
    return 200, {"ok": True}, session_cookie(req, "", 0)


def contact(req, d):
    name, email = clean(d, "full_name", 120), clean(d, "email", 254).lower()
    if not name or not EMAIL_RE.match(email):
        return 400, {"error": "Please enter your name and a valid email."}, None
    with DB() as db:
        db.run("INSERT INTO leads (full_name, email, phone, service, website, budget, goals, created_at) "
               "VALUES (?,?,?,?,?,?,?,?)",
               (name, email, clean(d, "phone", 40), clean(d, "service", 120), clean(d, "website", 200),
                clean(d, "budget", 60), clean(d, "goals", 4000), now_iso()))
    return 201, {"ok": True}, None


def dump():
    init_db()
    with DB() as db:
        for table, cols in (("users", "id, role, account_type, full_name, company, email, phone, country, created_at, last_login"),
                            ("leads", "id, full_name, email, service, budget, created_at")):
            rows = db.all(f"SELECT {cols} FROM {table} ORDER BY id DESC")
            print(f"\n== {table} ({len(rows)})")
            for r in rows:
                print(" | ".join("" if v is None else str(v) for v in r.values()))


# ---------- HTTP glue ----------
class APIHandlerMixin:
    """Mix into a BaseHTTPRequestHandler to answer /api/* requests."""

    def client_ip(self):
        fwd = self.headers.get("X-Forwarded-For")
        return fwd.split(",")[0].strip() if fwd else self.client_address[0]

    def serve_api(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            n = 0
        body = self.rfile.read(min(n, MAX_BODY + 1)) if n else b""
        status, payload, cookie = handle(Request(self.command, self.path, self.headers, body, self.client_ip()))
        raw = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(raw)


class VercelHandler(APIHandlerMixin, BaseHTTPRequestHandler):
    def do_GET(self):
        self.serve_api()

    def do_POST(self):
        self.serve_api()
