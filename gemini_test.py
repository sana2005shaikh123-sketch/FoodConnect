from google import genai


import os
from google import genai

apikey = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=apikey)

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Explain artificial intelligence in 2 simple sentences."
)

print(response.text)