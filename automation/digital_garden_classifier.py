"""
Digital Garden Content Classifier
Claude APIを使用したコンテンツ分類・構造化システム

Author: Claude Code Assistant
Date: 2025-10-04
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from automation.utils.env_loader import get_required_env, load_environment

# 環境変数をロード
load_environment()

@dataclass
class ClassificationResult:
    """分類結果"""
    category: str  # insights, ideas, weekly-reviews
    title: str
    description: str
    tags: List[str]
    confidence: float
    markdown_content: str
    frontmatter: Dict[str, Any]

class DigitalGardenClassifier:
    """
    デジタルガーデン用コンテンツ分類システム
    Claude 3.5 Sonnetを使用してテキストを自動分類・構造化
    """

    def __init__(self):
        """初期化"""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic package not installed. "
                "Install with: pip install anthropic"
            )

        self.api_key = get_required_env("ANTHROPIC_API_KEY")
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        self.client = anthropic.Anthropic(api_key=self.api_key)

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
  "description": "内容の要約（100文字以内）",
  "tags": ["タグ1", "タグ2", "タグ3"],
  "confidence": 0.95,
  "markdown_content": "構造化されたマークダウンコンテンツ"
}}
```

## 注意事項

1. **タイトル**: キャッチーで検索しやすい
2. **description**: SEO対策も考慮した要約
3. **tags**: 技術名、トピック、分野など（3-5個）
4. **markdown_content**:
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

            return ClassificationResult(
                category=result_json["category"],
                title=result_json["title"],
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

        # ファイル名生成（タイトルから）
        slug = self._generate_slug(result.title)
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
        """タイトルからスラグを生成"""
        import re

        # 英数字と日本語以外を削除
        slug = re.sub(r'[^\w\s-]', '', title.lower())

        # スペースをハイフンに
        slug = re.sub(r'[\s_]+', '-', slug)

        # 連続するハイフンを1つに
        slug = re.sub(r'-+', '-', slug)

        # 前後のハイフンを削除
        slug = slug.strip('-')

        # 長すぎる場合は切り詰め
        if len(slug) > 50:
            slug = slug[:50].rsplit('-', 1)[0]

        # 空の場合はタイムスタンプ
        if not slug:
            slug = datetime.now().strftime("%Y%m%d-%H%M%S")

        return slug

    def _generate_markdown(self, result: ClassificationResult) -> str:
        """マークダウンファイルの内容を生成"""
        # フロントマター
        frontmatter_lines = ["---"]
        frontmatter_lines.append(f"title: '{result.frontmatter['title']}'")
        frontmatter_lines.append(f"description: '{result.frontmatter['description']}'")
        frontmatter_lines.append(f"pubDate: {result.frontmatter['pubDate']}")
        frontmatter_lines.append(f"tags: {json.dumps(result.frontmatter['tags'], ensure_ascii=False)}")
        frontmatter_lines.append(f"category: '{result.frontmatter['category']}'")
        frontmatter_lines.append(f"draft: {str(result.frontmatter['draft']).lower()}")
        frontmatter_lines.append("---")

        # コンテンツ
        content = f"\n{result.markdown_content}\n"

        return "\n".join(frontmatter_lines) + content


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
