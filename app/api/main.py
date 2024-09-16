from fastapi import FastAPI
from .routers import data, users


#uvicorn app.api.main:app --reload

app = FastAPI()

app.include_router(data.router)
app.include_router(users.router)