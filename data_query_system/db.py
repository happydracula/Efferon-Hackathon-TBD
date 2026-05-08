

import os
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cloud:scape@localhost:5432/hack_db",
)

# Lazy-initialised thread-safe connection pool
_pool: pool.ThreadedConnectionPool | None = None


def get_pool() -> pool.ThreadedConnectionPool:
    global _pool
    if _pool is None:
        _pool = pool.ThreadedConnectionPool(minconn=1, maxconn=10, dsn=DATABASE_URL)
    return _pool


def get_conn():
    """Borrow a connection from the pool."""
    return get_pool().getconn()


def put_conn(conn) -> None:
    """Return a connection to the pool."""
    get_pool().putconn(conn)


def apply_schema() -> None:
    """Create all tables/indexes/views if they do not yet exist."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path) as f:
        sql = f.read()
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print("[db] Schema applied successfully.")
    finally:
        put_conn(conn)