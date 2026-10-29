#!/usr/bin/env python3
"""Seçilen yazarların Vikikaynak metinlerini yazar. Kelime değiştirilmez."""

from __future__ import annotations

import html
import importlib.util
import json
import re
import urllib.parse
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
CACHE = Path("/tmp/toplu-cache")
TARIH = "2026-10-29"

spec = importlib.util.spec_from_file_location("akif", KOK / "scripts" / "aktar-mehmet-akif.py")
akif = importlib.util.module_from_spec(spec)
spec.loader.exec_module(akif)

LATIN_YAZAR = {
    "Sabahattin Ali",
    "Orhan Veli Kanık",
    "Memduh Şevket Esendal",
    "Neyzen Tevfik",
    "İsmail Habip Sevük",
    "Azmiye Hami Güven",
}

NUTUK_AD = {
    1: "Harb-i Umumî'de Anadolu'nun durumu ve halâs çareleri",
    2: "Millî teşkilatların vücuda getirilmesi ve kongreler",
    3: "İstanbul Hükûmeti ile münasebetler",
    4: "Teşkilât-ı milliyenin yeniden tanzimi",
    5: "Misak-ı Millî ve gelişmeler",
    6: "Türkiye Büyük Millet Meclisinin toplanması",
    7: "Dahilî isyanlar ve Şark Cephesi'ndeki gelişmeler",
    8: "Muntazam ordu vücuda getirmek kararı",
    9: "İstanbul Hükûmeti'nin Ankara ile temas arayışları",
    10: "Garp Cephesi'ndeki gelişmeler ve Birinci İnönü Zaferi",
    11: "Londra Konferansı ve İkinci İnönü Zaferi",
    12: "Sakarya Meydan Muharebesi ve müteakip gelişmeler",
    13: "Büyük Taarruz ve Başkumandan Muharebesi, Mudanya Konferansı",
    14: "Lozan Konferansı ve saltanatın lağvı, hilâfet meselesi",
    15: "Halk Fırkasını teşkil teşebbüleri, Lozan Muâhedesi ve müteakip gelişmeler",
    16: "Cumhuriyetin ilânı",
    17: "Hilâfetin lağvı",
    18: "Cumhuriyete karşı dahili muhâlefet, paşalar mücadelesi ve Teşkilât-ı Esasiye",
    19: "Türk gençliğine bıraktığım emanet",
}
ROMA = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX"]


def tr_lower(s: str) -> str:
    return s.replace("İ", "i").replace("I", "ı").lower()


