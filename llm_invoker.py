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

import math
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


def get_embedding(text: str, model_name = "google/gemini-embedding-001"):
    # Use the specific embedding model
    result = client.embeddings.generate(
       model=model_name,
       input=text
    )
    return result.data[0].embedding


# emb_1 = get_embedding("Lactate was an indicator of so and so")
# emb_2 = get_embedding("Lactate levels in sepsis patients")
# def get_cosine_similarity(v1, v2):
#     dot_product = sum(x * y for x, y in zip(v1, v2))
#     mag1 = math.sqrt(sum(x**2 for x in v1))
#     mag2 = math.sqrt(sum(x**2 for x in v2))
#     return dot_product / (mag1 * mag2) if (mag1 * mag2) > 0 else 0

# print(get_cosine_similarity(emb_1, emb_2))