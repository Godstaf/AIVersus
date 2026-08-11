"""
OAuth2 / JWT Authentication Module
==================================
A faithful port of the standard FastAPI OAuth2-password + JWT tutorial
(Fast-API-Tutorial-main/main.py) into this Flask app. Same building blocks,
same names, adapted to Flask idioms and a PostgreSQL-backed user store:

  - Typed models          -> Token, TokenData, User, UserInDB (dataclasses)
  - Password hashing      -> bcrypt ($2b$ hashes, like the tutorial)
  - Token create/decode   -> python-jose, HS256
  - get_user / authenticate_user
  - get_current_user / get_current_active_user  (the "disabled" gate)
  - token_required        -> Flask equivalent of FastAPI's Depends(get_current_active_user)

Note on hashing: the tutorial uses passlib's CryptContext(schemes=["bcrypt"]),
but passlib 1.7.4 is incompatible with bcrypt >= 4.1 / Python 3.13+ (its backend
detection crashes). We therefore call the `bcrypt` library directly, which
produces the exact same `$2b$` hashes. Existing users hashed by the previous
Werkzeug implementation (pbkdf2:/scrypt: prefixes) are still verified, so no one
is locked out.
"""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Optional

import bcrypt
import psycopg2
from flask import request, jsonify, g
from jose import JWTError, jwt
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

from db import get_cursor

# Ensure .env is loaded before we read secrets (auth.py may be imported before
# app.py calls load_dotenv()).
load_dotenv()

# ── Configuration ──────────────────────────────────────────────
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Never fall back to a known/weak secret: forge-able tokens = full account
# takeover. Fail fast at startup instead.
_WEAK_SECRETS = {
    "",
    "changeme",
    "change_this_to_a_long_random_string",
    "83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11662",  # the tutorial's public secret
}
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
if SECRET_KEY in _WEAK_SECRETS:
    raise RuntimeError(
        "JWT_SECRET_KEY is missing or set to a known-weak value. "
        "Generate a strong one with:\n"
        '    python -c "import secrets; print(secrets.token_hex(32))"\n'
        "and set it in your environment / .env as JWT_SECRET_KEY."
    )


# ── Models (mirror the tutorial's Pydantic models) ─────────────
@dataclass
class Token:
    access_token: str
    token_type: str


@dataclass
class TokenData:
    username: Optional[str] = None


@dataclass
class User:
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


@dataclass
class UserInDB(User):
    hashed_password: str = ""


# ── Auth errors (Flask equivalent of the tutorial's HTTPException) ──
class AuthError(Exception):
    """Raised by the auth dependency chain; carries an HTTP status + message."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


# ── Password hashing (bcrypt, with legacy Werkzeug fallback) ───
def _to_bcrypt_bytes(password: str) -> bytes:
    # bcrypt only uses the first 72 bytes and errors on longer input.
    return password.encode("utf-8")[:72]


def get_password_hash(password: str) -> str:
    """Hash a password with bcrypt (returns a `$2b$...` string)."""
    return bcrypt.hashpw(_to_bcrypt_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a stored hash.

    Handles both new bcrypt hashes and legacy Werkzeug hashes (pbkdf2:/scrypt:)
    so existing accounts keep working after the migration to bcrypt.
    """
    if not hashed_password:
        return False
    try:
        if hashed_password.startswith(("pbkdf2:", "scrypt:")):
            return check_password_hash(hashed_password, plain_password)
        return bcrypt.checkpw(_to_bcrypt_bytes(plain_password),
                              hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def is_legacy_hash(hashed_password: str) -> bool:
    """True if the stored hash is an old Werkzeug hash (candidate for re-hashing)."""
    return bool(hashed_password) and hashed_password.startswith(("pbkdf2:", "scrypt:"))


# ── User store (Postgres "user" table; tutorial used an in-memory dict) ──
def get_user(email: str) -> Optional[UserInDB]:
    """Look up a user by email. Returns a UserInDB or None."""
    row = None
    try:
        with get_cursor() as cur:
            cur.execute(
                'SELECT name, email, password, disabled FROM "user" WHERE email = %s',
                (email,),
            )
            row = cur.fetchone()
    except psycopg2.errors.UndefinedColumn:
        # 'disabled' column not migrated yet — fall back gracefully.
        with get_cursor() as cur:
            cur.execute(
                'SELECT name, email, password FROM "user" WHERE email = %s',
                (email,),
            )
            base = cur.fetchone()
            if base is not None:
                row = (base[0], base[1], base[2], False)

    if row is None:
        return None

    name, user_email, hashed_password, disabled = row
    return UserInDB(
        username=user_email,
        email=user_email,
        full_name=name,
        disabled=bool(disabled),
        hashed_password=hashed_password,
    )


def authenticate_user(email: str, password: str):
    """Return the UserInDB if credentials are valid, else False (tutorial parity)."""
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# ── JWT token ──────────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT. `data` must include a 'sub' claim (the user id)."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT. Raises jose.JWTError if invalid/expired."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# ── Dependency chain (mirrors get_current_user / get_current_active_user) ──
def get_current_user(token: str) -> UserInDB:
    """Decode the token and load the matching user, or raise AuthError(401)."""
    credentials_error = AuthError(401, "Could not validate credentials")
    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
        if email is None:
            raise credentials_error
        token_data = TokenData(username=email)
    except JWTError:
        raise credentials_error

    user = get_user(token_data.username)
    if user is None:
        raise credentials_error
    return user


def get_current_active_user(current_user: UserInDB) -> UserInDB:
    """Reject disabled accounts, mirroring the tutorial's active-user gate."""
    if current_user.disabled:
        raise AuthError(400, "Inactive user")
    return current_user


# ── Flask route guard (equivalent to FastAPI's Depends(get_current_active_user)) ──
def token_required(f):
    """
    Protect a route with JWT auth. Runs the full dependency chain
    (get_current_user -> get_current_active_user), stashes the resolved user on
    ``flask.g.current_user``, and passes the user's email as the first argument
    to the view (preserving the existing route signatures).
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.split(" ", 1)[1] if auth_header.startswith("Bearer ") else None

        if not token:
            return jsonify({
                "status": "error",
                "message": "Authentication required. Please log in.",
            }), 401

        try:
            user = get_current_active_user(get_current_user(token))
        except AuthError as e:
            return jsonify({"status": "error", "message": e.message}), e.status_code

        g.current_user = user
        return f(user.email, *args, **kwargs)

    return decorated
