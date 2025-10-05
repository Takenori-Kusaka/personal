#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check available Google AI models"""

import os
import sys
from google import genai
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

load_dotenv()

GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")

if not GOOGLE_AI_API_KEY:
    print("Error: GOOGLE_AI_API_KEY not set")
    sys.exit(1)

client = genai.Client(api_key=GOOGLE_AI_API_KEY)

print("Available models:")
print("=" * 70)

try:
    models = client.models.list()
    for model in models:
        print(f"- {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"  Methods: {model.supported_generation_methods}")
except Exception as e:
    print(f"Error: {e}")
