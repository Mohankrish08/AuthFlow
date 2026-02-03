# app/routes/user_routes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from supabase import Client

from app.core import get_db
from app.models import UserCreate, UserResponse
from app.services import user_service
from app.services import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Client = Depends(get_db), current_user: dict = Depends(get_current_user)):
    data = user_service.get_user_by_id(db, user_id)
    if not data:
        raise HTTPException(status_code=404, detail="User not found")
    return data[0]

@router.get("/", response_model=List[UserResponse])
def get_all_users(db: Client = Depends(get_db)):
    return user_service.get_all_users(db)   

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Client = Depends(get_db), current_user: dict = Depends(get_current_user)):
    new_user = user_service.create_user(db, user)
    if not new_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return new_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: Client = Depends(get_db), current_user: dict = Depends(get_current_user)):
    updated = user_service.update_user(db, user_id, user)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated[0]

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Client = Depends(get_db), current_user: dict = Depends(get_current_user)):
    deleted = user_service.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted
