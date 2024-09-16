import os
from random import randrange
import sqlite3
from typing import Generator, Optional, List
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

class IndicatorMetadataResponse(BaseModel):
    id_indicator: int
    name: str
    description: str
    units: str
    units_descr: str
    calculation: str
    source: str
    source_code: str
    attributes: Optional[str] = None
    class Config:
        from_attributes = True

# Endpoint para obtener los valores de un indicador específico
@app.get("/indicator/{id}", response_model=List[IndicatorMetadataResponse])
def get_indicator(id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
        SELECT id_indicator, name, description, units, units_desc AS units_descr, 
               calculation, source, source_code, attributes 
        FROM indicator 
        WHERE id_indicator = ?
    """, (id,))
    
    rows = cursor.fetchall()  # Usamos fetchall() para obtener todas las filas
    
    if not rows:
        raise HTTPException(status_code=404, detail=f"Indicator with id {id} not found")
    
    # Convertir cada fila en un diccionario que coincida con el modelo
    return [dict(row) for row in rows]  # Devolver todos los resultados como una lista de diccionarios
