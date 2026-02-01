from supabase import Client
from passlib.context import CryptContext
from app.models.user import UserCreate


def password_hasing():
    return CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    pass_hash = password_hasing()
    return pass_hash.hash(password)

def get_user_by_id(db: Client, user_id: int):
    response = (
        db.table("sample_login")
        .select("id, name, email, role", "username")
        .eq("id", user_id)
        .execute()
    )
    return response.data


def get_all_users(db: Client):
    return db.table("sample_login").select("*").execute().data

def create_user(db: Client, user: UserCreate):
    existing = db.table("sample_login").select('email').eq('email', user.email).execute()
    if existing.data:
        return None

    data = user.dict()
    data['password'] = get_password_hash(user.password)
    if data.get("created_at"):
        data["created_at"] = data["created_at"].isoformat()

    new_user = db.table("sample_login").insert(data).execute()
    if new_user:
        return new_user[0]
    return None

def update_user(db: Client, user_id: int, user: UserCreate):
    data = user.dict()
    if data.get("created_at"):
        data["created_at"] = data["created_at"].isoformat()

    update = (
        db.table("sample_login")
        .update(data)
        .eq("id", user_id)
        .execute()
    )
    return update.data

def delete_user(db: Client, user_id: int):
    return db.table("sample_login").delete().eq("id", user_id).execute().data
