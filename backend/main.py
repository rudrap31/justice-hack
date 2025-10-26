from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from model.request_models import ChatRequest
from services.gemini_client import get_chat, uris, get_form_chat, create_form_chat_client
from services.supabase_client import search_similar
from services.file_handler import combine_pdfs, text_to_pdf
import os
from google.genai import types
from services.pdf_form_handler_class import PDFFormFiller


app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

uploaded_files = []

chat_with_file = False
filler = None
form_tobesaved = None

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
    global chat_with_file
    user_message = request.message
    response = None
    if chat_with_file:
        response = get_form_chat().send_message(user_message)
    else:
        response = get_chat().send_message(user_message)
    
    
    response_text = response.text.replace("**", "")
    
    # Check if response is a report
    is_report = response_text.__contains__("START_REPORT")
    
    # Clean up the START_REPORT marker from the response
    if is_report:
        response_text = response_text.replace("START_REPORT", "").strip()

    if user_message.lower().startswith("yes"):
        chat_with_file = True

    if response.text.startswith("```json"):
        filler.fill_form(response.text[7:-3], "filled_form.pdf")
        return {
            "reply": "i have filled out and sent it back",
            "is_report": is_report,
        }

    return {
        "reply": response_text,
        "is_report": is_report,
    }

# @app.post("/chat-form")
# def ask_ai_form(request: ChatRequest):
#     user_message = request.message
#     response = get_form_chat().send_message(user_message)
    
#     response_text = response.text.replace("**", "")

#     return {
#         "reply": response_text,
#     }

@app.post("/after-report")
def after_report(report: ChatRequest):
    after_report_text = _process_report(report.message)

    return {
        "reply": after_report_text
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
    # similar_docs = search_similar(report_text)

    # print("\n" + "="*50)
    # print("GENERATED REPORT")
    # print("="*50)
    # print(report_text)
    # print("="*50 + "\n")

    # if similar_docs:
    #     print("SIMILAR DOCUMENTS FOUND:")
    #     print("-"*50)
    #     for doc in similar_docs:
    #         print(f"\nContent: {doc.get('content', 'N/A')}")
    #         print(f"Similarity: {doc.get('similarity', 'N/A')}")
    #         print("-"*50)

    # similar_content = ""
    # if similar_docs:
    #     contents = [doc.get('content', '') for doc in similar_docs if doc.get('content')]
    #     similar_content = "\n\n".join(contents)
    global filler
    global form_tobesaved

    text_to_pdf(report_text, "Report.pdf", title="Complaint Report")
    combine_pdfs(uploaded_files)

    msg = f"Based on the report you just generated, which one of these forms that i am giving you now make the most sense to fill out? Is it the BC Employers Standards Act Complaint Form, BC HRT Individual Complaint, CHRC Individual, CIRB Part II Reprisal Complaint Form, CIRB Part III Reprisal Complaint Form, CLC Monetary and Non-Monetary, CLC Trucking Monetary and Non-Monetary, or CLC Unjust Dismissal? You have to choose from one of these. Tell me the name of the form from the ones i just specified, what the form is about, how it relates to my problem, and ask me if I would like it get filled out by you. Don't ask me if you need additional information for now, I will provide that later. If i say something like yes or continue or anything like that, then "
    response = get_chat().send_message([
        types.Part(text=msg)
        # *[types.Part(file_data=types.FileData(file_uri=uri)) for uri in uris]  
    ])

    forms = [
        "BC Employers Standards Act Complaint Form",
        "BC HRT Individual Complaint",
        "CHRC Individual",
        "CIRB Part II Reprisal Complaint Form",
        "CIRB Part III Reprisal Complaint Form",
        "CLC Monetary and Non-Monetary",
        "CLC Trucking Monetary and Non-Monetary",
        "CLC Unjust Dismissal"
    ]

    response_lower = response.text.lower()
    found_form = next((form for form in forms if form.lower() in response_lower), None)

    form_tobesaved = f"{found_form}.pdf"
    filler = PDFFormFiller(form_tobesaved)
    template = filler.get_form_template()

    create_form_chat_client(report_text, template)

    return response.text