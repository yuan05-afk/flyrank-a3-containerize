"""
Repository — the ONLY module that talks to Postgres.

Storage swap #3: memory (A1) -> SQLite (A2) -> Postgres (A3). The routes never
change; only this file knows about the database. Every query is parameterized
(psycopg uses %s placeholders) so user input is never glued into SQL.
"""

from __future__ import annotations

import os
from typing import Any

import psycopg
from psycopg.rows import dict_row

SEED_TASKS = [
    ("Draft SEO report outline for client onboarding", False),
    ("Review Crawl API response schemas", True),
    ("Run the whole stack with one command", False),
]


def _dsn() -> str:
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL is not set (copy .env.example to .env)")
    # psycopg accepts postgres:// and postgresql://
    return dsn


def connect() -> psycopg.Connection:
    return psycopg.connect(_dsn(), row_factory=dict_row)


def init_db() -> None:
    """Create the table if missing and seed three tasks only on first run."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id    SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done  BOOLEAN NOT NULL DEFAULT FALSE
            )
            """
        )
        cur.execute("SELECT COUNT(*) AS c FROM tasks")
        if cur.fetchone()["c"] == 0:
            cur.executemany(
                "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                SEED_TASKS,
            )
        conn.commit()


def list_tasks() -> list[dict[str, Any]]:
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM tasks ORDER BY id")
        return cur.fetchall()


def get_task(task_id: int) -> dict[str, Any] | None:
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        return cur.fetchone()


def create_task(title: str) -> dict[str, Any]:
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *",
            (title, False),
        )
        row = cur.fetchone()
        conn.commit()
        return row


def update_task(task_id: int, title: str, done: bool) -> dict[str, Any] | None:
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *",
            (title, done, task_id),
        )
        row = cur.fetchone()
        conn.commit()
        return row


def delete_task(task_id: int) -> bool:
    with connect() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        deleted = cur.rowcount > 0
        conn.commit()
        return deleted


def ping() -> bool:
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1")
        return cur.fetchone() is not None
