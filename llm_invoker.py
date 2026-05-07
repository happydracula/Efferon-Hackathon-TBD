from openrouter import OpenRouter
import os
from dotenv import load_dotenv
import json

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenRouter(
    api_key=OPENROUTER_API_KEY
)
def call_llm(prompt: str):

    response = client.chat.send(

        model="openai/gpt-5.2",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return json.loads(response.choices[0].message.content)