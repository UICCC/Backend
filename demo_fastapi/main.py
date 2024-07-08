# main.py
from fastapi import FastAPI
from model.users import router

app = FastAPI()

# Include CRUD routes from users module
app.include_router(router, prefix="/api")

