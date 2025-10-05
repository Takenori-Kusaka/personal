"""
Mermaid Diagram Generator
Generates simple, clear Mermaid diagrams for articles using Claude API
"""

import anthropic
import os
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class MermaidGenerator:
    """
    Generate simple and clear Mermaid diagrams for article content
    Focus: Minimal nodes (3-5), clear relationships, visual clarity
    """

    def __init__(self, config: dict = None):
        """Initialize Mermaid generator with Claude client"""
        self.client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )
        self.config = config or {}

        # Simplified system prompt focusing on clarity
        self.system_prompt = """あなたはシンプルで明確なMermaid図を生成する専門家です。

重要なルール:
1. ノード数: 3-5個（多すぎない）
2. ラベル: 簡潔（各ノード10文字以内推奨）
3. 関係性: 一目で理解できる明確さ
4. スタイル: graph TD または flowchart を使用
5. 日本語対応

出力形式:
```mermaid
（図のコードのみ）
```

説明や前置きは不要。Mermaidコードのみ出力してください。"""

    async def generate_diagram(
        self,
        title: str,
        content: str,
        category: str = "insight"
    ) -> Optional[str]:
        """
        Generate Mermaid diagram for article

        Args:
            title: Article title
            content: Article content (first 1000 chars used)
            category: Article category

        Returns:
            Mermaid diagram code or None if generation fails
        """
        try:
            # Limit content length for efficiency
            content_preview = content[:1000] if len(content) > 1000 else content

            # Create generation prompt
            prompt = self._create_diagram_prompt(title, content_preview, category)

            logger.info(f"Generating Mermaid diagram for: {title}")

            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                temperature=0.3,  # Lower temperature for consistency
                system=self.system_prompt,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract Mermaid code
            response_text = message.content[0].text
            mermaid_code = self._extract_mermaid_code(response_text)

            if mermaid_code:
                logger.info("✅ Mermaid diagram generated successfully")
                return mermaid_code
            else:
                logger.warning("⚠️ Failed to extract Mermaid code from response")
                return None

        except Exception as e:
            logger.error(f"❌ Failed to generate Mermaid diagram: {e}")
            return None

    def _create_diagram_prompt(
        self,
        title: str,
        content: str,
        category: str
    ) -> str:
        """Create optimized prompt for Mermaid generation"""

        category_hints = {
            'insight': "洞察の流れや因果関係を表現",
            'idea': "アイデアの構造や関連性を表現",
            'weekly-review': "時系列や進捗を表現"
        }

        hint = category_hints.get(category, "概念間の関係を表現")

        return f"""記事のMermaid図を生成してください。

タイトル: {title}
カテゴリ: {category}
ヒント: {hint}

記事内容（抜粋）:
{content}

要件:
- ノード数: 3-5個
- ラベル: 簡潔で明確
- 関係性: 直感的に理解可能
- スタイル: graph TD または flowchart TD

一目で記事の核心を理解できる図を生成してください。"""

    def _extract_mermaid_code(self, response: str) -> Optional[str]:
        """Extract Mermaid code from Claude's response"""

        # Look for ```mermaid ... ``` blocks
        pattern = r'```mermaid\n(.*?)\n```'
        match = re.search(pattern, response, re.DOTALL)

        if match:
            return match.group(1).strip()

        # Fallback: check if response is direct Mermaid code
        # (starts with graph/flowchart/etc.)
        response_stripped = response.strip()
        mermaid_keywords = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram']

        if any(response_stripped.startswith(keyword) for keyword in mermaid_keywords):
            return response_stripped

        logger.warning("Could not extract Mermaid code from response")
        return None

    def validate_diagram(self, mermaid_code: str) -> bool:
        """
        Basic validation of Mermaid code

        Args:
            mermaid_code: Mermaid diagram code

        Returns:
            True if valid, False otherwise
        """
        if not mermaid_code or len(mermaid_code) < 10:
            return False

        # Check for basic Mermaid structure
        mermaid_keywords = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram']
        has_keyword = any(keyword in mermaid_code for keyword in mermaid_keywords)

        # Check for arrows/connections
        has_connections = '-->' in mermaid_code or '--' in mermaid_code or '->' in mermaid_code

        return has_keyword and has_connections


# Example usage for testing
if __name__ == "__main__":
    import asyncio

    async def test_generation():
        generator = MermaidGenerator()

        test_title = "Claude 4.5の進化：自律性向上と開発支援の強化"
        test_content = """
        Claude 4.5の自律性向上とSuperClaudeの機能について分析。
        より広範な自律的動作が可能になり、以前の課題であった無限ループや
        論理的整合性の問題が解決された。開発支援機能の強化により、
        抽象的なレベルでのコーディング指示が実用的になった。
        """

        diagram = await generator.generate_diagram(
            title=test_title,
            content=test_content,
            category="insight"
        )

        if diagram:
            print("✅ Generated Mermaid diagram:")
            print("```mermaid")
            print(diagram)
            print("```")
        else:
            print("❌ Failed to generate diagram")

    asyncio.run(test_generation())
