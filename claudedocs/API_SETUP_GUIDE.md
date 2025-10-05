# 🔑 API設定ガイド

## 📋 目次

1. [必要なAPI](#必要なapi)
2. [Anthropic Claude API設定](#anthropic-claude-api設定)
3. [Perplexity AI API設定](#perplexity-ai-api設定)
4. [GitHub設定](#github設定)
5. [環境変数設定](#環境変数設定)
6. [トラブルシューティング](#トラブルシューティング)

---

## 🎯 必要なAPI

本システムでは以下のAPIキーが必要です:

| API | 用途 | 必須/オプション | 料金 |
|-----|------|----------------|------|
| **Anthropic Claude** | コンテンツ分類・構造化 | 必須 | 従量課金 |
| **Perplexity AI** | 事実確認・情報補足 | 必須 | 従量課金 |
| **GitHub** | リポジトリ操作・Actions | 必須 | 無料 |
| **Hugging Face** | Whisperモデル | 任意 | 無料 |

---

## 🤖 Anthropic Claude API設定

### ステップ1: アカウント作成

1. **Anthropic Consoleにアクセス**
   - URL: https://console.anthropic.com/

2. **サインアップ**
   - メールアドレスで登録
   - 認証コードを入力

3. **支払い情報登録**
   - クレジットカード情報を入力
   - 初回クレジット: $5（プロモーション時）

### ステップ2: APIキー発行

1. **APIキー作成**
   ```
   Console → Settings → API Keys → Create Key
   ```

2. **キー名設定**
   ```
   Name: digital-garden-automation
   ```

3. **APIキーをコピー**
   ```
   sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

   ⚠️ **重要**: このキーは二度と表示されません。必ず安全な場所に保存してください。

### ステップ3: 利用プラン確認

**料金体系（2025年10月現在）:**
```
Claude 3.5 Sonnet:
- Input:  $3.00 / 1M tokens
- Output: $15.00 / 1M tokens

目安:
- 1記事分類: 約1,000トークン = $0.018
- 月100記事: 約$1.80
```

### ステップ4: 使用量モニタリング

```
Console → Usage → API Usage
```

**アラート設定:**
```
Settings → Billing → Usage Alerts
月間上限を設定: $50
```

---

## 🔍 Perplexity AI API設定

### ステップ1: アカウント作成

1. **Perplexity APIポータルにアクセス**
   - URL: https://www.perplexity.ai/settings/api

2. **サインアップ**
   - Googleアカウントまたはメールで登録

3. **APIアクセス申請**
   - プロフィール情報を入力
   - 利用目的を記載

### ステップ2: APIキー発行

1. **APIキー作成**
   ```
   Settings → API → Generate New API Key
   ```

2. **キー名設定**
   ```
   Name: digital-garden-research
   ```

3. **APIキーをコピー**
   ```
   pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### ステップ3: 利用プラン選択

**料金体系（2025年10月現在）:**
```
Sonar Small (128K context):
- $1.00 / 1M input tokens
- $1.00 / 1M output tokens

目安:
- 1記事調査: 約2,000トークン = $0.004
- 月100記事: 約$0.40
```

### ステップ4: 使用量確認

```
API Dashboard → Usage → Monthly Usage
```

---

## 🐙 GitHub設定

### ステップ1: リポジトリ設定

1. **リポジトリ作成（済みの場合はスキップ）**
   ```bash
   # ローカルで初期化
   git init
   git remote add origin https://github.com/yourusername/personal.git
   ```

2. **GitHub Pagesを有効化**
   ```
   Repository → Settings → Pages
   Source: GitHub Actions
   ```

### ステップ2: GitHub Secrets設定

1. **Secretsページにアクセス**
   ```
   Repository → Settings → Secrets and variables → Actions
   ```

2. **APIキーを追加**
   ```
   New repository secret

   Name: ANTHROPIC_API_KEY
   Secret: sk-ant-api03-xxxxx...

   Name: PERPLEXITY_API_KEY
   Secret: pplx-xxxxx...
   ```

### ステップ3: GitHub CLI設定（オプション）

**インストール:**
```bash
# Windows (winget)
winget install --id GitHub.cli

# macOS (Homebrew)
brew install gh

# Linux (apt)
sudo apt install gh
```

**認証:**
```bash
gh auth login
```

**トークン設定:**
```bash
# Personal Access Token作成
GitHub → Settings → Developer settings → Personal access tokens → Generate new token

Permissions:
☑ repo (Full control of private repositories)
☑ workflow (Update GitHub Action workflows)

# トークンを環境変数に設定
export GITHUB_TOKEN="ghp_xxxxx..."
```

---

## ⚙️ 環境変数設定

### Windows

**方法1: システム環境変数**
```powershell
# PowerShellで設定
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'sk-ant-...', 'User')
[System.Environment]::SetEnvironmentVariable('PERPLEXITY_API_KEY', 'pplx-...', 'User')
```

**方法2: .envファイル**
```bash
# プロジェクトルートに.envファイル作成
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx...
PERPLEXITY_API_KEY=pplx-xxxxx...
GITHUB_TOKEN=ghp_xxxxx...

# .envファイルを.gitignoreに追加
echo ".env" >> .gitignore
```

**方法3: Python-dotenv**
```python
# automation/utils/env_loader.py
from dotenv import load_dotenv
import os

def load_environment():
    """環境変数読み込み"""
    load_dotenv()

    required_vars = [
        "ANTHROPIC_API_KEY",
        "PERPLEXITY_API_KEY"
    ]

    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing environment variables: {missing}")

    return {
        "anthropic_key": os.getenv("ANTHROPIC_API_KEY"),
        "perplexity_key": os.getenv("PERPLEXITY_API_KEY"),
        "github_token": os.getenv("GITHUB_TOKEN", "")
    }
```

### macOS/Linux

**方法1: .bashrc/.zshrc**
```bash
# ~/.bashrcまたは~/.zshrcに追加
export ANTHROPIC_API_KEY="sk-ant-api03-xxxxx..."
export PERPLEXITY_API_KEY="pplx-xxxxx..."
export GITHUB_TOKEN="ghp_xxxxx..."

# 反映
source ~/.bashrc  # または source ~/.zshrc
```

**方法2: .envファイル**
```bash
# プロジェクトルートに.envファイル作成
# （Windowsと同様）
```

---

## 🧪 動作確認

### Claude API接続テスト

```python
# test_claude_api.py
import anthropic
import os

def test_claude_connection():
    """Claude API接続テスト"""
    try:
        client = anthropic.Anthropic(
            api_key=os.environ["ANTHROPIC_API_KEY"]
        )

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Hello, Claude!"}
            ]
        )

        print("✅ Claude API接続成功")
        print(f"Response: {message.content[0].text}")
        return True

    except Exception as e:
        print(f"❌ Claude API接続失敗: {e}")
        return False

if __name__ == "__main__":
    test_claude_connection()
```

**実行:**
```bash
python test_claude_api.py
```

### Perplexity API接続テスト

```python
# test_perplexity_api.py
import requests
import os

def test_perplexity_connection():
    """Perplexity API接続テスト"""
    try:
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.environ['PERPLEXITY_API_KEY']}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "user",
                    "content": "What is 2+2?"
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        print("✅ Perplexity API接続成功")
        print(f"Response: {response.json()['choices'][0]['message']['content']}")
        return True

    except Exception as e:
        print(f"❌ Perplexity API接続失敗: {e}")
        return False

if __name__ == "__main__":
    test_perplexity_connection()
```

**実行:**
```bash
python test_perplexity_api.py
```

### 統合テスト

```bash
# 自動化システムのテストモード実行
python automation/run_automation.py --test-components
```

**期待される出力:**
```
🤖 Digital Garden Automation System - Component Test

🎙️  Testing Whisper Transcription...
✅ Whisper: Available (kotoba-whisper-v2.0)

🧠 Testing Claude Classification...
✅ Claude: Available (claude-3-5-sonnet-20241022)

🔍 Testing Perplexity Research...
✅ Perplexity: Available (llama-3.1-sonar-small-128k-online)

📦 Testing Git Automation...
✅ Git: Available (Repository: /path/to/personal)

All components operational! ✅
```

---

## 🐛 トラブルシューティング

### エラー1: APIキーが見つからない

**症状:**
```
Error: ANTHROPIC_API_KEY environment variable not set
```

**対策:**
```bash
# 環境変数が設定されているか確認
echo $ANTHROPIC_API_KEY  # macOS/Linux
$env:ANTHROPIC_API_KEY    # Windows PowerShell

# 設定されていない場合は再設定
export ANTHROPIC_API_KEY="sk-ant-..."  # macOS/Linux
$env:ANTHROPIC_API_KEY="sk-ant-..."     # Windows PowerShell
```

### エラー2: APIレート制限

**症状:**
```
Error: Rate limit exceeded (429 Too Many Requests)
```

**対策:**
```python
# リトライロジックの実装
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def call_api_with_retry():
    # API呼び出し
    pass
```

### エラー3: 認証エラー

**症状:**
```
Error: Authentication failed (401 Unauthorized)
```

**対策:**
```bash
# APIキーの有効性を確認
# 1. コンソールでキーが有効か確認
# 2. キーの権限を確認
# 3. 必要に応じて新しいキーを発行
```

### エラー4: GitHub Actions失敗

**症状:**
```
Error: secrets.ANTHROPIC_API_KEY not found
```

**対策:**
```bash
# GitHub SecretsにAPIキーが設定されているか確認
Repository → Settings → Secrets and variables → Actions

# 確認項目:
# ✅ ANTHROPIC_API_KEY
# ✅ PERPLEXITY_API_KEY

# 設定されていない場合は追加
```

---

## 💰 コスト管理

### 月間コスト試算

**想定使用量:**
```yaml
処理数: 月100記事

Claude API:
  - 分類: 100回 × $0.018 = $1.80
  - 合計: $1.80/月

Perplexity API:
  - 調査: 50回（Insightのみ） × $0.004 = $0.20
  - 合計: $0.20/月

総計: 約$2.00/月
```

### コスト最適化

**1. キャッシング活用**
```python
# 分類結果をキャッシュ
CACHE_TTL = 24  # hours

@cached(ttl=CACHE_TTL)
def classify_content(content_hash: str):
    # 同じコンテンツは再分類しない
    pass
```

**2. バッチ処理**
```python
# 複数コンテンツを一度に処理
async def process_batch(contents: List[str]):
    # 並列処理でAPI呼び出し削減
    pass
```

**3. 使用量モニタリング**
```python
def log_api_usage(api_name: str, tokens: int, cost: float):
    """API使用量をログ記録"""
    logger.info(f"{api_name}: {tokens} tokens, ${cost:.4f}")
```

---

## 📚 関連ドキュメント

- [日々の運用ガイド](./DAILY_OPERATIONS_GUIDE.md)
- [プロジェクト全体構成](./PROJECT_OVERVIEW.md)
- [技術アーキテクチャ詳細](./TECHNICAL_ARCHITECTURE.md)

---

## 🔗 公式リンク

- **Anthropic Claude**: https://console.anthropic.com/
- **Perplexity AI**: https://www.perplexity.ai/settings/api
- **GitHub API**: https://docs.github.com/en/rest
- **Hugging Face**: https://huggingface.co/kotoba-tech/kotoba-whisper-v2.0

---

**最終更新**: 2025-10-05
**バージョン**: 2.0
