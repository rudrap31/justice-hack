import os
from PyPDF2 import PdfReader
from config import supabase, client
import numpy as np
from google.genai import types
import numpy as np
import re

# --------- SETTINGS ---------
PDF_DIR = "pdfs"
CHUNK_SIZE = 1000
EMBED_DIM = 1536    # embedding dimension

# --------- HELPERS ---------
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    return "\n".join([page.extract_text() for page in reader.pages])

import re

def chunk_text(text, size=1000):
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + size, text_length)

        # Look backward from 'end' to find the last sentence-ending punctuation
        match = re.search(r'[.!?]\s', text[start:end][::-1])  # reversed search
        if match:
            # Adjust 'end' to after the punctuation
            cut_index = end - match.start()
        else:
            cut_index = end  # no punctuation found, just cut at max size

        chunk = text[start:cut_index].strip()
        if chunk:  # avoid empty chunks
            chunks.append(chunk)
        start = cut_index

    return chunks


def get_embedding(text):
    # Use the updated Gemini embedding model
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=EMBED_DIM)
    )
    embedding_values = result.embeddings[0].values
    # Normalize embedding for semantic similarity tasks
    embedding_np = np.array(embedding_values)
    normed_embedding = (embedding_np / np.linalg.norm(embedding_np)).tolist()
    return normed_embedding

def insert_into_supabase(content, embedding, title):
    supabase.table("bc_laws").insert({
        "title": title,
        "content": content,
        "embedding": embedding
    }).execute()

# --------- MAIN PIPELINE ---------
def process_pdfs():
    for filename in os.listdir(PDF_DIR):
        if filename.endswith(".pdf"):
            path = os.path.join(PDF_DIR, filename)
            print(f"📄 Processing {filename}...")

            text = extract_text_from_pdf(path)
            chunks = chunk_text(text)

            for i, chunk in enumerate(chunks):
                embedding = get_embedding(chunk)
                insert_into_supabase(chunk, embedding, filename)
                print(f"✅ Inserted chunk {i+1}/{len(chunks)}")

def search_similar(query):
    query_embedding = get_embedding(query)

    embedding_str = str(query_embedding)

    response = supabase.rpc(
        "match_documents",
        {"query_embedding": embedding_str, "match_count": 5}
    ).execute()
    print(response)

    return response.data

if __name__ == "__main__":
    process_pdfs()
    print("All PDFs processed and stored in Supabase!")
    