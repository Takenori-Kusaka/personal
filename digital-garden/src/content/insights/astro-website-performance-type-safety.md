---
title: 'AstroでWebサイト構築：パフォーマンスと型安全性の発見'
description: 'AstroのゼロJSデフォルト設計とContent Collections機能を活用し、高速で型安全なデジタルガーデンを構築した経験と学び'
pubDate: 2025-10-04
tags: ["Astro", "TypeScript", "Performance", "Content Collections", "Tailwind CSS"]
category: 'insights'
draft: false
---
## パフォーマンスの発見

- AstroのゼロJSデフォルトアーキテクチャにより、Lighthouseスコア98点を達成
- 必要な部分のみにJavaScriptを適用可能
- Tailwind CSS v4のViteプラグインで、ビルド時間が50%短縮

## Content Collectionsの威力

### 型安全なコンテンツ管理
TypeScriptによるフロントマターの厳密な管理が可能：

```typescript
const contentSchema = z.object({
  title: z.string(),
  description: z.string(),
  pubDate: z.coerce.date(),
  tags: z.array(z.string()),
  category: z.enum(['insights', 'ideas', 'weekly-reviews']),
});
```

### 主なメリット
- ビルド時のエラー検出
- タイポや型の不一致を事前に防止
- コンテンツ構造の保証

## 実装上の学び

- 動的ルーティングは`getStaticPaths()`を使用
- Content Collectionsとの組み合わせでシンプルな実装が可能

## 今後の展望

- Pagefindによる検索機能の実装
- PWA対応の検討

## まとめ

Astroは静的サイトジェネレーターとして優れており、特にコンテンツ中心のサイトに最適。

## 参考リンク

- [Astro公式ドキュメント](https://docs.astro.build/)
- [Content Collections Guide](https://docs.astro.build/en/guides/content-collections/)
