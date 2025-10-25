from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

EMBED_DIM = 1536

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

initial_context = "You are an AI that helps people file claims when their workplace has done them wrong. You are to ask the person these questions and ask the subquestions or clarifying questions when necessary. Once you are done with asking these questions and are satisfied with the responses, generate a 1 page report on all the info you collected. At the beginning of this report, write the word START_REPORT so that I know that this message is the report. Do not add any personal opinions of yours and don't add any extra stuff in the report that don't need to be there. Here are the questions: When did you start working?What was your salary? Were you working full-time?What was your job title?If job title includes “manager” or “director” - managerial testWhat is the name of the company?What location/province do you work in?What does the company do?If in specific fields, ask follow-up questions to check jurisdictionIndigenous reservesTransportation that crosses provincial borders?Employer who operates in multiple provincesDo you know if you’re employed in a federally regulated industry (banking, telecom, interprovincial transport etc)"

chat = client.chats.create(
    model="gemini-2.5-flash",
    history=[
        types.Content(
            role="user",
            parts=[
                types.Part(text=initial_context)
            ]
        ),
        types.Content(
            role="model",
            parts=[
                types.Part(text="Understood! Bring in your first client.")
            ]
        ),
        types.Content(
            role="user",
            parts=[
                types.Part(text="Here is my first client.")
            ]
        ),
        types.Content(
            role="model",
            parts=[
                types.Part(text="Hi! How can I help you today?")
            ]
        ),
    ]
)

def get_client():
    return client

def get_chat():
    return chat

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