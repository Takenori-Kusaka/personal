# Usage Guide - Personal Digital Garden & Resume System

このリポジトリには2つのシステムがあります：**履歴書管理システム**と**デジタルガーデン自動化システム**

---

## 🚀 クイックスタート

### 前提条件

1. **Python 3.9+** with pip installed
2. **Git** configured with your credentials
3. **Node.js 18+** and npm (Astro用)
4. **API Keys** (デジタルガーデン自動化用):
   - `ANTHROPIC_API_KEY` - Claude AI分類用
   - `GEMINI_API_KEY` - Imagen 4サムネイル生成用（オプション）
   - `PERPLEXITY_API_KEY` - 事実確認用（オプション）

### インストール

```bash
# リポジトリをクローン
git clone <your-repo-url>
cd personal

# Python仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate     # Windows

# Python依存関係のインストール
pip install -r requirements.txt

# Astroプロジェクトのセットアップ
cd digital-garden
npm install
cd ..
```

---

## 🌿 デジタルガーデン自動化システム（メインシステム）

テキスト・音声・動画からAIで構造化されたコンテンツを自動生成。

### 環境変数設定

プロジェクトルートに`.env`ファイルを作成：

```bash
# 必須
ANTHROPIC_API_KEY=sk-ant-xxxxx

# オプション（機能を有効化する場合）
GEMINI_API_KEY=xxxxx           # Imagen 4サムネイル生成用
PERPLEXITY_API_KEY=pplx-xxxxx  # 事実確認用

# モデル設定（オプション）
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

### 基本的な使い方

#### 1. テキストファイルを処理

```bash
# フル機能で処理（分類 → サムネイル → Mermaid → 事実確認 → Git → GitHub Pages）
python process_content.py input/text/my-article.txt

# オプション付きで処理
python process_content.py input/text/my-article.txt --no-thumbnail  # サムネイルなし
python process_content.py input/text/my-article.txt --no-git       # Git操作なし
python process_content.py input/text/my-article.txt --no-push      # コミットのみ
```

#### 2. ディレクトリ全体を処理

```bash
# input/text/ 内の全.txtファイルを一括処理
python process_content.py input/text/
```

#### 3. 個別システムの実行

```bash
# Claude分類のみ
PYTHONPATH=. python automation/digital_garden_classifier.py input/text/article.txt

# ビジュアル強化のみ（サムネイル + Mermaid）
python automation/visual_enhancer.py digital-garden/src/content/insights/article.md

# 事実確認のみ
python automation/fact_checker.py digital-garden/src/content/insights/article.md

# Git自動化のみ
python automation/git_automation.py deploy
```

### 自動処理フロー

```
テキスト入力
    ↓
[1] Claude分類システム
    ├─ カテゴリ判定（insights/ideas/weekly-reviews）
    ├─ タイトル生成
    ├─ タグ付け
    └─ マークダウン構造化
    ↓
[2] ビジュアル強化
    ├─ Imagen 4でサムネイル生成
    └─ ClaudeでMermaid図表生成
    ↓
[3] 事実確認
    ├─ Perplexity APIで技術的主張を検証
    └─ 引用情報を追加
    ↓
[4] Astroビルド
    └─ 静的サイト生成
    ↓
[5] Git自動化
    ├─ Claudeでコミットメッセージ生成
    ├─ 変更をコミット
    └─ GitHub Pagesにプッシュ
    ↓
✅ デプロイ完了！
```

### コマンドラインオプション

| オプション | 説明 | デフォルト |
|------------|------|-----------|
| `--no-thumbnail` | サムネイル生成を無効化 | 有効 |
| `--no-mermaid` | Mermaid図表生成を無効化 | 有効 |
| `--no-fact-check` | 事実確認を無効化 | 有効 |
| `--no-git` | Git操作を無効化 | 有効 |
| `--no-push` | プッシュせずコミットのみ | プッシュする |

### カスタマイズ例

```bash
# ローカル確認用（Gitなし、サムネイルなし、事実確認なし）
python process_content.py input/text/draft.txt --no-git --no-thumbnail --no-fact-check

# コミットのみ（プッシュしない）
python process_content.py input/text/article.txt --no-push

