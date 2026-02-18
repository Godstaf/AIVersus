"""
OAuth2 JWT Authentication Module
================================
Mirrors the structure from Fast-API-Tutorial-main/main.py,
adapted for Flask.

Components:
  - Password hashing (bcrypt via passlib)
  - JWT token creation / verification (python-jose)
  - token_required decorator (Flask equivalent of FastAPI Depends)
"""

from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import request, jsonify
from jose import JWTError, jwt
from werkzeug.security import generate_password_hash, check_password_hash
import os

# ── Configuration ──────────────────────────────────────────────
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11662")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ── Password Hashing (Werkzeug) ─────────────────────────────────
# Replaced passlib due to incompatibility with newer bcrypt/Python versions

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hash."""
    try:
        return check_password_hash(hashed_password, plain_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return generate_password_hash(password)


# ── JWT Token ──────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload dict (must include "sub" for the user identifier)
        expires_delta: Optional custom expiry duration
    
    Returns:
        Encoded JWT string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    
    Returns:
        Decoded payload dict
    
    Raises:
        JWTError: If token is invalid or expired
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# ── Flask Decorator (equivalent to FastAPI Depends) ────────────

def token_required(f):
    """
    Flask decorator that protects a route with JWT authentication.
    
    Equivalent to FastAPI's:
        async def get_current_user(token: str = Depends(oauth2_scheme))
    
    Usage:
        @app.route("/protected")
        @token_required
        def protected_route(current_user_email):
            ...
    
    The decorated function receives `current_user_email` as its first argument.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Extract Bearer token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

        if not token:
            return jsonify({
                "status": "error",
                "message": "Authentication required. Please log in."
            }), 401

        try:
            payload = decode_access_token(token)
            current_user_email = payload.get("sub")
            if current_user_email is None:
                return jsonify({
                    "status": "error",
                    "message": "Invalid token: no user identifier"
                }), 401
        except JWTError:
            return jsonify({
                "status": "error",
                "message": "Token is invalid or expired. Please log in again."
            }), 401

        # Pass the authenticated user's email to the route function
        return f(current_user_email, *args, **kwargs)

    return decorated
