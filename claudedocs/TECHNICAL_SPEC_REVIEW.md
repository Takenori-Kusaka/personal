# Digital Garden 技術仕様書（事前レビュー用）

## 📋 概要

本ドキュメントは、Digital Gardenシステムの技術仕様を説明し、採用技術の妥当性を事前レビューいただくためのものです。

---

## 🎨 フロントエンド技術スタック

### ✅ 採用技術（提案）

#### **コアフレームワーク: バニラJS + Modern CSS**

**選定理由:**
1. **シンプルさ**: 静的サイトジェネレーター不要、ビルドプロセス最小化
2. **パフォーマンス**: フレームワークのオーバーヘッドなし
3. **GitHub Pages互換性**: 完全な静的HTML/CSS/JSで動作
4. **メンテナンス性**: 依存関係が少なく、長期保守が容易

#### **スタイリング**
```yaml
CSS:
  - Pure CSS (CSS Variables使用)
  - CSS Grid / Flexbox
  - モバイルファースト レスポンシブデザイン
  - アニメーション: CSS Transitions/Animations

フォント:
  - Google Fonts: Noto Sans JP（日本語）
  - システムフォントフォールバック
```

#### **JavaScript**
```yaml
アーキテクチャ:
  - ES6+ モジュール（type="module"）
  - Vanilla JavaScript（フレームワーク不使用）
  - Fetch API（コンテンツ動的読み込み）

機能:
  - マークダウンファイルの動的読み込み
  - コンテンツフィルタリング・検索
  - タグベースナビゲーション
  - レスポンシブメニュー
```

#### **マークダウン処理**
```yaml
ライブラリ: marked.js (CDN経由)
  - 理由: 軽量（~5KB gzipped）
  - フロントマター対応
  - サニタイゼーション組込み
  - カスタムレンダラー拡張可能
```

### 🔄 代替案との比較

| 技術 | メリット | デメリット | 採用判断 |
|------|----------|------------|----------|
| **React/Next.js** | 高度なUI、SEO最適化 | ビルド必要、複雑 | ❌ オーバースペック |
| **Vue.js** | 学習曲線緩やか | ビルド必要 | ❌ 静的サイトには不要 |
| **Jekyll/Hugo** | 完全静的生成 | Ruby/Go環境必要 | ❌ Python環境と不一致 |
| **11ty** | シンプル静的生成 | Node.js環境必要 | △ 検討可能 |
| **Vanilla JS** | 依存なし、軽量 | 手動実装必要 | ✅ **採用** |

---

## 🔧 バックエンド（自動化パイプライン）技術スタック

### ✅ 採用技術（確定）

#### **言語: Python 3.10+**
```yaml
理由:
  - AI/ML ライブラリの豊富さ
  - Whisper, Transformersとの親和性
  - 非同期処理（asyncio）サポート
  - 既存プロジェクト（Resume生成）との統一
```

#### **音声認識: Whisper (kotoba-whisper-v2.0)**
```yaml
モデル: kotoba-tech/kotoba-whisper-v2.0
プラットフォーム: Hugging Face Transformers

選定理由:
  - 日本語特化モデル（精度向上）
  - ローカル実行可能（APIコスト削減）
  - オープンソース（ライセンス問題なし）

代替案:
  - OpenAI Whisper API: 高精度だがAPIコスト発生
  - AssemblyAI: 英語特化、日本語精度劣る
```

#### **コンテンツ分類: Claude 3.5 Sonnet**
```yaml
モデル: claude-3-5-sonnet-20241022
API: Anthropic Claude API

選定理由:
  - 高度な文脈理解能力
  - 日本語の自然な処理
  - 長文コンテキスト対応（200K tokens）
  - 構造化出力（JSON mode）

代替案:
  - GPT-4: 同等だがコスト高
  - Gemini Pro: 日本語精度やや劣る
```

#### **事実確認: Perplexity AI (sonar)**
```yaml
モデル: sonar
API: Perplexity API

選定理由:
  - リアルタイムWeb検索統合
  - 引用ソース自動付与
  - 事実確認に最適化

代替案:
  - Tavily API: 検索特化だが引用機能弱い
  - Google Custom Search: APIクォータ制限厳しい
```

