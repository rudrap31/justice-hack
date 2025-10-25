from fastapi import FastAPI
from services.gemini_client import ask_gemini

app = FastAPI()

@app.get("/")
def hello_world():
    return {"message": "Hello, world!"}

@app.get("/ask")
def ask_ai(prompt: str):
    answer = ask_gemini(prompt)
    return {"prompt": prompt, "answer": answer}