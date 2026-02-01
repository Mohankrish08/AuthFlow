from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Pydantic Schemas
class UserCreate(BaseModel):
    name: str
    username: Optional[str] = None
    password: str
    email: EmailStr
    role: str
    created_at: Optional[datetime] = None

class UserResponse(BaseModel):
    id: int
    name: str
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True