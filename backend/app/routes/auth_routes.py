from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from supabase import Client
from datetime import timedelta
import os

from app.core import get_db
from app.services import (
    authenticate_user,
    create_access_token,
    get_current_user,
    create_refresh_token,  
    decode_refresh_token,
    get_user_by_username
)
from app.models import Token, RefreshTokenRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["Authorization"])

ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 7))

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

    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(data={"sub": user['username']}, expires_delta=refresh_token_expires)
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_request: RefreshTokenRequest, db: Client = Depends(get_db)): 
    token_data = decode_refresh_token(refresh_request.refresh_token)
    user = get_user_by_username(db, token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user['username']}, expires_delta=access_token_expires)

    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(data={"sub": user['username']}, expires_delta=refresh_token_expires)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user