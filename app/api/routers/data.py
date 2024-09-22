from datetime import datetime
import sqlite3
from fastapi import HTTPException, Depends, APIRouter

from ..oauth2 import current_user 

from ..schemas import IndicatorResponse
from ..database import get_db

router = APIRouter(
    prefix="/indicator",
    tags=['Indicators']
)

# Endpoint para obtener los valores de un indicador específico
@router.get("/{id}", response_model=IndicatorResponse)
def get_indicator(id: int, db: sqlite3.Connection = Depends(get_db), 
                  current_user: tuple = Depends(current_user)):  
    
    user_id, user_email = current_user
    print(f"Consulted by User ID: {user_id}, User Email: {user_email}")
    
    cursor = db.cursor()
    
    cursor.execute(""" 
        SELECT id_indicator, name, description, units, units_desc AS units_descr, 
               calculation, source, source_code, attributes 
        FROM indicator 
        WHERE id_indicator = ? 
    """, (id,))
    
    rows = cursor.fetchall()
    
    if not rows:
        raise HTTPException(status_code=404, detail=f"Indicator with id {id} not found")
    
    column_names = [description[0] for description in cursor.description]
    
    response_data = []
    for row in rows:
        indicator_data = dict(zip(column_names, row))
        response_data.append(indicator_data)
    
    return IndicatorResponse(user_email=user_email, consulted_at=datetime.now().isoformat(), indicators=response_data)