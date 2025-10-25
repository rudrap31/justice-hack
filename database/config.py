import os
from supabase import create_client
from google import genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access them
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure clients
client = genai.Client()
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


