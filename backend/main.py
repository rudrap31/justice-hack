from fastapi import FastAPI
from services.gemini_client import get_chat
from model.request_models import ChatRequest
from services.supabase_client import search_similar

app = FastAPI()

@app.get("/")
def hello_world():
    return {"message": "Hello, world!"}

@app.get("/chat")
def ask_ai(request: ChatRequest):
    user_message = request.message
    response = get_chat().send_message(user_message)

    if response.text.startswith("START_REPORT"):
        process_response(response)

    return {"reply": response.text}


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

    
