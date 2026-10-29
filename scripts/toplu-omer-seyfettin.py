#!/usr/bin/env python3
"""Ömer Seyfettin hikâyelerini Vikikaynak API'sinden aktarır.

Metin gövdesine kelime değiştirilmez. Yalnızca viki işaretleri, şablonlar,
editör dipnotları ve gezinti bağlantıları ayıklanır. İstekler arasında
en az 1 saniye beklenir.
"""

from __future__ import annotations

import html
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
API = "https://tr.wikisource.org/w/api.php"
UA = (
    "SanalbookBot/1.0 (public-domain literary archive; "
    "https://sanalbook.saydamonur2002.workers.dev)"
)
ONBELLEK = Path("/tmp/sanalbook-ose-cache")
VAR_OLAN = {"Kaşağı", "Forsa", "Pembe İncili Kaftan", "Diyet", "Bomba"}
VAR_OLAN_KISA = {"kasagi", "forsa", "pembe-incili-kaftan", "diyet", "bomba"}
AZAMI = 30
BEKLEME = 1.05

YAYINEVI = (
    "yapı kredi",
    "yapi kredi",
    "iş bankası",
    "is bankasi",
    "inkılap",
    "inkılâp",
    "inkilap",
    "can yayın",
    "bilgi yayınevi",
    "ötüken",
    "iletişim yayın",
    "everest",
    "dergâh",
    "remzi kitabevi",
    "morpa",
    "altın kitap",
    "türkiye iş bankası",
    "kırmızı kedi",
    "ithaki",
    "say yayın",
)


def tr_lower(metin: str) -> str:
    return metin.replace("İ", "i").replace("I", "ı").lower()


