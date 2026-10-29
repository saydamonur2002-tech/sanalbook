#!/usr/bin/env python3
"""Bölüm Markdown'ındaki MediaWiki kalıntılarını ayıklar.

Kelime değiştirilmez. <poem> satır sonları ayrı paragraf olur.
'-' ile başlayan diyalog satırları ayrı paragraf olur.
(1) gibi işaretlerin Vikikaynak dipnotu varsa Notlar'a yazılır, yoksa işaret silinir.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
BOLUMLER = KOK / "src" / "content" / "chapters"
ONBELLEK = Path("/tmp/sanalbook-ose-cache")

RAPOR: dict = {
    "isaretler": [],
    "tirnak": [],
    "poem": [],
    "ref": [],
    "diyalog": [],
    "belirsiz": [],
}


def html_kacis(metin: str) -> str:
    return metin.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tirnak_sil(metin: str) -> str:
    return re.sub(r"'{2,}", "", metin)


def dipnot_haritasi(viki: str) -> dict[str, str]:
    eslesme = re.search(r"==\s*Dipnotlar\s*==\s*(.*?)(?:\n==|\Z)", viki, flags=re.S)
    if not eslesme:
        return {}
    bolum = eslesme.group(1)
    notlar = {}
    for numara, metin in re.findall(r"^\((\d+)\)\s+(.+)$", bolum, flags=re.M):
        metin = re.sub(r"\{\{.*?\}\}", "", metin)
        metin = re.sub(r"\[https?://[^\]]+\]", "", metin)
        metin = tirnak_sil(html.unescape(metin)).strip()
        if metin:
            notlar[numara] = metin
    return notlar


def viki_bul(slug: str) -> str:
    works = KOK / "src" / "content" / "works" / f"{slug}.json"
    if not works.exists():
        return ""
    kayit = json.loads(works.read_text(encoding="utf-8"))
    rev = kayit.get("sourceRevision")
    if not ONBELLEK.exists():
        return ""
    for dosya in ONBELLEK.glob("*.json"):
        if dosya.name == "ozet.json":
            continue
        veri = json.loads(dosya.read_text(encoding="utf-8"))
        if veri.get("revid") == rev:
            return veri.get("wikitext") or ""
    return ""


def velinimet_govde() -> str:
    viki = ""
    for dosya in ONBELLEK.glob("*.json"):
        veri = json.loads(dosya.read_text(encoding="utf-8"))
        if veri.get("title") == "Velinimet":
            viki = veri.get("wikitext") or ""
            break
    if not viki:
        raise SystemExit("Velinimet vikimetni önbellekte yok")
    eslesme = re.search(r"<poem>(.*?)</poem>", viki, flags=re.S)
    if not eslesme:
        raise SystemExit("Velinimet poem bulunamadı")
    bloklar = []
    for satir in eslesme.group(1).splitlines():
        duz = tirnak_sil(html.unescape(satir)).strip()
        duz = re.sub(r"\s+", " ", duz)
        if not duz:
            continue
        if duz.startswith("-"):
            konusma = duz[1:].strip()
            bloklar.append(f'<p class="konusma">- {html_kacis(konusma)}</p>')
        else:
            bloklar.append(f'<p class="duz">{html_kacis(duz)}</p>')
    notlar = dipnot_haritasi(viki)
    if notlar:
        maddeler = "\n".join(
            f"<li>{html_kacis(notlar[anahtar])}</li>" for anahtar in sorted(notlar, key=int)
        )
        bloklar.append(
            "<section class=\"sozluk\">\n<h2>Notlar</h2>\n<ol>\n"
            + maddeler
            + "\n</ol>\n</section>"
        )
    return "\n\n".join(bloklar) + "\n"


def diyalog_bol(ic: str) -> list[tuple[str, str]] | None:
    if len(re.findall(r"(?<=\S)\s+-(?=\s*\S)", ic)) < 2:
        return None
    parcalar = re.split(r"(?<=\S)\s+-(?=\s*\S)", ic)
    sonuc = []
    for indeks, parca in enumerate(parcalar):
        parca = parca.strip()
        if not parca:
            continue
        if indeks == 0 and not parca.startswith("-"):
            sonuc.append(("duz", parca))
        else:
            if not parca.startswith("-"):
                parca = "- " + parca.lstrip()
            sonuc.append(("konusma", parca))
    return sonuc


def paragraf_sinifi(ic: str, sinif: str) -> str:
    if ic.lstrip().startswith("-"):
        return "konusma"
    return sinif


def isaretleri_isle(metin: str, slug: str, notlar: dict[str, str]) -> str:
    def degistir(eslesme: re.Match[str]) -> str:
        numara = eslesme.group(1)
        if numara in notlar:
            RAPOR["isaretler"].append(
                {
                    "eser": slug,
                    "isaret": f"({numara})",
                    "islem": "not-eklendi",
                    "not": notlar[numara],
                }
            )
            return eslesme.group(0)
        RAPOR["isaretler"].append(
            {"eser": slug, "isaret": f"({numara})", "islem": "silindi", "not": None}
        )
        return ""

    return re.sub(r"\((\d{1,2})\)", degistir, metin)


def not_bolumu(notlar: dict[str, str], kullanilan: set[str]) -> str:
    secilen = [(n, notlar[n]) for n in sorted(kullanilan, key=int) if n in notlar]
    if not secilen:
        return ""
    maddeler = "\n".join(f"<li>{html_kacis(metin)}</li>" for _, metin in secilen)
    return (
        "\n\n<section class=\"sozluk\">\n<h2>Notlar</h2>\n<ol>\n" + maddeler + "\n</ol>\n</section>\n"
    )


def dosyayi_temizle(yol: Path) -> None:
    slug = yol.parent.name
    ham = yol.read_text(encoding="utf-8")
    if not ham.startswith("---"):
        return
    bitis = ham.find("\n---", 3)
    on = ham[: bitis + 4]
    govde = ham[bitis + 4 :]
    if slug == "velinimet":
        govde = "\n\n" + velinimet_govde()
        RAPOR["poem"].append(slug)
        yol.write_text(on.rstrip() + "\n\n" + govde.lstrip("\n"), encoding="utf-8")
        for numara, metin in dipnot_haritasi(viki_bul(slug)).items():
            RAPOR["isaretler"].append(
                {"eser": slug, "isaret": f"({numara})", "islem": "not-eklendi", "not": metin}
            )
        return

    once = govde
    govde = govde.replace("&lt;poem&gt;", "").replace("&lt;/poem&gt;", "")
    govde = re.sub(r"</?poem>", "", govde, flags=re.I)
    ref_sayisi = len(re.findall(r"<ref\b|&lt;ref", govde, flags=re.I))
    govde = re.sub(r"<ref\b[^>]*>.*?</ref>", "", govde, flags=re.S | re.I)
    govde = re.sub(r"<ref\b[^>]*/\s*>", "", govde, flags=re.I)
    if ref_sayisi:
        RAPOR["ref"].append({"eser": slug, "adet": ref_sayisi})
    if re.search(r"'{2,}", govde):
        RAPOR["tirnak"].append(slug)
    govde = tirnak_sil(govde)

    notlar = dipnot_haritasi(viki_bul(slug))
    yeni_parcalar = []
    for parca in re.split(r"(<p class=\"(?:duz|konusma)\">.*?</p>)", govde, flags=re.S):
        eslesme = re.fullmatch(r"<p class=\"(duz|konusma)\">(.*)</p>", parca, flags=re.S)
        if not eslesme:
            yeni_parcalar.append(parca)
            continue
        sinif, ic = eslesme.group(1), eslesme.group(2).strip()
        if not ic or ic in {"&lt;poem&gt;", "&lt;/poem&gt;"}:
            continue
        bolunen = diyalog_bol(ic)
        if bolunen:
            RAPOR["diyalog"].append(slug)
            yeni_parcalar.append(
                "\n\n".join(f'<p class="{tur}">{metin}</p>' for tur, metin in bolunen)
            )
            continue
        sinif = paragraf_sinifi(ic, sinif)
        yeni_parcalar.append(f'<p class="{sinif}">{ic}</p>')
    govde = "".join(yeni_parcalar)
    govde = re.sub(r"\n{3,}", "\n\n", govde)

    if "<h2>Notlar</h2>" not in govde:
        govde = isaretleri_isle(govde, slug, notlar)
        kullanilan = set(re.findall(r"\((\d{1,2})\)", govde))
        ek = not_bolumu(notlar, kullanilan)
        if ek:
            govde = govde.rstrip() + ek
    yol.write_text(on.rstrip() + "\n\n" + govde.lstrip("\n"), encoding="utf-8")
    if govde != once and slug not in RAPOR["poem"]:
        pass


def yillar() -> None:
    for yol in BOLUMLER.rglob("*.md"):
        metin = yol.read_text(encoding="utf-8")
        for eslesme in re.finditer(r"\((1[0-9]{3}|20[0-9]{2})\)", metin):
            RAPOR["belirsiz"].append(
                {
                    "eser": yol.parent.name,
                    "isaret": eslesme.group(0),
                    "neden": "Dört haneli yıl; dipnot sayılmadı, metinde bırakıldı.",
                }
            )


def main() -> None:
    for yol in sorted(BOLUMLER.rglob("*.md")):
        dosyayi_temizle(yol)
    yillar()
    print(json.dumps(RAPOR, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
