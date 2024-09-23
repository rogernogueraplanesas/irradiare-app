import os
import sqlite3
from typing import Generator
from fastapi import FastAPI

#uvicorn main:app --reload

app = FastAPI()

# Path to the db from the current script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "sqlite_db.db")

def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Provides a connection to the SQLite database. Ensures the connection is closed after usage.

    Yields:
        Generator[sqlite3.Connection, None, None]: A SQLite database connection.

    Closes:
        The database connection after the generator is consumed.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dicts.
    try:
        yield conn
    finally:
        conn.close()