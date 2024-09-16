import os
from random import randrange
import sqlite3
from typing import Generator, Optional
from fastapi import Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel

#uvicorn main:app --reload

class Post_class(BaseModel):
    header: str
    description: str
    published: bool = True
    rating: Optional[int] = None
    id: int


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

@app.get("/indicator/{id}")
def get_indicator(id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id_indicator, name, description, units FROM indicator WHERE id_indicator = ?", (id,))
    row = cursor.fetchone()  # Usamos fetchone() porque esperamos una sola fila
    
    if row is None:
        raise HTTPException(status_code=404, detail=f"Indicator with id {id} not found")
    
    return {"data": dict(row)}  # Se devuelve el resultado como un diccionario









