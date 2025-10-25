# from google import genai
# from dotenv import load_dotenv
# import os
# from supabase import create_client, Client

# load_dotenv()

# url: str = os.environ.get("SUPABASE_URL")
# key: str = os.environ.get("SUPABASE_KEY")
# supabase: Client = create_client(url, key)

# # The client gets the API key from the environment variable `GEMINI_API_KEY`.
# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# response = client.models.generate_content(
#     model="gemini-2.5-flash", contents="Explain how AI works in a few words"
# )
# print(response.text)

# response2 = (
#     supabase.table("test")
#     .select("*")
#     .execute()
# )

# print(response2)
