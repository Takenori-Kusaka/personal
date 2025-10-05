#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Generation Script for Digital Garden
Generates hero-background.png, og-image.png, and favicon.png using Google Imagen 4
"""

import os
import sys
from pathlib import Path
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Load environment variables
load_dotenv()

# Configuration
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")
OUTPUT_DIR = Path("input")
OUTPUT_DIR.mkdir(exist_ok=True)

# Image specifications
IMAGES = {
    "hero-background": {
        "filename": "hero-background.png",
        "size": (1920, 1080),
        "prompt": (
            "A serene digital garden landscape with abstract geometric patterns representing knowledge nodes "
            "and connections, soft gradient from deep blue to teal, subtle circuit board patterns merged with "
            "organic plant growth motifs, minimalist modern design, abstract technology meets nature theme, "
            "clean professional aesthetic, designed for text overlay, 16:9 aspect ratio, high-end web design "
            "style, bokeh effect in background, soft lighting, photorealistic but stylized"
        )
    },
    "og-image": {
        "filename": "og-image.png",
        "size": (1200, 630),
        "prompt": (
            "Professional social media banner for Digital Garden technology platform, abstract visualization "
            "of AI-powered knowledge ecosystem with glowing blue neural networks connecting to blooming "
            "geometric flowers, gradient background from deep blue to cyan, modern tech aesthetic with organic "
            "growth metaphor, clean space for text overlay in center, high contrast and clarity for thumbnails, "
            "professional web design, 1200x630px social media format"
        )
    },
    "favicon": {
        "filename": "favicon.png",
        "size": (512, 512),
        "prompt": (
            "Minimalist app icon design for Digital Garden platform, simple geometric combination of a sprouting "
            "seedling and circuit board node, centered in square frame, bold blue and green gradient (#2563eb blue), "
            "clean modern tech aesthetic, high contrast for small sizes, flat design style, professional brand icon, "
            "512x512px square format, suitable for favicon and app icon use, extremely simple and recognizable at "
            "16x16 pixels"
        )
    }
}


def validate_api_key():
    """Validate that Google AI API key is configured"""
    if not GOOGLE_AI_API_KEY or GOOGLE_AI_API_KEY == "your_google_ai_api_key_here":
        raise ValueError(
            "GOOGLE_AI_API_KEY not configured. Please set it in .env file.\n"
            "Get your API key at: https://aistudio.google.com/app/apikey"
        )


def generate_image(image_type: str, config: dict) -> Image.Image:
    """
    Generate a single image using Google Gemini 2.0 Flash (Imagen 3)

    Args:
        image_type: Type of image (hero-background, og-image, favicon)
        config: Configuration dictionary with prompt and size

    Returns:
        PIL Image object
    """
    print(f"\n🎨 Generating {image_type}...")
    print(f"   Size: {config['size'][0]}x{config['size'][1]}px")
    print(f"   Prompt: {config['prompt'][:80]}...")

    # Initialize client
    client = genai.Client(api_key=GOOGLE_AI_API_KEY)

    # Generate with Imagen 4 (requires billing setup)
    try:
        response = client.models.generate_images(
            model='imagen-4.0-generate-001',  # Imagen 4 - now available with billing
            prompt=config['prompt'],
            config=types.GenerateImagesConfig(
                number_of_images=1,
            )
        )

        # Get the first generated image
        if response.generated_images:
            generated_image = response.generated_images[0]

            # The image is returned as bytes in the image.image_bytes field
            image_bytes = generated_image.image.image_bytes
            pil_image = Image.open(BytesIO(image_bytes))

            # Resize to exact dimensions
            if pil_image.size != config['size']:
                print(f"   Resizing from {pil_image.size} to {config['size']}")
                pil_image = pil_image.resize(config['size'], Image.Resampling.LANCZOS)

            print(f"   ✅ Generated successfully!")
            return pil_image
        else:
            raise RuntimeError("No images were generated")

    except Exception as e:
        print(f"   ❌ Error generating {image_type}: {str(e)}")
        raise


def save_image(image: Image.Image, filename: str):
    """Save PIL Image to file"""
    output_path = OUTPUT_DIR / filename
    image.save(output_path, format='PNG', optimize=True)
    print(f"   💾 Saved to: {output_path}")


def generate_all_images():
    """Generate all required images for Digital Garden"""
    print("=" * 70)
    print("🌱 Digital Garden Image Generation")
    print("=" * 70)

    # Validate API key
    try:
        validate_api_key()
    except ValueError as e:
        print(f"\n❌ {str(e)}")
        return False

    # Generate each image
    success_count = 0
    for image_type, config in IMAGES.items():
        try:
            image = generate_image(image_type, config)
            save_image(image, config['filename'])
            success_count += 1
        except Exception as e:
            print(f"\n⚠️  Failed to generate {image_type}")
            print(f"   Error: {str(e)}")
            continue

    # Summary
    print("\n" + "=" * 70)
    print(f"✅ Successfully generated {success_count}/{len(IMAGES)} images")
    print("=" * 70)

    if success_count == len(IMAGES):
        print("\n🎉 All images generated successfully!")
        print(f"\n📁 Images saved to: {OUTPUT_DIR.absolute()}")
        return True
    else:
        print(f"\n⚠️  {len(IMAGES) - success_count} images failed to generate")
        return False


if __name__ == "__main__":
    try:
        success = generate_all_images()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        exit(1)
