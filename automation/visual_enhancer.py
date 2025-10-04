"""
Digital Garden Visual Enhancer
記事のサムネイル画像生成（Google Imagen 4）とMermaid図表生成システム

Author: Claude Code Assistant
Date: 2025-10-04
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from automation.utils.env_loader import get_required_env, load_environment

# 環境変数をロード
load_environment()

@dataclass
class VisualEnhancement:
    """ビジュアル強化結果"""
    thumbnail_path: Optional[str] = None
    thumbnail_prompt: Optional[str] = None
    mermaid_diagrams: List[Dict[str, str]] = None

    def __post_init__(self):
        if self.mermaid_diagrams is None:
            self.mermaid_diagrams = []


class VisualEnhancer:
    """
    デジタルガーデン用ビジュアル強化システム
    - Google Imagen 4でサムネイル画像生成
    - Claude APIでMermaid図表自動生成
    """

    def __init__(self):
        """初期化"""
        # Gemini API設定（Imagen 4アクセス用）
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key and GEMINI_AVAILABLE:
            genai.configure(api_key=self.gemini_api_key)
            self.imagen_available = True
            print("[OK] Imagen 4 initialized via Gemini API")
        else:
            self.imagen_available = False
            print("[WARNING] Imagen 4 not available (GEMINI_API_KEY not set or google-generativeai not installed)")

        # Claude API設定（Mermaid生成用）
        try:
            import anthropic
            self.anthropic_api_key = get_required_env("ANTHROPIC_API_KEY")
            self.claude_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            self.claude_available = True
            print("[OK] Claude API initialized for Mermaid generation")
        except Exception as e:
            self.claude_available = False
            print(f"[WARNING] Claude API not available: {e}")

    def enhance_content(
        self,
        content: str,
        title: str,
        category: str,
        slug: str,
        output_dir: Path
    ) -> VisualEnhancement:
        """
        コンテンツのビジュアル強化を実行

        Args:
            content: 記事のマークダウンコンテンツ
            title: 記事タイトル
            category: カテゴリ（insights/ideas/weekly-reviews）
            slug: 記事のスラグ
            output_dir: 画像出力ディレクトリ（digital-garden/public/images/）

        Returns:
            VisualEnhancement: 強化結果
        """
        print(f"\n[INFO] Enhancing visuals for: {title}")

        enhancement = VisualEnhancement()

        # 1. サムネイル画像生成
        if self.imagen_available:
            thumbnail_path = self._generate_thumbnail(
                content, title, category, slug, output_dir
            )
            if thumbnail_path:
                enhancement.thumbnail_path = thumbnail_path
                print(f"  OK Thumbnail generated: {thumbnail_path}")

        # 2. Mermaid図表生成
        if self.claude_available:
            mermaid_diagrams = self._generate_mermaid_diagrams(content, title, category)
            if mermaid_diagrams:
                enhancement.mermaid_diagrams = mermaid_diagrams
                print(f"  OK Generated {len(mermaid_diagrams)} Mermaid diagram(s)")

        return enhancement

    def _generate_thumbnail(
        self,
        content: str,
        title: str,
        category: str,
        slug: str,
        output_dir: Path
    ) -> Optional[str]:
        """
        Imagen 4でサムネイル画像を生成

        Args:
            content: 記事コンテンツ
            title: タイトル
            category: カテゴリ
            slug: スラグ
            output_dir: 出力ディレクトリ

        Returns:
            生成された画像の相対パス（/images/thumbnails/から）
        """
        print(f"[INFO] Generating thumbnail with Imagen 4...")

        # サムネイルプロンプト生成
        prompt = self._create_thumbnail_prompt(content, title, category)
        print(f"[DEBUG] Thumbnail prompt: {prompt}")

        try:
            # Imagen 4で画像生成
            model = genai.GenerativeModel('imagen-3.0-generate-001')
            response = model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="16:9",  # サムネイル用
                safety_filter_level="block_some",
                person_generation="allow_adult"
            )

            # 画像保存
            thumbnails_dir = output_dir / "thumbnails"
            thumbnails_dir.mkdir(parents=True, exist_ok=True)

            image_filename = f"{slug}.png"
            image_path = thumbnails_dir / image_filename

            # 画像データを保存
            if response.images:
                image_data = response.images[0]._pil_image
                image_data.save(image_path)

                # 相対パスを返す（AstroのbaseUrl対応）
                relative_path = f"images/thumbnails/{image_filename}"
                return relative_path
            else:
                print("[WARNING] No image generated by Imagen 4")
                return None

        except Exception as e:
            print(f"[ERROR] Thumbnail generation failed: {e}")
            return None

    def _create_thumbnail_prompt(
        self,
        content: str,
        title: str,
        category: str
    ) -> str:
        """
        サムネイル画像生成用プロンプトを作成

        Args:
            content: 記事コンテンツ
            title: タイトル
            category: カテゴリ

        Returns:
            Imagen 4用プロンプト
        """
        # カテゴリ別のビジュアルスタイル
        category_styles = {
            "insights": "modern tech illustration with light bulb and circuit patterns, blue and white color scheme, minimalist design",
            "ideas": "creative brainstorming illustration with flowing connections and nodes, purple and cyan gradient, abstract style",
            "weekly-reviews": "calendar and progress chart illustration, organized grid layout, green and orange accents, professional style"
        }

        style = category_styles.get(category, "modern tech illustration")

        # コンテンツから主要キーワード抽出（最初の200文字）
        content_preview = content[:200].replace('\n', ' ')

        prompt = f"""Create a thumbnail image for a technical blog post.

Title: {title}
Category: {category}
Content preview: {content_preview}

