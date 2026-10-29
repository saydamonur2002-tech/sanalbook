#!/usr/bin/env python3
"""Mehmet Âkif Ersoy metinlerini önbellekteki Vikikaynak sürümlerinden yazar.

Kelime değiştirilmez. Şiirde dize ve kıta boşluğu durur. <pages> gömüsü
Sayfa: metni çekilebiliyorsa o metin kullanılır.
"""

from __future__ import annotations

import html
import json
import re
import urllib.parse
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
ONBELLEK = Path("/tmp/akif-cache")
YAZAR = "Mehmet Âkif Ersoy"
OLUM = 1936
TARIH = "2026-10-29"


def tr_lower(s: str) -> str:
    return s.replace("İ", "i").replace("I", "ı").lower()


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
            "’": "",
            "'": "",
            "“": "",
            "”": "",
            '"': "",
        }
    )
    s = baslik.translate(cevir).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def sablonlari_sil(metin: str) -> str:
    cikti = []
    i = 0
    n = len(metin)
    while i < n:
        if metin.startswith("{{", i):
            derinlik = 0
            j = i
            while j < n - 1:
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
            else:
                j = n
            i = j
        else:
            cikti.append(metin[i])
            i += 1
    return "".join(cikti)


def sablon_govde(metin: str, ad: str) -> str | None:
    m = re.search(r"\{\{\s*" + re.escape(ad) + r"\s*\|", metin, flags=re.I)
    if not m:
        return None
    i = m.end()
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
                return metin[i:j]
            j += 2
        else:
            j += 1
    return None


def alan(sablon: str, ad: str) -> str:
    if not sablon:
        return ""
    m = re.search(
        rf"(?:^|\|)\s*{ad}\s*=\s*(.*?)(?=\n\||\n\}}|\Z)",
        sablon,
        flags=re.S | re.I,
    )
    return m.group(1).strip() if m else ""


def bicim(satir: str, siir: bool) -> str:
    satir = re.sub(r"'''(.+?)'''", r"§B§\1§/B§", satir)
    satir = re.sub(r"''(.+?)''", r"§I§\1§/I§", satir)
    satir = satir.replace("'''", "").replace("''", "")
    if not siir:
        satir = re.sub(r"\s+", " ", satir).strip()
    satir = (
        satir.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("§B§", "<strong>")
        .replace("§/B§", "</strong>")
        .replace("§I§", "<em>")
        .replace("§/I§", "</em>")
    )
    return satir


def yetim_dipnot(metin: str) -> str:
    """Dipnot metni yoksa (1) gibi yetim işaretleri siler. Yûsuf(12) durur."""
    return re.sub(
        r"(?<![\wÂâÎîÛûÇçĞğİıÖöŞşÜü])\s*\(\d{1,2}\)(?=\s|$)",
        "",
        metin,
    )


