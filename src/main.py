#!/usr/bin/env python3
"""
Main entry point for resume management system v2.0
Generates Markdown and PDF from YAML data.
"""

import sys
import os
from pathlib import Path
import logging

# Fix Windows console encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from utils.yaml_handler import YAMLHandler
from core.converter import MarkdownConverter
from utils.html_generator import HTMLGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('resume_generation.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main function to generate resume from YAML data."""
    try:
        # Define paths
        project_root = Path(__file__).parent.parent
        data_file = project_root / "data" / "profile.yml"
        template_dir = project_root / "templates"
        styles_dir = project_root / "templates" / "styles"
        output_dir = project_root / "output"

        logger.info("🚀 Starting resume generation...")

        # Initialize handlers
        yaml_handler = YAMLHandler()
        converter = MarkdownConverter(template_dir)
        html_generator = HTMLGenerator(styles_dir)

        # Load data
        if not data_file.exists():
            logger.error(f"❌ Data file not found: {data_file}")
            return False

        data = yaml_handler.load_yaml(data_file)
        logger.info("✅ Successfully loaded profile data")

        # Generate Markdown
        markdown_file = output_dir / "resume.md"
        converter.convert_and_save(data, markdown_file)
        logger.info(f"✅ Generated Markdown: {markdown_file}")

        # Generate HTML
        html_file = output_dir / "resume.html"
        if html_generator.file_to_html(markdown_file, html_file):
            logger.info(f"✅ Generated HTML: {html_file}")
        else:
            logger.error("❌ HTML generation failed")

        # Print summary
        print_generation_summary(data, markdown_file, html_file)

        return True

    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        return False


def print_generation_summary(data, markdown_file, html_file=None):
    """Print generation summary with proper encoding."""
    print("\n" + "="*60)
    print("📋 RESUME GENERATION SUMMARY")
    print("="*60)

    profile = data.get("profile", {})
    personal = profile.get("personal", {})
    career = profile.get("career", {})
    companies = career.get("companies", [])

    print(f"👤 Name: {personal.get('name', 'Unknown')}")
    print(f"🎂 Age: {personal.get('age', 'Unknown')}")
    print(f"📍 Location: {personal.get('location', 'Unknown')}")

    print(f"\n💼 Career Summary:")
    print(f"   Companies: {len(companies)}")

    total_projects = 0
    for company in companies:
        projects = company.get("projects", [])
        total_projects += len(projects)
        print(f"   - {company.get('name', 'Unknown')}: {len(projects)} projects")

    print(f"   Total projects: {total_projects}")

    print(f"\n📄 Output:")
    print(f"   Markdown: {markdown_file}")
    print(f"   MD Size: {markdown_file.stat().st_size if markdown_file.exists() else 0} bytes")

    if html_file and html_file.exists():
        html_size_kb = round(html_file.stat().st_size / 1024, 1)
        print(f"   HTML: {html_file}")
        print(f"   HTML Size: {html_size_kb} KB")

    print("\n" + "="*60)
    print("✨ Generation completed successfully!")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)