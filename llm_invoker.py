import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure the SDK with your API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def call_llm(prompt: str):
    # Initialize the model (e.g., Gemini 1.5 Flash or Pro)
    model = genai.GenerativeModel("gemini-3.1-flash-lite")
    
    response = model.generate_content(prompt)
    
    # Note: Gemini returns text. If you expect JSON, ensure your 
    # prompt asks for it and use the text attribute.
    return json.loads(response.text)

def get_embedding(text: str):
    # Use the specific embedding model
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return result['embedding']