#### **Git自動化**
```yaml
ツール: GitPython + GitHub CLI (gh)

機能:
  - 自動コミット（Conventional Commits形式）
  - プルリクエスト自動作成
  - GitHub Actions トリガー
```

---

## 🏗️ システムアーキテクチャ

### **データフロー**

```
[入力ファイル]
  ├─ 音声/動画 (input/audio/, input/video/)
  └─ テキスト (input/text/)
         ↓
[1. Whisper文字起こし]
  - 音声/動画 → テキスト変換
  - メタデータ抽出（話者、タイムスタンプ）
         ↓
[2. Claude分類]
  - カテゴリ分類（Insights/Ideas/Weekly Reviews）
  - タグ自動付与
  - タイトル・要約生成
  - フロントマター作成
         ↓
[3. Perplexity事実確認]
  - 重要な主張の裏付け調査
  - 引用ソース追加
  - 信頼性スコア付与
         ↓
[4. マークダウン生成]
  - 構造化されたMDファイル作成
  - digital-garden/content/ に配置
         ↓
[5. Git自動デプロイ]
  - 変更を自動コミット
  - GitHub Actions トリガー
  - GitHub Pages 自動更新
         ↓
[公開Webサイト]
  - https://takenori-kusaka.github.io/personal/
```

### **ディレクトリ構造**

```
personal/
├── input/                          # 入力ファイル（gitignore）
│   ├── .gitkeep                    # ディレクトリ保持用
│   ├── audio/                      # 音声ファイル
│   ├── video/                      # 動画ファイル
│   ├── text/                       # テキストファイル
│   └── TODO_FOR_USER.md           # ユーザー様TODO
│
├── digital-garden/                 # 静的Webサイト
│   ├── index.html                  # ホームページ
│   ├── assets/
│   │   ├── css/
│   │   │   └── style.css           # メインスタイルシート
│   │   ├── js/
│   │   │   └── main.js             # メインスクリプト
│   │   └── images/                 # 画像ファイル
│   │
│   └── content/                    # コンテンツ（自動生成）
│       ├── insights/               # 洞察・気づき
│       ├── ideas/                  # アイデア・構想
│       └── weekly-reviews/         # 週次振り返り
│
├── automation/                     # 自動化システム
│   ├── digital_garden_processor.py # メインパイプライン
│   ├── components/
│   │   ├── transcription/
│   │   │   └── whisper_processor.py
│   │   ├── classification/
│   │   │   └── claude_classifier.py
│   │   ├── research/
│   │   │   └── perplexity_researcher.py
│   │   └── deployment/
│   │       └── git_automation.py
│   │
│   └── utils/
│       └── env_loader.py           # 環境変数管理
│
├── .github/
│   └── workflows/
│       └── build-and-deploy.yml    # GitHub Actions
│
├── .env                            # 環境変数（gitignore）
├── .env.template                   # 環境変数テンプレート
├── requirements.txt                # Python依存関係
└── requirements-test.txt           # テスト依存関係
```

---

## 🔐 セキュリティ・プライバシー考慮事項

### **APIキー管理**
```yaml
方式: .env ファイル（gitignore）

保護対象:
  - ANTHROPIC_API_KEY
  - PERPLEXITY_API_KEY

GitHub Actions:
  - GitHub Secrets経由で安全に注入
  - ログに出力されない設定
```

### **入力ファイル保護**
```yaml
方針: input/ ディレクトリ全体をgitignore

理由:
  - 個人情報・機密情報を含む可能性
  - 音声/動画ファイルは容量大
  - .gitkeep のみコミット
```

### **コンテンツ公開制御**
```yaml
自動公開: digital-garden/content/ のみ

手動レビュー:
  - Gitコミット前に内容確認可能
  - 公開したくない場合はコミット拒否
```

---

## ⚡ パフォーマンス最適化

