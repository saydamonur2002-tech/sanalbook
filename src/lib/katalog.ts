import { getCollection, type CollectionEntry } from 'astro:content';
import { telifDenetle } from './telif';

const AYIRILMIS_KISA_ADLAR = new Set(['hakkinda', 'telif', 'cerez-kvkk']);

export function basvuruKimligi(deger: string | { id: string }): string {
  return typeof deger === 'string' ? deger : deger.id;
}

export function ulkeYolu(slug: string): string {
  return `/${slug}`;
}

export function kategoriYolu(ulke: string, kategori: string): string {
  return `/${ulke}/${kategori}`;
}

export function eserYolu(ulke: string, kategori: string, eser: string): string {
  return `/${ulke}/${kategori}/${eser}`;
}

export function bolumYolu(ulke: string, kategori: string, eser: string, sira: number): string {
  return `/${ulke}/${kategori}/${eser}/${sira}`;
}

export interface CozulmusBolum {
  id: string;
  entry: CollectionEntry<'chapters'>;
  title: string;
  order: number;
  href: string;
}

export interface CozulmusEser {
  id: string;
  entry: CollectionEntry<'works'>;
  data: CollectionEntry<'works'>['data'];
  ulke: CollectionEntry<'countries'>['data'] & { id: string };
  kategori: CollectionEntry<'categories'>['data'] & { id: string };
  bolumler: CozulmusBolum[];
  href: string;
  gerekce: string;
}

export async function katalogYukle() {
  const ulkeKayitlari = (await getCollection('countries')).sort((a, b) => a.data.order - b.data.order);
  const kategoriKayitlari = (await getCollection('categories')).sort(
    (a, b) => a.data.order - b.data.order,
  );
  const eserKayitlari = (await getCollection('works')).sort((a, b) => a.data.order - b.data.order);
  const bolumKayitlari = (await getCollection('chapters')).sort((a, b) => a.data.order - b.data.order);

  const ulkeHaritasi = new Map(ulkeKayitlari.map((ulke) => [ulke.id, ulke]));
  const kategoriHaritasi = new Map(kategoriKayitlari.map((kategori) => [kategori.id, kategori]));

  for (const ulke of ulkeKayitlari) {
    if (AYIRILMIS_KISA_ADLAR.has(ulke.data.slug)) {
      throw new Error(`Ülke kısa adı ayrılmış bir sayfayla çakışıyor: ${ulke.data.slug}`);
    }
  }

  const eserler: CozulmusEser[] = eserKayitlari.map((eser) => {
    const ulke = ulkeHaritasi.get(basvuruKimligi(eser.data.country));
    const kategori = kategoriHaritasi.get(basvuruKimligi(eser.data.category));
    if (!ulke || !kategori) {
      throw new Error(`${eser.id}: ülke veya kategori bulunamadı.`);
    }
    if (basvuruKimligi(kategori.data.country) !== ulke.id) {
      throw new Error(`${eser.id}: kategori ${kategori.id} bu eserin ülkesine bağlı değil.`);
    }

    const sonuc = telifDenetle({
      title: eser.data.title,
      author: eser.data.author,
      authorDeathYear: eser.data.authorDeathYear,
      translator: eser.data.translator,
      translatorDeathYear: eser.data.translatorDeathYear,
    });
    if (!sonuc.serbest) {
      throw new Error(sonuc.hatalar.join('\n'));
    }

    const kendiBolumleri = bolumKayitlari
      .filter((bolum) => basvuruKimligi(bolum.data.work) === eser.id)
      .sort((a, b) => a.data.order - b.data.order);
    if (kendiBolumleri.length === 0) {
      throw new Error(`${eser.data.title}: en az bir bölüm gerekli.`);
    }

    const siralar = new Set<number>();
    for (const bolum of kendiBolumleri) {
      if (siralar.has(bolum.data.order)) {
        throw new Error(`${eser.data.title}: ${bolum.data.order}. bölüm birden fazla.`);
      }
      siralar.add(bolum.data.order);
    }

    const href = eserYolu(ulke.data.slug, kategori.data.slug, eser.data.slug);
    return {
      id: eser.id,
      entry: eser,
      data: eser.data,
      ulke: { id: ulke.id, ...ulke.data },
      kategori: { id: kategori.id, ...kategori.data },
      href,
      gerekce: sonuc.gerekce,
      bolumler: kendiBolumleri.map((bolum) => ({
        id: bolum.id,
        entry: bolum,
        title: bolum.data.title,
        order: bolum.data.order,
        href: bolumYolu(ulke.data.slug, kategori.data.slug, eser.data.slug, bolum.data.order),
      })),
    };
  });

  const sahipsiz = bolumKayitlari.filter(
    (bolum) => !eserler.some((eser) => eser.id === basvuruKimligi(bolum.data.work)),
  );
  if (sahipsiz.length > 0) {
    throw new Error(`Eseri olmayan bölümler: ${sahipsiz.map((bolum) => bolum.id).join(', ')}`);
  }

  const yollar = new Set<string>();
  for (const eser of eserler) {
    if (yollar.has(eser.href)) throw new Error(`Yinelenen eser yolu: ${eser.href}`);
    yollar.add(eser.href);
    for (const bolum of eser.bolumler) {
      if (yollar.has(bolum.href)) throw new Error(`Yinelenen bölüm yolu: ${bolum.href}`);
      yollar.add(bolum.href);
    }
  }

  const kategoriler = kategoriKayitlari.map((kategori) => {
    const ulke = ulkeHaritasi.get(basvuruKimligi(kategori.data.country));
    if (!ulke) throw new Error(`${kategori.id}: ülke bulunamadı.`);
    return {
      id: kategori.id,
      data: kategori.data,
      ulke,
      href: kategoriYolu(ulke.data.slug, kategori.data.slug),
      eserler: eserler.filter((eser) => eser.kategori.id === kategori.id),
    };
  });

  return {
    ulkeler: ulkeKayitlari.map((ulke) => ({
      id: ulke.id,
      data: ulke.data,
      href: ulkeYolu(ulke.data.slug),
      kategoriler: kategoriler.filter((kategori) => kategori.ulke.id === ulke.id),
    })),
    kategoriler,
    eserler,
  };
}

export function tarihYaz(iso: string): string {
  const [yil, ay, gun] = iso.split('-').map(Number);
  const aylar = [
    'Ocak',
    'Şubat',
    'Mart',
    'Nisan',
    'Mayıs',
    'Haziran',
    'Temmuz',
    'Ağustos',
    'Eylül',
    'Ekim',
    'Kasım',
    'Aralık',
  ];
  return `${gun} ${aylar[(ay ?? 1) - 1]} ${yil}`;
}
