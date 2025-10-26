from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from model.request_models import ChatRequest
from services.gemini_client import get_chat
from services.supabase_client import search_similar
from services.file_handler import combine_pdfs
import os


app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

uploaded_files = []

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "B.C. Employment Rights Assistant API"}


@app.post("/chat")
def ask_ai(request: ChatRequest):
    user_message = request.message
    response = get_chat().send_message(user_message)
    
    response_text = response.text.replace("**", "")
    
    # Check if response is a report
    is_report = response_text.__contains__("START_REPORT")
    
    # Clean up the START_REPORT marker from the response
    if is_report:
        response_text = response_text.replace("START_REPORT", "").strip()
        _process_report(response_text)

    return {
        "reply": response_text,
        "is_report": is_report
    }

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


@app.post("/confirm-report")
async def confirm_report(
    confirmed: bool = Form(...)
):
    """
    Handle report confirmation from user.
    
    Args:
        confirmed: Whether user confirmed the report is correct
        
    Returns:
        dict: Next steps or revision request
    """
    if confirmed:
        return {
            "reply": "Great! Your report has been confirmed. What would you like to do next?",
            "is_report": False
        }
    else:
        return {
            "reply": "I understand. Please let me know what needs to be corrected or what additional information you'd like to add.",
            "is_report": False
        }


def _process_report(report_text: str):
    """
    Process generated reports by searching for similar documents.
    
    Args:
        report_text: The generated report text
    """
    similar_docs = search_similar(report_text)

    print("\n" + "="*50)
    print("GENERATED REPORT")
    print("="*50)
    print(report_text)
    print("="*50 + "\n")

    if similar_docs:
        print("SIMILAR DOCUMENTS FOUND:")
        print("-"*50)
        for doc in similar_docs:
            print(f"\nContent: {doc.get('content', 'N/A')}")
            print(f"Similarity: {doc.get('similarity', 'N/A')}")
            print("-"*50)