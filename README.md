# sanalbook

Türkiye'de koruma süresi dolmuş edebî eserleri okumak için statik bir site. Arayüz Türkçedir. Üyelik, reklam ve analitik yoktur.

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

## Cloudflare Pages

Site statiktir. Sunucu uyarlaması (`@astrojs/cloudflare`) gerekmez. Pages, `dist` klasörünü olduğu gibi sunar.

Cloudflare panelinde **Workers & Pages → Create application → Pages → Import an existing Git repository**. Depoyu seçip **Begin setup**. **Set up builds and deployments** bölümü:

| Ayar | Değer |
| --- | --- |
| Production branch | `main` |
| Framework preset | Astro (yoksa None) |
| Build command | `npm run build` |
| Build directory | `dist` |
| Root directory | `/` (depo kökü) |

Ortam değişkeni:

| Değişken | Değer |
| --- | --- |
| `NODE_VERSION` | `22` |

Kayıttan sonra **Save and Deploy**. Her itmede üretim dalı yeniden derlenir. Çekme istekleri önizleme adresi alır.

Yerelde üretilmiş `dist` için **Direct Upload** da aynı klasörü kullanır. İşlev (Pages Functions), KV veya D1 gerekmez.

Ayrıntı: [Cloudflare Pages üzerinde Astro](https://developers.cloudflare.com/pages/framework-guides/deploy-an-astro-site/).
