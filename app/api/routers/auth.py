import sqlite3
from fastapi import Response, status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ..database import get_db
from ..schemas import Login_Class, User_Response, TokenData
from ..utils import verify_password
from ..oauth2 import create_access_token

router = APIRouter(
    tags=['Authentication']
)

@router.post('/login')
def login(login: OAuth2PasswordRequestForm = Depends(), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Consulta para encontrar al usuario por su email
    cursor.execute("""
        SELECT id_user, email, password 
        FROM users 
        WHERE email = ?
    """, (login.username,))
    
    user = cursor.fetchone()  # Obtenemos el primer (y único) resultado

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    
    user_id = user[0]
    password_hash = user[2]

    # Verificar la contraseña
    if not verify_password(login.password, password_hash):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    
    # Crear el token JWT
    created_token = create_access_token(data={"user_id": user_id})
    
    # Devolver el token en el formato estándar de OAuth2
    return {"access_token": created_token, "token_type": "bearer"}