### **フロントエンド**
```yaml
- Lazy Loading: 画像・コンテンツの遅延読み込み
- Code Splitting: 必要なJSのみ読み込み
- CSS Minification: 本番ビルド時に圧縮
- CDN利用: Google Fonts, marked.js
```

### **バックエンド**
```yaml
- 非同期処理: asyncioで並列実行
- キャッシュ: Whisperモデルをメモリ保持
- バッチ処理: 複数ファイルを効率的に処理
```

---

## 🧪 テスト戦略

### **テストカバレッジ目標**

| レイヤー | カバレッジ目標 | 現状 |
|----------|---------------|------|
| Unit Tests | 80%+ | 実装前 |
| Integration Tests | 60%+ | 実装前 |
| E2E Tests | 主要フロー網羅 | 基盤完成 |

### **テストツール**
```yaml
- pytest: Pythonユニット・統合テスト
- pytest-asyncio: 非同期処理テスト
- pytest-playwright: E2Eブラウザテスト
- pytest-cov: カバレッジ測定
```

---

## 📦 デプロイメント戦略

### **GitHub Pages（現状）**
```yaml
方式: GitHub Actions自動デプロイ

トリガー:
  - mainブランチへのpush
  - digital-garden/ 配下の変更
  - workflow_dispatch（手動実行）

URL: https://takenori-kusaka.github.io/personal/
```

### **将来的な拡張（オプション）**
```yaml
- カスタムドメイン設定
- Cloudflare Pages（高速化）
- Vercel/Netlify（プレビュー環境）
```

---

## 🔄 開発ワークフロー

### **フェーズ1: フロントエンド完成（現在）**
```
1. CSS実装（style.css）
2. JavaScript実装（main.js）
3. ダミーコンテンツで動作確認
4. レスポンシブデザイン検証
```

### **フェーズ2: バックエンド実装**
```
1. Whisper文字起こし実装
2. Claude分類実装
3. Perplexity事実確認実装
4. Git自動化実装
5. 統合テスト
```

### **フェーズ3: 本番運用**
```
1. 実データでE2Eテスト
2. パフォーマンス最適化
3. エラーハンドリング強化
4. ドキュメント整備
```

---

## 🤔 レビューポイント

### ご確認いただきたい点:

1. **フロントエンド技術選定**
   - バニラJS + Pure CSS で問題ないか？
   - フレームワーク（React/Vue等）を使用すべきか？

2. **AI モデル選定**
   - Whisper, Claude, Perplexityの組み合わせで適切か？
   - 他のモデル・サービスの検討が必要か？

3. **デザイン方向性**
   - 現在のHTML構造・デザインコンセプトで良いか？
   - 特定のデザインシステム・テーマの希望はあるか？

4. **セキュリティ・プライバシー**
   - 入力ファイルのgitignore対応で十分か？
   - 追加のセキュリティ要件はあるか？

5. **将来の拡張性**
   - 検索機能の追加
   - コメント機能（外部サービス連携）
   - RSS/Atom フィード生成
   - 多言語対応

---

## 📅 実装スケジュール（提案）

```
Week 1: フロントエンド完成
  - Day 1-2: CSS/JS実装
  - Day 3: レスポンシブ対応
  - Day 4: ダミーコンテンツテスト

Week 2: バックエンド実装
  - Day 5-6: Whisper + Claude
  - Day 7: Perplexity + Git
  - Day 8: 統合テスト

Week 3: 本番運用準備
  - Day 9-10: E2Eテスト
  - Day 11: 最適化
  - Day 12: ドキュメント
```

---

**レビュー依頼日**: 2025-10-04
**次回更新**: レビューフィードバック反映後

---

## 💬 フィードバックをお願いします

上記の技術仕様について、以下の点をご確認・ご指示ください：

- [ ] フロントエンド技術スタックの承認
- [ ] AIモデル選定の承認
- [ ] デザイン方向性の承認
- [ ] 追加要件・変更要望
- [ ] 優先順位の調整

ご不明点・ご要望があれば、お気軽にお知らせください！
