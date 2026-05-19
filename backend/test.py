from config import OPENROUTER_API_KEY
from openai import OpenAI

print("KEY =", repr(OPENROUTER_API_KEY))

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

response = client.chat.completions.create(
    model="openai/gpt-oss-120b:free",
    messages=[
        {
            "role": "user",
            "content": "hello"
        }
    ]
)

print(response.choices[0].message.content)