def api(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode(params)
    istek = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(istek, timeout=90) as yanit:
        return json.load(yanit)


def cek(baslik: str) -> dict:
    ONBELLEK.mkdir(parents=True, exist_ok=True)
    anahtar = re.sub(r"[^\w\-]+", "_", baslik, flags=re.UNICODE)
    dosya = ONBELLEK / f"{anahtar}.json"
    if dosya.exists():
        return json.loads(dosya.read_text(encoding="utf-8"))
    veri = api(
        {
            "action": "query",
            "titles": baslik,
            "redirects": "1",
            "prop": "revisions",
            "rvprop": "content|ids|timestamp",
            "rvslots": "main",
            "format": "json",
            "formatversion": "2",
        }
    )
    time.sleep(BEKLEME)
    sorgu = veri["query"]
    sayfa = sorgu["pages"][0]
    if sayfa.get("missing"):
        kayit = {"missing": True, "title": baslik, "wikitext": "", "revid": None, "timestamp": None}
    else:
        rev = sayfa["revisions"][0]
        kayit = {
            "missing": False,
            "title": sayfa["title"],
            "requested": baslik,
            "wikitext": rev["slots"]["main"]["content"],
            "revid": rev["revid"],
            "timestamp": rev["timestamp"],
            "redirects": sorgu.get("redirects", []),
        }
    dosya.write_text(json.dumps(kayit, ensure_ascii=False), encoding="utf-8")
    return kayit


def hikaye_listesi(kisi_viki: str) -> list[tuple[str, str]]:
    bolum = kisi_viki.split("== Hikâyeleri ==")[1].split("== Şiirleri ==")[0]
    bulunan = []
    for hedef, etiket in re.findall(r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]", bolum):
        hedef = hedef.strip()
        if hedef.startswith(("w:", "Kategori:", "Dosya:", "Şablon:", "Kişi:")):
            continue
        gorunen = (etiket or hedef).strip()
        bulunan.append((hedef, gorunen))
    return bulunan


def sablon_al(viki: str, ad: str) -> str | None:
    eslesme = re.search(r"\{\{\s*" + re.escape(ad) + r"(.*?)\n\}\}", viki, flags=re.S | re.I)
    if not eslesme:
        return None
    return eslesme.group(1)


def alan(sablon: str | None, ad: str) -> str:
    if not sablon:
        return ""
    eslesme = re.search(rf"\|\s*{ad}\s*=\s*(.*?)(?=\n\||\n\}}|\Z)", sablon, flags=re.S | re.I)
    if not eslesme:
        return ""
    return eslesme.group(1).strip()


def viki_duz(metin: str) -> str:
    metin = re.sub(r"'''(.+?)'''", r"\1", metin)
    metin = re.sub(r"''(.+?)''", r"\1", metin)
    metin = re.sub(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", r"\1", metin)
    metin = re.sub(r"<[^>]+>", "", metin)
    metin = html.unescape(metin.replace("&mdash;", "—"))
    return re.sub(r"\s+", " ", metin).strip()


def ust_bilgi(viki: str) -> str:
    """Hikâye gövdesi hariç künye, şablon ve kaynakça."""
    govde_oncesi = viki
    kes = re.search(r"^==+\s*(Dipnotlar|Kaynakça|Kaynaklar)\s*==+", viki, flags=re.M | re.I)
    kaynakca = viki[kes.start() :] if kes else ""
    sablon = sablon_al(viki, "eser başlığı") or ""
    return "\n".join([sablon, kaynakca])


def suphe_nedenleri(viki: str, kelime: int) -> list[str]:
    nedenler = []
    kucuk = tr_lower(viki)
    if "sadeleştiren" in kucuk or "sadeleştirme" in kucuk or "günümüz türkçesine" in kucuk:
        nedenler.append('Sayfada "sadeleştiren", "sadeleştirme" veya "günümüz Türkçesine" ifadesi var.')
    bilgi = tr_lower(ust_bilgi(viki))
    yillar = [int(y) for y in re.findall(r"\b(19[5-9]\d|20[0-2]\d)\b", bilgi)]
    if yillar or any(ad in bilgi for ad in YAYINEVI):
        nedenler.append(
            "Sayfada 1950 sonrası bir baskı veya modern yayınevi kaynak gösterilmiş: "
            + (", ".join(str(y) for y in sorted(set(yillar))) or "yayınevi adı")
            + "."
        )
    if re.search(r"\{\{\s*(taslak|eksik|kontrol edilmemiş)", kucuk) or any(
        ifade in kucuk for ifade in ("{{taslak", "{{eksik", "kontrol edilmemiş", "şablon:taslak")
    ):
        nedenler.append('Sayfa "taslak", "eksik" veya "kontrol edilmemiş" şablonu taşıyor.')
    if kelime < 300:
        nedenler.append(f"Temizlenmiş metin 300 kelimeden kısa ({kelime}).")
    return nedenler


def sablonlari_sil(metin: str) -> str:
    cikti = []
    i = 0
    while i < len(metin):
        if metin.startswith("{{", i):
            derinlik = 0
            j = i
            while j < len(metin) - 1:
                if metin.startswith("{{", j):
                    derinlik += 1
                    j += 2
                elif metin.startswith("}}", j):
                    derinlik -= 1
                    j += 2
                    if derinlik == 0:
                        break
                else:
                    j += 1
            i = j
        else:
            cikti.append(metin[i])
            i += 1
    return "".join(cikti)


def govde_hazirla(viki: str) -> str:
    metin = html.unescape(viki)
    metin = re.sub(r"<ref\b[^>]*>.*?</ref>", "", metin, flags=re.S | re.I)
    metin = re.sub(r"<ref\b[^>]*/>", "", metin, flags=re.I)
    metin = re.sub(r"<br\s*/?>", "\n", metin, flags=re.I)
    metin = re.sub(r"</?(?:div|small|big|span|font)\b[^>]*>", "", metin, flags=re.I)
    kes = re.search(r"^==+\s*(Dipnotlar|Kaynakça|Kaynaklar|Ayrıca bakınız)\s*==+", metin, flags=re.M | re.I)
    if kes:
        metin = metin[: kes.start()]
    metin = sablonlari_sil(metin)
    metin = re.sub(r"\[\[Kategori:[^\]]+\]\]", "", metin)
    metin = re.sub(r"__(?:NOTOC|TOC|NOEDITSECTION)__", "", metin)
    metin = re.sub(r"\[https?://[^\s\]]+\s+([^\]]+)\]", r"\1", metin)
    metin = re.sub(r"\[https?://[^\s\]]+\]", "", metin)
    metin = re.sub(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", r"\1", metin)
    return metin


def cumle_sonu(metin: str) -> bool:
    temiz = metin.rstrip()
    return bool(temiz) and temiz[-1] in ".!?…:\"»”"


def sadece_nokta(metin: str) -> bool:
    cekirdek = metin.replace("—", "").replace('"', "").strip()
    return bool(cekirdek) and all(harf in ".…· " for harf in cekirdek)


def birlestir(sol: str, sag: str) -> str:
    sol, sag = sol.rstrip(), sag.lstrip()
    if not sol:
        return sag
    if not sag:
        return sol
    return f"{sol} {sag}"


def konusma_mu(satir: str) -> bool:
    return satir.startswith(("—", "&mdash;", '"', "“", ":"))


def paragraflar(viki: str) -> list[dict]:
    metin = govde_hazirla(viki)
    ogeler: list[dict] = []
    buf: dict | None = None

    def bosalt() -> None:
        nonlocal buf
        if buf and buf["text"].strip():
            ogeler.append(buf)
        buf = None

    for ham in metin.splitlines():
        satir = ham.rstrip()
        duz = satir.strip()
        if re.fullmatch(r"<center>\s*(?:🙝\s*🙟)?\s*</center>", duz) or duz in {"<center></center>"}:
            bosalt()
            if "🙝" in duz or "🙟" in duz:
                ogeler.append({"kind": "break", "text": ""})
            continue
        ithaf = re.fullmatch(r"<div[^>]*>(.*?)</div>", duz)
        if ithaf:
            bosalt()
            ic = re.sub(r"</?small>", "", ithaf.group(1)).replace("''", "").strip()
            if ic:
                ogeler.append({"kind": "dedication", "text": ic})
            continue
        buyuk = re.fullmatch(r"<big>(.*?)</big>", duz)
        if buyuk:
            ic = buyuk.group(1).strip()
            if tr_lower(ic) in {tr_lower("Ömer Seyfettin"), tr_lower("Omer Seyfettin")}:
                continue
            # Sayfa başlığının tekrarını at; alt başlık olarak kalmışsa paragrafa yaz.
            bosalt()
            buf = {"kind": "prose", "text": ic, "open_wrap": False, "pending_blank": False}
            bosalt()
            continue
        if duz == "":
            if buf and buf["kind"] == "prose" and not cumle_sonu(buf["text"]):
                buf["pending_blank"] = True
            else:
                bosalt()
            continue
        if re.fullmatch(r"=+\s*[^=]+=+", duz):
            baslik = re.sub(r"^=+\s*|\s*=+$", "", duz).strip()
            if tr_lower(baslik) in {"dipnotlar", "kaynakça", "kaynaklar"}:
                break
            bosalt()
            if baslik:
                buf = {"kind": "prose", "text": baslik, "open_wrap": False, "pending_blank": False}
                bosalt()
            continue
        if duz == ":":
            if buf:
                buf["open_wrap"] = True
            continue
        if duz.startswith(":"):
            icerik = re.sub(r"^:+", "", duz).strip()
            if not icerik:
                if buf:
                    buf["open_wrap"] = True
                continue
            if icerik.startswith("&mdash;"):
                icerik = "— " + icerik[len("&mdash;") :].strip()
            tur = "speech" if icerik.startswith(("—", '"', "“")) or sadece_nokta(icerik) else "prose"
            if tur == "speech" or sadece_nokta(icerik):
                if buf and buf.get("open_wrap") and not icerik.startswith(("—", '"', "“")) and not sadece_nokta(icerik):
                    buf["text"] = birlestir(buf["text"], icerik)
                    buf["open_wrap"] = False
                    continue
                bosalt()
                buf = {"kind": "speech" if icerik.startswith(("—", '"', "“")) else "prose", "text": icerik, "open_wrap": False, "pending_blank": False}
                continue
            if buf and (buf.get("open_wrap") or not cumle_sonu(buf["text"])):
                buf["text"] = birlestir(buf["text"], icerik)
                buf["open_wrap"] = False
                buf["pending_blank"] = False
                continue
            bosalt()
            buf = {"kind": "prose", "text": icerik, "open_wrap": False, "pending_blank": False}
            continue
        if duz.startswith(("—", "&mdash;")):
            if duz.startswith("&mdash;"):
                duz = "— " + duz[len("&mdash;") :].strip()
            bosalt()
            buf = {"kind": "speech", "text": duz, "open_wrap": False, "pending_blank": False}
            continue
        if buf and buf["kind"] == "prose" and not buf.get("pending_blank"):
            buf["text"] = birlestir(buf["text"], duz)
            continue
        if buf and buf["kind"] == "prose" and buf.get("pending_blank"):
            if not cumle_sonu(buf["text"]) and duz[:1].islower():
                buf["text"] = birlestir(buf["text"], duz)
                buf["pending_blank"] = False
                continue
            bosalt()
        if buf:
            bosalt()
        buf = {"kind": "prose", "text": duz, "open_wrap": False, "pending_blank": False}
    bosalt()
    return ogeler


def satir_ici(metin: str) -> str:
    metin = html.unescape(metin).replace("&mdash;", "—")
    metin = re.sub(r"'''(.+?)'''", r"§B§\1§/B§", metin)
    metin = re.sub(r"''(.+?)''", r"§I§\1§/I§", metin)
    metin = metin.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    metin = (
        metin.replace("§B§", "<strong>")
        .replace("§/B§", "</strong>")
        .replace("§I§", "<em>")
        .replace("§/I§", "</em>")
    )
    return re.sub(r"\s+", " ", metin).strip()


def html_paragraflar(ogeler: list[dict]) -> list[str]:
    bloklar = []
    for oge in ogeler:
        if oge["kind"] == "break":
            bloklar.append('<hr class="ayrac" />')
            continue
        if oge["kind"] == "dedication":
            bloklar.append(f'<p class="ithaf"><em>{satir_ici(oge["text"])}</em></p>')
            continue
        sinif = "konusma" if oge["kind"] == "speech" else "duz"
        bloklar.append(f'<p class="{sinif}">{satir_ici(oge["text"])}</p>')
    return bloklar


def kelime_say(metin: str) -> int:
    yalin = re.sub(r"<[^>]+>", " ", metin)
    return len(re.findall(r"\S+", yalin))


def cumlelere_bol(paragraf: str) -> list[str]:
    parcalar = re.split(r"(?<=[.!?…])\s+", paragraf.strip())
    parcalar = [p for p in parcalar if p.strip()]
    if len(parcalar) <= 1:
        return [paragraf]
    gruplar: list[str] = []
    buf: list[str] = []
    sayi = 0
    for cumle in parcalar:
        ek = kelime_say(cumle)
        if buf and sayi >= 2000 and sayi + ek > 3500:
            gruplar.append(" ".join(buf))
            buf, sayi = [], 0
        buf.append(cumle)
        sayi += ek
    if buf:
        gruplar.append(" ".join(buf))
    return gruplar


def parcalara_bol(bloklar: list[str]) -> list[list[str]]:
    toplam = sum(kelime_say(b) for b in bloklar)
    if toplam <= 6000:
        return [bloklar]
    parcalar: list[str] = []
    for blok in bloklar:
        if kelime_say(blok) > 3500 and blok.startswith("<p"):
            ic = re.sub(r"^<p class=\"[^\"]+\">|</p>$", "", blok)
            sinif = re.search(r'class="([^"]+)"', blok)
            sinif_adi = sinif.group(1) if sinif else "duz"
            for cumle_grubu in cumlelere_bol(re.sub(r"<[^>]+>", " ", html.unescape(ic))):
                parcalar.append(f'<p class="{sinif_adi}">{satir_ici(cumle_grubu)}</p>')
        else:
            parcalar.append(blok)
    kumeler: list[list[str]] = []
    guncel: list[str] = []
    sayi = 0
    for blok in parcalar:
        ek = kelime_say(blok)
        if guncel and sayi >= 2000 and sayi + ek > 3500:
            kumeler.append(guncel)
            guncel, sayi = [], 0
        guncel.append(blok)
        sayi += ek
    if guncel:
        kumeler.append(guncel)
    while len(kumeler) >= 2 and sum(kelime_say(b) for b in kumeler[-1]) < 2000:
        onceki = kumeler[-2]
        if len(onceki) <= 1:
            break
        tasinan = onceki.pop()
        if sum(kelime_say(b) for b in onceki) < 2000:
            onceki.append(tasinan)
            break
        kumeler[-1].insert(0, tasinan)
    if len(kumeler) >= 2 and sum(kelime_say(b) for b in kumeler[-1]) < 2000:
        birlesik = sum(kelime_say(b) for b in kumeler[-2]) + sum(kelime_say(b) for b in kumeler[-1])
        if birlesik <= 3500:
            kumeler[-2].extend(kumeler[-1])
            kumeler.pop()
    return kumeler


def kisa_ad(baslik: str) -> str:
    cevir = str.maketrans(
        {
            "ç": "c",
            "ğ": "g",
            "ı": "i",
            "ö": "o",
            "ş": "s",
            "ü": "u",
            "â": "a",
            "î": "i",
            "û": "u",
            "Ç": "c",
            "Ğ": "g",
            "İ": "i",
            "I": "i",
            "Ö": "o",
            "Ş": "s",
            "Ü": "u",
            "Â": "a",
            "Î": "i",
            "Û": "u",
        }
    )
    s = baslik.translate(cevir).lower()
    s = s.replace("’", "").replace("'", "").replace("“", "").replace("”", "").replace('"', "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def ilk_yayim(viki: str) -> str | None:
    sablon = sablon_al(viki, "eser başlığı")
    notlar = html.unescape(alan(sablon, "notlar"))
    notlar = re.sub(r"\[https?://[^\s\]]+(?:\|[^\]]+)?\]", "", notlar)
    notlar = re.sub(r"\[https?://[^\s\]]+\s+[^\]]+\]", "", notlar)
    notlar = re.sub(r"\s*Kaynak:\s*", " ", notlar)
    notlar = viki_duz(notlar)
    notlar = re.sub(r"^İlk yayım:\s*", "", notlar).strip(" -")
    if not notlar:
        return None
    kucuk = tr_lower(notlar)
    if kucuk in {"kalın yazı", "kalin yazi"}:
        return None
    if not re.search(r"\b(1[0-8]\d{2}|19[0-4]\d)\b", notlar) and not any(
        iz in kucuk for iz in ("mecmua", "gazete", "matbaa", "yayım", "yayim")
    ):
        return None
    return notlar


def aktaran_kisi(viki: str) -> str | None:
    sablon = sablon_al(viki, "eser başlığı") or ""
    for ad in ("aktaran", "çevirmen", "mütercim", "sadeleştiren"):
        deger = viki_duz(alan(sablon, ad))
        if not deger:
            continue
        kucuk = tr_lower(deger)
        if any(iz in kucuk for iz in ("mecmua", "gazete", "yayınevi", "matbaa", "kitabevi")):
            continue
        return deger
    return None


def puan(viki: str, yayim: str | None) -> int:
    puan_degeri = 0
    if sablon_al(viki, "eser başlığı"):
        puan_degeri += 3
    if yayim:
        puan_degeri += 8
    if "kaynakça" in tr_lower(viki) or "kaynakca" in tr_lower(viki):
        puan_degeri += 2
    if alan(sablon_al(viki, "eser başlığı"), "eser sahibi"):
        puan_degeri += 1
    return puan_degeri


def kaynak_url(baslik: str, revid: int) -> str:
    parca = urllib.parse.quote(baslik.replace(" ", "_"), safe="")
    return f"https://tr.wikisource.org/wiki/{parca}?oldid={revid}"


def fazlaliklari_sil(kalan: set[str]) -> None:
    for dosya in (KOK / "src" / "content" / "works").glob("*.json"):
        if dosya.stem in VAR_OLAN_KISA or dosya.stem in kalan:
            continue
        dosya.unlink()
    for klasor in (KOK / "src" / "content" / "chapters").iterdir():
        if not klasor.is_dir() or klasor.name in VAR_OLAN_KISA or klasor.name in kalan:
            continue
        for cocuk in klasor.glob("*"):
            cocuk.unlink()
        klasor.rmdir()


def yaz(secilen: list[dict]) -> None:
    fazlaliklari_sil({eser["slug"] for eser in secilen})
    for eser in secilen:
        klasor = KOK / "src" / "content" / "chapters" / eser["slug"]
        klasor.mkdir(parents=True, exist_ok=True)
        for sira, bloklar in enumerate(eser["bolumler"], start=1):
            baslik = eser["title"] if len(eser["bolumler"]) == 1 else f"Bölüm {sira}"
            govde = "\n\n".join(bloklar) + "\n"
            dosya = klasor / f"{sira:02d}.md"
            dosya.write_text(
                "---\n"
                f"title: {json.dumps(baslik, ensure_ascii=False)}\n"
                f"work: {eser['slug']}\n"
                f"order: {sira}\n"
                "---\n\n"
                f"{govde}",
                encoding="utf-8",
            )
        kayit = {
            "title": eser["title"],
            "slug": eser["slug"],
            "author": "Ömer Seyfettin",
            "authorDeathYear": 1920,
            "translator": "belirtilmemiş",
            "translatorDeathYear": None,
            "country": "turkiye",
            "category": "hikaye",
            "order": eser["order"],
            "sourceName": "Vikikaynak",
            "sourceUrl": eser["url"],
            "sourceRevision": eser["revid"],
            "sourceRetrieved": eser["tarih"],
            "originalPublication": eser["yayim"],
            "seri": None,
        }
        if not eser["yayim"]:
            kayit["sourceNote"] = (
                f"Vikikaynak sayfasında ilk yayım künyesi yok. Metin, sayfadaki aktarımın {eser['revid']}. sürümüdür."
            )
        (KOK / "src" / "content" / "works" / f"{eser['slug']}.json").write_text(
            json.dumps(kayit, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def supheli_yaz(satirlar: list[dict]) -> None:
    dizin = KOK / "icerik-kontrol"
    dizin.mkdir(parents=True, exist_ok=True)
    govde = [
        "# Ömer Seyfettin — şüpheli metinler",
        "",
        "Bu liste yayına alınmadı. Vikikaynak sayfası aşağıdaki nedenle elendi.",
        "",
    ]
    for satir in satirlar:
        govde.append(f"## {satir['title']}")
        govde.append(f"- Bağlantı: {satir['url']}")
        for neden in satir["nedenler"]:
            govde.append(f"- Neden: {neden}")
        govde.append("")
    (dizin / "omer-seyfettin-supheli.md").write_text("\n".join(govde), encoding="utf-8")


def main() -> None:
    kisi = cek("Kişi:Ömer Seyfettin")
    if kisi.get("missing"):
        raise SystemExit("Kişi:Ömer Seyfettin bulunamadı")
    adaylar = hikaye_listesi(kisi["wikitext"])
    print(f"listed={len(adaylar)}", flush=True)
    hazir = []
    supheli = []
    kullanilan_kisa: set[str] = set(VAR_OLAN_KISA)
    for hedef, gorunen in adaylar:
        if gorunen in VAR_OLAN or hedef in VAR_OLAN:
            continue
        baslik = gorunen
        try:
            sayfa = cek(hedef)
        except Exception as hata:
            supheli.append(
                {
                    "title": baslik,
                    "url": "https://tr.wikisource.org/wiki/" + urllib.parse.quote(hedef.replace(" ", "_"), safe=""),
                    "nedenler": [f"API isteği başarısız: {hata}"],
                }
            )
            print(f"hata {baslik} {hata}", flush=True)
            continue
        if sayfa.get("missing"):
            supheli.append(
                {
                    "title": baslik,
                    "url": "https://tr.wikisource.org/wiki/" + urllib.parse.quote(hedef.replace(" ", "_"), safe=""),
                    "nedenler": ["Vikikaynak sayfası bulunamadı."],
                }
            )
            print(f"missing {baslik}", flush=True)
            continue
        viki = sayfa["wikitext"]
        kanon = sayfa["title"]
        revid = sayfa["revid"]
        tarih = sayfa["timestamp"][:10]
        url = kaynak_url(kanon, revid)
        bloklar = html_paragraflar(paragraflar(viki))
        if bloklar:
            ilk_duz = re.sub(r"<[^>]+>", "", bloklar[0]).strip()
            if ilk_duz == baslik or ilk_duz == kanon:
                bloklar = bloklar[1:]
        if bloklar:
            son_duz = re.sub(r"<[^>]+>", "", bloklar[-1]).strip()
            if tr_lower(son_duz) in {"ömer seyfettin", "omer seyfettin"}:
                bloklar = bloklar[:-1]
        kelime = sum(kelime_say(b) for b in bloklar)
        nedenler = suphe_nedenleri(viki, kelime)
        kisi_adi = aktaran_kisi(viki)
        if kisi_adi:
            nedenler.append(
                f"Aktaran olarak «{kisi_adi}» yazılmış; ölüm yılı sayfada yok, 70 yıl kuralı doğrulanamadı."
            )
        if nedenler:
            supheli.append({"title": baslik, "url": url, "nedenler": nedenler})
            print(f"supheli {baslik} {kelime}", flush=True)
            continue
        yayim = ilk_yayim(viki)
        kisa = kisa_ad(baslik)
        if not kisa or kisa in kullanilan_kisa:
            n = 2
            temel = kisa or "hikaye"
            while f"{temel}-{n}" in kullanilan_kisa:
                n += 1
            kisa = f"{temel}-{n}"
        kullanilan_kisa.add(kisa)
        hazir.append(
            {
                "title": baslik,
                "slug": kisa,
                "url": url,
                "revid": revid,
                "tarih": tarih,
                "yayim": yayim,
                "puan": puan(viki, yayim),
                "kelime": kelime,
                "bloklar": bloklar,
            }
        )
        print(f"aday {baslik} puan={puan(viki, yayim)} kelime={kelime}", flush=True)

    hazir.sort(key=lambda eser: (-eser["puan"], eser["title"]))
    secilen = hazir[:AZAMI]
    for indeks, eser in enumerate(secilen, start=6):
        eser["order"] = indeks
        eser["bolumler"] = parcalara_bol(eser["bloklar"])
        eser["bolum_kelime"] = [sum(kelime_say(b) for b in grup) for grup in eser["bolumler"]]
    yaz(secilen)
    supheli_yaz(supheli)
    ozet = {
        "eklenen": [
            {
                "title": eser["title"],
                "slug": eser["slug"],
                "kelime": eser["kelime"],
                "puan": eser["puan"],
                "yayim": eser["yayim"],
                "revid": eser["revid"],
                "tarih": eser["tarih"],
                "url": eser["url"],
                "bolum": len(eser["bolumler"]),
                "bolum_kelime": eser["bolum_kelime"],
            }
            for eser in secilen
        ],
        "supheli_sayisi": len(supheli),
        "bolunen": [
            {
                "title": eser["title"],
                "kelime": eser["kelime"],
                "bolum_kelime": eser["bolum_kelime"],
            }
            for eser in secilen
            if len(eser["bolumler"]) > 1
        ],
        "elenen_aday": len(hazir) - len(secilen),
    }
    (ONBELLEK / "ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"EKLENDI {len(secilen)} SUPHELI {len(supheli)} BOLUNEN {len(ozet['bolunen'])}", flush=True)


if __name__ == "__main__":
    main()
