"""
Imagen4 Thumbnail Generator
Generates article thumbnails using Google AI Studio Imagen4 API

Based on official documentation:
https://ai.google.dev/gemini-api/docs/imagen
"""

import os
import logging
import requests
import base64
from typing import Optional
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class ImagenGenerator:
    """
    Generate article thumbnails using Google AI Studio Imagen4

    API Details:
    - Endpoint: https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict
    - Authentication: x-goog-api-key header
    - Model: imagen-4.0-generate-001 (Standard, $0.04/image)
    - Resolution: Up to 2K (2048px)
    - Aspect Ratio: 16:9 supported
    """

    def __init__(self, config: dict = None):
        """Initialize Imagen4 generator"""
        self.config = config or {}
        self.api_key = os.environ.get("GOOGLE_AI_API_KEY")
        self.enabled = bool(self.api_key) and os.environ.get("IMAGEN4_ENABLED", "true").lower() == "true"

        # API endpoint for Imagen4
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict"

        if self.enabled:
            logger.info("✅ Imagen4 initialized with Google AI Studio API")
            logger.info(f"📍 Endpoint: {self.endpoint}")
        else:
            if not self.api_key:
                logger.info("ℹ️ Imagen4 disabled: GOOGLE_AI_API_KEY not set")
            else:
                logger.info("ℹ️ Imagen4 disabled (set IMAGEN4_ENABLED=true to enable)")

    async def generate_thumbnail(
        self,
        title: str,
        description: str,
        category: str = "insight",
        output_path: Optional[Path] = None
    ) -> Optional[str]:
        """
        Generate thumbnail image for article using Imagen4

        Args:
            title: Article title
            description: Article description
            category: Article category (insights, ideas, weekly-reviews)
            output_path: Where to save the image (optional, auto-generated if None)

        Returns:
            Path to generated image file or None if generation fails
        """
        if not self.enabled:
            logger.info("ℹ️ Imagen4 disabled, skipping thumbnail generation")
            return None

        try:
            # Create optimized prompt for image generation
            image_prompt = self._create_image_prompt(title, description, category)

            logger.info(f"🎨 Generating thumbnail for: {title}")
            logger.info(f"📝 Prompt: {image_prompt[:100]}...")

            # Prepare API request
            headers = {
                "x-goog-api-key": self.api_key,
                "Content-Type": "application/json"
            }

            payload = {
                "instances": [{
                    "prompt": image_prompt
                }],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": "16:9",  # Perfect for blog thumbnails
                    "imageSize": "1K",      # 1024px, good balance of quality/size
                    "personGeneration": "dont_allow"  # Avoid person generation
                }
            }

            # Call Imagen4 API
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=60
            )

            response.raise_for_status()

            # Extract base64 image from response
            result = response.json()
            if "predictions" not in result or len(result["predictions"]) == 0:
                logger.error("❌ No predictions in response")
                return None

            base64_image = result["predictions"][0].get("bytesBase64Encoded")
            if not base64_image:
                logger.error("❌ No image data in response")
                return None

            # Decode and save image
            image_data = base64.b64decode(base64_image)

            # Generate output path if not provided
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = Path(f"thumbnails/thumbnail_{timestamp}.png")

            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save image
            output_path.write_bytes(image_data)

            logger.info(f"✅ Thumbnail generated: {output_path}")
            logger.info(f"📊 Image size: {len(image_data) / 1024:.1f} KB")

            return str(output_path)

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text[:500]}")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to generate thumbnail: {e}")
            return None

    def _create_image_prompt(
        self,
        title: str,
        description: str,
        category: str
    ) -> str:
        """
        Create optimized prompt for Imagen4

        Based on best practices:
        - Detailed descriptions improve quality
        - Specify style, mood, color palette
        - Avoid text in images (difficult to render correctly)
        """

        category_styles = {
            'insights': {
                'style': 'abstract modern design representing technical insights',
                'mood': 'professional, analytical, intelligent',
                'colors': 'cool blue and purple tones with white accents',
                'elements': 'geometric patterns, flowing data streams, neural networks'
            },
            'ideas': {
                'style': 'bright innovative design expressing creativity',
                'mood': 'inspiring, energetic, forward-thinking',
                'colors': 'vibrant blues, oranges, and yellows with white space',
                'elements': 'light bulbs, connections, innovative concepts, sparkles'
            },
            'weekly-reviews': {
                'style': 'calm reflective design for retrospection',
                'mood': 'thoughtful, balanced, growth-oriented',
                'colors': 'soft earth tones with gentle gradients',
                'elements': 'timeline, progress indicators, milestones'
            }
        }

        style_config = category_styles.get(
            category,
            {
                'style': 'professional polished design',
                'mood': 'clean, modern, trustworthy',
                'colors': 'neutral with accent colors',
                'elements': 'simple geometric shapes'
            }
        )

        # Create detailed English prompt (Imagen4 works best with English)
        prompt = f"""
A professional blog thumbnail image with {style_config['style']}.
Theme: {title[:100]}
Mood: {style_config['mood']}
Visual style: {style_config['colors']}
Elements: {style_config['elements']}

Requirements:
- NO TEXT OR LETTERS in the image
- Clean minimalist composition
- 16:9 aspect ratio
- High contrast for visibility
- Suitable for blog thumbnail
- Modern and professional appearance
- Abstract representation only, no specific people or brands
"""

        return prompt.strip()


# Example usage for testing
if __name__ == "__main__":
    import asyncio
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    async def test_generation():
        """Test Imagen4 thumbnail generation"""
        print("=" * 60)
        print("Imagen4 Thumbnail Generator - Test")
        print("=" * 60)

        generator = ImagenGenerator()

        if not generator.enabled:
            print("\n[ERROR] Imagen4 is disabled. Please set GOOGLE_AI_API_KEY environment variable.")
            print("Get your API key at: https://aistudio.google.com/app/apikey")
            sys.exit(1)

        test_title = "Claude 4.5の進化：自律性向上と開発支援の強化"
        test_description = "Claude 4.5の自律性向上とSuperClaude機能について分析"

        print("\n[TEST] Test Article:")
        print(f"Title: {test_title}")
        print(f"Description: {test_description}")
        print(f"Category: insights")
        print("\n" + "=" * 60)

        image_path = await generator.generate_thumbnail(
            title=test_title,
            description=test_description,
            category="insights",
            output_path=Path("test_thumbnail.png")
        )

        print("=" * 60)
        if image_path:
            print(f"\n[SUCCESS] Thumbnail generated at {image_path}")
            print(f"You can view the image at: {Path(image_path).absolute()}")
        else:
            print("\n[FAILED] Thumbnail generation failed")
            print("Check the logs above for error details")

    asyncio.run(test_generation())
