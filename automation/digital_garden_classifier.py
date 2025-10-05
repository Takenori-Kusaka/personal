"""
Digital Garden Content Classifier
Claude APIを使用したコンテンツ分類・構造化システム

Author: Claude Code Assistant
Date: 2025-10-05 (Updated with Mermaid and Template support)
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from automation.utils.env_loader import get_required_env, load_environment

# ✨ New: Import visual and templating components
from automation.components.visual.mermaid_generator import MermaidGenerator
from automation.components.templating.simple_template import SimpleTemplateManager

# 環境変数をロード
load_environment()

@dataclass
class ClassificationResult:
    """分類結果"""
    category: str  # insights, ideas, weekly-reviews
    title: str
    slug: str  # URL-safe slug
    description: str
    tags: List[str]
    confidence: float
    markdown_content: str
    frontmatter: Dict[str, Any]

class DigitalGardenClassifier:
    """
    デジタルガーデン用コンテンツ分類システム
    Claude 3.5 Sonnetを使用してテキストを自動分類・構造化

    ✨ Enhanced with:
    - Mermaid diagram generation
    - Template-based structure
    """

    def __init__(self, enable_enhancements: bool = True):
        """
        初期化

        Args:
            enable_enhancements: Mermaid/Template機能を有効にするか（デフォルト: True）
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic package not installed. "
                "Install with: pip install anthropic"
            )

        self.api_key = get_required_env("ANTHROPIC_API_KEY")
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        self.client = anthropic.Anthropic(api_key=self.api_key)

        # ✨ New: Initialize enhancement components
        self.enable_enhancements = enable_enhancements
        if self.enable_enhancements:
            self.mermaid_generator = MermaidGenerator()
            self.template_manager = SimpleTemplateManager()
            print(f"[OK] Claude Classifier initialized with enhancements (Mermaid + Templates)")
        else:
            print(f"[OK] Claude Classifier initialized with model: {self.model}")

    def classify_content(
        self,
        content: str,
        source_file: Optional[str] = None
    ) -> ClassificationResult:
        """
        コンテンツを分類して構造化されたマークダウンを生成

        Args:
            content: 分類するテキスト
            source_file: ソースファイル名（オプション）

        Returns:
            ClassificationResult: 分類結果
        """
        print(f"\n[INFO] Classifying content ({len(content)} characters)...")

        # プロンプト作成
        prompt = self._create_classification_prompt(content, source_file)

        # Claude API呼び出し
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # レスポンス解析
            result_text = response.content[0].text
            result = self._parse_classification_result(result_text, content)

            print(f"[OK] Classification completed")
            print(f"  - Category: {result.category}")
            print(f"  - Title: {result.title}")
            print(f"  - Tags: {', '.join(result.tags)}")
            print(f"  - Confidence: {result.confidence:.2%}")

            return result

        except Exception as e:
            print(f"[ERROR] Classification failed: {e}")
            raise

    def _create_classification_prompt(
        self,
        content: str,
        source_file: Optional[str]
    ) -> str:
        """分類プロンプトを作成"""
        return f"""あなたは、デジタルガーデンのコンテンツを分類する専門家です。

以下のテキストを分析し、適切なカテゴリに分類してください。

# カテゴリ定義

## insights（洞察・気づき）
- 学びや発見、技術的な理解
- 「〜ということがわかった」「〜に気づいた」
- 問題解決の経験、トラブルシューティング
- 技術記事、チュートリアル的な内容

## ideas（アイデア・構想）
- 新しい発想、将来の計画
- 「〜を作りたい」「〜したらどうか」
- システム設計、アーキテクチャ構想
- 改善案、最適化のアイデア

## weekly-reviews（週次振り返り）
- 定期的な振り返り、進捗報告
- 複数の出来事のまとめ
- 学びの統合、次週の計画
- メタ認知的な内容

# タスク

以下のテキストを分析し、JSON形式で結果を返してください。

**入力テキスト:**
{content}

{f"**ソースファイル:** {source_file}" if source_file else ""}

# 出力形式

以下のJSON形式で返してください：

```json
{{
  "category": "insights | ideas | weekly-reviews のいずれか",
  "title": "魅力的でわかりやすいタイトル（40文字以内）",
  "slug": "url-safe-english-slug",
  "description": "内容の要約（100文字以内）",
  "tags": ["タグ1", "タグ2", "タグ3"],
  "confidence": 0.95,
  "markdown_content": "構造化されたマークダウンコンテンツ"
}}
```

## 注意事項

1. **タイトル**: キャッチーで検索しやすい
2. **slug**: URL-safe な英語のスラグ（小文字、ハイフン区切り、40文字以内）
   - 日本語タイトルの場合は意味を反映した英語スラグを生成
   - 例: "Claude 4.5の進化" → "claude-45-evolution"
   - 例: "Web3.0コミュニティ" → "web30-community"
3. **description**: SEO対策も考慮した要約
4. **tags**: 技術名、トピック、分野など（3-5個）
5. **markdown_content**:
   - 見出し（##, ###）を適切に使用
   - コードブロックは```言語名で囲む
   - リストや強調を活用
   - 元のテキストを整形・構造化する
   - オリジナルの内容を保持する

それでは、分析を開始してください。JSON形式のみ返してください（コードブロックで囲まずに）。
"""

    def _parse_classification_result(
        self,
        result_text: str,
        original_content: str
    ) -> ClassificationResult:
        """分類結果をパース"""
        try:
            # JSONをパース
            result_text = result_text.strip()

            # コードブロックで囲まれている場合は除去
            if result_text.startswith("```"):
                lines = result_text.split("\n")
                result_text = "\n".join(lines[1:-1])

            result_json = json.loads(result_text)

            # フロントマター作成
            frontmatter = {
                "title": result_json["title"],
                "description": result_json["description"],
                "pubDate": datetime.now().strftime("%Y-%m-%d"),
                "tags": result_json["tags"],
                "category": result_json["category"],
                "draft": False,
            }

            # Claude-generated slug を取得、なければタイトルから生成
            slug = result_json.get("slug")
            if not slug:
                slug = self._generate_slug(result_json["title"])

            return ClassificationResult(
                category=result_json["category"],
                title=result_json["title"],
                slug=slug,
                description=result_json["description"],
                tags=result_json["tags"],
                confidence=result_json.get("confidence", 0.0),
                markdown_content=result_json["markdown_content"],
                frontmatter=frontmatter
            )

        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse JSON: {e}")
            print(f"[DEBUG] Raw response:\n{result_text}")
            raise

    def generate_markdown_file(
        self,
        result: ClassificationResult,
        output_dir: Path
    ) -> Path:
        """
        マークダウンファイルを生成

        Args:
            result: 分類結果
            output_dir: 出力ディレクトリ

        Returns:
            生成されたファイルのパス
        """
        # 出力ディレクトリ作成
        category_dir = output_dir / result.category
        category_dir.mkdir(parents=True, exist_ok=True)

        # ファイル名はresult.slugを使用（Claude APIが生成）
        slug = result.slug
        output_file = category_dir / f"{slug}.md"

        # ファイルが既に存在する場合はタイムスタンプを追加
        if output_file.exists():
            timestamp = datetime.now().strftime("%H%M%S")
            output_file = category_dir / f"{slug}-{timestamp}.md"

        # マークダウン生成
        markdown = self._generate_markdown(result)

        # ファイル書き込み
        output_file.write_text(markdown, encoding="utf-8")

        print(f"[OK] Markdown file generated: {output_file}")

        return output_file

    def _generate_slug(self, title: str) -> str:
        """タイトルからURL-safeなスラグを生成"""
        import re
        import unicodedata

        # Unicode正規化（NFKDで分解して、結合文字を削除）
        slug = unicodedata.normalize('NFKD', title)

        # ASCIIのみを保持（日本語などを削除）
        slug = slug.encode('ascii', 'ignore').decode('ascii')

        # 小文字化
        slug = slug.lower()

        # 英数字とハイフン以外を削除
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)

        # スペースをハイフンに
        slug = re.sub(r'[\s_]+', '-', slug)

        # 連続するハイフンを1つに
        slug = re.sub(r'-+', '-', slug)

        # 前後のハイフンを削除
        slug = slug.strip('-')

        # 長すぎる場合は切り詰め
        if len(slug) > 50:
            slug = slug[:50].rsplit('-', 1)[0]

        # 空の場合はタイムスタンプ（日本語タイトルなどでASCII変換後に空になった場合）
        if not slug:
            slug = datetime.now().strftime("%Y%m%d-%H%M%S")

        return slug

    def _generate_markdown(self, result: ClassificationResult) -> str:
        """
        マークダウンファイルの内容を生成

        ✨ Enhanced with:
        - Mermaid diagram (if enhancements enabled)
        - Template structure (if enhancements enabled)
        """
        # フロントマター
        frontmatter_lines = ["---"]
        frontmatter_lines.append(f"title: '{result.frontmatter['title']}'")
        frontmatter_lines.append(f"description: '{result.frontmatter['description']}'")
        frontmatter_lines.append(f"pubDate: {result.frontmatter['pubDate']}")
        frontmatter_lines.append(f"tags: {json.dumps(result.frontmatter['tags'], ensure_ascii=False)}")
        frontmatter_lines.append(f"category: '{result.frontmatter['category']}'")
        frontmatter_lines.append(f"draft: {str(result.frontmatter['draft']).lower()}")
        frontmatter_lines.append("---")

        # ✨ Enhanced content with Mermaid and Template
        if self.enable_enhancements:
            enhanced_content = self._enhance_content(result)
            content = f"\n{enhanced_content}\n"
        else:
            content = f"\n{result.markdown_content}\n"

        return "\n".join(frontmatter_lines) + content

    def _enhance_content(self, result: ClassificationResult) -> str:
        """
        ✨ New: Enhance content with Mermaid diagram and template structure

        Args:
            result: Classification result

        Returns:
            Enhanced markdown content
        """
        try:
            print("[INFO] Enhancing content with Mermaid and Template...")

            # 1. Generate Mermaid diagram
            mermaid_diagram = asyncio.run(
                self.mermaid_generator.generate_diagram(
                    title=result.title,
                    content=result.markdown_content,
                    category=result.category
                )
            )

            # 2. Apply template structure
            structured_content = self.template_manager.apply_template(
                content=result.markdown_content,
                title=result.title,
                category=result.category
            )

            # 3. Combine: Mermaid diagram + Structured content
            enhanced_parts = []

            # Add Mermaid diagram if generated
            if mermaid_diagram:
                enhanced_parts.append("## 概要図\n")
                enhanced_parts.append("```mermaid")
                enhanced_parts.append(mermaid_diagram)
                enhanced_parts.append("```\n")
                print("[OK] Mermaid diagram added")
            else:
                print("[WARN] Mermaid diagram generation failed, continuing without it")

            # Add structured content
            enhanced_parts.append(structured_content)

            print("[OK] Content enhancement completed")
            return "\n".join(enhanced_parts)

        except Exception as e:
            print(f"[ERROR] Content enhancement failed: {e}")
            print("[FALLBACK] Using original content")
            return result.markdown_content


def main():
    """メイン関数（テスト用）"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python digital_garden_classifier.py <input_file>")
        sys.exit(1)

    input_file = Path(sys.argv[1])

    if not input_file.exists():
        print(f"[ERROR] File not found: {input_file}")
        sys.exit(1)

    # テキスト読み込み
    content = input_file.read_text(encoding="utf-8")

    # 分類
    classifier = DigitalGardenClassifier()
    result = classifier.classify_content(content, str(input_file))

    # マークダウン生成
    output_dir = Path("digital-garden/src/content")
    output_file = classifier.generate_markdown_file(result, output_dir)

    print(f"\n[SUCCESS] Content classified and saved to: {output_file}")


if __name__ == "__main__":
    main()
