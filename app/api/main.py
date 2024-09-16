import os
from random import randrange
import sqlite3
from typing import Generator, Optional, List
from fastapi import Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel

import schemas as s

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

# Endpoint para obtener los valores de un indicador específico
@app.get("/indicator/{id}", response_model=List[s.IndicatorMetadataResponse])
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


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=s.User_Response)
def create_user(user: s.User_Class, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Ejecutar la consulta para insertar un nuevo usuario
    cursor.execute("""
        INSERT INTO users (email, password)
        VALUES (?, ?)
    """, (user.email, user.password))
    
    # Confirmar los cambios en la base de datos
    db.commit()
    
    # Obtener el ID del último registro insertado
    id_user = cursor.lastrowid
    
    # Recuperar el nuevo usuario de la base de datos
    cursor.execute("""
        SELECT email FROM users WHERE id_user = ?
    """, (id_user,))
    
    row = cursor.fetchone()
    
    if row is None:
        raise HTTPException(status_code=404, detail="User not found after insertion")
    
    # Devolver la información del nuevo usuario
    new_user = s.User_Response(email=row["email"])
    return new_user
