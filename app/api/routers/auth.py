from fastapi import Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from ..schemas import Login_Class
from .. import models

router = APIRouter(
    tags=['Authentication']
)
