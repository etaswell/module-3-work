"""
Quick API connectivity test
"""
import os
from openai import OpenAI

client = OpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)
MODEL = os.environ.get("OPENAI_MODEL", "qwen3")

print("Testing API connection...")
print(f"Base URL: {os.environ.get('OPENAI_BASE_URL')}")
print(f"Model: {MODEL}")
print()

try:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": "Say 'API is working' if you can read this."}
        ],
        response_format={"type": "json_object"},
        extra_body={"chat_template_kwargs": {"thinking": False}},
        temperature=0.0,
        timeout=30.0,
    )
    
    print(" Connection successful!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"✗ Connection failed: {e}")
