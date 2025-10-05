// @ts-check
import { defineConfig } from 'astro/config';

import tailwind from '@astrojs/tailwind';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://takenori-kusaka.github.io',
  base: '/personal',

  integrations: [
    tailwind(),
    mdx(),
    sitemap()
  ],

  output: 'static',

  markdown: {
    shikiConfig: {
      theme: 'github-dark',
      wrap: true
    }
  }
});