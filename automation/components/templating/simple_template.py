"""
Simple Template Manager
Applies minimal, effective structure to articles
Focus: 4 sections - Core Insight, Details, Practical Implications, Summary
"""

import anthropic
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class SimpleTemplateManager:
    """
    Manage simple, effective article templates
    Philosophy: Minimal information, maximum effect
    """

    def __init__(self, config: dict = None):
        """Initialize template manager with Claude client"""
        self.client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )
        self.config = config or {}

        # Simplified system prompt
        self.system_prompt = """あなたは記事を明確で簡潔な構造に整理する専門家です。

重要な原則:
- 最小限の情報で最大の効果
- 冗長を避ける
- 簡潔で明確な表現
- 読みやすさ優先

記事は以下の4セクションに構造化:
1. 核心的な洞察（最も重要な気づき）
2. 詳細（必要な説明のみ）
3. 実践的示唆（具体的なアクション）
4. まとめ（要点の再確認）

各セクションは簡潔に。不要な情報は削除してください。"""

    def apply_template(
        self,
        content: str,
        title: str,
        category: str = "insight"
    ) -> str:
        """
        Apply simple template structure to content

        Args:
            content: Raw article content
            title: Article title
            category: Article category

        Returns:
            Structured article content
        """
        try:
            logger.info(f"Applying template structure to: {title}")

            # Create structuring prompt
            prompt = self._create_structuring_prompt(content, title, category)

            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.5,
                system=self.system_prompt,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            structured_content = message.content[0].text

            logger.info("✅ Template applied successfully")
            return structured_content

        except Exception as e:
            logger.error(f"❌ Failed to apply template: {e}")
            # Fallback: return original content
            return content

    def _create_structuring_prompt(
        self,
        content: str,
        title: str,
        category: str
    ) -> str:
        """Create prompt for content structuring"""

        category_guidance = {
            'insight': "洞察と気づきを明確に",
            'idea': "アイデアの核心と実現可能性を",
            'weekly-review': "振り返りと学びを簡潔に"
        }

        guidance = category_guidance.get(category, "内容を明確に")

        return f"""以下の記事を4つのセクションに構造化してください。

タイトル: {title}
カテゴリ: {category}
ガイダンス: {guidance}

記事内容:
{content}

---

以下の構造で出力してください:

## 核心的な洞察

（最も重要な気づきを2-3段落で簡潔に）

## 詳細

（必要な詳細説明を3-4段落で。冗長を避ける）

## 実践的示唆

（具体的なアクションを箇条書きで3-5項目）
-
-
-

## まとめ

（要点を1-2段落で再確認）

---

重要: 各セクションは簡潔に。不要な情報は削除。読みやすさを最優先。"""

    def get_template_for_category(self, category: str) -> Dict[str, str]:
        """
        Get template structure for specific category

        Args:
            category: Article category

        Returns:
            Dictionary with section titles and descriptions
        """
        base_template = {
            'core_insight': {
                'title': '核心的な洞察',
                'description': '最も重要な気づき'
            },
            'details': {
                'title': '詳細',
                'description': '必要な詳細説明'
            },
            'practical_implications': {
                'title': '実践的示唆',
                'description': '具体的なアクション'
            },
            'summary': {
                'title': 'まとめ',
                'description': '要点の再確認'
            }
        }

        # Category-specific customizations
        if category == 'idea':
            base_template['core_insight']['title'] = 'アイデアの核心'
            base_template['practical_implications']['title'] = '実現可能性'
        elif category == 'weekly-review':
            base_template['core_insight']['title'] = '今週の学び'
            base_template['practical_implications']['title'] = '来週への活用'

        return base_template


# Example usage for testing
if __name__ == "__main__":
    import asyncio

    async def test_template():
        manager = SimpleTemplateManager()

        test_content = """
        Claude 4.5の自律性向上とSuperClaudeの機能について分析。
        より広範な自律的動作が可能になり、以前の課題であった無限ループや
        論理的整合性の問題が解決された。開発支援機能の強化により、
        抽象的なレベルでのコーディング指示が実用的になった。
        CLI呼び出しによるClaude Code連携も実現している。
        SuperClaudeではペルソナ定義による機能拡張と充実したプロンプト
        エンジニアリングが可能になっている。
        """

        structured = manager.apply_template(
            content=test_content,
            title="Claude 4.5の進化：自律性向上と開発支援の強化",
            category="insight"
        )

        print("✅ Structured content:")
        print(structured)

    asyncio.run(test_template())
