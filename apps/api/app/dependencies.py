from __future__ import annotations

from collections.abc import Generator

import psycopg

from .config import settings


def get_connection() -> Generator[psycopg.Connection, None, None]:
    """Yield one PostgreSQL connection per API request and always close it."""
    connection = psycopg.connect(settings.database_url)
    try:
        yield connection
    finally:
        connection.close()
