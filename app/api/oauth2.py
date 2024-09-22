import sqlite3
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app.api.database import get_db
from .schemas import TokenData
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY="c6d6e6d9b1b1d7a3e4f5c5e6f7d7e6f7d7e6f7d7e6f7d7e6f7d7e6f7d7e6f7d"
ALGORITHM="HS256"
EXPIRE_TIME_MINUTES= 30

oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now() + timedelta(minutes=EXPIRE_TIME_MINUTES)

    to_encode.update({"expires":str(expire)})

    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

    return encoded_jwt 


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    return user_id


def current_user(token: str = Depends(oauth2_schema), db: sqlite3.Connection = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Could not validate credentials", 
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    # Verificamos y decodificamos el token
    user_id = verify_token(token, credentials_exception)
    
    # Buscamos el usuario en la base de datos
    cursor = db.cursor()
    cursor.execute("""
        SELECT id_user, email 
        FROM users 
        WHERE id_user = ?
    """, (user_id,))
    
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user

