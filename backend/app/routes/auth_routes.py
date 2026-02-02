from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from supabase import Client
from datetime import timedelta

from app.core.dbHandler import get_db
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.models.auth import Token
from app.models.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authorization"])


@router.post("/token", response_model=Token)
async def login_from_access_token(formData: OAuth2PasswordRequestForm  = Depends(),
                                  db:Client = Depends(get_db)):
    user = authenticate_user(db, formData.username, formData.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Validate the credentials", 
                            headers={"www.Authenticate": "Bearer"},)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect user and password")
    
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user['username']},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user