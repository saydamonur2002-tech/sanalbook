/**
 * Telif hesabının yerel denetimi. `npm run build` bunu çalıştırmaz;
 * içerik şemasındaki denetim derlemeyi durdurur. Bu dosya hesabı kilitler.
 */
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { telifDenetle, serbestlikYili } from '../src/lib/telif.ts';

const kok = join(dirname(fileURLToPath(import.meta.url)), '..');

assert.equal(serbestlikYili(1920), 1991);
assert.equal(serbestlikYili(1955), 2026);
assert.equal(serbestlikYili(1956), 2027);

const ornek = {
  title: 'Kaşağı',
  author: 'Ömer Seyfettin',
  authorDeathYear: 1920,
  translator: null,
  translatorDeathYear: null,
};

assert.equal(telifDenetle(ornek, 2026).serbest, true);
assert.equal(telifDenetle(ornek, 1991).serbest, true);
assert.equal(telifDenetle(ornek, 1990).serbest, false);

const gecCevirmen = {
  ...ornek,
  translator: 'Örnek Çevirmen',
  translatorDeathYear: 1960,
};
assert.equal(telifDenetle(gecCevirmen, 2026).serbest, false);
assert.equal(telifDenetle({ ...gecCevirmen, translatorDeathYear: 1940 }, 2026).serbest, true);
assert.equal(telifDenetle({ ...gecCevirmen, translatorDeathYear: 1940 }, 2010).serbest, false);

assert.equal(
  telifDenetle({ ...ornek, translator: 'Biri', translatorDeathYear: null }, 2026).serbest,
  false,
);
assert.equal(
  telifDenetle({ ...ornek, translatorDeathYear: 1920 }, 2026).serbest,
  false,
);
assert.equal(telifDenetle({ ...ornek, authorDeathYear: 2027 }, 2026).serbest, false);

const belirtilmemis = telifDenetle(
  { ...ornek, translator: 'belirtilmemiş', translatorDeathYear: null },
  2026,
);
assert.equal(belirtilmemis.serbest, true);
assert.equal(belirtilmemis.gerekce, telifDenetle(ornek, 2026).gerekce);
assert.equal(
  telifDenetle({ ...ornek, translator: 'belirtilmemiş', translatorDeathYear: 1920 }, 2026).serbest,
  false,
);

function yuru(dizin) {
  const sonuc = [];
  for (const ad of readdirSync(dizin)) {
    const yol = join(dizin, ad);
    if (statSync(yol).isDirectory()) sonuc.push(...yuru(yol));
    else if (ad.endsWith('.json')) sonuc.push(yol);
  }
  return sonuc;
}

const eserler = yuru(join(kok, 'src/content/works'));
if (eserler.length === 0) {
  console.error('Hiç eser kaydı yok.');
  process.exit(1);
}

for (const yol of eserler) {
  const eser = JSON.parse(readFileSync(yol, 'utf8'));
  const sonuc = telifDenetle(eser, new Date().getFullYear());
  if (!sonuc.serbest) {
    console.error(sonuc.hatalar.join('\n'));
    process.exit(1);
  }
  const bolumler = join(kok, 'src/content/chapters', eser.slug);
  const dosyalar = readdirSync(bolumler).filter((ad) => ad.endsWith('.md'));
  if (dosyalar.length === 0) {
    console.error(`${eser.slug}: bölüm dosyası yok.`);
    process.exit(1);
  }
}

console.log(`Telif denetimi geçti (${eserler.length} eser).`);
