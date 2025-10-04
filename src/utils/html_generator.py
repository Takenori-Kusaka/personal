"""
HTML generation utilities for resume management system.
Converts Markdown to HTML with professional styling.
"""

from pathlib import Path
from typing import Optional
import logging
import markdown

logger = logging.getLogger(__name__)


class HTMLGenerator:
    """Generate professional HTML documents from Markdown."""

    def __init__(self, styles_dir: Path):
        """
        Initialize HTML generator.

        Args:
            styles_dir: Directory containing CSS style files
        """
        self.styles_dir = styles_dir

        # Setup markdown extensions
        self.md = markdown.Markdown(extensions=[
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.toc',
            'markdown.extensions.attr_list',
            'markdown.extensions.meta'
        ])

    def markdown_to_html(self, markdown_content: str,
                        css_file: str = "web_style.css") -> str:
        """
        Convert Markdown content to HTML.

        Args:
            markdown_content: Markdown source content
            css_file: CSS file name for styling

        Returns:
            Complete HTML document
        """
        try:
            # Convert markdown to HTML
            body_html = self.md.convert(markdown_content)

            # Load CSS if available
            css_content = self._load_css(css_file)

            # Create full HTML document
            html_document = self._create_html_document(
                body_html, css_content, "職務経歴書"
            )

            logger.info("Successfully converted Markdown to HTML")
            return html_document

        except Exception as e:
            logger.error(f"Error converting Markdown to HTML: {e}")
            raise

    def file_to_html(self, input_file: Path, output_path: Path,
                    css_file: str = "web_style.css") -> bool:
        """
        Convert Markdown file to HTML.

        Args:
            input_file: Input Markdown file path
            output_path: Output HTML file path
            css_file: CSS file name for styling

        Returns:
            True if successful, False otherwise
        """
        try:
            if not input_file.exists():
                logger.error(f"Input file not found: {input_file}")
                return False

            # Read Markdown content
            with open(input_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            # Convert to HTML
            html_content = self.markdown_to_html(markdown_content, css_file)

            # Save HTML
            return self.save_html(html_content, output_path)

        except Exception as e:
            logger.error(f"Error processing file {input_file}: {e}")
            return False

    def save_html(self, html_content: str, output_path: Path) -> bool:
        """
        Save HTML content to file.

        Args:
            html_content: HTML content to save
            output_path: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save HTML with UTF-8 encoding
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"Successfully saved HTML to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving HTML to {output_path}: {e}")
            return False

    def _load_css(self, css_file: str) -> str:
        """
        Load CSS content from file.

        Args:
            css_file: CSS file name

        Returns:
            CSS content or empty string if not found
        """
        css_path = self.styles_dir / css_file
        if css_path.exists():
            try:
                with open(css_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Could not load CSS file {css_path}: {e}")

        return ""

    def _create_html_document(self, body_html: str, css_content: str,
                             title: str = "Resume") -> str:
        """
        Create complete HTML document.

        Args:
            body_html: Body HTML content
            css_content: CSS styling content
            title: Document title

        Returns:
            Complete HTML document
        """
        html_template = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="職務経歴書">
    <meta name="author" content="Resume Management System v2.0">
    <title>{title}</title>
    <style>
{css_content}
    </style>
</head>
<body>
    <div class="container">
{body}
    </div>
    <footer class="footer-info">
        <p>本職務経歴書は自動生成システム (Resume Management System v2.0) により作成されています</p>
        <p>最終更新: <span id="update-date"></span></p>
    </footer>
    <script>
        // Set current date
        document.getElementById('update-date').textContent = new Date().toLocaleDateString('ja-JP');
    </script>
</body>
</html>"""

        return html_template.format(
            title=title,
            css_content=css_content,
            body=body_html
        )

    def get_html_info(self, html_path: Path) -> Optional[dict]:
        """
        Get information about generated HTML file.

        Args:
            html_path: Path to HTML file

        Returns:
            Dictionary with HTML file information
        """
        if not html_path.exists():
            return None

        try:
            stat = html_path.stat()
            return {
                'size_bytes': stat.st_size,
                'size_kb': round(stat.st_size / 1024, 2),
                'modified': stat.st_mtime,
                'path': str(html_path)
            }
        except Exception as e:
            logger.error(f"Error getting HTML info: {e}")
            return None