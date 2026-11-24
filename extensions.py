"""Database helper. One MySQL connection per request, closed automatically."""
from decimal import Decimal

import mysql.connector
from flask import current_app, g


def get_db():
    if "db" not in g:
        cfg = current_app.config
        g.db = mysql.connector.connect(
            host=cfg["DB_HOST"],
            port=cfg["DB_PORT"],
            user=cfg["DB_USER"],
            password=cfg["DB_PASSWORD"],
            database=cfg["DB_NAME"],
            charset="utf8mb4",
            autocommit=False,
        )
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def _clean(row):
    # Decimal -> float so JSON and templates work easily
    return {k: (float(v) if isinstance(v, Decimal) else v) for k, v in row.items()}


def query(sql, params=(), one=False):
    """Run a SELECT. Always pass values in params (never build SQL with f-strings)."""
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        rows = [_clean(r) for r in cur.fetchall()]
    finally:
        cur.close()
    db.rollback()  # end the read transaction so the next read is fresh
    if one:
        return rows[0] if rows else None
    return rows


def execute(sql, params=()):
    """Run INSERT / UPDATE / DELETE and commit. Returns the new row id."""
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute(sql, params)
        db.commit()
        return cur.lastrowid
    except Exception:
        db.rollback()
        raise
    finally:
        cur.close()


def placeholders(n):
    """'%s,%s,%s' for IN (...) queries."""
    return ",".join(["%s"] * n)
