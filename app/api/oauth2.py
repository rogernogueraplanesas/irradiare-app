import sqlite3
from typing import Dict, Tuple, Union
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app.api.database import get_db
from .schemas import TokenData
from fastapi.security import OAuth2PasswordBearer
from .config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
EXPIRE_TIME_MINUTES= settings.TOKEN_EXPIRATION_MINUTES

oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: Dict[str, Union[str, int]]) -> str:
    """
    Create a JWT access token with an expiration time.

    Args:
        data (Dict[str, Union[str, int]]): The payload data to encode in the token.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()

    # Create a timestamp with expiration time
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_TIME_MINUTES)
    
    # Add the expiration time to the token
    to_encode.update({"exp": expire})

    # Encode the JWT with the secret key
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt



def verify_token(token: str, credentials_exception: HTTPException) -> str:
    """
    Verify and decode a JWT token. Extracts the user ID from the token.

    Args:
        token (str): The JWT token to verify.
        credentials_exception (HTTPException): The exception to raise if verification fails.

    Returns:
        str: The user ID extracted from the token.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Obtain the user id from the payload
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    return user_id



def current_user(token: str = Depends(oauth2_schema), db: sqlite3.Connection = Depends(get_db)) -> Tuple[int, str]:
    """
    Retrieve the current user based on the provided JWT token.

    Args:
        token (str): The JWT token for authentication.
        db (sqlite3.Connection): The database connection.

    Returns:
        Tuple[int, str]: The user ID and email of the authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
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

