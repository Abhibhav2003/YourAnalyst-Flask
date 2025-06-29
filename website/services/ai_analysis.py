from google import genai
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv('G_SECRET_KEY')

with open('website\services\system_instructions.txt', 'r', encoding='utf-8') as file:
    content = file.read()

def enter_data(user_prompt,data):
    client = genai.Client(api_key = key)
    prompt = f"{user_prompt} + {data}"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=content
        ),
        contents = prompt
    )
    
    return response.text