def kacis(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def bicim_satir(satir: str, siir: bool) -> str:
    satir = re.sub(r"'''(.+?)'''", r"§B§\1§/B§", satir)
    satir = re.sub(r"''(.+?)''", r"§I§\1§/I§", satir)
    satir = satir.replace("'''", "").replace("''", "")
    if not siir:
        satir = re.sub(r"\s+", " ", satir).strip()
    return (
        kacis(satir)
        .replace("§B§", "<strong>")
        .replace("§/B§", "</strong>")
        .replace("§I§", "<em>")
        .replace("§/I§", "</em>")
    )


def sablon_sil(metin: str) -> str:
    return akif.sablonlari_sil(metin)


def kelime(metin: str) -> int:
    yalin = re.sub(r"<[^>]+>", " ", metin)
    yalin = html.unescape(yalin)
    return len(re.findall(r"\S+", yalin))


def kes_sade(viki: str) -> str:
    m = re.search(r"^==+\s*[^\n]*(sadeleştir|güncelleştir)[^\n]*==+", viki, flags=re.M | re.I)
    if m:
        return viki[: m.start()]
    return viki


def sade_kubde(viki: str) -> bool:
    govde = akif.sablon_govde(viki, "eser başlığı") or akif.sablon_govde(viki, "eser") or ""
    k = tr_lower(govde + "\n" + "\n".join(viki.splitlines()[:8]))
    return any(x in k for x in ("sadeleştiren", "sadeleştirme", "sadeleştirilmiş", "günümüz türkçesi", "güncelleştir"))


def alan_satir(govde: str, ad: str) -> str:
    if not govde:
        return ""
    m = re.search(rf"(?:^|\n)\|\s*{ad}\s*=\s*([^\n]*)", govde)
    return m.group(1).strip() if m else ""


def ceviri_adi(viki: str) -> str | None:
    govde = akif.sablon_govde(viki, "eser başlığı") or akif.sablon_govde(viki, "eser") or ""
    for ad in ("çevirmen", "mütercim", "aktaran", "çeviren"):
        deger = akif.viki_duz(alan_satir(govde, ad))
        if not deger or tr_lower(deger) in {"yok", "?", "-", "—"} or len(deger) > 80 or "|" in deger:
            continue
        return deger
    if re.search(r"çevirmen\s*=\s*\[\[Kullanıcı:", govde, flags=re.I):
        return "Vikikaynak kullanıcısı"
    return None


def yil_bul(viki: str, satir_yil: int | None, olum: int) -> int | None:
    govde = akif.sablon_govde(viki, "eser başlığı") or akif.sablon_govde(viki, "eser") or ""
    notlar = akif.viki_duz(alan_satir(govde, "notlar"))
    yillar = [int(y) for y in re.findall(r"\b(1[89]\d{2}|20\d{2})\b", notlar)]
    ham = alan_satir(govde, "yıl")
    if re.fullmatch(r"\d{4}", ham.strip()):
        yillar.append(int(ham.strip()))
    if satir_yil:
        yillar.append(satir_yil)
    uygun = [y for y in yillar if y <= olum + 1]
    return min(uygun) if uygun else None


def latin_mi(yazar: str, yil: int | None) -> bool:
    if yil is not None and yil >= 1929:
        return True
    if yil is not None and yil <= 1928:
        return False
    return yazar in LATIN_YAZAR


def ilk_yayim(viki: str) -> str | None:
    govde = akif.sablon_govde(viki, "eser başlığı") or akif.sablon_govde(viki, "eser") or ""
    notlar = akif.viki_duz(alan_satir(govde, "notlar"))
    if notlar and re.search(r"\b(1[89]\d{2}|20\d{2})\b", notlar) and "kullanıcı" not in tr_lower(notlar):
        if len(notlar) > 240:
            notlar = notlar.split(". ")[0].strip()
            if not notlar.endswith("."):
                notlar += "."
        return notlar
    return None


def baslik_al(viki: str, yedek: str) -> str:
    govde = akif.sablon_govde(viki, "eser başlığı") or akif.sablon_govde(viki, "eser") or ""
    baslik = akif.viki_duz(alan_satir(govde, "başlık"))
    if baslik and baslik not in {"{{PAGENAME}}", "PAGENAME"} and "nutuk" != tr_lower(baslik):
        if not baslik.lower().startswith("[["):
            return baslik
    yedek = re.sub(r"\s*\([^)]*\)\s*$", "", yedek).strip()
    return yedek


def siir_html(metin: str) -> str:
    satirlar = [bicim_satir(ln, True) for ln in metin.split("\n")]
    return '<pre class="siir">' + "\n".join(satirlar) + "</pre>"


def duz_html(metin: str) -> str:
    sinif = "konusma" if metin.startswith(("–", "—", "- ")) else "duz"
    return f'<p class="{sinif}">{bicim_satir(metin, False)}</p>'


def sablon_ac(metin: str, ad: str) -> str:
    bas = re.search(r"\{\{\s*" + re.escape(ad) + r"\s*\|", metin, flags=re.I)
    if not bas:
        return metin
    i = bas.end()
    derinlik = 1
    j = i
    n = len(metin)
    while j < n - 1 and derinlik:
        if metin.startswith("{{", j):
            derinlik += 1
            j += 2
        elif metin.startswith("}}", j):
            derinlik -= 1
            if derinlik == 0:
                return metin[: bas.start()] + metin[i:j] + metin[j + 2 :]
            j += 2
        else:
            j += 1
    return metin


def siir_metni(ic: str) -> str:
    ic = ic.replace("{{'}}", "'")
    for ad in ("ortalı ve hizalı", "orta", "sağa hizala", "xxx-larger", "center"):
        for _ in range(4):
            yeni = sablon_ac(ic, ad)
            if yeni == ic:
                break
            ic = yeni
    ic = re.sub(r"<br\s*/?>\s*", "\n", ic, flags=re.I)
    ic = re.sub(r"\{\{\s*orta\s*\|(.*?)\}\}", r"\1", ic, flags=re.S | re.I)
    ic = re.sub(r"\{\{\s*sağa hizala\s*\|(.*?)\}\}", r"\1", ic, flags=re.S | re.I)
    ic = re.sub(r"\{\{[^}]*\}\}", "", ic)
    ic = sablon_sil(ic)
    ic = re.sub(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", r"\1", ic)
    ic = re.sub(r"</?(?:center|big|div|span|u)\b[^>]*>", "", ic, flags=re.I)
    ic = re.sub(r"<[^>]+>", "", ic)
    ic = html.unescape(ic)
    ic = akif.yetim_dipnot(ic)
    satirlar = []
    for ln in ic.splitlines():
        ln = re.sub(r"^:+", "", ln).rstrip()
        satirlar.append(ln)
    while satirlar and not satirlar[0].strip():
        satirlar.pop(0)
    while satirlar and not satirlar[-1].strip():
        satirlar.pop()
    return "\n".join(satirlar)


def tablo_siir(viki: str) -> str | None:
    m = re.search(r"\{\|(.*?)\|\}", viki, flags=re.S)
    if not m:
        return None
    govde = m.group(1)
    parcalar = []
    for satir_grup in re.split(r"\n\|-", govde):
        hucreler = re.split(r"\n\|", satir_grup)
        if len(hucreler) < 2:
            continue
        latin = hucreler[-1]
        latin = re.sub(r"</?big>", "", latin)
        latin = re.sub(r"<[^>]+>", "", latin)
        latin = html.unescape(latin)
        if re.search(r"[\u0600-\u06FF]", latin) and not re.search(r"[A-Za-zÇĞİÖŞÜçğıöşüâîû]", latin):
            continue
        satirlar = [ln.rstrip() for ln in latin.splitlines()]
        while satirlar and not satirlar[0].strip():
            satirlar.pop(0)
        while satirlar and not satirlar[-1].strip():
            satirlar.pop()
        if any(re.search(r"[A-Za-zÇĞİÖŞÜçğıöşüâîû]", ln) for ln in satirlar):
            if parcalar:
                parcalar.append("")
            parcalar.extend(satirlar)
    if len([p for p in parcalar if p.strip()]) < 4:
        return None
    return "\n".join(parcalar)


def bloklar(viki: str) -> list[tuple[str, str]]:
    viki = kes_sade(viki)
    viki = viki.replace("{{'}}", "'")
    if "<poem>" not in viki.lower():
        tablo = tablo_siir(viki)
        if tablo:
            return [("siir", tablo)]
        iki_nokta = []
        for ln in viki.splitlines():
            if re.match(r"^:+\S", ln.strip()) or re.match(r"^:+", ln):
                iki_nokta.append(re.sub(r"^:+", "", ln).rstrip())
        dolu = [ln for ln in viki.splitlines() if ln.strip() and not ln.strip().startswith(("{", "|", "[", "<", "="))]
        if iki_nokta and len(iki_nokta) >= max(3, len(dolu) // 2):
            return [("siir", "\n".join(iki_nokta).strip())]
    parcalar: list[tuple[str, str]] = []
    kalan = viki
    while True:
        m = re.search(r"<poem>(.*?)</poem>", kalan, flags=re.S | re.I)
        if not m:
            for p in duz_parcalar(kalan):
                parcalar.append(p)
            break
        for p in duz_parcalar(kalan[: m.start()]):
            parcalar.append(p)
        siir = siir_metni(m.group(1))
        if siir.strip():
            parcalar.append(("siir", siir))
        kalan = kalan[m.end() :]
    return parcalar


def duz_parcalar(metin: str) -> list[tuple[str, str]]:
    metin = metin.replace("{{'}}", "'")
    metin = re.sub(r"\{\{\s*girinti\s*\|[^}]*\}\}", "\n\n", metin, flags=re.I)
    metin = re.sub(r"\[\[Kategori:[^\]]+\]\]", "", metin, flags=re.I)
    metin = re.sub(r"\[\[Dosya:[^\]]+\]\]", "", metin, flags=re.I)
    metin = sablon_sil(metin)
    metin = re.sub(r"<br\s*/?>", "\n", metin, flags=re.I)
    metin = re.sub(r"<div\b[^>]*>", "\n\n", metin, flags=re.I)
    metin = re.sub(r"</div>", "\n\n", metin, flags=re.I)
    metin = re.sub(r"</?(?:center|big|small|span|font|u)\b[^>]*>", "", metin, flags=re.I)
    metin = re.sub(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", r"\1", metin)
    metin = re.sub(r"\[https?://[^\]]+\]", "", metin)
    metin = re.sub(r"<[^>]+>", "", metin)
    metin = html.unescape(metin)
    metin = akif.yetim_dipnot(metin)
    cikti = []
    for blok in re.split(r"\n\s*\n", metin):
        satirlar = [re.sub(r"^:+", "", s).strip() for s in blok.splitlines() if s.strip()]
        satirlar = [s for s in satirlar if not s.lower().startswith("kategori:") and s not in {"|-", "|}"}]
        if not satirlar:
            continue
        grup: list[str] = []

        def bosalt() -> None:
            if grup:
                cikti.append(("duz", re.sub(r"\s+", " ", " ".join(grup)).strip()))
                grup.clear()

        for satir in satirlar:
            if re.match(r"^==+", satir):
                continue
            if satir.startswith(("–", "—", "- ")):
                bosalt()
                cikti.append(("konusma", satir))
            else:
                grup.append(satir)
        bosalt()
    temiz = []
    for tur, p in cikti:
        if not p or p.startswith("|") or re.fullmatch(r"[{}|=\-–—.\s]+", p):
            continue
        if kelime(p) == 0:
            continue
        temiz.append((tur, p))
    return temiz


def html_blok(parcalar: list[tuple[str, str]], baslik: str) -> str:
    bloklar = []
    for tur, metin in parcalar:
        if tur == "duz" and akif.baslik_esit(metin, baslik):
            continue
        if tr_lower(metin).strip() in {tr_lower(baslik), "içindekiler"}:
            continue
        if tur == "siir":
            if not metin.strip():
                continue
            bloklar.append(siir_html(metin))
        elif tur == "konusma":
            bloklar.append(duz_html(metin))
        else:
            bloklar.append(duz_html(metin))
    return "\n\n".join(bloklar)


def html_wiki(viki: str, baslik: str) -> str:
    return html_blok(bloklar(viki), baslik)


def sayfa_metin(w: str) -> str:
    w = re.sub(r"<noinclude>.*?</noinclude>", "", w, flags=re.S | re.I)
    return w.strip()


def sayfalar_html(parcalar: list[str], baslik: str, siir_zorunlu: bool = False) -> str:
    siirler = []
    duzler = []
    for ham in parcalar:
        w = sayfa_metin(ham)
        if not w:
            continue
        if siir_zorunlu or "<poem>" in w.lower():
            ic = siir_metni(re.sub(r"^.*?<poem>|</poem>.*$", "", w, flags=re.S | re.I) if "<poem>" in w.lower() else w)
            # poem extract properly
            bulunan = re.findall(r"<poem>(.*?)</poem>", w, flags=re.S | re.I)
            if bulunan:
                ic = "\n\n".join(siir_metni(p) for p in bulunan if siir_metni(p).strip())
            elif siir_zorunlu:
                ic = siir_metni(w)
            else:
                ic = ""
            if ic.strip():
                siirler.append(ic)
                continue
        duzler.append(w)
    if siirler and not duzler:
        return siir_html("\n\n".join(siirler))
    # prose pages
    birlesik = ""
    for ham in parcalar:
        govde = sayfa_govde(ham)
        if not govde:
            continue
        if not birlesik:
            birlesik = govde
            continue
        once, sonra = birlesik.rstrip(), govde.lstrip()
        if once and sonra and once[-1] not in ".!?…:\"»”" and not sonra.startswith(("–", "—", "- ")):
            birlesik = once + " " + sonra
        else:
            birlesik = once + "\n\n" + sonra
    return html_blok([("duz" if t != "konusma" else "konusma", m) for t, m in duz_parcalar(birlesik)], baslik) if birlesik else ""


def sayfa_govde(w: str) -> str:
    w = sayfa_metin(w)
    w = w.replace("{{'}}", "'")
    w = re.sub(r"\{\{\s*girinti\s*\|[^}]*\}\}", "\n\n", w, flags=re.I)
    w = re.sub(r"\{\{\s*orta\s*\|(.*?)\}\}", r"\n\n\1\n\n", w, flags=re.S | re.I)
    w = re.sub(r"\{\{\s*sağa hizala\s*\|(.*?)\}\}", r"\n\n\1\n\n", w, flags=re.S | re.I)
    w = re.sub(r"\{\{\s*center\s*\|(.*?)\}\}", r"\n\n\1\n\n", w, flags=re.S | re.I)
    w = sablon_sil(w)
    w = re.sub(r"<br\s*/?>", "\n", w, flags=re.I)
    w = re.sub(r"</?(?:center|big|small|span|div|font|u)\b[^>]*>", "", w, flags=re.I)
    w = re.sub(r"\[\[Dosya:[^\]]+\]\]", "", w, flags=re.I)
    w = re.sub(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", r"\1", w)
    w = re.sub(r"<poem>|</poem>", "", w, flags=re.I)
    w = re.sub(r"<[^>]+>", "", w)
    return html.unescape(w).strip()


class Depo:
    def __init__(self) -> None:
        self.eser = json.loads((CACHE / "eserler.json").read_text(encoding="utf-8"))["sayfalar"]
        self.ek = json.loads((CACHE / "ek.json").read_text(encoding="utf-8"))
        self.diger = json.loads((CACHE / "diger.json").read_text(encoding="utf-8"))
        self.nutuk = json.loads((CACHE / "nutuk-yaprak.json").read_text(encoding="utf-8"))
        self.kuyu = json.loads((CACHE / "kuyucak.json").read_text(encoding="utf-8"))
        self.sayfa = json.loads((CACHE / "sayfa.json").read_text(encoding="utf-8"))
        self.leaves = json.loads((CACHE / "nutuk-leaves.json").read_text(encoding="utf-8"))
        self.orhan = json.loads((CACHE / "orhan-liste.json").read_text(encoding="utf-8"))

    def kayit(self, title: str) -> dict | None:
        for havuz in (self.eser, self.ek, self.diger, self.nutuk, self.kuyu):
            if title in havuz:
                return havuz[title]
        return None

    def sayfa_aralik(self, index: str, a: int, b: int) -> list[str]:
        cikti = []
        for n in range(a, b + 1):
            anahtar = f"Sayfa:{index}/{n}"
            kayit = self.sayfa.get(anahtar)
            if kayit and kayit.get("wikitext"):
                cikti.append(kayit["wikitext"])
        return cikti

    def sayfa_tek(self, index: str) -> str:
        want = "Sayfa:" + index.strip().strip('"')
        for anahtar, kayit in self.sayfa.items():
            if anahtar.strip().strip('"') == want and kayit.get("wikitext"):
                return kayit["wikitext"]
        return ""


def url(baslik: str, revid: int) -> str:
    yol = urllib.parse.quote(baslik.replace(" ", "_"), safe="()_")
    return f"https://tr.wikisource.org/wiki/{yol}?oldid={revid}"


def oncekini_sil(yazarlar: set[str]) -> None:
    for yol in (KOK / "src" / "content" / "works").glob("*.json"):
        try:
            veri = json.loads(yol.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if veri.get("author") not in yazarlar:
            continue
        yol.unlink()
        klasor = KOK / "src" / "content" / "chapters" / veri["slug"]
        if klasor.exists():
            for cocuk in klasor.glob("*"):
                cocuk.unlink()
            klasor.rmdir()


def main() -> None:
    yazarlar = {
        "Ziya Gökalp",
        "Süleyman Nazif",
        "Ahmet Rasim",
        "Yusuf Akçura",
        "Abdülhak Hâmit Tarhan",
        "Ali Ekrem Bolayır",
        "Ahmet Refik Altınay",
        "Mustafa Kemal Atatürk",
        "Hüseyin Rahmi Gürpınar",
        "Mehmet Emin Yurdakul",
        "Emine Semiye",
        "Osman Cemal Kaygılı",
        "Ömer Bedrettin Uşaklı",
        "Ebubekir Hâzım Tepeyran",
        "Kemalettin Kamu",
        "Rıza Tevfik Bölükbaşı",
        "Sabahattin Ali",
        "Orhan Veli Kanık",
        "Memduh Şevket Esendal",
        "Neyzen Tevfik",
        "İsmail Habip Sevük",
        "Azmiye Hami Güven",
    }
    oncekini_sil(yazarlar)
    depo = Depo()
    kullanilan = {p.stem for p in (KOK / "src" / "content" / "works").glob("*.json")}
    sira = {"hikaye": 0, "siir": 0, "yazi": 0, "roman": 0, "tarih": 0}
    for yol in (KOK / "src" / "content" / "works").glob("*.json"):
        veri = json.loads(yol.read_text(encoding="utf-8"))
        kat = veri.get("category")
        if kat in sira:
            sira[kat] = max(sira[kat], int(veri.get("order") or 0))
    yazar_eser: dict[str, list] = {}
    supheli: dict[str, list] = {}

    def ekle(yazar, olum, baslik, kategori, viki, revid, sayfa_baslik, seri=None, satir_yil=None, html=None, bolumler=None):
        if sade_kubde(viki or ""):
            supheli.setdefault(yazar, []).append((baslik, "Sadeleştirilmiş veya günümüz Türkçesi ibaresi var."))
            return
        ceviri = ceviri_adi(viki or "")
        if ceviri:
            supheli.setdefault(yazar, []).append((baslik, f"Başkasının çevirisi: {ceviri}"))
            return
        if html is None:
            html = html_wiki(viki, baslik)
        if not bolumler:
            nkel = kelime(html)
            siir_mi = '<pre class="siir">' in html
            if nkel < (4 if siir_mi else 12) or "{{" in html or "[[" in html:
                supheli.setdefault(yazar, []).append((baslik, f"Metin çıkmadı veya çok kısa ({nkel} kelime)."))
                return
            bolumler = [{"title": baslik, "html": html}]
        else:
            bolumler = [b for b in bolumler if kelime(b["html"]) >= 8 and "{{" not in b["html"]]
            if not bolumler:
                supheli.setdefault(yazar, []).append((baslik, "Bölüm metni çıkmadı."))
                return
        yil = yil_bul(viki or "", satir_yil, olum)
        latin = latin_mi(yazar, yil)
        slug = akif.kisa_ad(baslik)
        if slug in kullanilan:
            slug = akif.kisa_ad(baslik + " " + yazar.split()[-1])
        n = 2
        kok_slug = slug
        while slug in kullanilan:
            slug = f"{kok_slug}-{n}"
            n += 1
        kullanilan.add(slug)
        sira[kategori] += 1
        yazar_eser.setdefault(yazar, []).append(
            {
                "title": baslik,
                "slug": slug,
                "author": yazar,
                "authorDeathYear": olum,
                "translator": None if latin else "belirtilmemiş",
                "translatorDeathYear": None,
                "country": "turkiye",
                "category": kategori,
                "order": sira[kategori],
                "sourceName": "Vikikaynak",
                "sourceUrl": url(sayfa_baslik, revid),
                "sourceRevision": revid,
                "sourceRetrieved": TARIH,
                "originalPublication": ilk_yayim(viki or ""),
                "seri": seri,
                **({"yazim": "latin"} if latin else {}),
                "bolumler": bolumler,
                "tur": kategori,
            }
        )

    def tek(yazar, olum, hedef, kategori, seri=None, satir_yil=None, baslik=None):
        kayit = depo.kayit(hedef)
        if not kayit or kayit.get("missing") or not kayit.get("wikitext"):
            supheli.setdefault(yazar, []).append((baslik or hedef, "Sayfa yok."))
            return
        ad = baslik or baslik_al(kayit["wikitext"], kayit.get("title") or hedef)
        ekle(
            yazar,
            olum,
            ad,
            kategori,
            kayit["wikitext"],
            kayit["revid"],
            kayit.get("title") or hedef,
            seri=seri,
            satir_yil=satir_yil,
        )

    def sayfa_eser(yazar, olum, hedef, kategori, index, a, b, seri=None, satir_yil=None, siir=False, baslik=None):
        kayit = depo.kayit(hedef)
        if not kayit or not kayit.get("revid"):
            supheli.setdefault(yazar, []).append((baslik or hedef, "Eser sayfası yok."))
            return
        parcalar = depo.sayfa_aralik(index, a, b)
        if not parcalar:
            tek_sayfa = depo.sayfa_tek(index)
            parcalar = [tek_sayfa] if tek_sayfa else []
        if not parcalar:
            supheli.setdefault(yazar, []).append((baslik or hedef, "Sayfa: taramasından metin çekilemedi."))
            return
        ad = baslik or baslik_al(kayit["wikitext"], kayit.get("title") or hedef)
        html = sayfalar_html(parcalar, ad, siir_zorunlu=siir)
        ekle(yazar, olum, ad, kategori, kayit["wikitext"], kayit["revid"], kayit.get("title") or hedef, seri=seri, satir_yil=satir_yil, html=html)

    # Ziya Gökalp
    for ad in ["Asker Duası", "Lisân", "Medeniyyet", "Turan", "Vatan"]:
        tek("Ziya Gökalp", 1924, ad, "siir")
    supheli.setdefault("Ziya Gökalp", []).append(("Kızıl Elma ve diğer kitap adları", "Bağlantısız ad; metin sayfası yok. Türk Töresi yalnızca Dizin: taraması."))
    supheli["Ziya Gökalp"].append(("Ziya Gökalp'ın mezar taşındaki yazı", "Mezar yazısı, eser listesine alınmadı."))

    # Süleyman Nazif
    for ad in ["Subhaneke Yâ Muhavvilel Ahvâl!...", "Bir İzah", "Ali Kemal Bey'e Cevabım - I", "Mütareke İmzalanırken"]:
        tek("Süleyman Nazif", 1927, ad, "yazi")
    for ad in ["Ali Kemal Bey'e Cevabım - II", "Ferit Paşa'nın Hücumları", "Ali Kemal Bey'e Cevabım - III", "Allahuekber!..", "Bir İnfisâh", "İki Sukut Bir Tezat", "Harpten Mesul", "Ah bilmem ki", "Son nefesimle hasbihal", "Dicle ve ben"]:
        supheli.setdefault("Süleyman Nazif", []).append((ad, "Sayfa yok."))
    for hedef, etiket in [
        ("Fırâk-ı Irak/Anneme", "Anneme"),
        ("Fırâk-ı Irak/Eyvâh!...", "Eyvâh!..."),
        ("Fırâk-ı Irak/Hüseyn-i Mazlûma", "Hüseyn-i Mazlûma"),
        ("Fırâk-ı Irak/Dicle ve Ben", "Dicle ve Ben"),
        ("Fırâk-ı Irak/Yâr-ı Nâim", "Yâr-ı Nâim"),
        ("Fırâk-ı Irak/Diyâr-ı Fuzûlî", "Diyâr-ı Fuzûlî"),
        ("Fırâk-ı Irak/Fuzûlî-i Bağdâdî'den Nef'î-i Erzurumî'ye", "Fuzûlî-i Bağdâdî'den Nef'î-i Erzurumî'ye"),
        ("Fırâk-ı Irak/Basra'ya Bir Niyâz", "Basra'ya Bir Niyâz"),
        ("Fırâk-ı Irak/Yine O Mehcûreye", "Yine O Mehcûreye"),
        ("Fırâk-ı Irak/Muhibb-i Edîbim Ahmet Râsim Bey'e", "Muhibb-i Edîbim Ahmet Râsim Bey'e"),
        ("Fırâk-ı Irak/Şehîdin Babası", "Şehîdin Babası"),
        ("Fırâk-ı Irak/Sübhâneke Yâ Muhavvile'l-Ahvâl!...", "Sübhâneke Yâ Muhavvile'l-Ahvâl!..."),
        ("Fırâk-ı Irak/Bir Derd-i Kadîme Râci", "Bir Derd-i Kadîme Râci"),
    ]:
        kayit = depo.kayit(hedef)
        kat = "siir" if kayit and "<poem>" in (kayit.get("wikitext") or "").lower() else "yazi"
        if kayit and kelime(html_wiki(kayit["wikitext"], etiket)) > 400 and kat == "yazi":
            kat = "hikaye" if "Şehîd" in etiket or "Derd" in etiket else "yazi"
        tek("Süleyman Nazif", 1927, hedef, kat, seri="Fırâk-ı Irak", baslik=etiket)

    tek("Ahmet Rasim", 1932, "Nedim Bey Merhum", "yazi")
    supheli.setdefault("Yusuf Akçura", []).append(("Kişi sayfası", "tr.vikikaynak'ta Kişi:Yusuf Akçura yok. Metin uydurulmadı."))

    for ad in ["Bir Sefilenin Hasbihalinden", "Belde", "Makber", "Sahra", "Sinema Şairi"]:
        tek("Abdülhak Hâmit Tarhan", 1937, ad, "siir")
    for ad in ["Elvâh-ı Tabiat'ten", "Güzelsin", "Küçük Ali'm", "Saat", "Sancak", "Şehîd Oğlum", "Son Bûse", "Vasiyyet"]:
        tek("Ali Ekrem Bolayır", 1937, ad, "siir")

    # Yirmi Beş Sene
    bolumler = []
    for i, (a, b, ad) in enumerate(
        [
            (9, 12, "1 - Atalarımızın Gayreti"),
            (13, 16, "2 - Girit seferi nasıl başladı?"),
            (17, 19, "3 - Giridde murat aga, deli kudret"),
            (20, 27, "4 - Murad aganıñ kahramanlıkları"),
            (28, 35, "5 - Kanlı hücûm, kaleniñ fethi"),
            (36, 38, "6 - Deñiz kahramanları"),
        ],
        1,
    ):
        parcalar = depo.sayfa_aralik("Yirmi beş sene siper kavgası.pdf", a, b)
        html = sayfalar_html(parcalar, ad)
        bolumler.append({"title": ad, "html": html})
    kayit = depo.kayit("Yirmi Beş Sene Siper Gavgası")
    ekle(
        "Ahmet Refik Altınay",
        1937,
        "Yirmi Beş Sene Siper Gavgası",
        "tarih",
        kayit["wikitext"] if kayit else "",
        kayit["revid"] if kayit else 0,
        "Yirmi Beş Sene Siper Gavgası",
        satir_yil=1917,
        bolumler=bolumler,
    )

    # Nutuk
    grup: dict[int, list] = {}
    for yaprak in depo.leaves:
        if yaprak["bolum"] >= 20:
            continue
        grup.setdefault(yaprak["bolum"], [])
        if not grup[yaprak["bolum"]] or grup[yaprak["bolum"]][-1]["hedef"] != yaprak["hedef"]:
            grup[yaprak["bolum"]].append(yaprak)
    nutuk_bolum = []
    for n in range(1, 20):
        if n == 19:
            kayit = depo.kayit("Nutuk/19. bölüm")
            html = html_wiki(kayit["wikitext"], "Türk gençliğine bıraktığım emanet") if kayit else ""
        else:
            parca = []
            for yaprak in grup.get(n, []):
                kayit = depo.nutuk.get(yaprak["hedef"])
                if not kayit or not kayit.get("wikitext"):
                    continue
                html_k = html_wiki(kayit["wikitext"], yaprak["etiket"])
                if kelime(html_k) < 8:
                    continue
                parca.append(f"<h2>{kacis(yaprak['etiket'])}</h2>\n\n{html_k}")
            html = "\n\n".join(parca)
        nutuk_bolum.append({"title": f"{ROMA[n]}. {NUTUK_AD[n]}", "html": html})
    kayit = depo.kayit("Nutuk")
    ekle(
        "Mustafa Kemal Atatürk",
        1938,
        "Nutuk",
        "yazi",
        kayit["wikitext"] if kayit else "",
        kayit["revid"] if kayit else 0,
        "Nutuk",
        satir_yil=1927,
        bolumler=nutuk_bolum,
    )
    supheli.setdefault("Mustafa Kemal Atatürk", []).append(("Nutuk XX. bölüm: Vesikalar", "Belge eki; okuma metnine alınmadı."))
    supheli["Mustafa Kemal Atatürk"].append(("Söylev, mektup ve diğer metinler", "Bu turda yalnız Nutuk alındı."))

    supheli.setdefault("Hüseyin Rahmi Gürpınar", []).append(("Kişi sayfası", "tr.vikikaynak'ta Hüseyin Rahmi Gürpınar sayfası yok. Metin uydurulmadı."))

    sayfa_eser("Mehmet Emin Yurdakul", 1944, "10 Temmuz", "siir", "Türk Sazı.pdf", 55, 57, seri="Türk Sazı", siir=True)
    supheli.setdefault("Mehmet Emin Yurdakul", []).append(("Türk Sazı", "1979 yıl alanlı 132 sayfalık tarama; şiirler ayrılmamış. Yalnızca 10 Temmuz alındı."))

    supheli.setdefault("Emine Semiye", []).append(("Kişi sayfası", "tr.vikikaynak'ta Emine Semiye sayfası yok. Metin uydurulmadı."))

    sayfa_eser(
        "Osman Cemal Kaygılı",
        1945,
        "İstanbul'da Semai Kahveleri ve Meydan Şairleri",
        "tarih",
        "İstanbul'da Semai Kahveleri ve Meydan Şairleri.pdf",
        2,
        34,
        satir_yil=1937,
    )
    supheli.setdefault("Osman Cemal Kaygılı", []).append(("Roman, öykü ve oyun adları", "Kişi sayfasında bağlantısız. Yalnızca İstanbul'da Semai Kahveleri bağlıydı."))

    tek("Ömer Bedrettin Uşaklı", 1946, "Deniz Hasreti", "siir")
    for ad in ["Yayla Dumanı", "Sarıkız Mermerleri", "Deniz Sarhoşları"]:
        supheli.setdefault("Ömer Bedrettin Uşaklı", []).append((ad, "Sayfa yok."))

    supheli.setdefault("Ebubekir Hâzım Tepeyran", []).append(("Kişi sayfası", "tr.vikikaynak'ta sayfa yok. Sitede de yok. Metin uydurulmadı."))
    tek("Kemalettin Kamu", 1948, "Türkün Duası", "siir")
    for ad in ["Hastayım Yalnızım", "Şu Yüce Dağları Duman Kaplamış", "Uçun Kuşlar Uçun"]:
        tek("Rıza Tevfik Bölükbaşı", 1949, ad, "siir")

    # Sabahattin Ali
    sayfa_eser("Sabahattin Ali", 1948, "Kürk Mantolu Madonna", "roman", "Kürk Mantolu Madonna.djvu", 1, 179, satir_yil=1943)
    supheli.setdefault("Sabahattin Ali", []).append(("Kuyucaklı Yusuf", "Birinci, İkinci ve Üçüncü Kısım sayfaları yok."))
    sayfa_eser("Sabahattin Ali", 1948, "Birdenbire Sönen Kandilin Hikayesi", "hikaye", "Birdenbire sönen kandilin hikayesi.pdf", 1, 7)
    sayfa_eser("Sabahattin Ali", 1948, "Dağlar (Sabahattin Ali)", "siir", "Dağlar.pdf", 1, 1, siir=True, baslik="Dağlar")
    sayfa_eser("Sabahattin Ali", 1948, "Nefes (Sabahattin Ali)", "siir", "Nefes .pdf", 1, 1, siir=True, baslik="Nefes")
    sayfa_eser("Sabahattin Ali", 1948, "Sabahattin Ali'nin Mustafa Kemal'e mektubu", "yazi", "Sabahattin Ali'nin Atatürk'e mektubu.jpg", 0, -1, baslik="Mustafa Kemal'e mektubu")
    supheli.setdefault("Sabahattin Ali", []).append(("Antigone ve Alman Darülfünunlarındaki Vak'alara Dair", "Çevirileri bölümünde; başkasının metni."))
    supheli["Sabahattin Ali"].append(("Mufassal Cermenistân Seyâhatnâmesi", "Metin, akademik bir PDF taramasına gömülü. Ayrı özgün sayfa olarak alınmadı."))

    # mektup uses single sayfa key not range. Fix call: a=0,b=-1 won't work.
    # handled below if empty — see sayfa_eser when a>b

    for ad in depo.orhan:
        if ad.strip() in {"?", ""}:
            supheli.setdefault("Orhan Veli Kanık", []).append((ad, "Geçersiz başlık."))
            continue
        tek("Orhan Veli Kanık", 1950, ad, "siir")
    # png poems that failed tek because no poem in wikitext: handled if html empty -> suspicious. Then try sayfa.
    for ad, index in [
        ("Deniz Kızı", "Deniz kızı.png"),
        ("İçerde", "İçerde.png"),
        ("Bir Duyma da Gör", "Bir duyma da gör.png"),
        ("Bedava", "Bedava.png"),
        ("Baharın İlk Sabahları", "Baharın ilk sabahları.png"),
        ("Sucunun Türküsü", "Sucunun türküsü.png"),
        ("Dalgacı Mahmut", "Dalgacı Mahmut.png"),
        ("Ahmetler", "Ahmetler.png"),
        ("Sizin İçin", "Sizin için.png"),
    ]:
        if any(e["title"] == ad for e in yazar_eser.get("Orhan Veli Kanık", [])):
            continue
        sayfa_eser("Orhan Veli Kanık", 1950, ad, "siir", index, 0, -1, siir=True, baslik=ad)
    sayfa_eser("Orhan Veli Kanık", 1950, "Bayrak", "siir", "Papirüs dergisinden Orhan Veli şiirleri.pdf", 1, 2, siir=True)
    sayfa_eser("Orhan Veli Kanık", 1950, "Orhan Veli", "siir", "Papirüs dergisinden Orhan Veli şiirleri.pdf", 3, 3, siir=True, baslik="Ben Orhan Veli")
    sayfa_eser("Orhan Veli Kanık", 1950, "İstanbul'u Dinliyorum", "siir", "İstanbul'u Dinliyorum.pdf", 1, 1, siir=True)

    supheli.setdefault("Memduh Şevket Esendal", []).append(("Otlakçı", "Sayfa yok."))
    supheli["Memduh Şevket Esendal"].append(("Ayaşlı ile Kiracıları", "Sayfa yok."))
    supheli["Memduh Şevket Esendal"].append(("Diğer kitap adları", "Kişi sayfasında bağlantısız."))

    for ad in ["Anladın Mı?", "Ben Sana", "Binamaz", "Felek", "Geçer", "Kime Sordumsa Seni", "Para (Neyzen Tevfik)", "Sahne-i Ömrümden Nefs-i Emmareye Hitabım", "Vatanın Tarihi", "İhtiyarlık ile Gençlik", "Şahid-i Şevk u Safa"]:
        tek("Neyzen Tevfik", 1953, ad, "siir")

    supheli.setdefault("İsmail Habip Sevük", []).append(("Kişi sayfası", "tr.vikikaynak'ta sayfa yok. Metin uydurulmadı."))
    supheli.setdefault("Azmiye Hami Güven", []).append(("Kişi sayfası", "tr.vikikaynak'ta sayfa yok. Metin uydurulmadı."))

    # mektup: sayfa_eser with a>b uses sayfa_tek if aralik empty. a=0,b=-1 makes range empty then sayfa_tek. Good if index matches.
    # But sayfa_eser calls sayfa_aralik first which is empty, then sayfa_tek(index). index passed is the jpg name. Good.

    dosya_ad = {
        "Ziya Gökalp": "ziya-gokalp",
        "Süleyman Nazif": "suleyman-nazif",
        "Ahmet Rasim": "ahmet-rasim",
        "Yusuf Akçura": "yusuf-akcura",
        "Abdülhak Hâmit Tarhan": "abdulhak-hamit-tarhan",
        "Ali Ekrem Bolayır": "ali-ekrem-bolayir",
        "Ahmet Refik Altınay": "ahmet-refik-altinay",
        "Mustafa Kemal Atatürk": "mustafa-kemal-ataturk",
        "Hüseyin Rahmi Gürpınar": "huseyin-rahmi-gurpinar",
        "Mehmet Emin Yurdakul": "mehmet-emin-yurdakul",
        "Emine Semiye": "emine-semiye",
        "Osman Cemal Kaygılı": "osman-cemal-kaygili",
        "Ömer Bedrettin Uşaklı": "omer-bedrettin-usakli",
        "Ebubekir Hâzım Tepeyran": "ebubekir-hazim-tepeyran",
        "Kemalettin Kamu": "kemalettin-kamu",
        "Rıza Tevfik Bölükbaşı": "riza-tevfik-bolukbasi",
        "Sabahattin Ali": "sabahattin-ali",
        "Orhan Veli Kanık": "orhan-veli-kanik",
        "Memduh Şevket Esendal": "memduh-sevket-esendal",
        "Neyzen Tevfik": "neyzen-tevfik",
        "İsmail Habip Sevük": "ismail-habip-sevuk",
        "Azmiye Hami Güven": "azmiye-hami-guven",
    }
    tur_ad = {"siir": "şiir", "hikaye": "hikâye", "yazi": "yazı", "roman": "roman", "tarih": "tarih"}
    if any(e["category"] == "roman" for eserler in yazar_eser.values() for e in eserler):
        (KOK / "src/content/categories/roman.json").write_text(
            json.dumps({"name": "Roman", "slug": "roman", "country": "turkiye", "order": 4, "description": "Romanlar."}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if any(e["category"] == "tarih" for eserler in yazar_eser.values() for e in eserler):
        (KOK / "src/content/categories/tarih.json").write_text(
            json.dumps({"name": "Tarih", "slug": "tarih", "country": "turkiye", "order": 5, "description": "Tarih ve araştırma."}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    ozet = {}
    for yazar, kod in dosya_ad.items():
        eserler = yazar_eser.get(yazar, [])
        for eser in eserler:
            bolum_dizin = KOK / "src" / "content" / "chapters" / eser["slug"]
            bolum_dizin.mkdir(parents=True, exist_ok=True)
            for i, bolum in enumerate(eser["bolumler"], 1):
                (bolum_dizin / f"{i:02d}.md").write_text(
                    "---\n"
                    f"title: {json.dumps(bolum['title'], ensure_ascii=False)}\n"
                    f"work: {eser['slug']}\n"
                    f"order: {i}\n"
                    "---\n\n"
                    f"{bolum['html']}\n",
                    encoding="utf-8",
                )
            kayit = {k: v for k, v in eser.items() if k not in {"bolumler", "tur"}}
            (KOK / "src" / "content" / "works" / f"{eser['slug']}.json").write_text(
                json.dumps(kayit, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        eklenen_ad = {e["title"] for e in eserler}
        supheli[yazar] = [cift for cift in supheli.get(yazar, []) if cift[0] not in eklenen_ad]
        sayilar: dict[str, int] = {}
        for eser in eserler:
            sayilar[eser["tur"]] = sayilar.get(eser["tur"], 0) + 1
        ozet[yazar] = {"n": len(eserler), "tur": sayilar}
        satir = [
            f"# {yazar} — eklenmeyenler",
            "",
            "Tarama: 29 Ekim 2026. Kaynak: tr.wikisource.org.",
            "Bu dosya site içeriği değildir; `dist/` içine kopyalanmaz.",
            "",
            f"Eklenen: {len(eserler)} eser.",
            "",
        ]
        if not supheli.get(yazar):
            satir.append("Şüpheli kayıt yok.")
        else:
            for ad, neden in supheli[yazar]:
                satir.append(f"- {ad} — {neden}")
        satir.append("")
        (KOK / "icerik-kontrol" / f"{kod}-supheli.md").write_text("\n".join(satir), encoding="utf-8")
        print(yazar, len(eserler), sayilar, flush=True)
    (CACHE / "ozet-yazar.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
