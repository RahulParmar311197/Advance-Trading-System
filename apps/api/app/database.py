from __future__ import annotations

from collections.abc import Iterator

import psycopg

from .config import settings


def connection() -> Iterator[psycopg.Connection]:
    """Open a short-lived PostgreSQL connection for a request/job."""
    conn = psycopg.connect(settings.database_url)
    try:
        yield conn
    finally:
        conn.close()
