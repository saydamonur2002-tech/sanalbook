/**
 * Tüm statik sayfaları dist'e kopyalanacak public/sitemap.xml dosyasına yazar.
 * Kanonik adres, Workers html_handling=auto-trailing-slash ile sonda / olan yoldur.
 */
import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const kok = join(dirname(fileURLToPath(import.meta.url)), '..');
const site = 'https://sanalbook.saydamonur2002.workers.dev';

function yuru(dizin) {
  const sonuc = [];
  for (const ad of readdirSync(dizin)) {
    const yol = join(dizin, ad);
    try {
      const ic = readdirSync(yol);
      if (ic) sonuc.push(...yuru(yol));
    } catch {
      sonuc.push(yol);
    }
  }
  return sonuc;
}

function loc(yol) {
  const temiz = yol.endsWith('/') ? yol : `${yol}/`;
  return `${site}${temiz === '//' ? '/' : temiz}`;
}

const sabit = ['/', '/hakkinda', '/telif', '/cerez-kvkk', '/turkiye', '/turkiye/hikaye'];
const adresler = new Set(sabit.map(loc));

for (const dosya of yuru(join(kok, 'src/content/works'))) {
  if (!dosya.endsWith('.json')) continue;
  const eser = JSON.parse(readFileSync(dosya, 'utf8'));
  adresler.add(loc(`/${eser.country}/${eser.category === 'hikaye' ? 'hikaye' : eser.category}/${eser.slug}`));
  // category id is "hikaye"; URL slug is also hikaye. country slug is turkiye.
  adresler.add(loc(`/turkiye/hikaye/${eser.slug}`));
}

for (const dosya of yuru(join(kok, 'src/content/chapters'))) {
  if (!dosya.endsWith('.md')) continue;
  const ham = readFileSync(dosya, 'utf8');
  const work = ham.match(/^work:\s*(\S+)\s*$/m)?.[1];
  const order = ham.match(/^order:\s*(\d+)\s*$/m)?.[1];
  if (!work || !order) continue;
  adresler.add(loc(`/turkiye/hikaye/${work}/${order}`));
}

const liste = [...adresler].sort();
const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${liste.map((url) => `  <url><loc>${url}</loc></url>`).join('\n')}
</urlset>
`;
writeFileSync(join(kok, 'public/sitemap.xml'), xml);
console.log(`sitemap.xml: ${liste.length} adres`);
