import sqlite3
from typing import List
from fastapi import HTTPException, Depends, APIRouter 

from ..schemas import IndicatorMetadataResponse
from ..database import get_db

router = APIRouter(
    prefix="/indicator",
    tags=['Indicators']
)

# Endpoint para obtener los valores de un indicador específico
@router.get("/{id}", response_model=List[IndicatorMetadataResponse])
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