# 分類とビジュアルのみ
python process_content.py input/text/quick-note.txt --no-fact-check --no-git
```

---

## 📄 履歴書管理システム

YAMLデータから専門的な履歴書を生成。

### 使い方

1. **プロフィールデータを編集**:
   ```bash
   nano data/profile.yml
   ```

2. **履歴書生成**:
   ```bash
   python src/main.py
   ```

3. **出力を確認**:
   - Markdown: `output/resume.md`
   - HTML: `output/resume.html`

### カスタマイズ

- **テンプレート**: `templates/resume_template.md`を編集
- **スタイリング**: `templates/styles/web_style.css`を変更
- **データ構造**: `data/schema.yml`を参照

---

## 🎯 コンテンツカテゴリ

デジタルガーデンシステムが自動分類するカテゴリ：

- **💡 Insights** (`insights/`): 技術的学び、洞察、トラブルシューティング
- **💭 Ideas** (`ideas/`): アイデア、構想、システム設計
- **📅 Weekly Reviews** (`weekly-reviews/`): 週次振り返り、進捗報告

---

## 🔧 ディレクトリ構造

```
personal/
├── automation/                        # 自動化システム
│   ├── digital_garden_classifier.py  # Claude分類
│   ├── visual_enhancer.py            # ビジュアル強化
│   ├── fact_checker.py               # 事実確認
│   ├── git_automation.py             # Git自動化
│   ├── integrated_pipeline.py        # 統合パイプライン
│   └── utils/
│       └── env_loader.py             # 環境変数管理
│
├── input/                            # 入力ファイル（gitignore）
│   ├── text/                         # テキストファイル
│   ├── audio/                        # 音声ファイル（将来）
│   └── video/                        # 動画ファイル（将来）
│
├── digital-garden/                   # Astroサイト
│   ├── src/
│   │   ├── content/                  # コンテンツコレクション
│   │   │   ├── insights/
│   │   │   ├── ideas/
│   │   │   └── weekly-reviews/
│   │   ├── pages/                    # ページテンプレート
│   │   ├── layouts/                  # レイアウトコンポーネント
│   │   └── components/               # UIコンポーネント
│   └── public/
│       └── images/                   # 生成画像
│           └── thumbnails/
│
├── process_content.py                # メインエントリーポイント
├── requirements.txt                  # Python依存関係
└── .env                              # 環境変数（gitignore）
```

---

## 🐛 トラブルシューティング

### よくある問題

#### 1. ModuleNotFoundError: No module named 'automation'

```bash
# 解決方法: PYTHONPATH を設定
export PYTHONPATH=.  # Linux/Mac
set PYTHONPATH=.     # Windows

# または、プロジェクトルートから実行
python -m automation.digital_garden_classifier input/text/article.txt
```

#### 2. ANTHROPIC_API_KEY not found

```bash
# .envファイルがプロジェクトルートにあることを確認
ls -la .env

# 環境変数が正しく読み込まれているか確認
python -c "from automation.utils.env_loader import load_environment; load_environment(); import os; print(os.getenv('ANTHROPIC_API_KEY'))"
```

#### 3. Imagen 4画像生成エラー

```bash
# サムネイル生成を無効化して実行
python process_content.py input/text/article.txt --no-thumbnail
```

#### 4. Perplexity API エラー

```bash
# 事実確認を無効化して実行
python process_content.py input/text/article.txt --no-fact-check
```

#### 5. Git push エラー

```bash
# リモートリポジトリの設定を確認
git remote -v

# プッシュせずコミットのみ
python process_content.py input/text/article.txt --no-push
```

#### 6. Astro build エラー

```bash
# Astro依存関係を再インストール
cd digital-garden
npm install
npm run build
```

---

## 📊 ワークフロー例

### 日次コンテンツ処理

```bash
# 1. 新しいテキストファイルを作成
echo "今日学んだこと..." > input/text/daily-learning.txt

# 2. 自動処理実行
python process_content.py input/text/daily-learning.txt

# 3. 結果確認
git log --oneline -1
```

### 週次履歴書更新

```bash
# 1. プロフィール情報を更新
nano data/profile.yml

# 2. 履歴書生成
python src/main.py

# 3. 出力確認
open output/resume.html
```

---

## 📚 その他のリソース

- **API Documentation**:
  - [Anthropic Claude API](https://docs.anthropic.com/)
  - [Google Gemini API (Imagen 4)](https://ai.google.dev/docs)
  - [Perplexity API](https://docs.perplexity.ai/)
- **Astro Documentation**: [docs.astro.build](https://docs.astro.build/)

---

## 🤝 コントリビュート

1. リポジトリをフォーク
2. フィーチャーブランチを作成: `git checkout -b feature-name`
3. 変更を加えて十分にテスト
4. プルリクエストを提出

---

**Last Updated**: 2025-10-04
**Version**: 2.0.0 - Digital Garden Automation Enhanced
