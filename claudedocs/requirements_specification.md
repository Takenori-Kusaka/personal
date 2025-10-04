# 職務経歴書管理システム v2.0 - 要件定義書

**作成日**: 2025年10月04日
**プロジェクト名**: 個人職務経歴書管理システム モダナイゼーション
**対象者**: 日下武紀（個人専用システム）
**優先方針**: 技術モダナイゼーション重視

---

## 1. プロジェクト概要

### 1.1 背景・目的
- **現状**: AsciiDoc＋古いPython環境による職務経歴書生成システム
- **課題**: 技術陳腐化、出力品質不足、メンテナンス困難
- **目的**: Markdown中心の現代的ワークフローへの移行とCI/CD自動化

### 1.2 プロジェクトスコープ
- **対象**: 個人専用（日下武紀氏）職務経歴書管理システム
- **公開範囲**: 個人ポートフォリオサイトの一部として公開（GitHub Pages）
- **運用形態**: ローカル開発 ＋ GitHub管理 ＋ Web公開のハイブリッド

---

## 2. 機能要件

### 2.1 コア機能

#### 2.1.1 データ管理機能
- **主データ形式**: YAML（profile.yml継続使用）
- **データ完全移行**: 既存profile.ymlの全内容を新システムに移行
- **長文管理**: YAMLの複数行文字列（`|`記法）を活用した長文記載対応
- **外部編集対応**: VS Code + YAML Language Server による編集環境最適化

#### 2.1.2 文書生成機能
- **Markdown生成**: YAML → Markdown変換（中間フォーマット）
- **HTML生成**: Markdown → 高品質HTML（GitHub Pages対応）
- **PDF生成**: Markdown → 企業提出レベルPDF（A4印刷対応）
- **テンプレート管理**: 職務経歴書フォーマットのテンプレート化

#### 2.1.3 品質保証機能
- **データバリデーション**: YAML形式・必須項目チェック
- **文章校正**: 誤字脱字・敬語・ビジネス文書適切性・技術用語統一性
- **出力品質検証**: PDF生成結果の自動検証

### 2.2 拡張機能

#### 2.2.1 自動化機能
- **GitHub Actions CI/CD**: コミット時の自動生成・検証・デプロイ
- **継続的品質改善**: 文章校正結果の蓄積と改善提案
- **バージョン管理**: 履歴書バージョンの自動管理

#### 2.2.2 公開・共有機能
- **GitHub Pages統合**: 個人ポートフォリオサイトとしての統合公開
- **URL共有**: 職務経歴書への直接リンク提供
- **ダウンロード対応**: PDF直接ダウンロード機能

---

## 3. 非機能要件

### 3.1 品質要件

#### 3.1.1 PDF出力品質
- **参考品質**: 提供サンプル画像レベル（企業提出レベル）
- **フォーマット**: A4サイズ、印刷対応レイアウト
- **デザイン要素**:
  - 清潔で読みやすいレイアウト
  - 適切な余白とフォント設定
  - プロフェッショナルな見た目
  - セクション分けの明確化

#### 3.1.2 文章品質
- **校正対象**:
  - 誤字脱字の完全チェック
  - 敬語・ビジネス文書としての適切性
  - 文章長さと構造の最適化
  - 技術用語の統一性と正確性
- **品質基準**: 企業提出可能レベルの文章品質

### 3.2 技術要件

#### 3.2.1 開発環境
- **言語**: Python 3.9+
- **主要ライブラリ**:
  - PyYAML: YAML処理
  - Markdown: Markdown生成
  - WeasyPrint/Puppeteer: PDF生成
  - pre-commit: Git hooks管理
- **エディタ**: VS Code + 拡張機能（YAML, Markdown, 校正ツール）

#### 3.2.2 実行環境
- **ローカル**: Windows 10/11 対応
- **CI/CD**: GitHub Actions
- **公開**: GitHub Pages
- **依存関係**: requirements.txt管理

### 3.3 運用要件

#### 3.3.1 保守性
- **モジュール設計**: 機能別モジュール分割
- **設定管理**: 外部設定ファイルでのカスタマイズ対応
- **ログ出力**: デバッグ・運用時のログ管理
- **エラーハンドリング**: 適切な例外処理と回復処理

#### 3.3.2 拡張性
- **テンプレート**: 新フォーマット追加の容易さ
- **出力形式**: 新出力形式追加の柔軟性
- **データ構造**: データスキーマの拡張対応

---

## 4. システムアーキテクチャ

### 4.1 全体構成
```
[YAML Data] → [Python Processing] → [Markdown] → [Multi Output]
     ↓              ↓                   ↓           ↓
profile.yml → conversion_engine.py → resume.md → [HTML, PDF]
     ↓              ↓                   ↓           ↓
[Validation] → [Quality Check] → [GitHub Pages] → [Public Access]
```

