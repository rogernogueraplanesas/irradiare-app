from datetime import datetime
import sqlite3
from typing import Optional, Tuple
from fastapi import HTTPException, Depends, APIRouter, Query

from ..oauth2 import current_user 

from ..schemas import MetadataResponse, DataResponse
from ..database import get_db

router = APIRouter(
    prefix="/indicator",
    tags=['Indicators']
)

# Endpoint to obtain metadata from an indicator (based on id)
@router.get("/metadata/{id}", response_model=MetadataResponse)
def get_indicator(
    id: int, 
    db: sqlite3.Connection = Depends(get_db), 
    current_user: Tuple[int, str] = Depends(current_user)
) -> MetadataResponse:
    """
    Fetch metadata for a specific indicator from the database.
    
    Args:
        id (int): The ID of the indicator to retrieve metadata for.
        db (sqlite3.Connection): The database connection.
        current_user (Tuple[int, str]): Current authenticated user's ID and email.

    Returns:
        MetadataResponse: The metadata information for the specified indicator.
    
    Raises:
        HTTPException: If the indicator with the specified ID is not found.
    """
    user_id, user_email = current_user
    print(f"Consulted by User ID: {user_id}, User Email: {user_email}")
    
    cursor = db.cursor()
    
    cursor.execute(""" 
        SELECT id_indicator, name, description, units, units_desc, 
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
    
    return MetadataResponse(user_email=user_email, consulted_at=datetime.now().isoformat(), indicators=response_data)




# Endpoint to obtain data values from an indicator based on id (optional filter by time/location)
@router.get("/{id}", response_model=DataResponse)
def get_indicator_data(
    id: int, 
    min_timecode: Optional[str] = Query(None, alias="minTimecode"),  # Optional parameter (min. timecode)
    max_timecode: Optional[str] = Query(None, alias="maxTimecode"),  # Optional parameter (max. timecode)
    geocode: Optional[str] = Query(None),  # # Optional parameter (geocode)
    db: sqlite3.Connection = Depends(get_db), 
    current_user: Tuple[int, str] = Depends(current_user)
) -> DataResponse:
    """
    Fetch data values for a specific indicator, with optional filters for timecodes and geocode.
    
    Args:
        id (int): The ID of the indicator to retrieve data for.
        min_timecode (Optional[str]): The minimum timecode for the data (optional).
        max_timecode (Optional[str]): The maximum timecode for the data (optional).
        geocode (Optional[str]): The geographical code to filter the data (optional).
        db (sqlite3.Connection): The database connection.
        current_user (Tuple[int, str]): Current authenticated user's ID and email.

    Returns:
        DataResponse: The data values and metadata for the specified indicator.
    
    Raises:
        HTTPException: If no data is found for the specified indicator.
    """
    user_id, user_email = current_user
    print(f"Consulted by User ID: {user_id}, User Email: {user_email}")

    cursor = db.cursor()

    # Base query
    query = """
        SELECT 
            i.id_indicator, i.name, i.description, i.units, i.units_desc, 
            i.source, i.attributes, 
            dv.timecode, dv.value, 
            gd.geocode, 
            gl.distrito, gl.concelho, gl.freguesia, 
            n.nuts1, n.nuts2, n.nuts3
        FROM 
            indicator i
        INNER JOIN 
            data_values dv ON i.id_indicator = dv.id_indicator
        INNER JOIN 
            geodata gd ON dv.id_geodata = gd.id_geodata
        INNER JOIN 
            geolevel gl ON gd.id_geolevel = gl.id_geolevel
        INNER JOIN 
            nuts n ON gd.id_nuts = n.id_nuts
        WHERE 
            i.id_indicator = ?
    """

    parameters = [id]

    # Filters for min. and max. timecode
    if min_timecode:
        query += " AND dv.timecode >= ?"
        parameters.append(min_timecode)

    if max_timecode:
        query += " AND dv.timecode <= ?"
        parameters.append(max_timecode)

    # Filters for geocode
    if geocode:
        query += " AND gd.geocode = ?"
        parameters.append(geocode)

    # Execution of the query
    cursor.execute(query, tuple(parameters))
    rows = cursor.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail=f"Indicator with id {id} not found")

    column_names = [description[0] for description in cursor.description]
    
    response_data = []
    for row in rows:
        indicator_data = dict(zip(column_names, row))
        response_data.append(indicator_data)
    
    return DataResponse(user_email=user_email, consulted_at=datetime.now().isoformat(), indicators=response_data)