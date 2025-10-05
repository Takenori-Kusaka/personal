# ユーザー様へのTODOリスト

このファイルが更新されたら、以下のコンテンツのご準備をお願いします。

## 🖼️ 必要な画像・メディアファイル

### プロフィール関連
- [x] `input/profile-photo.png` - プロフィール写真（推奨サイズ: 400x400px以上）背景透過→読み込むときに正方形補正してください
- [x] `input/hero-background.png` - ヒーローセクションの背景画像（1920x1080px）**✨ Google Imagen 4で生成完了**

### OGP（SNSシェア用）
- [x] `input/og-image.png` - SNSシェア時に表示される画像（1200x630px）**✨ Google Imagen 4で生成完了**

### アイコン・ファビコン
- [x] `input/favicon.png` - ブラウザタブに表示されるアイコン（512x512px）**✨ Google Imagen 4で生成完了**

## 📝 テストコンテンツの準備（オプション）

自動化システムのテスト用に、以下のいずれかをご用意いただけるとすぐにテストできます：

### 音声ファイル（Whisper文字起こしテスト用）
- [ ] `input/audio/sample-voice-memo.mp3` - 音声メモのサンプル
- [ ] `input/audio/sample-presentation.m4a` - プレゼンテーション録音のサンプル

日下回答：すぐに手に入らないので保留します

### 動画ファイル（Whisper文字起こしテスト用）
- [ ] `input/video/sample-tutorial.mp4` - チュートリアル動画のサンプル

日下回答：すぐに手に入らないので保留します

### テキストファイル（Claude分類テスト用）
- [x] `input/text/sample-insight.txt` - 洞察・気づきのサンプルテキスト
- [x] `input/text/sample-idea.txt` - アイデア・構想のサンプルテキスト
- [x] `input/text/sample-diary.txt` - 日記のサンプルテキスト

## 📋 その他の情報

### SNS・外部リンク
現在の情報:
- GitHub: `https://github.com/Takenori-Kusaka`
- Resume: `/resume/`

以下を追加されたい場合は、お知らせください：
- [ ] Twitter/X アカウント
- [ ] LinkedIn プロフィール
- [ ] その他のSNS

#### Podcastのリンク

- [x] ホームページ: https://takenori-kusaka.github.io/
- [x] YouTube: https://www.youtube.com/channel/UCD1zo-WnyFdE5w0pqvKblkA
- [x] Listen: https://listen.style/p/recalog

### プロフィール情報の更新
`data/profile.yml` に以下の情報が含まれていますが、Digital Garden用に追加したい情報があればお知らせください：
- 自己紹介文の調整
- キャッチフレーズの追加
- 専門分野の強調ポイント

まずは大丈夫です。できあがった後にチェックして気になったらコメントしますね

---

## ⚙️ 現在の進捗状況

✅ 完了:
- テスト基盤の構築（84/84テスト成功）
- .env環境変数管理システム
- GitHub Pages デプロイ成功
- Perplexity API連携確認
- HTML構造の実装
- 画像生成（Google Imagen 4）
  - hero-background.png (1920x1080px)
  - og-image.png (1200x630px)
  - favicon.png (512x512px)

🔄 進行中:
- CSS/JavaScriptの実装
- 自動化パイプラインの実装

---

**更新日時**: 2025-10-04
**次回更新**: CSS実装完了後
