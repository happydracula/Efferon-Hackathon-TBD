"""
setup_db.py
-----------
Run once to create the database, user, and apply the schema.

Usage
-----
    # As the postgres superuser:
    python setup_db.py

Alternatively, run the SQL manually (see comments below).
"""

import os
import subprocess
import sys

DB_NAME = "sepsis_atlas"
DB_USER = "sepsis_user"
DB_PASS = "sepsis_pass"


def run_psql(sql: str, db: str = "postgres") -> None:
    result = subprocess.run(
        ["psql", "-h", "127.0.0.1", "-U", "postgres", "-d", db, "-c", sql],
        capture_output=True, text=True
    )
    if result.returncode != 0 and "already exists" not in result.stderr:
        print(f"[psql] stderr: {result.stderr.strip()}")
    else:
        print(f"[psql] OK: {sql[:60]}")


def main():
    print("=== Sepsis Atlas – Database Setup ===\n")

    run_psql(f"CREATE USER {DB_USER} WITH PASSWORD '{DB_PASS}';")
    run_psql(f"CREATE DATABASE {DB_NAME} OWNER {DB_USER};")
    run_psql(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER};")

    # Enable pgvector in the new database
    run_psql("CREATE EXTENSION IF NOT EXISTS vector;", db=DB_NAME)

    # Apply schema
    schema_path = os.path.join(os.path.dirname(__file__), "db", "schema.sql")
    result = subprocess.run(
        ["psql", "-h", "127.0.0.1", "-U", DB_USER, "-d", DB_NAME, "-f", schema_path],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print(f"[psql] stderr: {result.stderr.strip()}")

    print("\n✅ Database ready. Copy .env.example to .env and update if needed.")


if __name__ == "__main__":
    main()
