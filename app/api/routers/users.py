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
def create_user(user: User_Class, db: sqlite3.Connection = Depends(get_db)) -> User_Response:
    """
    Create a new user with the provided email and password. The password is hashed before storing.

    Args:
        user (User_Class): The user data containing email and password.
        db (sqlite3.Connection): The database connection.

    Returns:
        User_Response: The newly created user's email.

    Raises:
        HTTPException: If the user cannot be found after insertion.
    """
    cursor = db.cursor()

    hashed_password = hash_password(password=user.password)
    user.password = hashed_password
    
    # Query to create a new (unique) user
    cursor.execute("""
        INSERT INTO users (email, password)
        VALUES (?, ?)
    """, (user.email, user.password))

    db.commit()
    
    # Get the id from the new user
    id_user = cursor.lastrowid
    
    # Retrieve the email for the id
    cursor.execute("""
        SELECT email FROM users WHERE id_user = ?
    """, (id_user,))
    
    row = cursor.fetchone()
    
    if row is None:
        raise HTTPException(status_code=404, detail="User not found after insertion")
    
    # Give back the user's email
    new_user = User_Response(email=row["email"])
    return new_user


@router.get("/{id}", response_model=User_Response)
def get_user(id: int, db: sqlite3.Connection = Depends(get_db)) -> User_Response:
    """
    Retrieve a user by their ID.

    Args:
        id (int): The user ID to search for.
        db (sqlite3.Connection): The database connection.

    Returns:
        User_Response: The user's email if found.

    Raises:
        HTTPException: If no user is found with the given ID.
    """
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
