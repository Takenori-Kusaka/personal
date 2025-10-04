"""
Digital Garden Fact Checker
Perplexity APIを使用した技術記事の事実確認システム

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
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from automation.utils.env_loader import get_required_env, load_environment

# 環境変数をロード
load_environment()

@dataclass
class FactCheckResult:
    """事実確認結果"""
    original_claim: str
    verification_status: str  # "verified", "partially_verified", "unverified", "incorrect"
    confidence: float
    sources: List[Dict[str, str]]
    corrected_claim: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class ArticleFactCheck:
    """記事全体の事実確認結果"""
    total_claims: int
    verified_count: int
    unverified_count: int
    corrections_needed: int
    fact_check_results: List[FactCheckResult]
    overall_accuracy: float
    citations: List[Dict[str, str]]


class FactChecker:
    """
    デジタルガーデン用事実確認システム
    - Perplexity APIで技術的主張を検証
    - Claude APIで主張抽出と結果分析
    """

    def __init__(self):
        """初期化"""
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests package not installed. Install with: pip install requests")

        # Perplexity API設定
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        if self.perplexity_api_key:
            self.perplexity_available = True
            print("[OK] Perplexity API initialized")
        else:
            self.perplexity_available = False
            print("[WARNING] Perplexity API not available (PERPLEXITY_API_KEY not set)")

        # Claude API設定
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")

        self.anthropic_api_key = get_required_env("ANTHROPIC_API_KEY")
        self.claude_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        print("[OK] Claude API initialized for claim extraction")

    def check_article_facts(
        self,
        content: str,
        title: str,
        category: str
    ) -> ArticleFactCheck:
        """
        記事の事実確認を実行

        Args:
            content: 記事のマークダウンコンテンツ
            title: 記事タイトル
            category: カテゴリ

        Returns:
            ArticleFactCheck: 事実確認結果
        """
        print(f"\n[INFO] Fact-checking article: {title}")

        if not self.perplexity_available:
            print("[WARNING] Perplexity API not available, skipping fact check")
            return self._create_empty_result()

        # 1. Claudeで技術的主張を抽出
        claims = self._extract_claims(content, title, category)
        print(f"  Extracted {len(claims)} claims to verify")

        if not claims:
            print("[INFO] No verifiable claims found in article")
            return self._create_empty_result()

        # 2. Perplexityで各主張を検証
        fact_check_results = []
        for i, claim in enumerate(claims, 1):
            print(f"  Verifying claim {i}/{len(claims)}: {claim[:50]}...")
            result = self._verify_claim(claim, title, category)
            if result:
                fact_check_results.append(result)

        # 3. 結果を集計
        verified_count = sum(1 for r in fact_check_results if r.verification_status == "verified")
        unverified_count = sum(1 for r in fact_check_results if r.verification_status in ["unverified", "incorrect"])
        corrections_needed = sum(1 for r in fact_check_results if r.corrected_claim is not None)

        overall_accuracy = verified_count / len(fact_check_results) if fact_check_results else 0.0

        # 4. 引用情報を収集
        citations = self._collect_citations(fact_check_results)

        print(f"[OK] Fact check completed: {verified_count}/{len(claims)} verified ({overall_accuracy:.1%})")

        return ArticleFactCheck(
            total_claims=len(claims),
            verified_count=verified_count,
            unverified_count=unverified_count,
            corrections_needed=corrections_needed,
            fact_check_results=fact_check_results,
            overall_accuracy=overall_accuracy,
            citations=citations
        )

    def _extract_claims(
        self,
        content: str,
        title: str,
        category: str
    ) -> List[str]:
        """
        Claudeで技術的主張を抽出

        Args:
            content: 記事コンテンツ
            title: タイトル
            category: カテゴリ

        Returns:
            検証可能な主張のリスト
        """
        prompt = f"""以下の技術記事から、事実確認が必要な具体的な技術的主張を抽出してください。

# 記事情報
タイトル: {title}
カテゴリ: {category}

# 記事コンテンツ
{content}

