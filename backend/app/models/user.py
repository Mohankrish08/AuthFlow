from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Pydantic Schemas
class UserCreate(BaseModel):
    name: str
    password: str
    email:str
    role: str
    created_at: Optional[datetime] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attribute = True

class Token(BaseModel):
    access_token: str
    token_type: str