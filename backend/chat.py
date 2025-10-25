# gemini_chat.py
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv


load_dotenv()

def main():
    # Initialize the client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # Start a chat session with Gemini
    chat = client.chats.create(model="gemini-2.5-flash")
    print("Chat started! Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Ending chat. Goodbye!")
            break

        # Send message to Gemini
        response = chat.send_message(user_input)
        print(f"Gemini: {response.text}\n")

if __name__ == "__main__":
    main()
