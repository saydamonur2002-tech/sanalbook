import { defineConfig } from 'astro/config';

// Tamamen statik çıktı. Wrangler bu `dist` klasörünü Workers Static Assets olarak sunar.
export default defineConfig({
  output: 'static',
  build: {
    format: 'directory',
  },
  compressHTML: true,
});
