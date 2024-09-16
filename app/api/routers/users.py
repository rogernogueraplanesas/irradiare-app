import sqlite3
from fastapi import status, HTTPException, Depends, APIRouter 

from ..schemas import User_Class, User_Response
from ..database import get_db
from ..utils import hash_password

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=User_Response)
def create_user(user: User_Class, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()

    hashed_password = hash_password(password=user.password)
    user.password = hashed_password
    
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
    new_user = User_Response(email=row["email"])
    return new_user


@router.get("/{id}",response_model=User_Response)
def get_user(id, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()

    cursor.execute("""
    SELECT * FROM users
    WHERE id_user = ?
    """, (id,))

    row = cursor.fetchone()

    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail= "No id with such a value")
    
    user = User_Response(email=row["email"])
    return user
