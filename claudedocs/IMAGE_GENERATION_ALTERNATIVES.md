# Digital Garden画像生成の代替案

## 課題
Google AI Studio APIでは画像生成機能（Imagen 4）が課金ユーザーのみアクセス可能で、無料枠では利用できませんでした。

## 必要な画像
1. **hero-background.png** (1920x1080px) - ヒーローセクション背景
2. **og-image.png** (1200x630px) - SNSシェア用OGP画像
3. **favicon.png** (512x512px) - ファビコン・アプリアイコン

## 代替案

### 方法1: 無料画像生成AIサービス

#### Ideogram (推奨)
- **URL**: https://ideogram.ai/
- **無料枠**: 毎日25枚生成可能
- **特徴**: 高品質、テキスト表示が得意、商用利用OK
- **手順**:
  1. アカウント登録（無料）
  2. プロンプトを入力して生成
  3. ダウンロードして`input/`に配置

#### Leonardo.ai
- **URL**: https://leonardo.ai/
- **無料枠**: 毎日150トークン（約30枚）
- **特徴**: リアルなビジュアル、多様なスタイル
- **手順**: Ideogramと同様

#### Playground AI
- **URL**: https://playgroundai.com/
- **無料枠**: 毎日100枚生成可能
- **特徴**: 使いやすいUI、Stable Diffusion XL対応

### 方法2: Canvaでテンプレート作成

#### Canva (デザインツール)
- **URL**: https://www.canva.com/
- **無料枠**: 基本機能無料
- **手順**:
  1. アカウント登録
  2. カスタムサイズで新規作成
  3. テンプレート選択 + カスタマイズ
  4. PNG形式でダウンロード

**推奨テンプレート検索キーワード**:
- hero-background: "Technology Background", "Digital Abstract", "Network Pattern"
- og-image: "Social Media Banner", "Technology Brand"
- favicon: "App Icon", "Logo Design"

### 方法3: Unsplash + 画像編集

#### Unsplash (無料写真)
- **URL**: https://unsplash.com/
- **ライセンス**: 商用利用OK、クレジット不要
- **手順**:
  1. キーワードで検索（例: "technology blue", "network abstract", "digital garden"）
  2. 高解像度でダウンロード
  3. Photopea等で編集・リサイズ

#### Photopea (オンライン画像編集)
- **URL**: https://www.photopea.com/
- **無料**: 完全無料、Photoshop互換
- **用途**: リサイズ、テキスト追加、フィルター適用

## 画像生成プロンプト（各サービス共通）

### hero-background.png
```
A serene digital garden landscape with abstract geometric patterns
representing knowledge nodes and connections, soft gradient from
deep blue to teal, subtle circuit board patterns merged with
organic plant growth motifs, minimalist modern design, abstract
technology meets nature theme, clean professional aesthetic,
designed for text overlay, 16:9 aspect ratio
```

### og-image.png
```
Professional social media banner for Digital Garden technology
platform, abstract visualization of AI-powered knowledge ecosystem
with glowing blue neural networks connecting to blooming geometric
flowers, gradient background from deep blue to cyan, modern tech
aesthetic with organic growth metaphor, 1200x630px format
```

### favicon.png
```
Minimalist app icon design for Digital Garden platform, simple
geometric combination of a sprouting seedling and circuit board
node, centered in square frame, bold blue (#2563eb) and green
gradient, clean modern tech aesthetic, high contrast for small
sizes, flat design style, 512x512px square format
```

## 推奨ワークフロー

### 最速（15分）
1. Ideogram.aiでアカウント作成
2. 上記プロンプトを3回実行
3. ダウンロードして`input/`に保存
4. 必要に応じてリサイズ

### 高品質（1時間）
1. Unsplashで背景画像検索
2. Photopea/Canvaで編集
3. テキスト・ロゴ追加
4. 最適化してダウンロード

### カスタム（2-3時間）
1. Figmaで一から デザイン
2. ブランドガイドライン準拠
3. 複数バリエーション作成
4. エクスポート・最適化

## デザインガイドライン（再掲）

### カラーパレット
- **Primary Blue**: #2563eb
- **Text Gray**: #374151
- **Background Gray**: #f9fafb
- **White**: #ffffff

### ビジュアルメタファー
- **知識の成長**: 種→芽→植物→エコシステム
- **ネットワーク**: 接続されたノード、洞察
- **AI自動化**: 回路パターン、ニューラルネットワーク
- **技術スタック**: Whisper、Claude、Perplexityの抽象表現

### タイポグラフィ
- **フォント**: Noto Sans JP
- **スタイル**: クリーン、モダン、プロフェッショナル

## 次のステップ

### オプション1: 手動作成を依頼
ユーザー様に上記のサービスを使って手動で画像を作成していただく

### オプション2: プレースホルダー使用
開発を進めながら、後で画像を差し替える

### オプション3: 別のAI APIを使用
- OpenAI DALL-E 3 (有料)
- Stability AI (有料)
- Midjourney (有料、Discord経由)

---

**更新日時**: 2025-10-04
**ステータス**: Google Imagen APIアクセス不可のため代替案検討中
