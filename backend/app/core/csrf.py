from fastapi import Request, HTTPException, status, Response
from fastapi.responses import JSONResponse
import secrets
from typing import Optional
import os 

csrf_tokens = {}

def generate_csrf_token()-> str:
    return secrets.token_urlsafe(32)

def set_csrf_cookie(response: Response, token: str):
    response.set_cookie(
        key="csrf_token",
        value=token,
        httponly=True,
        secure=os.getenv("ENVIRONMENT") == "production",
        samesite="lax",
        max_age=3600,
        path="/"
    )
    return response

async def verify_csrf_token(request: Request):
    cookie_token = request.cookies.get("csrf_token")
    header_token = request.headers.get("X-CSRF-Token")

    if not cookie_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing in cookies"
        )

    if not header_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing in headers"
        )
    
    if cookie_token != header_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token"
        )
    
    return True

def create_csrf_token_response(data: dict, csrf_token: str) -> JSONResponse:
    response = JSONResponse(content=data)
    set_csrf_cookie(response, csrf_token)
    return response