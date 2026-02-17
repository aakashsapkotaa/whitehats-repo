from fastapi import FastAPI
from app.database import db

app = FastAPI()

@app.get("/")
def home():
    return {"message": "EduHub Backend Running"}