# import os
# import json
# import google.generativeai as genai
# from dotenv import load_dotenv

# load_dotenv()

# # Configure the SDK with your API Key
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=GEMINI_API_KEY)

# def call_llm(prompt: str):
#     # Initialize the model (e.g., Gemini 1.5 Flash or Pro)
#     model = genai.GenerativeModel("gemini-3.1-flash-lite")
    
#     response = model.generate_content(prompt)
    
#     # Note: Gemini returns text. If you expect JSON, ensure your 
#     # prompt asks for it and use the text attribute.
#     return json.loads(response.text)

# def get_embedding(text: str):
#     # Use the specific embedding model
#     result = genai.embed_content(
#         model="models/gemini-embedding-001",
#         content=text,
#         task_type="retrieval_document"
#     )
#     return result['embedding']

from openrouter import OpenRouter
import os
from dotenv import load_dotenv
import json

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenRouter(
    api_key=OPENROUTER_API_KEY
)
def call_llm(prompt: str, get_as_json: bool = True):

    response = client.chat.send(

        model="openai/gpt-5.2",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    if get_as_json:
        return json.loads(response.choices[0].message.content)
    return response.choices[0].message.content


def get_embedding(text: str):
    # Use the specific embedding model
    result = client.embeddings.generate(
       model="google/gemini-embedding-001",
       input=text
    )
    return result.data[0].embedding