# sanalbook

Türkiye'de koruma süresi dolmuş edebî eserleri okumak için statik bir site. Arayüz Türkçedir. Üyelik ve reklam yoktur. Ziyaret sayıları çerezsiz Cloudflare Web Analytics ile toplu istatistik olarak tutulur.

Sıra: **ülke → kategori → eser → bölüm**.

İlk seçki Ömer Seyfettin'in beş hikâyesidir (Kaşağı, Forsa, Pembe İncili Kaftan, Diyet, Bomba). Metinler Vikikaynak'ın sabit sürümlerinden alınmıştır. Künye her eser sayfasındadır.

## Yerelde çalıştırma

Node.js 22 gerekir.

```bash
npm install
npm run dev
```

Derleme:

```bash
npm run build
```

Çıktı `dist` klasörüdür. Önizleme: `npm run preview`.

## İçerik koleksiyonları

Şema `src/content.config.ts` içindedir.

| Koleksiyon | Dosya | Ne işe yarar |
| --- | --- | --- |
| `countries` | `src/content/countries/*.json` | Ülke |
| `categories` | `src/content/categories/*.json` | Ülkeye bağlı kategori |
| `works` | `src/content/works/*.json` | Eser künyesi ve telif alanları |
| `chapters` | `src/content/chapters/<eser-kisa-adi>/*.md` | Bölüm metni |

Yeni bir özgün Türkçe hikâye için iki dosya yeter.

`src/content/works/ornek.json`:

```json
{
  "title": "Örnek",
  "slug": "ornek",
  "author": "Yazar Adı",
  "authorDeathYear": 1900,
  "translator": null,
  "translatorDeathYear": null,
  "country": "turkiye",
  "category": "hikaye",
  "order": 10,
  "sourceName": "Vikikaynak",
  "sourceUrl": "https://tr.wikisource.org/wiki/Ornek?oldid=1",
  "sourceRevision": 1,
  "sourceRetrieved": "2026-01-01",
  "originalPublication": null
}
```

`src/content/chapters/ornek/01.md`:

```markdown
---
title: Örnek
work: ornek
order: 1
---

<p class="duz">Bölüm metni.</p>
```

Çeviride `translator` çevirmenin adıdır ve `translatorDeathYear` dolu olmalıdır. Özgün metinde ikisi de `null` kalır; sitede «yok» görünür. `country` ve `category` ilgili kaydın dosya adıdır (uzantısız). Bölümdeki `work`, eser kaydının dosya adıdır.

Kısa adlar küçük harf, rakam ve kısa çizgidir. `hakkinda`, `telif` ve `cerez-kvkk` ülke kısa adı olamaz; bu yollar sabit sayfalardadır.

## Telif kuralı

Bir eser Türkiye'de ancak şu şartla yayımlanır: hem yazarın hem, varsa, çevirmenin veya aktaranın ölüm yılının sonundan itibaren 70 yıl geçmiştir.

Süre, ölüm yılını izleyen 1 Ocak'ta başlar ve 70 yıl sonra biter. Serbestlik, bir sonraki 1 Ocak'tır. 1920'de ölen bir yazar için bu tarih 1 Ocak 1991'dir. İki kişi varsa geç olan tarih esas alınır.

Hesap `src/lib/telif.ts` içindedir. Şema her eser kaydını derleme yılında bu işleve sorar. Süre dolmamışsa `npm run build` durur ve `dist` oluşmaz. Aynı denetim `scripts/check-telif.mjs` ile derlemenin başında da çalışır.

## Cloudflare Workers

Site statiktir. `@astrojs/cloudflare` uyarlaması ve Worker betiği yoktur. `wrangler.jsonc` derlenmiş `dist` klasörünü [Workers Static Assets](https://developers.cloudflare.com/workers/static-assets/) olarak sunar. Worker adı `sanalbook` olmalıdır; paneldeki proje bu addadır.

| Alan | Değer |
| --- | --- |
| `name` | `sanalbook` |
| `compatibility_date` | `2026-10-29` |
| `assets.directory` | `./dist` |
| `assets.html_handling` | `auto-trailing-slash` |
| `assets.not_found_handling` | `404-page` |

`html_handling`, Astro'nun klasör çıktısına uyar: `/turkiye` adresi `/turkiye/` adresine yönlenir ve `dist/turkiye/index.html` sunulur. `404-page`, eşleşmeyen istekte `src/pages/404.astro` çıktısı olan `dist/404.html` dosyasını 404 durumuyla döner.

Workers Builds iki adım çalıştırır. Ayarlar Worker içinde **Settings → Build** altındadır.

| Ayar | Değer |
| --- | --- |
| Production branch | `main` |
| Build command | `npm run build` |
| Deploy command | `npx wrangler deploy` |
| Root directory | `/` |

`NODE_VERSION` ortam değişkenini `22` yapın. Telif denetimi bu Node sürümünü kullanır. Deploy komutu, `package.json` içindeki Wrangler sürümünü çalıştırır.

Her `main` itmesi siteyi yeniden derler ve https://sanalbook.saydamonur2002.workers.dev/ adresine yayınlar. Yerelde denemek için `npm run build`, ardından `npx wrangler dev`.

Ayrıntı: [Astro on Workers](https://developers.cloudflare.com/workers/framework-guides/web-apps/astro/) ve [SSG yönlendirme](https://developers.cloudflare.com/workers/static-assets/routing/static-site-generation/).