Style: {style}

Requirements:
- 16:9 aspect ratio
- Professional and clean design
- Suitable for tech blog thumbnail
- No text or Japanese characters in the image
- Focus on visual metaphors related to the content
"""

        return prompt

    def _generate_mermaid_diagrams(
        self,
        content: str,
        title: str,
        category: str
    ) -> List[Dict[str, str]]:
        """
        Claude APIでMermaid図表を自動生成

        Args:
            content: 記事コンテンツ
            title: タイトル
            category: カテゴリ

        Returns:
            Mermaid図表のリスト [{"type": "flowchart", "title": "...", "code": "..."}]
        """
        print(f"[INFO] Generating Mermaid diagrams...")

        prompt = f"""以下の技術記事を分析し、内容を視覚化するMermaid図表を生成してください。

# 記事情報
タイトル: {title}
カテゴリ: {category}

# 記事コンテンツ
{content}

# タスク
この記事に適したMermaid図表を1-3個生成してください。以下のような図が考えられます：

1. **フローチャート**: プロセス、手順、アルゴリズムの流れ
2. **シーケンス図**: システム間のやり取り、API呼び出し
3. **クラス図**: データ構造、オブジェクト関係
4. **状態遷移図**: ステート管理、ライフサイクル
5. **ガントチャート**: タイムライン、スケジュール

# 出力形式
以下のJSON配列形式で返してください：

```json
[
  {{
    "type": "flowchart | sequence | class | state | gantt",
    "title": "図表のタイトル（日本語、30文字以内）",
    "description": "図表の説明（50文字以内）",
    "mermaid_code": "mermaid図表のコード（```mermaidブロックは不要）"
  }}
]
```

# 注意事項
- Mermaidの正しい構文を使用
- 日本語ラベルはダブルクォートで囲む
- 記事の内容を正確に反映
- 複雑すぎず、理解しやすい図を作成
- 図表がない方が良い場合は空配列 [] を返す

JSON配列のみ返してください（コードブロックなし）。
"""

        try:
            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text.strip()

            # コードブロックを除去
            if result_text.startswith("```"):
                lines = result_text.split("\n")
                result_text = "\n".join(lines[1:-1]) if len(lines) > 2 else result_text

            # JSONパース
            diagrams = json.loads(result_text)

            if not isinstance(diagrams, list):
                print("[WARNING] Unexpected response format (not a list)")
                return []

            return diagrams

        except Exception as e:
            print(f"[ERROR] Mermaid generation failed: {e}")
            return []

    def update_markdown_with_visuals(
        self,
        markdown_path: Path,
        enhancement: VisualEnhancement
    ) -> bool:
        """
        マークダウンファイルにビジュアル要素を追加

        Args:
            markdown_path: マークダウンファイルのパス
            enhancement: ビジュアル強化結果

        Returns:
            成功したかどうか
        """
        try:
            content = markdown_path.read_text(encoding="utf-8")

            # フロントマター部分と本文を分離
            parts = content.split("---", 2)
            if len(parts) < 3:
                print("[ERROR] Invalid markdown format (no frontmatter)")
                return False

            frontmatter = parts[1]
            body = parts[2]

            # 1. フロントマターにサムネイル追加
            if enhancement.thumbnail_path:
                frontmatter += f"\nthumbnail: '{enhancement.thumbnail_path}'"

            # 2. 本文にMermaid図表追加
            if enhancement.mermaid_diagrams:
                mermaid_section = "\n\n## 📊 図解\n\n"

                for diagram in enhancement.mermaid_diagrams:
                    mermaid_section += f"### {diagram['title']}\n\n"
                    if 'description' in diagram:
                        mermaid_section += f"{diagram['description']}\n\n"
                    mermaid_section += f"```mermaid\n{diagram['mermaid_code']}\n```\n\n"

                # 本文の最後に追加
                body = body.rstrip() + mermaid_section

            # ファイル更新
            updated_content = f"---{frontmatter}---{body}"
            markdown_path.write_text(updated_content, encoding="utf-8")

            print(f"[OK] Markdown updated with visuals: {markdown_path}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to update markdown: {e}")
            return False


def main():
    """メイン関数（テスト用）"""
    import sys
    from pathlib import Path

    if len(sys.argv) < 2:
        print("Usage: python visual_enhancer.py <markdown_file>")
        sys.exit(1)

    markdown_file = Path(sys.argv[1])

    if not markdown_file.exists():
        print(f"[ERROR] File not found: {markdown_file}")
        sys.exit(1)

    # マークダウン読み込み
    content = markdown_file.read_text(encoding="utf-8")

    # フロントマターからタイトルとカテゴリ抽出
    import yaml
    parts = content.split("---", 2)
    if len(parts) >= 3:
        frontmatter = yaml.safe_load(parts[1])
        title = frontmatter.get("title", "Untitled")
        category = frontmatter.get("category", "insights")
        body = parts[2]
    else:
        print("[ERROR] Invalid markdown format")
        sys.exit(1)

    # スラグ生成（ファイル名から）
    slug = markdown_file.stem

    # ビジュアル強化
    enhancer = VisualEnhancer()
    output_dir = Path("digital-garden/public/images")

    enhancement = enhancer.enhance_content(
        content=body,
        title=title,
        category=category,
        slug=slug,
        output_dir=output_dir
    )

    # マークダウン更新
    success = enhancer.update_markdown_with_visuals(markdown_file, enhancement)

    if success:
        print(f"\n[SUCCESS] Visual enhancement completed for: {markdown_file}")
    else:
        print(f"\n[FAILED] Could not complete visual enhancement")


if __name__ == "__main__":
    main()
