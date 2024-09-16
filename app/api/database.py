import os
import sqlite3
from typing import Generator
from fastapi import FastAPI

#uvicorn main:app --reload

app = FastAPI()

# Define la ruta al archivo de la base de datos desde la ubicación del script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "sqlite_db.db")

def get_db() -> Generator:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Devuelve filas como diccionarios
    try:
        yield conn
    finally:
        conn.close()