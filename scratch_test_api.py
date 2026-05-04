import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv('GEMINI_API_KEY')
print(f"Using key: {api_key[:10]}...")

client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

try:
    print("Listing models...")
    models = client.models.list()
    for m in models:
        print(f"- {m.id}")
    
    print("\nTesting chat completion with gemini-1.5-flash...")
    res = client.chat.completions.create(
        model="gemini-1.5-flash",
        messages=[{"role": "user", "content": "hi"}]
    )
    print(f"Response: {res.choices[0].message.content}")

except Exception as e:
    print(f"Error: {e}")
