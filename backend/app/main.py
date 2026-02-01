# app/main.py
from fastapi import FastAPI
from app.routes.user_routes import router as user_router

app = FastAPI(title="Integration with FastAPI")

@app.get("/")
def read_root():
    return {"message": "Success!!"}

app.include_router(user_router)
