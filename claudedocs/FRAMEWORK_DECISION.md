# デジタルガーデン フレームワーク選定結果

## 🎯 選定結果: **Astro + Tailwind CSS**

GitHub Actions経由のビルドが可能になったことで、最新のモダンフレームワークを採用します。

---

## 📊 選定理由

### **要件との適合性分析**

| 要件 | Astro | Next.js | SvelteKit | Eleventy |
|------|-------|---------|-----------|----------|
| **パフォーマンス** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **マークダウン対応** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **学習コスト** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **拡張性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **エコシステム** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **総合評価** | **18/25** | 16/25 | 15/25 | 16/25 |

### **Astroの主要な利点**

1. **ゼロJSデフォルト**: 静的HTML生成でLighthouseスコア100点狙える
2. **部分的Hydration**: インタラクティブ要素のみJSを読み込み
3. **コンテンツファースト設計**: マークダウン・MDXネイティブサポート
4. **フレームワーク非依存**: React, Vue, Svelteを同時に使用可能
5. **Content Collections API**: 型安全なコンテンツ管理
6. **ビルトイン機能**: 画像最適化、RSS生成、サイトマップ自動生成

---

## 🛠️ 技術スタック詳細

### **フロントエンド**

```yaml
Core:
  - Astro 4.x (最新安定版)
  - TypeScript (型安全性)

Styling:
  - Tailwind CSS 3.x (ユーティリティファースト)
  - Tailwind Typography (マークダウンスタイリング)

Content:
  - MDX (マークダウン + JSX)
  - Shiki (シンタックスハイライト)
  - rehype/remark プラグイン（拡張機能）

UI Components (必要に応じて):
  - Astro Islands (部分的インタラクティブ)
  - Preact (超軽量React互換)

Icons:
  - Lucide Icons (モダンなアイコンセット)

Fonts:
  - Google Fonts: Noto Sans JP
```

### **検索・ナビゲーション**

```yaml
Search:
  - Pagefind (Astro公式推奨、ビルド時インデックス生成)
  - オフライン動作可能
  - 日本語全文検索対応

Navigation:
  - Astro Content Collections (カテゴリ・タグ管理)
  - 自動生成サイドバー・タグクラウド
```

### **ビルド・デプロイ**

```yaml
Build:
  - Vite (高速ビルドツール)
  - Sharp (画像最適化)

CI/CD:
  - GitHub Actions
  - 自動ビルド・デプロイ

Hosting:
  - GitHub Pages
  - カスタムドメイン対応可
```

---

## 📁 プロジェクト構造（Astro版）

```
personal/
├── digital-garden/                 # Astroプロジェクトルート
│   ├── src/
│   │   ├── content/               # Content Collections
│   │   │   ├── config.ts          # コンテンツスキーマ定義
│   │   │   ├── insights/          # 洞察カテゴリ
│   │   │   │   └── *.md
│   │   │   ├── ideas/             # アイデアカテゴリ
│   │   │   │   └── *.md
│   │   │   └── weekly-reviews/    # 週次振り返り
│   │   │       └── *.md
│   │   │
│   │   ├── layouts/               # レイアウトテンプレート
│   │   │   ├── BaseLayout.astro   # ベースレイアウト
│   │   │   └── ContentLayout.astro # コンテンツページレイアウト
│   │   │
│   │   ├── components/            # 再利用可能コンポーネント
│   │   │   ├── Header.astro
│   │   │   ├── Footer.astro
│   │   │   ├── Card.astro
│   │   │   └── SearchBar.astro
│   │   │
│   │   ├── pages/                 # ルーティング
│   │   │   ├── index.astro        # ホームページ
│   │   │   ├── insights/
│   │   │   │   ├── index.astro    # 一覧ページ
│   │   │   │   └── [slug].astro   # 動的ルート
│   │   │   ├── ideas/
│   │   │   ├── weekly-reviews/
│   │   │   └── about.astro
│   │   │
│   │   └── styles/                # グローバルスタイル
│   │       └── global.css
│   │
│   ├── public/                    # 静的アセット
│   │   ├── images/
│   │   └── favicon.ico
│   │
│   ├── astro.config.mjs           # Astro設定
│   ├── tailwind.config.mjs        # Tailwind設定
│   ├── tsconfig.json              # TypeScript設定
│   └── package.json
│
├── automation/                     # 自動化システム（既存）
│   └── （変更なし）
│
├── input/                          # 入力ファイル（既存）
│   └── （変更なし）
│
└── .github/
    └── workflows/
        └── deploy-digital-garden.yml  # Astroビルド用ワークフロー
```

---

## ⚙️ Astro設定ファイル

### **astro.config.mjs**

