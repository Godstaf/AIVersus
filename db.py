"""
Per-request PostgreSQL connection helper
=========================================
Replaces the old module-level global connection/cursor that was shared across
every request (not thread-safe, and a failed query could leave the connection
stuck in an aborted-transaction state for later requests).

Instead, each request gets its own connection, stored on Flask's ``g`` object
and closed automatically when the request ends.

Usage:
    from db import get_cursor

    # read
    with get_cursor() as cur:
        cur.execute('SELECT ... ')
        row = cur.fetchone()

    # write (commit on success, rollback on error)
    with get_cursor(commit=True) as cur:
        cur.execute('INSERT ...', (...))
"""

import os
from contextlib import contextmanager

import psycopg2
from flask import g


def _connect():
    """Open a new psycopg2 connection using the DB_* environment variables."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME", "aiversus"),
    )


def get_db():
    """
    Return the connection for the current request, opening one on first use.

    The connection lives on ``flask.g`` so it is reused for the rest of the
    request and closed by ``close_db`` in the app teardown.
    """
    if "db_conn" not in g:
        g.db_conn = _connect()
    return g.db_conn


@contextmanager
def get_cursor(commit=False):
    """
    Yield a cursor from the current request's connection.

    On success, commits when ``commit=True``. On any exception the transaction
    is rolled back so the shared connection is never left in an aborted state.
    The cursor is always closed.
    """
    conn = get_db()
    cur = conn.cursor()
    try:
        yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def close_db(exc=None):
    """Close the request's connection, if any. Registered as a teardown handler."""
    conn = g.pop("db_conn", None)
    if conn is not None:
        conn.close()