# タスク
以下の条件を満たす技術的主張を抽出してください：

**抽出対象**:
1. 技術仕様や機能の説明（「Xには〜機能がある」など）
2. パフォーマンス指標や数値的な主張（「Yは〜倍速い」など）
3. ベストプラクティスや推奨事項（「Zを使うべき」など）
4. 技術の歴史的事実（「バージョン〜で追加された」など）

**除外対象**:
- 個人的な意見や感想
- 主観的な評価
- 将来の予測や憶測
- 一般的な常識

# 出力形式
検証可能な主張のみをJSON配列で返してください：

```json
[
  "主張1の文章",
  "主張2の文章",
  "主張3の文章"
]
```

主張が見つからない場合は空配列 [] を返してください。
JSON配列のみ返してください（コードブロックなし）。
"""

        try:
            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text.strip()

            # コードブロックを除去
            if result_text.startswith("```"):
                lines = result_text.split("\n")
                result_text = "\n".join(lines[1:-1]) if len(lines) > 2 else result_text

            claims = json.loads(result_text)

            if not isinstance(claims, list):
                print("[WARNING] Unexpected response format (not a list)")
                return []

            return claims

        except Exception as e:
            print(f"[ERROR] Claim extraction failed: {e}")
            return []

    def _verify_claim(
        self,
        claim: str,
        title: str,
        category: str
    ) -> Optional[FactCheckResult]:
        """
        Perplexity APIで主張を検証

        Args:
            claim: 検証する主張
            title: 記事タイトル（コンテキスト用）
            category: カテゴリ

        Returns:
            FactCheckResult or None
        """
        # Perplexity API呼び出し
        search_query = f"{claim} technical documentation verification"

        try:
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.perplexity_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-sonar-small-128k-online",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a technical fact-checker. Verify claims using official documentation and reliable sources."
                        },
                        {
                            "role": "user",
                            "content": f"Verify this technical claim: \"{claim}\"\n\nProvide: 1) verification status (verified/partially_verified/unverified/incorrect), 2) confidence score (0-1), 3) sources used, 4) corrected version if incorrect."
                        }
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.2,
                    "return_citations": True
                },
                timeout=30
            )

            if response.status_code != 200:
                print(f"[ERROR] Perplexity API error: {response.status_code}")
                return None

            result = response.json()

            # レスポンス解析
            verification_text = result["choices"][0]["message"]["content"]
            citations = result.get("citations", [])

            # Claudeで構造化
            return self._parse_verification_result(claim, verification_text, citations)

        except Exception as e:
            print(f"[ERROR] Verification failed for claim: {e}")
            return None

    def _parse_verification_result(
        self,
        claim: str,
        verification_text: str,
        citations: List[str]
    ) -> FactCheckResult:
        """
        検証結果を構造化

        Args:
            claim: 元の主張
            verification_text: Perplexityの検証結果
            citations: 引用URL

        Returns:
            FactCheckResult
        """
        # Claudeで結果を構造化
        prompt = f"""以下のPerplexity API検証結果を構造化してください。

元の主張: {claim}

検証結果:
{verification_text}

引用元: {json.dumps(citations, ensure_ascii=False)}

以下のJSON形式で返してください：

```json
{{
  "verification_status": "verified | partially_verified | unverified | incorrect",
  "confidence": 0.85,
  "corrected_claim": "修正版の主張（incorrectの場合のみ）",
  "notes": "検証に関する補足説明"
}}
```