def siir_temiz(ic: str) -> str:
    ic = ic.replace("{{'}}", "'").replace("{{’}}", "’")
    ic = re.sub(r"<br\s*/?>\s*", "\n", ic, flags=re.I)
    ic = re.sub(r"<div[^>]*>|</div>", "", ic, flags=re.I)
    ic = re.sub(r"</?(?:center|big|small|span|font)\b[^>]*>", "", ic, flags=re.I)
    ic = sablonlari_sil(ic)
    ic = re.sub(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", r"\1", ic)
    ic = re.sub(r"<ref\b[^>]*>.*?</ref>", "", ic, flags=re.S | re.I)
    ic = re.sub(r"<[^>]+>", "", ic)
    ic = html.unescape(ic)
    ic = yetim_dipnot(ic)
    satirlar = [ln.rstrip() for ln in ic.splitlines()]
    while satirlar and not satirlar[0].strip():
        satirlar.pop(0)
    while satirlar and not satirlar[-1].strip():
        satirlar.pop()
    return "\n".join(satirlar)


def duz_parcalar(metin: str) -> list[str]:
    metin = metin.replace("{{'}}", "'").replace("{{’}}", "’")
    metin = re.sub(
        r"\{\{\s*center\s*\|(.*?)\}\}",
        lambda m: "\n\n" + re.sub(r"'{2,}", "", m.group(1)).strip() + "\n\n",
        metin,
        flags=re.S | re.I,
    )
    metin = re.sub(r"\{\{\s*girinti\s*\|[^}]*\}\}", "\n\n", metin, flags=re.I)
    metin = sablonlari_sil(metin)
    metin = re.sub(r"\[\[Kategori:[^\]]+\]\]", "", metin, flags=re.I)
    metin = re.sub(r"<br\s*/?>", "\n", metin, flags=re.I)
    metin = re.sub(r"<div\b[^>]*>", "\n\n", metin, flags=re.I)
    metin = re.sub(r"</div>", "\n\n", metin, flags=re.I)
    metin = re.sub(r"</?(?:center|big|small|span|font)\b[^>]*>", "", metin, flags=re.I)
    metin = re.sub(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", r"\1", metin)
    metin = re.sub(r"\[https?://[^\s\]]+\s+([^\]]+)\]", r"\1", metin)
    metin = re.sub(r"\[https?://[^\s\]]+\]", "", metin)
    metin = re.sub(r"<[^>]+>", "", metin)
    metin = html.unescape(metin)
    metin = yetim_dipnot(metin)
    cikti = []
    for blok in re.split(r"\n\s*\n", metin):
        satirlar = [s.strip() for s in blok.splitlines() if s.strip()]
        if not satirlar:
            continue
        grup: list[str] = []

        def bosalt() -> None:
            if grup:
                cikti.append(re.sub(r"'{2,}", "", re.sub(r"\s+", " ", " ".join(grup))).strip())
                grup.clear()

        for satir in satirlar:
            if satir.startswith(("–", "—", "- ")) and grup:
                bosalt()
                cikti.append(satir)
            elif satir.startswith(("–", "—", "- ")) and not grup:
                cikti.append(satir)
            else:
                grup.append(satir)
        bosalt()
    return [p for p in cikti if p and not re.fullmatch(r"[\W_]+", p)]


def parcala(viki: str) -> list[tuple[str, str]]:
    """('siir'|'duz', metin) sırası. Şiir dizesi birleştirilmez."""
    if "<poem>" not in viki.lower():
        govde = sablon_govde(viki, "söz")
        if govde and govde.strip():
            return [("siir", siir_temiz(govde))]
    parcalar: list[tuple[str, str]] = []
    kalan = viki
    while True:
        m = re.search(r"<poem>(.*?)</poem>", kalan, flags=re.S | re.I)
        if not m:
            for p in duz_parcalar(kalan):
                parcalar.append(("duz", p))
            break
        for p in duz_parcalar(kalan[: m.start()]):
            parcalar.append(("duz", p))
        siir = siir_temiz(m.group(1))
        if siir.strip():
            parcalar.append(("siir", siir))
        kalan = kalan[m.end() :]
    return numara_ekle(parcalar)


def numara_ekle(parcalar: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Kıta numarası (1–10) bir sonraki şiirin başına yazılır."""
    sonuc: list[tuple[str, str]] = []
    i = 0
    while i < len(parcalar):
        tur, metin = parcalar[i]
        if (
            tur == "duz"
            and re.fullmatch(r"\d{1,2}", metin.strip())
            and i + 1 < len(parcalar)
            and parcalar[i + 1][0] == "siir"
        ):
            sonuc.append(("siir", metin.strip() + "\n\n" + parcalar[i + 1][1]))
            i += 2
            continue
        sonuc.append((tur, metin))
        i += 1
    return sonuc


def baslik_esit(a: str, b: str) -> bool:
    def sade(x: str) -> str:
        x = tr_lower(re.sub(r"[^\wÂâÎîÛûÇçĞğİıÖöŞşÜü]+", "", x, flags=re.UNICODE))
        return x

    return sade(a) == sade(b) and bool(sade(a))


def html_uret(parcalar: list[tuple[str, str]], baslik: str) -> str:
    bloklar = []
    for tur, metin in parcalar:
        if tur == "duz" and baslik_esit(metin, baslik):
            continue
        if tur == "siir":
            satirlar = [bicim(ln, True) for ln in metin.split("\n")]
            bloklar.append('<pre class="siir">' + "\n".join(satirlar) + "</pre>")
        else:
            sinif = "konusma" if metin.startswith(("–", "—", "- ")) else "duz"
            if metin in {"Mehmed Âkif", "Mehmet Âkif", "Mehmed Akif"}:
                sinif = "ithaf"
            bloklar.append(f'<p class="{sinif}">{bicim(metin, False)}</p>')
    return "\n\n".join(bloklar)


def sayfa_temiz(viki: str) -> str:
    viki = re.sub(r"<noinclude>.*?</noinclude>", "", viki, flags=re.S | re.I)
    viki = re.sub(r"<pagequality\b[^>]*/?>", "", viki, flags=re.I)
    return viki.strip()


def gorunen(metin: str) -> str:
    t = re.sub(r"<[^>]+>", " ", metin)
    t = re.sub(r"\{\{[^}]*\}\}", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def sayfalari_birlestir(parcalar: list[str]) -> str:
    sonuc = ""
    for ham in parcalar:
        parca = sayfa_temiz(ham)
        if not parca:
            continue
        if not sonuc:
            sonuc = parca
            continue
        once = gorunen(sonuc)
        sonra = gorunen(parca)
        devam = False
        if once and sonra:
            if sonra[0].islower() or sonra[0] in "'’\"":
                devam = True
            elif once[-1] not in ".!?…:\"»”":
                devam = True
        if devam:
            sonuc = sonuc.rstrip() + " " + parca.lstrip()
        else:
            sonuc = sonuc.rstrip() + "\n\n" + parca.lstrip()
    return sonuc


def kelime_say(html_metin: str) -> int:
    yalin = re.sub(r"<[^>]+>", " ", html_metin)
    yalin = html.unescape(yalin)
    return len(re.findall(r"\S+", yalin))


def viki_duz(metin: str) -> str:
    # ''{{'}} bitişik kalırsa kesme işareti kalın tırnakla birlikte silinir.
    metin = metin.replace("''{{'}}", "'").replace("{{'}}", "'")
    metin = sablonlari_sil(metin)
    metin = re.sub(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", r"\1", metin)
    metin = re.sub(r"'{2,}", "", metin)
    metin = re.sub(r"<[^>]+>", "", metin)
    metin = html.unescape(metin)
    return re.sub(r"\s+", " ", metin).strip()


def ilk_yayim(viki: str) -> str | None:
    govde = sablon_govde(viki, "eser başlığı") or ""
    notlar = viki_duz(alan(govde, "notlar"))
    if notlar and re.search(r"\b1[89]\d{2}\b|\b20\d{2}\b", notlar):
        if len(notlar) > 280:
            notlar = notlar.split(". ")[0].strip() + "."
        return notlar
    yil = alan(govde, "yıl").strip()
    if re.fullmatch(r"\d{4}", yil):
        return yil
    return None


def harf(s: str) -> str:
    return re.sub(r"[^a-z0-9âîûçğıöşü]", "", tr_lower(s))


def eser_basligi(kayit: dict) -> str:
    """Künyedeki başlık. Yazar sayfasındaki ad, künyedeki kısaltmanın tamamıysa o ad durur."""
    govde = sablon_govde(kayit["wikitext"], "eser başlığı") or ""
    baslik = viki_duz(alan(govde, "başlık"))
    etiket = kayit["etiket"]
    if not baslik:
        return etiket
    nb, ne = harf(baslik), harf(etiket)
    if nb and ne.startswith(nb):
        return etiket
    return baslik


def sayfa_anahtarlari(kayit: dict) -> list[str]:
    w = kayit["wikitext"]
    anahtarlar = []
    for m in re.finditer(r"<pages\b([^>]*?)/?>", w, flags=re.I | re.S):
        et = m.group(1)
        idx = re.search(r'index\s*=\s*"([^"]+)"', et) or re.search(r"index\s*=\s*'([^']+)'", et)
        if not idx:
            idx = re.search(r"index\s*=\s*(\S+)", et)
        if not idx:
            continue
        ad = idx.group(1).strip()
        fr = re.search(r'from\s*=\s*"?(\d+)', et, flags=re.I)
        to = re.search(r'to\s*=\s*"?(\d+)', et, flags=re.I)
        if fr and to:
            for n in range(int(fr.group(1)), int(to.group(1)) + 1):
                anahtarlar.append(f"Sayfa:{ad}/{n}")
        else:
            anahtarlar.append(f"Sayfa:{ad}")
    if not anahtarlar and "#tag:pages" in w:
        m = re.search(r"index=([^|}]+)", w)
        if m:
            anahtarlar.append("Sayfa:" + m.group(1).strip())
    return anahtarlar


def kaynak_url(baslik: str, revid: int) -> str:
    yol = urllib.parse.quote(baslik.replace(" ", "_"), safe="()_")
    return f"https://tr.wikisource.org/wiki/{yol}?oldid={revid}"


def oncekini_sil() -> None:
    works = KOK / "src" / "content" / "works"
    for yol in works.glob("*.json"):
        veri = json.loads(yol.read_text(encoding="utf-8"))
        if veri.get("author") == YAZAR:
            slug = veri["slug"]
            yol.unlink()
            klasor = KOK / "src" / "content" / "chapters" / slug
            if klasor.exists():
                for cocuk in klasor.glob("*"):
                    cocuk.unlink()
                klasor.rmdir()


def main() -> None:
    oncekini_sil()
    sayfalar = json.loads((ONBELLEK / "sayfalar.json").read_text(encoding="utf-8"))
    liste = json.loads((ONBELLEK / "liste.json").read_text(encoding="utf-8"))
    sayfa_ocr = json.loads((ONBELLEK / "sayfa.json").read_text(encoding="utf-8"))
    sira = {"siir": 0, "yazi": 0}
    eklenen = []
    supheli = []
    for oge in liste:
        kayit = sayfalar[oge["hedef"]]
        baslik = eser_basligi(kayit)
        kategori = "siir" if oge["bolum"] == "Şiirleri" else "yazi"
        if kayit["missing"] or not kayit["wikitext"]:
            supheli.append((baslik, "Sayfa yok (kırmızı bağlantı)."))
            continue
        viki = kayit["wikitext"]
        tarama = sayfa_anahtarlari(kayit)
        if tarama:
            parcalar_ham = []
            eksik = []
            for anahtar in tarama:
                bulunan = sayfa_ocr.get(anahtar)
                if not bulunan or bulunan.get("missing") or not bulunan.get("wikitext"):
                    eksik.append(anahtar)
                else:
                    parcalar_ham.append(bulunan["wikitext"])
            if eksik or not parcalar_ham:
                supheli.append(
                    (
                        baslik,
                        "Metin yalnızca tarama gömüsünde (<pages>) ve Sayfa: metni çekilemedi: "
                        + ", ".join(eksik or tarama),
                    )
                )
                continue
            viki_metin = sayfalari_birlestir(parcalar_ham)
        else:
            viki_metin = viki
        parcalar = parcala(viki_metin)
        govde = html_uret(parcalar, baslik)
        sozcuk = kelime_say(govde)
        if sozcuk < 8 or "{{" in govde or "<poem" in govde.lower() or "[[" in govde:
            supheli.append((baslik, f"Metin çıkarılamadı veya çok kısa ({sozcuk} kelime)."))
            continue
        sira[kategori] += 1
        slug = kisa_ad(baslik)
        eklenen.append(
            {
                "baslik": baslik,
                "slug": slug,
                "kategori": kategori,
                "order": sira[kategori],
                "revid": kayit["revid"],
                "sayfa": kayit["title"],
                "url": kaynak_url(kayit["title"], kayit["revid"]),
                "yayim": ilk_yayim(viki),
                "govde": govde,
                "kelime": sozcuk,
                "tur": "şiir" if kategori == "siir" else "yazı",
            }
        )

    slugs = [e["slug"] for e in eklenen]
    if len(slugs) != len(set(slugs)):
        raise SystemExit(f"kısa ad çakışması: {slugs}")

    for eser in eklenen:
        bolum = KOK / "src" / "content" / "chapters" / eser["slug"]
        bolum.mkdir(parents=True, exist_ok=True)
        (bolum / "01.md").write_text(
            "---\n"
            f"title: {json.dumps(eser['baslik'], ensure_ascii=False)}\n"
            f"work: {eser['slug']}\n"
            "order: 1\n"
            "---\n\n"
            f"{eser['govde']}\n",
            encoding="utf-8",
        )
        kayit = {
            "title": eser["baslik"],
            "slug": eser["slug"],
            "author": YAZAR,
            "authorDeathYear": OLUM,
            "translator": "belirtilmemiş",
            "translatorDeathYear": None,
            "country": "turkiye",
            "category": eser["kategori"],
            "order": eser["order"],
            "sourceName": "Vikikaynak",
            "sourceUrl": eser["url"],
            "sourceRevision": eser["revid"],
            "sourceRetrieved": TARIH,
            "originalPublication": eser["yayim"],
            "seri": None,
        }
        (KOK / "src" / "content" / "works" / f"{eser['slug']}.json").write_text(
            json.dumps(kayit, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    siir = sum(1 for e in eklenen if e["tur"] == "şiir")
    yazi = sum(1 for e in eklenen if e["tur"] == "yazı")
    satirlar = [
        "# Mehmet Âkif Ersoy — eklenmeyenler",
        "",
        "Tarama: 29 Ekim 2026. Kaynak: tr.wikisource.org, `Kişi:Mehmet Âkif Ersoy` (sürüm 162078).",
        "Bu dosya site içeriği değildir; `dist/` içine kopyalanmaz.",
        "",
        f"Eklenen: {len(eklenen)} eser ({siir} şiir, {yazi} yazı).",
        "",
        "## Kişi sayfasında olup eser sayılmayan",
        "",
        "- Mehmet Akif Ersoy'u Anma Günü Hakkında Yönetmelik — Hakkında bölümünde. Âkif'in eseri değil.",
        "",
        "## Şüpheli, metni alınmayan",
        "",
    ]
    if not supheli:
        satirlar.append("Kırmızı bağlantı yok. Tarama gömülü sayfaların Sayfa: metni çekilebildiği için onlar da eklendi. Çok kısa veya şablon yüzünden elenen eser yok.")
    else:
        for baslik, neden in supheli:
            satirlar.append(f"- {baslik} — {neden}")
    satirlar.append("")
    (KOK / "icerik-kontrol" / "mehmet-akif-supheli.md").write_text(
        "\n".join(satirlar), encoding="utf-8"
    )
    print(f"EKLENDI {len(eklenen)} siir={siir} yazi={yazi} supheli={len(supheli)}")
    for e in eklenen:
        print(f"  {e['order']:02d} {e['kategori']:5} {e['kelime']:5} {e['baslik']}")


if __name__ == "__main__":
    main()
