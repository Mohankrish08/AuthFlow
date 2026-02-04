from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from passlib.context import CryptContext
import os
from supabase import Client
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.core import get_db
from app.models import TokenData

# JWT config
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Refresh tokens
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 7))
REFRESH_SECRET_KEY = os.getenv("REFRESH_TOKEN")

# helper methods


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc)+ expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
 
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username)
        return token_data
    
    except JWTError as e:
        raise credentials_exception
    
    except Exception as e:
        raise credentials_exception
    
def decode_refresh_token(token: str) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "refresh":
            raise credentials_exception
        
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        
        return TokenData(username=username)
    
    except JWTError:
        raise credentials_exception
    
    
def get_user_by_username(db: Client, username:str):
    response = (
        db.table("sample_login")
        .select("*")
        .eq("username", username)
        .execute()
    )
    return response.data[0] if response.data else None

def authenticate_user(db: Client, username: str, password: str):
    user = get_user_by_username(db, username)

    if not user:
        return False
    
    if not verify_password(password, user['password']):
        return False
    return user

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Client = Depends(get_db)
):
    
    token_data = decode_access_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_username(db, token_data.username)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user