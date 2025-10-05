# 🏗️ 技術アーキテクチャ詳細

## 📋 目次

1. [システムアーキテクチャ](#システムアーキテクチャ)
2. [コンポーネント詳細](#コンポーネント詳細)
3. [データモデル](#データモデル)
4. [API統合](#api統合)
5. [パフォーマンス最適化](#パフォーマンス最適化)
6. [セキュリティ](#セキュリティ)
7. [拡張性・スケーラビリティ](#拡張性スケーラビリティ)

---

## 🎯 システムアーキテクチャ

### アーキテクチャパターン

本システムは以下のアーキテクチャパターンを採用しています:

1. **パイプライン・アーキテクチャ**: 順次処理フロー
2. **マイクロサービス風設計**: 疎結合なコンポーネント
3. **イベントドリブン**: Git pushトリガーのCI/CD
4. **静的サイト生成（SSG）**: Jamstackアーキテクチャ

### レイヤー構成

```
┌─────────────────────────────────────────────────┐
│         Presentation Layer (Frontend)          │
│  - Astro Static Site                           │
│  - Tailwind CSS Styling                        │
│  - TypeScript Type Safety                      │
└──────────────────┬──────────────────────────────┘
                   │ HTML/CSS/JS
┌──────────────────┴──────────────────────────────┐
│           Content Layer (Markdown)             │
│  - Astro Content Collections                   │
│  - MDX Support                                 │
│  - Frontmatter Metadata                        │
└──────────────────┬──────────────────────────────┘
                   │ File System
┌──────────────────┴──────────────────────────────┐
│        Processing Layer (Automation)           │
│  - Whisper Transcription                       │
│  - Claude Classification                       │
│  - Perplexity Research                         │
└──────────────────┬──────────────────────────────┘
                   │ API Calls
┌──────────────────┴──────────────────────────────┐
│          AI Services Layer (External)          │
│  - Anthropic Claude API                        │
│  - Perplexity AI API                           │
│  - Hugging Face Models                         │
└──────────────────┬──────────────────────────────┘
                   │ HTTP/REST
┌──────────────────┴──────────────────────────────┐
│        Infrastructure Layer (GitHub)           │
│  - GitHub Actions (CI/CD)                      │
│  - GitHub Pages (Hosting)                      │
│  - GitHub Repository (Version Control)         │
└─────────────────────────────────────────────────┘
```

---

## 🧩 コンポーネント詳細

### 1. Whisper Transcription Component

**技術スタック:**
- モデル: `kotoba-tech/kotoba-whisper-v2.0`
- フレームワーク: Hugging Face Transformers
- バックエンド: PyTorch

**アーキテクチャ:**
```python
class WhisperProcessor:
    def __init__(self, config: TranscriptionConfig):
        self.model_name = config.model_name
        self.device = self._detect_device(config.device)
        self.processor = WhisperProcessor.from_pretrained(self.model_name)
        self.model = WhisperForConditionalGeneration.from_pretrained(
            self.model_name
        ).to(self.device)

    async def transcribe(self, audio_path: Path) -> TranscriptionResult:
        """
        音声ファイルを文字起こし

        Process:
        1. 音声読み込み（librosa）
        2. 前処理（リサンプリング、正規化）
        3. モデル推論（セグメント単位）
        4. 後処理（信頼度計算、整形）

        Returns:
            TranscriptionResult with text and confidence
        """
        # 音声読み込み
        audio, sr = librosa.load(audio_path, sr=16000)

        # 前処理
        inputs = self.processor(
            audio,
            sampling_rate=16000,
            return_tensors="pt"
        ).to(self.device)

        # 推論
        with torch.no_grad():
            predicted_ids = self.model.generate(
                inputs.input_features,
                language="ja",
                task="transcribe"
            )

        # デコード
        transcription = self.processor.batch_decode(
            predicted_ids,
            skip_special_tokens=True
        )[0]

        # 信頼度計算
        confidence = self._calculate_confidence(predicted_ids)

        return TranscriptionResult(
            text=transcription,
            confidence=confidence,
            segments=self._extract_segments(predicted_ids)
        )
```

**最適化ポイント:**
- GPU自動検出（CUDA/MPS/CPU）
- バッチ処理対応
- メモリ効率的なストリーミング処理
- キャッシュ活用

### 2. Claude Classification Component

**技術スタック:**
- API: Anthropic Claude API
- モデル: claude-3-5-sonnet-20241022
- プロトコル: REST API

**アーキテクチャ:**
```python
class ClaudeClassifier:
    def __init__(self, config: ClassificationConfig):
        self.client = anthropic.Anthropic(
            api_key=os.environ["ANTHROPIC_API_KEY"]
        )
        self.model = config.model
        self.max_tokens = config.max_tokens
        self.temperature = config.temperature

    async def classify_content(
        self,
        content: str
    ) -> ClassificationResult:
        """
        コンテンツを分類・構造化

        Process:
        1. プロンプト構築
        2. Claude API呼び出し
        3. 構造化データ抽出
        4. バリデーション

        Returns:
            ClassificationResult with category, title, summary, tags
        """
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(content)

        # Claude API呼び出し
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        # 構造化データ抽出
        response_text = message.content[0].text
        structured_data = self._parse_response(response_text)

        # バリデーション
        validated_data = self._validate_classification(structured_data)

        return ClassificationResult(**validated_data)

    def _build_system_prompt(self) -> str:
        """システムプロンプト構築"""
        return """
        あなたは優れたコンテンツ分類・構造化アシスタントです。

        以下のカテゴリに分類してください:
        - insight: ビジネス洞察、技術学習、専門知識
        - idea: 新しいアイデア、将来構想、企画案
        - weekly-review: 週次振り返り、成長記録、目標評価

        以下の形式でJSON出力してください:
        {
          "category": "insight",
          "title": "魅力的なタイトル",
          "summary": "150文字以内の要約",
          "priority": "high | medium | low",
          "tags": ["タグ1", "タグ2"],
          "body": "構造化されたMarkdown本文"
        }
        """
```

**プロンプトエンジニアリング:**
- Few-shot learning: 分類例の提示
- Chain-of-thought: 段階的思考の誘導
- Structured output: JSON形式での出力指定

### 3. Perplexity Research Component

**技術スタック:**
- API: Perplexity AI API
- モデル: llama-3.1-sonar-small-128k-online
- 機能: リアルタイムWeb検索

**アーキテクチャ:**
```python
class PerplexityResearcher:
    def __init__(self, config: ResearchConfig):
        self.api_key = os.environ["PERPLEXITY_API_KEY"]
        self.model = config.model
        self.temperature = config.temperature

    async def research_content(
        self,
        content: ClassificationResult
    ) -> ResearchResult:
        """
        コンテンツの裏付け調査

        Process:
        1. 検索クエリ生成
        2. Perplexity API呼び出し
        3. 情報源の信頼性評価
        4. コンテンツへの統合

        Returns:
            ResearchResult with enhanced content and sources
        """
        # 検索クエリ生成
        queries = self._generate_research_queries(content)

        # 並列検索
        research_tasks = [
            self._search_query(query)
            for query in queries
        ]
        results = await asyncio.gather(*research_tasks)

        # 情報源評価
        evaluated_sources = self._evaluate_sources(results)

        # コンテンツ強化
        enhanced_content = self._enhance_content(
            content,
            evaluated_sources
        )

        return ResearchResult(
            enhanced_content=enhanced_content,
            sources=evaluated_sources,
            confidence=self._calculate_research_confidence(results)
        )

    def _evaluate_sources(
        self,
        results: List[SearchResult]
    ) -> List[EvaluatedSource]:
        """
        情報源の信頼性評価

        評価基準:
        - ドメイン信頼性（.gov, .edu, 公式サイト）
        - コンテンツ鮮度（公開日）
        - 引用数・評判
        """
        evaluated = []
        for result in results:
            score = 0.0

            # ドメイン評価
            if self._is_authoritative_domain(result.url):
                score += 0.4

            # 鮮度評価
            if self._is_recent(result.published_date):
                score += 0.3

            # コンテンツ評価
            if self._has_citations(result.content):
                score += 0.3

            evaluated.append(EvaluatedSource(
                url=result.url,
                title=result.title,
                snippet=result.snippet,
                credibility_score=score
            ))

        return sorted(evaluated, key=lambda x: x.credibility_score, reverse=True)
```

**信頼性評価ロジック:**
```python
AUTHORITATIVE_DOMAINS = {
    ".gov": 1.0,      # 政府機関
    ".edu": 0.9,      # 教育機関
    ".org": 0.7,      # 非営利団体
    "github.com": 0.8, # 技術リポジトリ
    "arxiv.org": 0.9,  # 学術論文
}

RECENCY_THRESHOLD = {
    "week": 1.0,
    "month": 0.8,
    "year": 0.5,
    "older": 0.2
}
```

### 4. Git Automation Component

**技術スタック:**
- ライブラリ: GitPython
- CLI: GitHub CLI（gh command）

**アーキテクチャ:**
```python
class GitAutomation:
    def __init__(self, config: GitConfig):
        self.repo = git.Repo(config.repository_path)
        self.main_branch = config.main_branch
        self.auto_push = config.auto_push
        self.create_pr = config.create_pr

    async def commit_and_deploy(
        self,
        files: List[Path],
        metadata: ContentMetadata
    ) -> DeploymentResult:
        """
        Git操作の自動化

        Process:
        1. ブランチ作成
        2. ファイル追加
        3. コミット作成
        4. プッシュ
        5. PR作成（オプション）

        Returns:
            DeploymentResult with commit hash and PR URL
        """
        # ブランチ作成
        branch_name = self._generate_branch_name(metadata)
        self.repo.git.checkout("-b", branch_name)

        # ファイル追加
        for file in files:
            self.repo.index.add([str(file)])

        # コミット
        commit_message = self._generate_commit_message(metadata)
        commit = self.repo.index.commit(commit_message)

        # プッシュ
        if self.auto_push:
            origin = self.repo.remote(name="origin")
            origin.push(branch_name)

        # PR作成
        pr_url = None
        if self.create_pr:
            pr_url = await self._create_pull_request(
                branch_name,
                metadata
            )

        return DeploymentResult(
            commit_hash=commit.hexsha,
            branch=branch_name,
            pr_url=pr_url
        )

    def _generate_commit_message(
        self,
        metadata: ContentMetadata
    ) -> str:
        """
        構造化されたコミットメッセージ生成

        Format:
        🤖 Automated content: {category} - {title}

        Generated from: {source_file}
        Session: {session_id}

        🤖 Generated with Claude Code Automation
        """
        return f"""🤖 Automated content: {metadata.category} - {metadata.title}

Generated from: {metadata.source_file}
Session: {metadata.session_id}

🤖 Generated with Claude Code Automation"""
```

---

## 📊 データモデル

### コンテンツスキーマ

```typescript
// digital-garden/src/content/config.ts

import { defineCollection, z } from 'astro:content';

const insightsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    category: z.enum(['insight', 'idea', 'weekly-review']),
    tags: z.array(z.string()),
    priority: z.enum(['high', 'medium', 'low']).default('medium'),
    draft: z.boolean().default(false),
    featured: z.boolean().default(false),
  }),
});

export const collections = {
  'insights': insightsCollection,
  'ideas': ideasCollection,
  'weekly-reviews': weeklyReviewsCollection,
};
```

### Resume YAMLスキーマ

```yaml
# data/profile.yml

profile:
  meta:
    version: '2.0'
    last_updated: '2025-10-05'
    generated_by: resume-system-v2

  personal:
    name: string
    gender: string
    birth_date: string
    age: string
    location: string
    hobbies: array<string>

  education:
    - level: string           # 中学校、高校、大学
      school_name: string
      department: string
      graduation_date: string
      notes: string

  career:
    companies:
      - company_id: string
        name: string
        employment_period:
          start_date: string
          end_date: string
        position: string
        description: string
        reason_for_leaving: string

        skills: array<string>

        projects:
          - project_id: string
            title: string
            period:
              start_date: string
              end_date: string
            role: string
            team_size: string
            responsibilities: array<string>
            achievements: array<string>
```

---

## 🔌 API統合

### Claude API

**エンドポイント:**
```
POST https://api.anthropic.com/v1/messages
```

**リクエスト:**
```json
{
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 4000,
  "temperature": 0.7,
  "system": "You are a content classification assistant...",
  "messages": [
    {
      "role": "user",
      "content": "Classify this content..."
    }
  ]
}
```

**レスポンス:**
```json
{
  "id": "msg_...",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "{\"category\": \"insight\", ...}"
    }
  ],
  "model": "claude-3-5-sonnet-20241022",
  "usage": {
    "input_tokens": 523,
    "output_tokens": 1247
  }
}
```

**エラーハンドリング:**
```python
async def call_claude_with_retry(
    self,
    prompt: str,
    max_retries: int = 3
) -> str:
    """リトライロジック付きAPI呼び出し"""
    for attempt in range(max_retries):
        try:
            return await self._call_claude(prompt)
        except anthropic.RateLimitError:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        except anthropic.APIError as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"API error, retrying: {e}")

    raise Exception("Max retries exceeded")
```

### Perplexity API

**エンドポイント:**
```
POST https://api.perplexity.ai/chat/completions
```

**リクエスト:**
```json
{
  "model": "llama-3.1-sonar-small-128k-online",
  "messages": [
    {
      "role": "system",
      "content": "You are a research assistant..."
    },
    {
      "role": "user",
      "content": "Research this topic: ..."
    }
  ],
  "temperature": 0.2,
  "max_tokens": 2000,
  "search_recency_filter": "month"
}
```

**レスポンス:**
```json
{
  "id": "...",
  "model": "llama-3.1-sonar-small-128k-online",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Research findings..."
      },
      "citations": [
        {
          "url": "https://...",
          "title": "...",
          "snippet": "..."
        }
      ]
    }
  ]
}
```

---

## ⚡ パフォーマンス最適化

### 1. Whisper最適化

**GPU活用:**
```python
def _detect_device(self, preferred: str = "auto") -> str:
    """最適なデバイス検出"""
    if preferred != "auto":
        return preferred

    if torch.cuda.is_available():
        return "cuda"  # NVIDIA GPU
    elif torch.backends.mps.is_available():
        return "mps"   # Apple Silicon
    else:
        return "cpu"
```

**バッチ処理:**
```python
async def transcribe_batch(
    self,
    audio_files: List[Path],
    batch_size: int = 4
) -> List[TranscriptionResult]:
    """バッチ処理で効率化"""
    results = []
    for i in range(0, len(audio_files), batch_size):
        batch = audio_files[i:i+batch_size]
        batch_results = await asyncio.gather(*[
            self.transcribe(file) for file in batch
        ])
        results.extend(batch_results)
    return results
```

### 2. API呼び出し最適化

**並列処理:**
```python
async def process_multiple_contents(
    self,
    contents: List[str]
) -> List[ClassificationResult]:
    """並列API呼び出し"""
    tasks = [self.classify_content(content) for content in contents]
    return await asyncio.gather(*tasks)
```

**キャッシング:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_classification(content_hash: str) -> Optional[ClassificationResult]:
    """分類結果のキャッシュ"""
    return self._cache.get(content_hash)
```

### 3. Astroビルド最適化

**設定:**
```javascript
// astro.config.mjs
export default defineConfig({
  output: 'static',
  build: {
    inlineStylesheets: 'auto',
  },
  vite: {
    build: {
      cssCodeSplit: true,
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor': ['react', 'react-dom'],
          },
        },
      },
    },
  },
});
```

**画像最適化:**
```astro
---
import { Image } from 'astro:assets';
import heroImage from '../assets/hero.png';
---

<Image
  src={heroImage}
  alt="Hero"
  width={1200}
  height={600}
  format="webp"
  quality={80}
/>
```

---

## 🔐 セキュリティ

### 1. APIキー管理

**環境変数:**
```bash
# 環境変数で管理（.envファイル）
ANTHROPIC_API_KEY="sk-ant-..."
PERPLEXITY_API_KEY="pplx-..."

# .envファイルは.gitignoreに追加
echo ".env" >> .gitignore
```

**GitHub Secrets:**
```yaml
# GitHub Actions用
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  PERPLEXITY_API_KEY: ${{ secrets.PERPLEXITY_API_KEY }}
```

### 2. 入力検証

```python
def validate_input_file(file_path: Path) -> bool:
    """入力ファイルの検証"""
    # サイズチェック
    if file_path.stat().st_size > 500 * 1024 * 1024:  # 500MB
        raise ValueError("File too large")

    # 形式チェック
    allowed_extensions = {'.mp3', '.wav', '.mp4', '.txt', '.md'}
    if file_path.suffix.lower() not in allowed_extensions:
        raise ValueError("Invalid file type")

    # セキュリティスキャン（オプション）
    if ENABLE_VIRUS_SCAN:
        scan_result = virus_scan(file_path)
        if not scan_result.is_clean:
            raise SecurityError("File failed security scan")

    return True
```

### 3. コンテンツサニタイゼーション

```python
def sanitize_content(content: str) -> str:
    """コンテンツのサニタイゼーション"""
    # PII（個人識別情報）除去
    if REMOVE_PII:
        content = remove_email_addresses(content)
        content = remove_phone_numbers(content)
        content = remove_credit_cards(content)

    # HTMLエスケープ
    content = html.escape(content)

    # 不適切な文字列除去
    content = remove_profanity(content)

    return content
```

---

## 🚀 拡張性・スケーラビリティ

### 1. 新しいAIモデル追加

```python
# automation/components/classification/new_model_classifier.py

class NewModelClassifier(BaseClassifier):
    """新しいAIモデルの統合"""

    async def classify_content(self, content: str) -> ClassificationResult:
        # 新しいモデルのロジック
        pass
```

### 2. 新しいコンテンツタイプ追加

```typescript
// digital-garden/src/content/config.ts

const newCollection = defineCollection({
  type: 'content',
  schema: z.object({
    // 新しいスキーマ
  }),
});

export const collections = {
  'insights': insightsCollection,
  'ideas': ideasCollection,
  'weekly-reviews': weeklyReviewsCollection,
  'new-type': newCollection,  // 追加
};
```

### 3. スケーリング戦略

**水平スケーリング:**
- 複数インスタンスでの並列処理
- ロードバランシング

**垂直スケーリング:**
- GPUリソースの増強
- メモリ・CPU拡張

---

## 📚 関連ドキュメント

- [日々の運用ガイド](./DAILY_OPERATIONS_GUIDE.md)
- [プロジェクト全体構成](./PROJECT_OVERVIEW.md)
- [API設定ガイド](./API_SETUP_GUIDE.md)

---

**最終更新**: 2025-10-05
**バージョン**: 2.0