JSON形式のみ返してください（コードブロックなし）。
"""

        try:
            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text.strip()

            # コードブロックを除去
            if result_text.startswith("```"):
                lines = result_text.split("\n")
                result_text = "\n".join(lines[1:-1]) if len(lines) > 2 else result_text

            parsed = json.loads(result_text)

            # 引用情報を整形
            sources = [{"url": url, "title": url} for url in citations[:5]]

            return FactCheckResult(
                original_claim=claim,
                verification_status=parsed["verification_status"],
                confidence=parsed["confidence"],
                sources=sources,
                corrected_claim=parsed.get("corrected_claim"),
                notes=parsed.get("notes")
            )

        except Exception as e:
            print(f"[ERROR] Result parsing failed: {e}")
            # フォールバック
            return FactCheckResult(
                original_claim=claim,
                verification_status="unverified",
                confidence=0.5,
                sources=[],
                notes="解析エラーが発生しました"
            )

    def _collect_citations(
        self,
        fact_check_results: List[FactCheckResult]
    ) -> List[Dict[str, str]]:
        """
        引用情報を収集

        Args:
            fact_check_results: 事実確認結果リスト

        Returns:
            引用情報のリスト
        """
        citations = []
        seen_urls = set()

        for result in fact_check_results:
            for source in result.sources:
                url = source["url"]
                if url not in seen_urls:
                    citations.append({
                        "title": source.get("title", url),
                        "url": url,
                        "snippet": f"Verification for: {result.original_claim[:50]}..."
                    })
                    seen_urls.add(url)

        return citations

    def _create_empty_result(self) -> ArticleFactCheck:
        """空の結果を作成"""
        return ArticleFactCheck(
            total_claims=0,
            verified_count=0,
            unverified_count=0,
            corrections_needed=0,
            fact_check_results=[],
            overall_accuracy=1.0,
            citations=[]
        )

    def update_markdown_with_fact_check(
        self,
        markdown_path: Path,
        fact_check: ArticleFactCheck
    ) -> bool:
        """
        マークダウンファイルに事実確認結果を追加

        Args:
            markdown_path: マークダウンファイルのパス
            fact_check: 事実確認結果

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

            # 1. フロントマターに引用情報追加
            if fact_check.citations:
                citations_json = json.dumps(fact_check.citations, ensure_ascii=False, indent=2)
                frontmatter += f"\nresearchCitations: {citations_json}"

            # 2. 本文に事実確認セクション追加（corrections_neededがある場合のみ）
            if fact_check.corrections_needed > 0:
                corrections_section = "\n\n## 📝 事実確認結果\n\n"
                corrections_section += f"この記事の技術的主張のうち、{fact_check.corrections_needed}件に修正が推奨されます。\n\n"

                for result in fact_check.fact_check_results:
                    if result.corrected_claim:
                        corrections_section += f"### 修正推奨\n\n"
                        corrections_section += f"**元の主張**: {result.original_claim}\n\n"
                        corrections_section += f"**推奨される修正**: {result.corrected_claim}\n\n"
                        if result.notes:
                            corrections_section += f"**補足**: {result.notes}\n\n"

                body = body.rstrip() + corrections_section

            # ファイル更新
            updated_content = f"---{frontmatter}---{body}"
            markdown_path.write_text(updated_content, encoding="utf-8")

            print(f"[OK] Markdown updated with fact check results: {markdown_path}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to update markdown: {e}")
            return False


def main():
    """メイン関数（テスト用）"""
    import sys
    from pathlib import Path

    if len(sys.argv) < 2:
        print("Usage: python fact_checker.py <markdown_file>")
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

    # 事実確認
    checker = FactChecker()
    fact_check = checker.check_article_facts(
        content=body,
        title=title,
        category=category
    )

    # マークダウン更新
    success = checker.update_markdown_with_fact_check(markdown_file, fact_check)

    # 結果表示
    print(f"\n{'='*60}")
    print(f"Fact Check Summary")
    print(f"{'='*60}")
    print(f"Total claims checked: {fact_check.total_claims}")
    print(f"Verified: {fact_check.verified_count}")
    print(f"Unverified: {fact_check.unverified_count}")
    print(f"Corrections needed: {fact_check.corrections_needed}")
    print(f"Overall accuracy: {fact_check.overall_accuracy:.1%}")
    print(f"Citations collected: {len(fact_check.citations)}")

    if success:
        print(f"\n[SUCCESS] Fact check completed and saved")
    else:
        print(f"\n[FAILED] Could not save fact check results")


if __name__ == "__main__":
    main()