### 4.2 ディレクトリ構造
```
personal/
├── data/
│   ├── profile.yml              # メインプロファイル
│   ├── schema.yml              # データスキーマ定義
│   └── validation_rules.yml    # バリデーションルール
├── templates/
│   ├── resume_template.md      # Markdownテンプレート
│   ├── styles/
│   │   ├── pdf_style.css      # PDF用スタイル
│   │   └── web_style.css      # Web用スタイル
│   └── layouts/
│       └── base.html          # HTMLベーステンプレート
├── src/
│   ├── core/
│   │   ├── converter.py       # YAML→Markdown変換
│   │   ├── generator.py       # 各種出力生成
│   │   └── validator.py       # データ・品質検証
│   ├── utils/
│   │   ├── yaml_handler.py    # YAML処理ユーティリティ
│   │   ├── text_processor.py  # 文章校正処理
│   │   └── pdf_generator.py   # PDF生成処理
│   └── config/
│       ├── settings.py        # 設定管理
│       └── logging_config.py  # ログ設定
├── output/
│   ├── resume.md              # 生成されたMarkdown
│   ├── resume.html            # 生成されたHTML
│   ├── resume.pdf             # 生成されたPDF
│   └── validation_report.md   # 品質検証レポート
├── docs/                      # GitHub Pages用
│   ├── index.html             # ポートフォリオサイト
│   ├── resume/                # 職務経歴書専用ページ
│   └── assets/                # 静的リソース
├── .github/
│   └── workflows/
│       ├── ci.yml             # 継続的インテグレーション
│       └── deploy.yml         # GitHub Pagesデプロイ
├── tests/                     # テストコード
├── requirements.txt           # Python依存関係
├── pyproject.toml            # プロジェクト設定
└── README.md                 # プロジェクト説明
```

### 4.3 技術スタック選択理由

#### 4.3.1 データ管理：YAML継続
- **理由**: 手動編集の容易さ、既存データ資産活用
- **対策**: VS Code環境整備による編集体験向上
- **拡張**: スキーマ定義による構造管理

#### 4.3.2 中間フォーマット：Markdown採用
- **理由**: エコシステム豊富、GitHub標準、将来性
- **メリット**: 多様な出力形式対応、ツールチェーン豊富
- **移行**: AsciiDoc→Markdownの段階的移行

#### 4.3.3 PDF生成：WeasyPrint/Puppeteer
- **WeasyPrint**: Python生態系統合、CSS完全対応
- **Puppeteer**: 高品質レンダリング、Chromiumベース
- **選択基準**: 出力品質とメンテナンス性のバランス

---

## 5. データ移行仕様

### 5.1 既存データ分析
- **現在のprofile.yml**: 334行、詳細な経歴データ
- **データ構造**: 基本情報、学歴、職歴（3社）、各プロジェクト詳細
- **移行要件**: 100%の情報保持、データ整合性保証

### 5.2 移行戦略

#### 5.2.1 データ構造改善
```yaml
# 現行構造の改善例
profile:
  meta:
    version: "2.0"
    last_updated: "2025-10-04"
    generated_by: "resume-system-v2"

  personal:
    name: "日下武紀"
    # 既存データをそのまま移行

  career:
    companies:
      - company_id: "omron_software"
        name: "オムロンソフトウェア株式会社"
        projects:
          - project_id: "ai_poc_2023"
            title: "生成AIを用いたPoC用のWebアプリ、クラウドインフラの構築"
            description: |
              プロジェクトの全体計画立案、市場調査と戦略立案...
              （複数行での詳細記載）
```

#### 5.2.2 段階的移行
1. **Phase 1**: 既存データの新形式への完全変換
2. **Phase 2**: データバリデーション・品質チェック
3. **Phase 3**: 出力テスト・品質確認
4. **Phase 4**: 本格運用開始

---

## 6. CI/CD仕様

### 6.1 GitHub Actions ワークフロー

#### 6.1.1 品質チェック（Pull Request時）
```yaml
name: Quality Check
on:
  pull_request:
    paths: ['data/**', 'src/**']

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: YAML Schema Validation
      - name: Data Integrity Check
      - name: Text Quality Analysis
      - name: Generate Preview
```

#### 6.1.2 デプロイメント（main branch時）
```yaml
name: Build and Deploy
on:
  push:
    branches: [main]
    paths: ['data/**']

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Generate All Formats
      - name: Quality Validation
      - name: Deploy to GitHub Pages
      - name: Create Release
```

### 6.2 文章校正詳細仕様

#### 6.2.1 校正項目
1. **誤字脱字チェック**
   - 日本語スペルチェック
   - カタカナ表記統一
   - 数字・記号の適切性

2. **敬語・ビジネス文書適切性**
   - 敬語レベルの一貫性
   - ビジネス文書としての適切な表現
   - 冗長表現の検出・改善提案

3. **文章構造最適化**
   - 文長の適切性（読みやすさ）
   - 段落構成の論理性
   - 箇条書きの効果的活用

4. **技術用語統一性**
   - IT技術用語の表記統一
   - 略語の一貫使用
   - 専門用語の正確性

