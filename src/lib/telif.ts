/**
 * Türkiye'de koruma süresi.
 *
 * Süre, ölüm yılının sonundan itibaren 70 yıldır: eser, ölüm yılını takip
 * eden takvim yılının başından başlayarak 70 yıl korunur ve bir sonraki
 * 1 Ocak'ta serbest kalır. 1920'de ölen bir yazarın eseri 1 Ocak 1991'de
 * serbesttir (1920 + 70 = 1990 sonunda biter).
 *
 * Çeviri ve aktarmalarda hem yazarın hem çevirmenin süresi dolmuş olmalıdır.
 * Özgün Türkçe metinde çevirmen yoktur.
 */
export const KORUMA_YILI = 70;

export interface EserHakki {
  title: string;
  author: string;
  authorDeathYear: number;
  translator: string | null;
  translatorDeathYear: number | null;
}

export interface TelifSonucu {
  /** Derleme yılında Türkiye'de yayımlanabilir mi? */
  serbest: boolean;
  /** Serbestliğin başladığı yıl (1 Ocak). Geçersiz kayıtta null. */
  serbestYil: number | null;
  /** Eser sayfasındaki "Türkiye'de serbest" gerekçesi. Yalnızca serbest eserlerde olumlu cümle. */
  gerekce: string;
  hatalar: string[];
}

export function korumaBitisYili(olumYili: number): number {
  return olumYili + KORUMA_YILI;
}

/** Serbestliğin başladığı takvim yılı. */
export function serbestlikYili(olumYili: number): number {
  return olumYili + KORUMA_YILI + 1;
}

function yilHatasi(rol: string, yil: number, bugun: number): string | null {
  if (!Number.isInteger(yil) || yil < 1 || yil > bugun) {
    return `${rol} ölüm yılı geçersiz (${yil}). 1 ile ${bugun} arasında bir yıl olmalı.`;
  }
  return null;
}

export function telifDenetle(eser: EserHakki, bugun = new Date().getFullYear()): TelifSonucu {
  const hatalar: string[] = [];
  const yazarYilHatasi = yilHatasi('Yazar', eser.authorDeathYear, bugun);
  if (yazarYilHatasi) hatalar.push(`${eser.title}: ${yazarYilHatasi}`);

  const cevirmen = eser.translator;
  const cevirmenVar = cevirmen !== null;
  if (cevirmen !== null && cevirmen.trim() === '') {
    hatalar.push(
      `${eser.title}: çevirmen adı boş. Özgün Türkçe metinde çevirmen null bırakılır ve künyede "yok" görünür.`,
    );
  }
  if (!cevirmenVar && eser.translatorDeathYear !== null) {
    hatalar.push(`${eser.title}: çevirmen yokken çevirmen ölüm yılı dolu olamaz.`);
  }
  if (cevirmenVar && eser.translatorDeathYear === null) {
    hatalar.push(`${eser.title}: çevirmen veya aktaran varsa ölüm yılı zorunludur.`);
  }
  if (eser.translatorDeathYear !== null) {
    const cevirmenYilHatasi = yilHatasi('Çevirmen', eser.translatorDeathYear, bugun);
    if (cevirmenYilHatasi) hatalar.push(`${eser.title}: ${cevirmenYilHatasi}`);
  }

  const yazarSerbest = serbestlikYili(eser.authorDeathYear);
  const cevirmenSerbest =
    eser.translatorDeathYear === null ? null : serbestlikYili(eser.translatorDeathYear);
  const serbestYil =
    cevirmenSerbest === null ? yazarSerbest : Math.max(yazarSerbest, cevirmenSerbest);

  if (!yazarYilHatasi && bugun < yazarSerbest) {
    hatalar.push(
      `${eser.title}: yazar ${eser.author} (${eser.authorDeathYear}) için 70 yıl dolmamıştır. Serbestlik 1 Ocak ${yazarSerbest} tarihinde başlar; derleme yılı ${bugun}.`,
    );
  }
  if (
    cevirmenVar &&
    eser.translatorDeathYear !== null &&
    bugun < serbestlikYili(eser.translatorDeathYear)
  ) {
    hatalar.push(
      `${eser.title}: çevirmen/aktaran ${cevirmen} (${eser.translatorDeathYear}) için 70 yıl dolmamıştır. Serbestlik 1 Ocak ${serbestlikYili(eser.translatorDeathYear)} tarihinde başlar; derleme yılı ${bugun}.`,
    );
  }

  const serbest = hatalar.length === 0;

  const gerekce = serbest
    ? cevirmenVar
      ? `Yazar ${eser.author} ${eser.authorDeathYear} yılında, çevirmen/aktaran ${cevirmen} ${eser.translatorDeathYear} yılında ölmüştür. sanalbook bir çeviriyi ancak hem yazarın hem çevirmenin ölüm yılının sonundan itibaren 70 yıl geçtikten sonra yayımlar. Yazar için serbestlik 1 Ocak ${yazarSerbest}, çevirmen için 1 Ocak ${cevirmenSerbest} başlar. Eser, geç olan tarihten, yani 1 Ocak ${serbestYil} tarihinden beri Türkiye'de serbesttir.`
      : `${eser.author} ${eser.authorDeathYear} yılında ölmüştür. Metin Türkçe özgün olduğu için çevirmen veya aktaran yoktur. Türkiye'de koruma süresi ölüm yılının sonundan itibaren 70 yıldır; bu süre 31 Aralık ${korumaBitisYili(eser.authorDeathYear)} tarihinde biter. Eser 1 Ocak ${yazarSerbest} tarihinden beri Türkiye'de serbesttir.`
    : hatalar.join(' ');

  return { serbest, serbestYil: serbest ? serbestYil : null, gerekce, hatalar };
}
