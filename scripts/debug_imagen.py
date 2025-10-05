#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug Imagen 4 response structure"""

import os
import sys
from google import genai
from google.genai import types
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

print("Testing Imagen 4 image generation...")
print("=" * 70)

try:
    response = client.models.generate_images(
        model='imagen-4.0-generate-001',
        prompt='A simple blue circle on white background',
        config=types.GenerateImagesConfig(
            number_of_images=1,
        )
    )

    print(f"Response type: {type(response)}")
    print(f"Response attributes: {dir(response)}")

    if hasattr(response, 'generated_images'):
        print(f"\ngenerated_images type: {type(response.generated_images)}")
        print(f"Number of images: {len(response.generated_images)}")

        if response.generated_images:
            first_image = response.generated_images[0]
            print(f"\nFirst image type: {type(first_image)}")
            print(f"First image attributes: {dir(first_image)}")

            if hasattr(first_image, 'image'):
                print(f"\nimage attribute type: {type(first_image.image)}")
                print(f"image attribute value: {first_image.image}")

                # Check if it's bytes or PIL Image
                if isinstance(first_image.image, bytes):
                    print("Image is bytes data")
                    from PIL import Image
                    from io import BytesIO
                    pil_image = Image.open(BytesIO(first_image.image))
                    print(f"PIL Image size: {pil_image.size}")
                    print(f"PIL Image mode: {pil_image.mode}")
                else:
                    print(f"Image object type: {type(first_image.image)}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
