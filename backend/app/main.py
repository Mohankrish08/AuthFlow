# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.routes.user_routes import router as user_router
from app.routes.auth_routes import router as auth_router
from dotenv import load_dotenv
import os

# Initialize env
load_dotenv()

app = FastAPI(title="AuthFlow", description="Secure Authentication API with JWT", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ************************* After deploy *********************************

# if os.getenv("ENVIRONMENT") == "production": 
#     app.add_middleware(
#         TrustedHostMiddleware,
#         allowed_hosts=[]
#     )

@app.get("/")
def read_root():
    return {"message": "Success!!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.include_router(user_router)
app.include_router(auth_router)
