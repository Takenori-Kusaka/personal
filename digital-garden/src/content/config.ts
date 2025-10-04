import { defineCollection, z } from 'astro:content';

// コンテンツスキーマ定義
const contentSchema = z.object({
  title: z.string(),
  description: z.string(),
  pubDate: z.coerce.date(),
  updatedDate: z.coerce.date().optional(),
  tags: z.array(z.string()),
  category: z.enum(['insights', 'ideas', 'weekly-reviews']),
  draft: z.boolean().default(false),
  author: z.string().default('日下武紀'),
  image: z.string().optional(),
  thumbnail: z.string().optional(), // Imagen 4生成サムネイル
  // 自動化システムで追加されるフィールド
  transcriptionSource: z.string().optional(), // 元の音声/動画ファイル
  researchCitations: z.array(z.object({
    title: z.string(),
    url: z.string(),
    snippet: z.string()
  })).optional(), // Perplexity APIの引用情報
});

// Content Collections定義
const insightsCollection = defineCollection({
  type: 'content',
  schema: contentSchema,
});

const ideasCollection = defineCollection({
  type: 'content',
  schema: contentSchema,
});

const weeklyReviewsCollection = defineCollection({
  type: 'content',
  schema: contentSchema,
});

export const collections = {
  'insights': insightsCollection,
  'ideas': ideasCollection,
  'weekly-reviews': weeklyReviewsCollection,
};
