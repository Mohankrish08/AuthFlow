import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('sample_login_proj_url')
key = os.getenv('sample_login_publisher_api_key')

def get_db() -> Client:
    return create_client(url, key)
