from fastapi import FastAPI, UploadFile, File
from services.gemini_client import get_chat
from model.request_models import ChatRequest
from services.supabase_client import search_similar
from services.file_handler import combine_pdfs
import os


app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

uploaded_files = []

@app.get("/")
def hello_world():
    return {"message": "Hello, world!"}

"""
    API call: /chat
    
    Body: Json in the following format
    {
        "message": {userMessage: str}
    }

    Returns:
    {
        "reply": {modelMessage: str}
    }
"""
@app.post("/chat")
def ask_ai(request: ChatRequest):
    user_message = request.message
    response = get_chat().send_message(user_message)

    if response.text.startswith("START_REPORT"):
        process_response(response)
        combine_pdfs(uploaded_files)

    return {"reply": response.text}

"""
    API call: /upload
    
    Body: Form-Data in the following format
    {
        key: file,
        type: File
        value: {one of .pdf, .png, .jpg, .jpeg}
    }

    Returns:
    {
        "reply": "File uploaded successfully",
        "file_path": {filePath: str}
    }
"""
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save the file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    uploaded_files.append(file_path)
    return {"message": "File uploaded successfully", "file_path": file_path}


def process_response(response: str):
    similar = search_similar(response)

    print(" ")
    print(" ")
    print("------------")
    print(response)
    print("------------")
    print(" ")
    print(" ")

    for doc in similar:
        print(" ")
        print(" ")
        print(doc["content"])
        print(" ")
        print(doc["similarity"])
        print(" ")
        print(" ")

    
