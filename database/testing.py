import numpy as np
from supabase import create_client
import os
from dotenv import load_dotenv

# Load env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Example query function
def search_similar(query_text, top_k=5):
    # 1️⃣ Get embedding for query
    import google.generativeai as genai
    from google.genai import types
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)
    client = genai.Client()

    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=query_text,
        config=types.EmbedContentConfig(output_dimensionality=768)
    )
    embedding_values = np.array(result.embeddings[0].values)
    normed_embedding = (embedding_values / np.linalg.norm(embedding_values)).tolist()

    # 2️⃣ Query Supabase using similarity
    # Use the raw SQL filter with pgvector operator <=> for cosine similarity
    query = f"""
    SELECT title, content, embedding <=> '{normed_embedding}' AS similarity
    FROM documents
    ORDER BY similarity
    LIMIT {top_k};
    """

    response = supabase.rpc("exec_sql", {"sql": query}).execute()
    return response.data

# Usage
query = "What is Rivian Mission?"
results = search_similar(query, top_k=3)
for r in results:
    print(r['title'], r['content'])