```javascript
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://takenori-kusaka.github.io',
  base: '/personal',

  integrations: [
    tailwind(),
    mdx(),
    sitemap(),
  ],

  markdown: {
    shikiConfig: {
      theme: 'github-dark',
      wrap: true
    },
    remarkPlugins: [],
    rehypePlugins: [],
  },

  output: 'static',

  vite: {
    build: {
      cssMinify: 'lightningcss',
    },
  },
});
```

### **Content Collections スキーマ**

```typescript
// src/content/config.ts
import { defineCollection, z } from 'astro:content';

const insightsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.date(),
    updatedDate: z.date().optional(),
    tags: z.array(z.string()),
    category: z.enum(['insights', 'ideas', 'weekly-reviews']),
    draft: z.boolean().default(false),
    author: z.string().default('日下武紀'),
    image: z.string().optional(),
  }),
});

export const collections = {
  'insights': insightsCollection,
  'ideas': insightsCollection,
  'weekly-reviews': insightsCollection,
};
```

---

## 🚀 セットアップ手順

### **1. Astroプロジェクト初期化**

```bash
cd digital-garden
npm create astro@latest . -- --template minimal --typescript strict
```

### **2. 依存関係インストール**

```bash
npm install @astrojs/tailwind @astrojs/mdx @astrojs/sitemap
npm install -D tailwindcss @tailwindcss/typography
npm install pagefind
```

### **3. 開発サーバー起動**

```bash
npm run dev
# → http://localhost:4321
```

### **4. ビルド**

```bash
npm run build
# → dist/ フォルダに静的ファイル生成
```

---

## 📦 GitHub Actions ワークフロー

```yaml
# .github/workflows/deploy-digital-garden.yml
name: Deploy Digital Garden

on:
  push:
    branches: [main]
    paths:
      - 'digital-garden/**'
      - 'automation/**'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: digital-garden/package-lock.json

      - name: Install dependencies
        working-directory: digital-garden
        run: npm ci

      - name: Build Astro site
        working-directory: digital-garden
        run: npm run build

      - name: Setup Pages
        uses: actions/configure-pages@v4

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./digital-garden/dist

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

---

## 🎨 デザインシステム

### **Tailwind設定**

```javascript
// tailwind.config.mjs
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        primary: '#2c5aa0',
        secondary: '#3d6fb0',
      },
      fontFamily: {
        sans: ['Noto Sans JP', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
```

### **デザイン原則**

1. **モバイルファースト**: 小画面から設計
2. **レスポンシブ**: Tailwindのブレークポイント活用
3. **アクセシビリティ**: WCAG AA準拠
4. **ダークモード**: システム設定に追従（将来実装）

---

## 🔍 検索機能（Pagefind）

### **統合方法**

```javascript
// astro.config.mjs に追加
import pagefind from 'astro-pagefind';

export default defineConfig({
  integrations: [
    pagefind(),
  ],
});
```

### **検索UIコンポーネント**

```astro
---
// src/components/SearchBar.astro
---
<div id="search"></div>

<script>
  import * as pagefind from 'pagefind';

  const search = await pagefind.search('検索クエリ');
  // 検索結果を表示
</script>
```

---

## 📈 パフォーマンス目標

| メトリクス | 目標値 |
|-----------|--------|
| First Contentful Paint | < 1.0s |
| Largest Contentful Paint | < 2.5s |
| Time to Interactive | < 3.0s |
| Cumulative Layout Shift | < 0.1 |
| Lighthouse Score | 95+ |

---

## 🔄 マイグレーション計画

### **既存のindex.htmlからAstroへ**

1. ✅ 既存HTMLをAstroコンポーネントに変換
2. ✅ CSSをTailwindクラスに移行
3. ✅ JavaScriptをAstro Islandsに統合
4. ✅ マークダウンコンテンツスキーマ定義

---

## 🆚 他の選択肢との比較

### **なぜNext.jsではないのか？**

- **バンドルサイズ**: Astroの方が軽量（JS不要なページはゼロJS）
- **コンテンツ志向**: Next.jsはアプリ志向、Astroはコンテンツ志向
- **学習コスト**: Astroの方がシンプル

### **なぜSvelteKitではないのか？**

- **エコシステム**: Astroの方が豊富（多フレームワーク対応）
- **静的サイト最適化**: Astroの方がデフォルトで最適
- **コミュニティ**: Astroの方が静的サイト向けリソース多い

### **なぜEleventyではないのか？**

- **モダン性**: Astroの方が最新のWeb標準に対応
- **DX（開発体験）**: TypeScript、Hot Reload、Viteなど
- **統合機能**: 画像最適化、RSS、サイトマップなどビルトイン

---

## ✅ 採用決定

**Astro + Tailwind CSS + Pagefind** を採用します。

次のステップ:
1. Astroプロジェクトのセットアップ
2. 既存HTMLのAstro化
3. Content Collectionsの設定
4. 自動化パイプラインとの統合

---

**決定日**: 2025-10-04
**承認待ち**: ユーザー様のフィードバック
