import { defineConfig } from 'astro/config';

// Tamamen statik çıktı. Cloudflare Pages `dist` klasörünü olduğu gibi sunar.
export default defineConfig({
  output: 'static',
  build: {
    format: 'directory',
  },
  compressHTML: true,
});
