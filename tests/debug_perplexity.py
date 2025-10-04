"""
Debug script to test Perplexity API
"""

import os
import sys
import asyncio
import httpx
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from automation.utils.env_loader import load_environment

async def test_perplexity():
    load_environment()

    api_key = os.getenv("PERPLEXITY_API_KEY")
    print(f"API Key: {api_key[:15]}... (length: {len(api_key)})")

    async with httpx.AsyncClient(timeout=60) as client:
        try:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar",  # Try the basic model first
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant."
                        },
                        {
                            "role": "user",
                            "content": "Hello, can you tell me about AI?"
                        }
                    ],
                    "max_tokens": 100,
                    "temperature": 0.2
                }
            )

            print(f"\nStatus Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"\nResponse Body:")
            print(response.text)

            if response.status_code == 200:
                data = response.json()
                print(f"\nSuccess! Content: {data['choices'][0]['message']['content']}")

        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_perplexity())
