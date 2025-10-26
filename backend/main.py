from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.gemini_client import get_chat
from model.request_models import ChatRequest
from services.supabase_client import search_similar

app = FastAPI()

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def hello_world():
    return {"message": "Hello, world!"}

@app.post("/chat")
def ask_ai(request: ChatRequest):
    user_message = request.message
    response = get_chat().send_message(user_message)
    cleanresp = response.text.replace("*", "")

    if response.text.startswith("START_REPORT"):
        process_response(response.text)

    return {"reply": cleanresp}


def process_response(response_text: str):
    similar = search_similar(response_text)

    print(" ")
    print(" ")
    print("------------")
    print(response_text)
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