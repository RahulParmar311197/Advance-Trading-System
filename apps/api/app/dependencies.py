from __future__ import annotations

from collections.abc import Generator

import psycopg

from .config import settings


def get_connection() -> Generator[psycopg.Connection, None, None]:
    """Yield one PostgreSQL connection per API request with a bounded connect timeout."""
    connection = psycopg.connect(
        settings.database_url,
        connect_timeout=settings.database_connect_timeout_seconds,
    )
    try:
        yield connection
    finally:
        connection.close()
