import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import tailwind from '@astrojs/tailwind';
import vercel from '@astrojs/vercel/static';
import { remarkReadingTime } from './src/utils/reading-time.mjs';

// https://astro.build/config
export default defineConfig({
  site: 'https://kusaka-digital-garden.vercel.app',
  output: 'static',
  adapter: vercel({
    webAnalytics: { enabled: true }
  }),
  integrations: [
    mdx({
      remarkPlugins: [remarkReadingTime],
      gfm: true,
    }),
    sitemap({
      filter: (page) => !page.includes('/api/'),
    }),
    tailwind({
      config: { applyBaseStyles: false }
    })
  ],
  markdown: {
    remarkPlugins: [remarkReadingTime],
    shikiConfig: {
      theme: 'github-dark-dimmed',
      langs: ['javascript', 'typescript', 'python', 'yaml', 'json', 'mermaid'],
      wrap: true,
    },
  },
  vite: {
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor': ['react', 'react-dom'],
            'mermaid': ['mermaid'],
            'utils': ['fuse.js', 'date-fns', 'clsx']
          }
        }
      }
    },
    optimizeDeps: {
      include: ['react', 'react-dom', 'date-fns', 'fuse.js', 'clsx']
    }
  },
  image: {
    domains: ['res.cloudinary.com'],
    formats: ['avif', 'webp', 'jpg'],
  },
  experimental: {
    contentCollectionCache: true,
  }
});