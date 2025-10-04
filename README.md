# Personal Digital Garden & Resume Management System

**AI-Powered Content Processing and Resume Generation Platform**

An integrated system combining intelligent content automation with professional resume management, featuring AI-powered transcription, classification, and digital garden publishing.

[![Build and Deploy](https://github.com/[username]/personal/actions/workflows/build-and-deploy.yml/badge.svg)](https://github.com/[username]/personal/actions/workflows/build-and-deploy.yml)

## 🎯 概要

このシステムは2つの主要コンポーネントで構成されています：

### 🤖 Digital Garden Automation System
AI-powered content processing pipeline that transforms audio, video, and text inputs into structured digital garden content.

**主な機能:**
- 🎙️ **Whisper Transcription**: Japanese-optimized audio/video transcription
- 🧠 **Claude Classification**: Intelligent content categorization and structuring
- 🔍 **Perplexity Research**: Fact-checking and information enhancement
- 📦 **Git Automation**: Automated commits, PRs, and GitHub Pages deployment

### 📄 Resume Management System
YAML-based professional resume generation system for efficient career documentation.

**主な機能:**
- 📝 **YAML Data Management**: Version-controlled, easily editable career data
- 🔄 **Automatic Generation**: Markdown and HTML format conversion
- 🎨 **Professional Design**: Corporate-ready, high-quality output
- 🚀 **CI/CD Integration**: Automated builds via GitHub Actions

## 📁 プロジェクト構成

```
personal/
├── 📁 automation/                    # 🤖 Digital Garden Automation System
│   ├── digital_garden_processor.py  # メインオーケストレーションシステム
│   ├── run_automation.py            # CLIエントリーポイント
│   ├── requirements.txt             # Python依存関係
│   ├── README.md                    # 自動化システムドキュメント
│   ├── 📁 components/
│   │   ├── 📁 transcription/        # Whisper転写システム
│   │   ├── 📁 classification/       # Claude分類システム
│   │   ├── 📁 research/             # Perplexity研究システム
│   │   └── 📁 deployment/           # Git自動化システム
│   ├── 📁 config/
│   │   ├── settings.py             # 設定管理
│   │   └── default.yaml            # デフォルト設定
│   └── 📁 utils/                   # 共通ユーティリティ
├── 📁 input/                       # 自動化システム入力ディレクトリ
│   ├── 📁 audio/                   # 音声ファイル
│   ├── 📁 video/                   # 動画ファイル
│   ├── 📁 text/                    # テキストファイル
│   └── 📁 processed/               # 処理済みファイル
├── 📁 digital-garden/              # デジタルガーデン出力
│   └── 📁 src/content/             # Astro CMS構造化コンテンツ
├── 📁 src/                         # 📄 Resume Management System
│   ├── 📁 core/
│   │   ├── converter.py            # YAML→Markdown変換エンジン
│   │   └── __init__.py
│   ├── 📁 utils/
│   │   ├── yaml_handler.py         # YAML処理ユーティリティ
│   │   ├── html_generator.py       # HTML生成エンジン
│   │   └── __init__.py
│   ├── main.py                     # メインエントリーポイント
│   └── migrate_data.py             # データ移行スクリプト
├── 📁 data/
│   ├── profile.yml                 # メインプロファイルデータ
│   └── schema.yml                  # データスキーマ定義
├── 📁 templates/
│   ├── resume_template.md          # Markdownテンプレート
│   └── 📁 styles/
│       ├── web_style.css           # Web表示用スタイル
│       └── pdf_style.css           # PDF生成用スタイル
├── 📁 claudedocs/                  # プロジェクト分析・設計文書
├── 📁 .github/workflows/           # CI/CD自動化
└── 📁 output/                      # 履歴書生成ファイル
│   ├── resume.md               # 生成されたMarkdown
│   └── resume.html             # 生成されたHTML
├── .gitignore                  # Git無視設定
├── requirements.txt            # Python依存関係
├── pyproject.toml             # プロジェクト設定
├── profile_legacy_backup.yml  # レガシーデータバックアップ
└── README.md                   # このファイル
```

## 🚀 使用方法

### 前提条件

- Python 3.9+
- 必要なパッケージ（requirements.txt参照）

### ローカル実行

1. **環境セットアップ**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate

   pip install -r requirements.txt
   ```

2. **職務経歴書生成**
   ```bash
   python src/main.py
   ```

3. **出力確認**
   - `output/resume.md`: Markdown形式
   - `output/resume.html`: HTML形式

### データ更新

1. `data/profile.yml` を編集
2. Git にコミット・プッシュ
3. GitHub Actions が自動実行
4. GitHub Pages が自動更新

## 📊 生成例

### コンソール出力
```
🚀 Starting resume generation...
✅ Successfully loaded profile data
✅ Generated Markdown: output/resume.md
✅ Generated HTML: output/resume.html

============================================================
📋 RESUME GENERATION SUMMARY
============================================================
👤 Name: 日下武紀
🎂 Age: 33
📍 Location: 滋賀県

💼 Career Summary:
   Companies: 3
   - 太陽精機株式会社: 1 projects
   - 株式会社メイテック: 4 projects
   - オムロンソフトウェア株式会社: 9 projects
   Total projects: 14

📄 Output:
   Markdown: output/resume.md
   MD Size: 11520 bytes
   HTML: output/resume.html
   HTML Size: 21.8 KB
============================================================
```

## 🔧 技術仕様

### アーキテクチャ
```
YAML Data → Python Processing → Markdown → Multi Output
    ↓             ↓                ↓          ↓
profile.yml → converter.py → resume.md → [HTML, Web]
    ↓             ↓                ↓          ↓
[Validation] → [Quality Check] → [GitHub Pages] → [Public Access]
```

### 主要ライブラリ
- **PyYAML**: YAML データ処理
- **Jinja2**: テンプレートエンジン
- **Markdown**: Markdown→HTML変換
- **Rich**: 美しいコンソール出力

### 依存関係の最小化
- **コア機能**: 3つのライブラリのみでシンプル構成
- **拡張性**: 将来のPDF生成、文章校正機能に対応
- **開発ツール**: 品質管理用ツールは開発時のみ使用

## 🎨 デザイン仕様

### Web版特徴
- **レスポンシブデザイン**: 全デバイス対応
- **プロフェッショナル**: 企業提出レベル
- **アクセシビリティ**: WCAG 2.1 準拠
- **SEO最適化**: 検索エンジン対応

### 印刷対応
- **A4サイズ**: 印刷レイアウト最適化
- **高品質フォント**: Noto Sans JP
- **適切な余白**: 読みやすさ重視

## 🤖 自動化ワークフロー

### GitHub Actions
- **品質チェック**: YAML検証、ファイル生成テスト
- **自動ビルド**: Markdown・HTML生成
- **自動デプロイ**: GitHub Pages公開
- **エラー通知**: 失敗時の詳細レポート

### トリガー
- `main` ブランチへのプッシュ
- `data/`, `src/`, `templates/` の変更
- プルリクエスト時の品質チェック

## 📈 今後の拡張予定

### Phase 6: 高度機能実装
- [ ] **PDF生成**: Windows対応のPDF出力機能
- [ ] **文章校正**: AI活用による自動校正機能
- [ ] **多言語対応**: 英語版職務経歴書生成
- [ ] **テーマシステム**: 複数デザインテーマ対応

### Phase 7: 分析・最適化
- [ ] **統計ダッシュボード**: プロジェクト分析と可視化
- [ ] **SEO強化**: 検索エンジン最適化
- [ ] **パフォーマンス向上**: 生成速度の最適化
- [ ] **ユーザビリティ改善**: よりユーザーフレンドリーな操作

## 🔧 メンテナンス

### 定期メンテナンス
- **依存関係更新**: 月次でライブラリバージョン確認
- **セキュリティ**: 脆弱性スキャン実行
- **バックアップ**: プロファイルデータの定期バックアップ

### 品質管理
- **自動テスト**: GitHub Actionsでの品質チェック
- **コード品質**: Black、Flake8、mypyでの静的解析
- **文書同期**: READMEと実装の整合性維持

## 📝 ライセンス

個人使用目的のプライベートプロジェクトです。

## 👤 作成者

**日下武紀 (Takenori Kusaka)**
- IoT・クラウド・生成AIエンジニア
- オムロンソフトウェア株式会社

---

**システムバージョン**: v2.0
**最終更新**: 2025年10月04日
**生成システム**: Resume Management System v2.0