from supabase import create_client
import os
from dotenv import load_dotenv
from services.gemini_client import get_embedding
from google.genai import types
import numpy as np


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)



# def get_users():
#     response = supabase.table("users").select("*").execute()
#     return response.data

def search_similar(user_response: str):
    query_embedding = get_embedding(user_response)

    embedding_str = str(query_embedding)

    response = supabase.rpc(
        "match_documents",
        {"query_embedding": embedding_str, "match_count": 5}
    ).execute()
    # print(response)

    return response.data