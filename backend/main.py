# importing libraries
import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# load the env
load_dotenv()

# Initailizing FastAPI app
app = FastAPI(title="Integration with FastAPI")


# Database setup
url = os.getenv('sample_login_proj_url')
key = os.getenv('sample_login_publisher_api_key')

# Pydantic Schemas
class UserCreate(BaseModel):
    name: str
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


# Dependency to get DB session
def get_db() -> Client:
    return create_client(url, key)
    

    
# Endpoints 

# Health check
@app.get("/")
def read_root():
    return {"message": "Success!!"}

# Get the User
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Client = Depends(get_db)):
    response = (
        db.table("sample_login")
        .select("id, name, email, role")
        .eq("id", user_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")

    return response.data[0]

# Get all the users
@app.get("/users/", response_model=List[UserResponse])
def get_all_users(db: Client = Depends(get_db)):
    response = (db.table("sample_login")
                .select("*")
                .execute())
    return response.data


# # Create User
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Client = Depends(get_db)):
    existing = (db.table("sample_login").select('email').eq('email', user.email).execute())
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    data = user.dict()
    data['created_at'] = data['created_at'].isoformat()
    print(f"user details: {data}")
    new_user = (db.table("sample_login").insert(data).execute())
    return new_user.data[0]

# Update User
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: Client = Depends(get_db)):
    existing = (db.table("sample_login").select("email", "id").eq("email", user.email).execute())
    if existing.data:
        print("Existing data: ", existing.data)
        data = user.dict()
        data['created_at'] = data['created_at'].isoformat()
        print(f"data: {data}")
        update = (db.table("sample_login")
                  .update(data)
                  .eq("id" , user_id)
                  .execute())
        return update.data[0]
    
    raise HTTPException(status_code=400, detail="No Matching Record Found")

# Delete User
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Client = Depends(get_db)):
    delete = (db.table("sample_login").delete().eq("id", user_id).execute()) 
    print("Delete: ", delete)
    if delete:       
        return delete.data
    
    raise HTTPException(status_code=404, detail="User not Found")

