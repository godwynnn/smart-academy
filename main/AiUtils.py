from pydantic import BaseModel
from google import genai
from django.conf import settings
import json


client = genai.Client(api_key='AIzaSyBC2fxSmEO5NzNGxGUV9djbENKIyWTtl3Q')

class Quiz(BaseModel):
    question: str
    options: list[str]
    answer:str

def generate_from_prompt(prompt):
     
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[Quiz]
            },
        )

        data = json.loads(response.text)

        return data,response.text
        