#### 6.2.2 校正ツール
- **primary**: textlint（日本語対応）
- **secondary**: AI校正（OpenAI/Claude API）
- **output**: 校正結果レポートの自動生成

---

## 7. GitHub Pages統合仕様

### 7.1 個人ポートフォリオサイト構成

#### 7.1.1 サイト構造
```
https://[username].github.io/personal/
├── /                          # トップページ（個人紹介）
├── /resume/                   # 職務経歴書ページ
│   ├── index.html            # Web版職務経歴書
│   ├── resume.pdf            # PDF直接ダウンロード
│   └── assets/               # スタイルシート等
├── /projects/                # プロジェクト詳細（将来拡張）
└── /contact/                 # 連絡先情報
```

#### 7.1.2 職務経歴書ページ仕様
- **レスポンシブデザイン**: PC・タブレット・モバイル対応
- **SEO最適化**: 検索エンジン対応メタデータ
- **アクセシビリティ**: WCAG 2.1 レベルAA準拠
- **パフォーマンス**: Core Web Vitals最適化

### 7.2 公開範囲・プライバシー
- **公開レベル**: フルオープン（検索エンジン登録対応）
- **個人情報保護**: 住所詳細・電話番号等の適切なマスキング
- **更新頻度**: データ更新時の自動反映

---

## 8. 実装ロードマップ

### 8.1 Phase 1: 基盤構築（優先度: 高）
**期間**: 1-2週間
- [x] 現状分析・要件定義
- [ ] 新ディレクトリ構造作成
- [ ] Python環境セットアップ（requirements.txt）
- [ ] 基本データ移行スクリプト作成
- [ ] YAML→Markdown変換エンジン実装

### 8.2 Phase 2: コア機能実装（優先度: 高）
**期間**: 2-3週間
- [ ] Markdown→HTML変換
- [ ] 高品質PDF生成機能
- [ ] データバリデーション機能
- [ ] 基本的な文章校正機能
- [ ] 出力品質の検証・調整

### 8.3 Phase 3: 自動化・CI/CD（優先度: 中）
**期間**: 1-2週間
- [ ] GitHub Actions設定
- [ ] 品質チェックワークフロー
- [ ] 自動デプロイメント設定
- [ ] エラーハンドリング改善

### 8.4 Phase 4: 公開・統合（優先度: 中）
**期間**: 1-2週間
- [ ] GitHub Pages設定
- [ ] ポートフォリオサイト基本構造
- [ ] レスポンシブデザイン実装
- [ ] SEO・アクセシビリティ対応

### 8.5 Phase 5: 品質向上・最適化（優先度: 低）
**期間**: 継続的改善
- [ ] AI校正機能強化
- [ ] PDF出力品質のファインチューニング
- [ ] パフォーマンス最適化
- [ ] ユーザビリティ改善

---

## 9. 成功基準・受け入れ条件

### 9.1 機能要件の受け入れ基準
- [ ] 既存profile.ymlのデータが100%移行されている
- [ ] 生成されたPDFが企業提出レベル（参考画像品質）に達している
- [ ] 4項目の文章校正が全て機能している
- [ ] GitHub Pagesで職務経歴書が公開されている
- [ ] ローカル環境でのワンコマンド生成が可能

### 9.2 品質要件の受け入れ基準
- [ ] PDF品質：A4印刷でプロフェッショナルな見た目
- [ ] 文章品質：誤字脱字・敬語・構造・技術用語が全て適切
- [ ] システム品質：エラー処理・ログ出力が適切
- [ ] 保守性：コードがモジュール化され、拡張が容易

### 9.3 運用要件の受け入れ基準
- [ ] データ更新→公開までが30分以内に完了
- [ ] CI/CDが正常に動作し、品質チェックが機能
- [ ] 外部依存関係が明確に管理されている
- [ ] プロジェクト文書が整備されている

---

## 10. リスク管理

### 10.1 技術リスク
- **PDF生成品質**: 複数ライブラリでの品質比較・検証
- **文章校正精度**: 人間による最終チェックとの併用
- **GitHub Pages制限**: 静的サイト制限への適切な対応

### 10.2 運用リスク
- **データ紛失**: Git管理＋定期バックアップ
- **品質劣化**: 継続的な品質監視＋改善サイクル
- **依存関係問題**: 定期的な依存関係更新・互換性確認

### 10.3 緩和策
- **段階的実装**: フェーズ分けによるリスク分散
- **バックアップ戦略**: 既存システムの併行運用期間設定
- **品質保証**: 手動チェック工程の維持

---

## 11. 付録

### 11.1 技術調査結果
- **Markdown PDF生成**: WeasyPrint vs Puppeteer 比較
- **文章校正**: textlint vs AI校正ツール比較
- **CI/CD**: GitHub Actions vs 他サービス比較

### 11.2 参考資料
- 現状分析レポート: `project_analysis_report.md`
- 既存profile.yml: 334行のデータ構造
- 理想PDF品質: `image.png`参考サンプル

---

**本要件定義書承認後、Phase 1の実装を開始します。**