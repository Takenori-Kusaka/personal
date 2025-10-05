# 🌱 Digital Garden - プロジェクト全体構成

## 📋 目次

1. [プロジェクト概要](#プロジェクト概要)
2. [アーキテクチャ全体像](#アーキテクチャ全体像)
3. [ディレクトリ構成](#ディレクトリ構成)
4. [主要コンポーネント](#主要コンポーネント)
5. [技術スタック](#技術スタック)
6. [データフロー](#データフロー)
7. [デプロイメント構成](#デプロイメント構成)

---

## 🎯 プロジェクト概要

### プロジェクト名
**Personal Digital Garden with AI Automation**

### 目的
音声メモ・動画・テキストから自動的にブログ記事を生成し、個人の知識・学びを"育てる"デジタルガーデンシステム

### コンセプト
従来のブログ（時系列）ではなく、知識を有機的につなげ継続的に育てる「デジタルガーデン」の思想に基づく

### 主要機能

1. **自動コンテンツ生成**
   - 音声/動画からの自動文字起こし（Whisper）
   - AI分類・構造化（Claude）
   - 事実確認・裏付け調査（Perplexity）

2. **Resume管理システム**
   - YAMLベースの職務経歴管理
   - 自動HTML/Markdown生成
   - GitHub Actions連携

3. **静的サイト生成**
   - Astro 5.14.1による高速サイト
   - Tailwind CSSスタイリング
   - レスポンシブデザイン

4. **CI/CD自動化**
   - GitHub Actions完全自動デプロイ
   - GitHub Pages公開
   - 自動ビルド・テスト

---

## 🏗️ アーキテクチャ全体像

```
┌─────────────────────────────────────────────────────────────┐
│                     INPUT LAYER                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │  Audio   │  │  Video   │  │  Text    │                  │
│  │  Files   │  │  Files   │  │  Files   │                  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
│       └──────────────┴──────────────┘                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 PROCESSING LAYER                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Whisper Transcription (kotoba-whisper-v2.0)        │   │
│  │  - Japanese-optimized speech-to-text                │   │
│  │  - Confidence scoring                               │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Claude Classification (claude-3-5-sonnet)          │   │
│  │  - Content categorization                           │   │
│  │  - Title/summary generation                         │   │
│  │  - Structured content creation                      │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Perplexity Research (llama-3.1-sonar)              │   │
│  │  - Fact checking                                    │   │
│  │  - Information enhancement                          │   │
│  │  - Source credibility                               │   │
│  └────────────────────┬─────────────────────────────────┘   │
└───────────────────────┼─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   CONTENT LAYER                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Digital Garden Content (Astro Collections)         │   │
│  │  ┌──────────┐  ┌──────────┐  ┌────────────────┐    │   │
│  │  │ Insights │  │  Ideas   │  │ Weekly Reviews │    │   │
│  │  └──────────┘  └──────────┘  └────────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Resume System (YAML → HTML/Astro)                  │   │
│  │  - profile.yml (source of truth)                    │   │
│  │  - Auto-generation on changes                       │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  BUILD & DEPLOY LAYER                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Git Automation                                      │   │
│  │  - Auto commit & push                               │   │
│  │  - Branch management                                │   │
│  │  - PR creation (optional)                           │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  GitHub Actions                                      │   │
│  │  - Resume generation                                │   │
│  │  - Astro build                                      │   │
│  │  - Deploy to GitHub Pages                           │   │
│  └────────────────────┬─────────────────────────────────┘   │
└───────────────────────┼─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  GitHub Pages                                        │   │
│  │  https://takenori-kusaka.github.io/personal/        │   │
│  │  - Static site hosting                              │   │
│  │  - CDN delivery                                     │   │
│  │  - HTTPS enabled                                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 ディレクトリ構成

```
personal/
├── .github/
│   └── workflows/
│       └── deploy-digital-garden.yml      # GitHub Actions設定
│
├── automation/                            # 自動化パイプライン
│   ├── components/                        # 処理コンポーネント
│   │   ├── transcription/
│   │   │   └── whisper_processor.py       # Whisper文字起こし
│   │   ├── classification/
│   │   │   └── claude_classifier.py       # Claude分類
│   │   ├── research/
│   │   │   └── perplexity_researcher.py   # Perplexity調査
│   │   └── deployment/
│   │       └── git_automation.py          # Git自動化
│   ├── config/
│   │   ├── default.yaml                   # デフォルト設定
│   │   └── settings.py                    # 設定管理
│   ├── utils/
│   │   ├── logging_setup.py               # ログ設定
│   │   └── file_handler.py                # ファイル操作
│   ├── digital_garden_processor.py        # メインオーケストレーター
│   ├── run_automation.py                  # CLIエントリーポイント
│   ├── requirements.txt                   # Python依存関係
│   └── README.md                          # 自動化システムREADME
│
├── data/                                  # データソース
│   ├── profile.yml                        # 職務経歴データ（source of truth）
│   └── schema.yml                         # データスキーマ定義
│
├── digital-garden/                        # Astroサイト
│   ├── src/
│   │   ├── content/                       # コンテンツコレクション
│   │   │   ├── config.ts                  # コンテンツ設定
│   │   │   ├── insights/                  # 洞察・学び
│   │   │   ├── ideas/                     # アイデア・構想
│   │   │   └── weekly-reviews/            # 週次振り返り
│   │   ├── layouts/
│   │   │   ├── BaseLayout.astro           # ベースレイアウト
│   │   │   └── ContentLayout.astro        # コンテンツレイアウト
│   │   ├── components/
│   │   │   ├── Header.astro               # ヘッダー
│   │   │   ├── Footer.astro               # フッター
│   │   │   ├── Card.astro                 # カードコンポーネント
│   │   │   └── Hero.astro                 # ヒーローセクション
│   │   ├── pages/
│   │   │   ├── index.astro                # トップページ
│   │   │   ├── about.astro                # プロフィール
│   │   │   ├── resume.astro               # 職務経歴書
│   │   │   ├── insights/
│   │   │   │   ├── index.astro            # Insights一覧
│   │   │   │   └── [slug].astro           # 個別記事
│   │   │   ├── ideas/
│   │   │   │   ├── index.astro            # Ideas一覧
│   │   │   │   └── [slug].astro           # 個別記事
│   │   │   └── weekly-reviews/
│   │   │       ├── index.astro            # 週次振り返り一覧
│   │   │       └── [slug].astro           # 個別振り返り
│   │   └── styles/
│   │       └── global.css                 # グローバルスタイル
│   ├── public/                            # 静的ファイル
│   │   ├── favicon.png
│   │   ├── hero-background.png
│   │   ├── og-image.png
│   │   └── profile-photo.png
│   ├── astro.config.mjs                   # Astro設定
│   ├── tailwind.config.mjs                # Tailwind設定
│   ├── tsconfig.json                      # TypeScript設定
│   └── package.json                       # Node依存関係
│
├── input/                                 # 入力ファイル（.gitignore）
│   ├── audio/                             # 音声ファイル
│   ├── video/                             # 動画ファイル
│   ├── text/                              # テキストファイル
│   └── processed/                         # 処理済みアーカイブ
│
├── src/                                   # Resume生成システム
│   ├── main.py                            # メイン処理
│   ├── core/
│   │   ├── generator.py                   # HTML生成
│   │   └── parser.py                      # YAMLパース
│   └── config/
│       └── settings.py                    # 設定
│
├── output/                                # 生成ファイル出力
│   ├── resume.html                        # 生成されたHTML
│   └── resume.md                          # 生成されたMarkdown
│
├── templates/                             # テンプレート
│   ├── layouts/
│   │   └── resume_template.html
│   └── styles/
│       └── resume.css
│
├── claudedocs/                            # プロジェクトドキュメント
│   ├── DAILY_OPERATIONS_GUIDE.md          # 運用ガイド
│   ├── PROJECT_OVERVIEW.md                # この文書
│   ├── TECHNICAL_ARCHITECTURE.md          # 技術詳細
│   └── API_SETUP_GUIDE.md                 # API設定
│
├── logs/                                  # ログファイル
│   └── automation.log
│
├── tests/                                 # テストコード
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── requirements.txt                       # Python依存関係（全体）
├── pyproject.toml                         # Pythonプロジェクト設定
├── README.md                              # プロジェクトREADME
└── USAGE.md                               # 使い方ガイド
```

---

## 🧩 主要コンポーネント

### 1. 自動化パイプライン (`automation/`)

**役割**: コンテンツの自動処理・生成

**主要クラス:**

#### WhisperProcessor
```python
# automation/components/transcription/whisper_processor.py
class WhisperProcessor:
    """
    音声/動画ファイルの文字起こし
    - モデル: kotoba-tech/kotoba-whisper-v2.0
    - 日本語最適化
    - 信頼度スコアリング
    """
```

#### ClaudeClassifier
```python
# automation/components/classification/claude_classifier.py
class ClaudeClassifier:
    """
    コンテンツ分類・構造化
    - カテゴリ判定（insight/idea/weekly-review）
    - タイトル・要約生成
    - タグ付け
    - Markdown構造化
    """
```

#### PerplexityResearcher
```python
# automation/components/research/perplexity_researcher.py
class PerplexityResearcher:
    """
    事実確認・情報補足
    - 最新情報検索
    - 信頼性検証
    - 情報源追加
    """
```

#### GitAutomation
```python
# automation/components/deployment/git_automation.py
class GitAutomation:
    """
    Git操作自動化
    - commit作成
    - push実行
    - PR作成（オプション）
    """
```

### 2. Resume管理システム (`src/`)

**役割**: YAML → HTML/Astro変換

**データフロー:**
```
data/profile.yml → src/main.py → output/resume.html
                              → output/resume.md
```

**自動化:**
- GitHub Actionsでprofile.yml変更を検知
- 自動生成してresume.astroに配置
- Astroビルドに組み込み

### 3. Digital Garden (`digital-garden/`)

**役割**: 静的サイト生成・公開

**Astroコンテンツコレクション:**
```typescript
// src/content/config.ts
const insightsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.date(),
    tags: z.array(z.string()),
    priority: z.enum(['high', 'medium', 'low'])
  })
});
```

**ページ構成:**
- `/`: トップページ（最新記事表示）
- `/about/`: プロフィール
- `/resume/`: 職務経歴書
- `/insights/`: 洞察・学び一覧
- `/ideas/`: アイデア一覧
- `/weekly-reviews/`: 週次振り返り

---

## 🛠️ 技術スタック

### フロントエンド

| 技術 | バージョン | 用途 |
|------|-----------|------|
| Astro | 5.14.1 | 静的サイト生成 |
| TypeScript | 5.x | 型安全性 |
| Tailwind CSS | 3.x | スタイリング |
| MDX | - | Markdown拡張 |

### バックエンド（自動化）

| 技術 | バージョン | 用途 |
|------|-----------|------|
| Python | 3.9+ | 自動化スクリプト |
| Whisper | kotoba-v2.0 | 音声認識 |
| Claude API | 3.5 Sonnet | AI分類 |
| Perplexity API | Sonar | AI検索 |

### Python主要ライブラリ

```txt
anthropic==0.42.0           # Claude API
openai-whisper==20231117    # Whisper
transformers==4.36.0        # Hugging Face
pyyaml==6.0.1              # YAML処理
jinja2==3.1.2              # テンプレート
requests==2.31.0           # HTTP通信
gitpython==3.1.40          # Git操作
```

### インフラ・CI/CD

| 技術 | 用途 |
|------|------|
| GitHub Actions | CI/CDパイプライン |
| GitHub Pages | 静的サイトホスティング |
| Git | バージョン管理 |

---

## 🔄 データフロー

### コンテンツ生成フロー

```
1. INPUT
   ├─ 音声ファイル: input/audio/*.m4a
   ├─ 動画ファイル: input/video/*.mp4
   └─ テキスト: input/text/*.txt

2. TRANSCRIPTION
   ├─ Whisper処理
   ├─ 信頼度スコア算出
   └─ テキスト出力

3. CLASSIFICATION
   ├─ Claude API呼び出し
   ├─ カテゴリ判定
   ├─ タイトル生成
   ├─ 要約生成
   └─ タグ付け

4. RESEARCH（Insightのみ）
   ├─ Perplexity API呼び出し
   ├─ 事実確認
   ├─ 情報補足
   └─ 参考資料追加

5. GENERATION
   ├─ Markdownファイル生成
   └─ Frontmatter付与

6. OUTPUT
   └─ digital-garden/src/content/{category}/{slug}.md

7. GIT AUTOMATION
   ├─ git add
   ├─ git commit
   └─ git push

8. CI/CD
   ├─ GitHub Actions起動
   ├─ Resumeビルド
   ├─ Astroビルド
   └─ GitHub Pages公開

9. PUBLICATION
   └─ https://takenori-kusaka.github.io/personal/
```

### Resume更新フロー

```
1. YAML SOURCE
   └─ data/profile.yml

2. EDIT & COMMIT
   ├─ profile.yml編集
   └─ git push

3. GITHUB ACTIONS TRIGGER
   ├─ python src/main.py
   ├─ resume.html生成
   └─ digital-garden/src/pages/resume.astroにコピー

4. BUILD & DEPLOY
   ├─ Astroビルド
   └─ GitHub Pages公開
```

---

## 🚀 デプロイメント構成

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy-digital-garden.yml

name: Deploy Digital Garden

on:
  push:
    branches: [main]
    paths:
      - 'digital-garden/**'
      - 'data/**'
      - 'src/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      # 1. Checkout
      - uses: actions/checkout@v4

      # 2. Setup Python
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      # 3. Generate Resume
      - run: python src/main.py
      - run: cp output/resume.html digital-garden/src/pages/resume.astro

      # 4. Setup Node.js
      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      # 5. Build Astro
      - working-directory: digital-garden
        run: |
          npm ci
          npm run build

      # 6. Deploy to GitHub Pages
      - uses: actions/upload-pages-artifact@v3
        with:
          path: digital-garden/dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/deploy-pages@v4
```

### デプロイメントフロー

```
開発環境（ローカル）
  ├─ コンテンツ作成: input/に配置
  ├─ 自動処理実行: python automation/run_automation.py
  ├─ ローカル確認: npm run dev
  └─ commit & push

         ↓

GitHub（リモート）
  ├─ Actions起動
  ├─ Resume生成
  ├─ Astroビルド
  └─ Pages公開

         ↓

本番環境（GitHub Pages）
  └─ https://takenori-kusaka.github.io/personal/
```

---

## 🔐 環境変数・設定

### 必須環境変数

```bash
# Claude API
export ANTHROPIC_API_KEY="sk-ant-..."

# Perplexity API
export PERPLEXITY_API_KEY="pplx-..."

# GitHub CLI（オプション）
export GITHUB_TOKEN="ghp_..."
```

### 設定ファイル

```yaml
# automation/config/default.yaml

paths:
  input_audio: "input/audio"
  input_video: "input/video"
  input_text: "input/text"
  digital_garden: "digital-garden"

transcription:
  model_name: "kotoba-tech/kotoba-whisper-v2.0"
  device: "auto"
  language: "ja"

classification:
  model: "claude-3-5-sonnet-20241022"
  temperature: 0.7

research:
  model: "llama-3.1-sonar-small-128k-online"
  temperature: 0.2

git:
  auto_push: true
  create_pr: false
```

---

## 📊 パフォーマンス特性

### ビルド時間

| 項目 | 時間 |
|------|------|
| Whisper文字起こし（10分音声） | 2-3分 |
| Claude分類 | 5-10秒 |
| Perplexity調査 | 10-20秒 |
| Astroビルド | 10-20秒 |
| **合計（1コンテンツ）** | **約3-5分** |

### サイトパフォーマンス

| メトリクス | スコア |
|-----------|--------|
| Lighthouse Performance | 95+ |
| First Contentful Paint | <1s |
| Time to Interactive | <2s |
| Total Blocking Time | <100ms |

---

## 🧪 テスト戦略

### 単体テスト
```bash
pytest tests/unit/
```

### 統合テスト
```bash
pytest tests/integration/
```

### E2Eテスト
```bash
pytest tests/e2e/
```

---

## 📚 関連ドキュメント

- [日々の運用ガイド](./DAILY_OPERATIONS_GUIDE.md)
- [技術アーキテクチャ詳細](./TECHNICAL_ARCHITECTURE.md)
- [API設定ガイド](./API_SETUP_GUIDE.md)
- [自動化システムREADME](../automation/README.md)

---

**プロジェクト開始**: 2025-10-04
**最終更新**: 2025-10-05
**バージョン**: 2.0
**メンテナ**: 日下武紀 (Takenori Kusaka)
