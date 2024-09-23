import sqlite3
from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ..database import get_db
from ..utils import verify_password
from ..oauth2 import create_access_token

router = APIRouter(
    tags=['Authentication']
)

@router.post('/login')
def login(
    login: OAuth2PasswordRequestForm = Depends(),
    db: sqlite3.Connection = Depends(get_db)
) -> dict:
    """
    Authenticates a user based on their email and password, and returns a JWT token
    if the credentials are valid.

    Args:
        login (OAuth2PasswordRequestForm): Form containing the username (email) and password.
        db (sqlite3.Connection): Database connection provided by dependency injection.

    Returns:
        dict: A dictionary containing the access token and its type.

    Raises:
        HTTPException: If the credentials are invalid or the user is not found.
    """
    cursor = db.cursor()
    
    # Find user by email
    cursor.execute("""
        SELECT id_user, email, password 
        FROM users 
        WHERE email = ?
    """, (login.username,))
    
    user = cursor.fetchone()  # Retrieve a single result

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    
    user_id = user[0]
    password_hash = user[2]

    # Verify password
    if not verify_password(login.password, password_hash):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    
    # Create JWT
    created_token = create_access_token(data={"user_id": user_id})
    
    # Return token in standard OAuth2 format
    return {"access_token": created_token, "token_type": "bearer"}


