import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv('OPENROUTER_API_KEY')
print(f"Using key: {api_key[:10] if api_key else 'None'}...")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

try:
    print("Listing models...")
    # NOTE: OpenRouter does not support standard models.list() easily, so skipping
    # models = client.models.list()
    # for m in models:
    #     print(f"- {m.id}")
    
    print("\nTesting chat completion with google/gemma-4-31b-it:free...")
    res = client.chat.completions.create(
        model="google/gemma-4-31b-it:free",
        messages=[{"role": "user", "content": "hi"}]
    )
    print(f"Response: {res.choices[0].message.content}")

except Exception as e:
    print(f"Error: {e}")
