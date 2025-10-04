"""
YAML to Markdown converter for resume management system.
Converts structured YAML data to formatted Markdown using Jinja2 templates.
"""

from pathlib import Path
from typing import Dict, Any
import logging
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)


class MarkdownConverter:
    """Convert YAML resume data to Markdown format."""

    def __init__(self, template_dir: Path):
        """
        Initialize converter with template directory.

        Args:
            template_dir: Directory containing Jinja2 templates
        """
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Add custom filters
        self.env.filters['join'] = self._join_filter

    def convert(self, data: Dict[str, Any], template_name: str = "resume_template.md") -> str:
        """
        Convert YAML data to Markdown using specified template.

        Args:
            data: YAML data dictionary
            template_name: Template file name

        Returns:
            Generated Markdown content

        Raises:
            FileNotFoundError: If template file doesn't exist
            Exception: If template rendering fails
        """
        try:
            template = self.env.get_template(template_name)

            # Process data for template
            processed_data = self._preprocess_data(data)

            # Render template
            markdown_content = template.render(**processed_data)

            logger.info(f"Successfully converted data to Markdown using {template_name}")
            return markdown_content

        except Exception as e:
            logger.error(f"Error converting to Markdown: {e}")
            raise

    def _preprocess_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess data for template rendering.

        Args:
            data: Raw YAML data

        Returns:
            Processed data for template
        """
        processed = data.copy()

        # Ensure profile exists
        if "profile" not in processed:
            logger.warning("No profile section found in data")
            processed["profile"] = {}

        profile = processed["profile"]

        # Ensure required sections exist
        self._ensure_section(profile, "meta", {})
        self._ensure_section(profile, "personal", {})
        self._ensure_section(profile, "education", [])
        self._ensure_section(profile, "career", {"companies": []})

        # Clean up empty values and normalize data
        self._clean_data(profile)

        return processed

    def _ensure_section(self, data: Dict[str, Any], section: str, default: Any):
        """Ensure section exists with default value."""
        if section not in data:
            data[section] = default

    def _clean_data(self, profile: Dict[str, Any]):
        """Clean up data for better template rendering."""
        # Clean personal info
        personal = profile.get("personal", {})
        for key, value in personal.items():
            if value is None:
                personal[key] = ""

        # Clean education entries
        education = profile.get("education", [])
        for edu in education:
            for key, value in edu.items():
                if value is None:
                    edu[key] = ""

        # Clean career data
        career = profile.get("career", {})
        companies = career.get("companies", [])

        for company in companies:
            # Clean company info
            for key, value in company.items():
                if value is None and key != "projects":
                    company[key] = ""

            # Ensure projects exist
            if "projects" not in company:
                company["projects"] = []

            # Clean project data
            for project in company.get("projects", []):
                for key, value in project.items():
                    if value is None:
                        if key in ["responsibilities", "achievements"]:
                            project[key] = []
                        else:
                            project[key] = ""

                # Ensure lists are lists
                for list_field in ["responsibilities", "achievements"]:
                    if list_field not in project:
                        project[list_field] = []

            # Clean skills data
            skills = company.get("skills", {})
            for skill_type in ["mechanical", "electrical", "software"]:
                if skill_type not in skills:
                    skills[skill_type] = []
                elif skills[skill_type] is None:
                    skills[skill_type] = []

    def _join_filter(self, value, separator=", "):
        """Custom join filter for Jinja2."""
        if not value:
            return ""
        if isinstance(value, list):
            # Filter out None and empty values
            filtered = [str(item) for item in value if item is not None and str(item).strip()]
            return separator.join(filtered)
        return str(value)

    def save_markdown(self, markdown_content: str, output_path: Path):
        """
        Save Markdown content to file.

        Args:
            markdown_content: Generated Markdown content
            output_path: Output file path
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            logger.info(f"Successfully saved Markdown to {output_path}")

        except Exception as e:
            logger.error(f"Error saving Markdown to {output_path}: {e}")
            raise

    def convert_and_save(self, data: Dict[str, Any], output_path: Path, template_name: str = "resume_template.md"):
        """
        Convert data to Markdown and save to file.

        Args:
            data: YAML data dictionary
            output_path: Output file path
            template_name: Template file name
        """
        markdown_content = self.convert(data, template_name)
        self.save_markdown(markdown_content, output_path)