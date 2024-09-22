from fastapi import FastAPI
from .routers import data, users, auth


#uvicorn app.api.main:app --reload

app = FastAPI()

app.include_router(data.router)
app.include_router(users.router)
app.include_router(auth.router)