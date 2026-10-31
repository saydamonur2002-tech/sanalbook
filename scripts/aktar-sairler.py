#!/usr/bin/env python3
"""Ölüm yılı 1955 ve öncesi, sitede olmayan şairlerin şiirlerini yazar.

Kelime değiştirilmez. Nesir, sadeleştirme ve başkasının çevirisi eklenmez.
Ölüm yılı kesin değilse kişi atlanır. Önbellek: /tmp/sair-cache
"""

from __future__ import annotations

import html
import importlib.util
import json
import re
import urllib.parse
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
CACHE = Path("/tmp/sair-cache")
TARIH = "2026-10-30"

spec = importlib.util.spec_from_file_location("kesfet", KOK / "scripts" / "kesfet-sairler.py")
kesfet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kesfet)

spec2 = importlib.util.spec_from_file_location("toplu", KOK / "scripts" / "aktar-toplu-yazarlar.py")
toplu = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(toplu)
akif = toplu.akif

ATLA = re.compile(
    r"hakkında|hakkinda|dış bağlantı|kaynakça|kaynakca|ayrıca|çeviri|uyarlan|"
    r"kendisine|galeri|bakınız|kategori",
    re.I,
)
NESIR = re.compile(
    r"roman|hikây|hikay|öykü|tiyatro|oyun|makale|mektup|nesir|düzyaz|duzyaz|"
    r"nutuk|hatıra|vaaz|deneme|düz yaz|mensur|inşa",
    re.I,
)
HUKUK = re.compile(
    r"ferman|kanun|hatt-ı|hattı hümayun|yasakname|berat|ahid|antlaşma|"
    r"genelge|tezkere|lâyiha|layiha|hutbe|buyruk|nizamname|nizamnâme",
    re.I,
)
SIIR_BOLUM = re.compile(
    r"şiir|gazel|kaside|kasîde|türkü|mani|mâni|nefes|ilahi|ilâh|koşma|"
    r"şarkı|rubai|rüba|beyit|mesnevi|divan|varsağ|semai|semâi|murabba|"
    r"muhammes|tuyuğ|manzum|güfte|kıt'a|kıta|müstezat|terkib|terci",
    re.I,
)
YABANCI = re.compile(
    r"fransız|ingiliz|irlandalı|alman|rus |japon|yunan|amerikalı|ispanyol|"
    r"italyan|isveç|norveç|polony|macar |ermen|arap |fars |hint |gürcü|"
    r"bulgar|sırp|çinli|latin şair",
    re.I,
)
TURK = re.compile(r"türk|osmanlı|azer|kazak|uygur|tatar|türkmen|kırgız|özbek|çağatay", re.I)


def tr_lower(s: str) -> str:
    return s.replace("İ", "i").replace("I", "ı").lower()


def norm(s: str) -> str:
    return kesfet.norm(s)


def yabanci_mi(kategoriler: list[str], viki: str) -> bool:
    govde = kesfet.sablon_govde(viki, "Kişi") or ""
    alan = kesfet.alanlar(govde)
    metin = " ".join(kategoriler) + " " + alan.get("açıklamalar", "")
    if TURK.search(metin):
        return False
    return bool(YABANCI.search(metin))


def seri_ad(satir: str) -> str | None:
    m = re.search(r"''([^']+)''", satir)
    ad = m.group(1) if m else re.sub(r"^\*+\s*", "", satir)
    ad = re.sub(r"\([^)]*\)", "", ad)
    ad = re.sub(r"'{2,}", "", ad).strip(" *'\"")
    ad = re.sub(r"\s+", " ", ad).strip()
    if not ad or len(ad) > 80:
        return None
    return ad


def yil_parantez(satir: str) -> int | None:
    m = re.search(r"\((1[0-9]{3}|20[0-9]{2})\)", satir)
    return int(m.group(1)) if m else None


def aday_listesi(viki: str) -> list[dict]:
    bolum = "giriş"
    seri = None
    seri_yil = None
    sonuc = []
    gorulen = set()
    for satir in viki.splitlines():
        bas = re.match(r"^(=+)\s*(.+?)\s*\1\s*$", satir.strip())
        if bas:
            bolum = bas.group(2).strip()
            seri = None
            seri_yil = None
            continue
        bolum_k = tr_lower(bolum)
        if ATLA.search(bolum_k) or NESIR.search(bolum_k) or HUKUK.search(bolum_k):
            continue
        duz = satir.strip()
        if duz.startswith("*") and not duz.startswith("**") and "[[" not in duz and "''" in duz:
            seri = seri_ad(duz)
            seri_yil = yil_parantez(duz)
            continue
        if "{{" in satir and not duz.startswith(("*", "#")):
            continue
        if not (duz.startswith(("*", "#")) or re.fullmatch(r"\[\[[^\]]+\]\]", duz)):
            continue
        if duz.startswith("*") and not duz.startswith("**"):
            # Üst düzey bağlantı bir kitap değilse seri sıfırlanır.
            if "''" not in duz:
                seri = None
                seri_yil = None
        for m in re.finditer(r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]", satir):
            hedef = m.group(1).strip().replace("_", " ")
            if not hedef or hedef.startswith("#") or kesfet.ns_mi(hedef):
                continue
            if hedef in gorulen:
                continue
            gorulen.add(hedef)
            etiket = re.sub(r"\s+", " ", (m.group(2) or hedef).strip())
            sonuc.append(
                {
                    "hedef": hedef,
                    "etiket": etiket,
                    "bolum": bolum,
                    "seri": seri,
                    "seri_yil": seri_yil,
                }
            )
    return sonuc


def kisiler() -> list[dict]:
    sayfalar = json.loads((CACHE / "kisi-sayfalar.json").read_text(encoding="utf-8"))
    sitede = kesfet.sitedekiler()
    cikti = []
    for baslik, sayfa in sayfalar.items():
        if sayfa.get("missing"):
            continue
        ad = baslik.split(":", 1)[-1]
        viki = sayfa.get("wikitext") or ""
        kat = sayfa.get("kategoriler") or []
        yil, kaynak, belirsiz = kesfet.olum_yili(viki, kat)
        baglar = aday_listesi(viki)
        sinyaller = kesfet.sair_sinyali(viki, kat, kesfet.baglantilar(viki))
        siir_bag = any(SIIR_BOLUM.search(b["hedef"] + " " + b["bolum"] + " " + b["etiket"]) for b in baglar)
        sair = bool(sinyaller) or siir_bag or ad in {"Yusuf Has Hacib", "Şeref Hanım"}
        cikti.append(
            {
                "ad": ad,
                "baslik": baslik,
                "revid": sayfa.get("revid"),
                "yil": yil,
                "yil_kaynak": kaynak,
                "belirsiz": belirsiz,
                "sair": sair,
                "sinyaller": sinyaller,
                "sitede": kesfet.sitede_var(ad, sitede),
                "yabanci": yabanci_mi(kat, viki),
                "baglar": baglar,
            }
        )
    return cikti


def secilecek(kayitlar: list[dict]) -> list[dict]:
    sonuc = []
    for k in kayitlar:
        if not k["sair"] or k["sitede"] or k["yabanci"]:
            continue
        if not isinstance(k["yil"], int) or k["yil"] > 1955 or k["yil"] < 1:
            continue
        sonuc.append(k)
    sonuc.sort(key=lambda k: (-len(k["baglar"]), k["ad"]))
    return sonuc


def parcalara(ogeler: list, n: int):
    for i in range(0, len(ogeler), n):
        yield ogeler[i : i + n]


def sayfa_kaydi(sayfa: dict) -> dict:
    if sayfa.get("missing"):
        return {"missing": True, "title": sayfa.get("title"), "wikitext": "", "revid": None}
    rev = (sayfa.get("revisions") or [{}])[0]
    slot = (rev.get("slots") or {}).get("main") or {}
    return {
        "missing": False,
        "title": sayfa.get("title"),
        "revid": rev.get("revid"),
        "wikitext": slot.get("content") or "",
    }


def cek(basliklar: list[str], havuz: dict) -> None:
    eksik = []
    for baslik in basliklar:
        if baslik not in havuz:
            eksik.append(baslik)
    eksik = list(dict.fromkeys(eksik))
    for i, parca in enumerate(parcalara(eksik, 12)):
        veri = kesfet.ISTEK.al(
            {
                "action": "query",
                "prop": "revisions",
                "rvprop": "content|ids",
                "rvslots": "main",
                "redirects": "1",
                "titles": "|".join(parca),
            }
        )
        sorgu = veri.get("query") or {}
        yon = {r["from"]: r["to"] for r in sorgu.get("redirects") or []}
        normal = {n["from"]: n["to"] for n in sorgu.get("normalized") or []}
        sayfalar = {s["title"]: s for s in sorgu.get("pages") or []}
        for istenen in parca:
            ad = yon.get(istenen, normal.get(istenen, istenen))
            ad = yon.get(ad, ad)
            bulunan = sayfalar.get(ad) or sayfalar.get(istenen)
            if not bulunan:
                havuz[istenen] = {"missing": True, "title": istenen, "wikitext": "", "revid": None}
                continue
            kayit = sayfa_kaydi(bulunan)
            havuz[istenen] = kayit
            if kayit.get("title"):
                havuz[kayit["title"]] = kayit
        print(f"  eser {min((i + 1) * 12, len(eksik))}/{len(eksik)}", flush=True)


def alt_baglar(viki: str, sayfa_baslik: str) -> list[dict]:
    sonuc = []
    gorulen = set()
    for m in re.finditer(r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]", viki):
        hedef = m.group(1).strip().replace("_", " ")
        if hedef.startswith("/"):
            hedef = f"{sayfa_baslik}{hedef}"
        elif hedef.startswith(sayfa_baslik + "/"):
            pass
        else:
            continue
        if kesfet.ns_mi(hedef) or hedef in gorulen:
            continue
        gorulen.add(hedef)
        etiket = (m.group(2) or hedef.split("/")[-1]).strip()
        etiket = re.sub(r"^/", "", etiket)
        sonuc.append({"hedef": hedef, "etiket": etiket})
    return sonuc


def indeks_mi(viki: str, sayfa_baslik: str) -> bool:
    if len(alt_baglar(viki, sayfa_baslik)) < 3:
        return False
    if "<poem>" in viki.lower():
        return False
    kolon = sum(1 for ln in viki.splitlines() if ln.strip().startswith(":"))
    return kolon < 4


def sablon_alan(viki: str) -> dict[str, str]:
    govde = ""
    for ad in ("eser başlığı", "eser", "Eser başlık"):
        govde = akif.sablon_govde(viki, ad)
        if govde:
            break
    return kesfet.alanlar(govde) if govde else {}


def cevirmen(viki: str) -> str | None:
    alan = sablon_alan(viki)
    for ad in ("çevirmen", "mütercim", "aktaran", "çeviren", "sadeleştiren"):
        deger = toplu.akif.viki_duz(alan.get(ad, ""))
        if not deger or tr_lower(deger) in {"yok", "?", "-", "—"} or len(deger) > 80:
            continue
        return deger
    govde = " ".join(alan.values())
    if re.search(r"çevirmen\s*=\s*\[\[Kullanıcı:", viki, flags=re.I):
        return "Vikikaynak kullanıcısı"
    if "kullanıcı:" in tr_lower(govde):
        return "Vikikaynak kullanıcısı"
    return None


def sade_mi(viki: str) -> bool:
    alan = sablon_alan(viki)
    k = tr_lower(" ".join(alan.values()) + "\n" + "\n".join(viki.splitlines()[:12]))
    return any(x in k for x in ("sadeleştiren", "sadeleştirme", "sadeleştirilmiş", "günümüz türkçesi", "güncelleştir"))


def baslik_sec(viki: str, etiket: str, yazar: str) -> str:
    alan = sablon_alan(viki)
    baslik = toplu.akif.viki_duz(alan.get("başlık", ""))
    if not baslik or baslik in {"{{PAGENAME}}", "PAGENAME"} or baslik.startswith("[["):
        baslik = etiket
    baslik = re.sub(r"\s+", " ", baslik).strip()
    m = re.match(r"^(.*?)\s*\(([^)]+)\)\s*$", baslik)
    if m and (norm(m.group(2)) in norm(yazar) or norm(yazar) in norm(m.group(2))):
        baslik = m.group(1).strip()
    return baslik or etiket


def kolon_siir(viki: str) -> str | None:
    if "<poem>" in viki.lower():
        return None
    satirlar: list[str] = []
    basladi = False
    for ln in viki.splitlines():
        if re.match(r"^\s*:", ln):
            basladi = True
            satirlar.append(re.sub(r"^\s*:+", "", ln).rstrip())
        elif basladi and not ln.strip():
            satirlar.append("")
        elif basladi and (ln.strip().startswith(("==", "[[Kategori", "{{Kategori")) or tr_lower(ln.strip()).startswith("kategori:")):
            break
        elif basladi and ln.strip() and not ln.strip().startswith(("{", "|", "<")):
            break
    while satirlar and not satirlar[0].strip():
        satirlar.pop(0)
    while satirlar and not satirlar[-1].strip():
        satirlar.pop()
    dolu = [s for s in satirlar if s.strip()]
    if len(dolu) < 4:
        return None
    return "<poem>\n" + "\n".join(satirlar) + "\n</poem>"


def dipnotlar(viki: str) -> dict[str, str]:
    notlar: dict[str, str] = {}
    m = re.search(r"==+\s*Dipnotlar\s*==+\s*(.*?)(?:\n==+|\Z)", viki, flags=re.S | re.I)
    if m:
        for numara, metin in re.findall(r"^\((\d+)\)\s+(.+)$", m.group(1), flags=re.M):
            metin = toplu.akif.viki_duz(metin)
            if metin:
                notlar[numara] = metin
    for i, metin in enumerate(re.findall(r"<ref\b[^>]*>(.*?)</ref>", viki, flags=re.S | re.I), start=1):
        temiz = toplu.akif.viki_duz(metin)
        if temiz:
            while str(i) in notlar:
                i += 1
            notlar[str(i)] = temiz
    return notlar


def dipnot_isaret(viki: str, notlar: dict[str, str]) -> str:
    def degistir(m: re.Match[str]) -> str:
        n = m.group(1)
        if n in notlar:
            return f"§N{n}§"
        return m.group(0)

    return re.sub(r"(?<![\wÂâÎîÛûÇçĞğİıÖöŞşÜü])\((\d{1,2})\)", degistir, viki)


def notlar_html(notlar: dict[str, str]) -> str:
    if not notlar:
        return ""
    maddeler = "\n".join(
        f"<li>{toplu.kacis(notlar[n])}</li>" for n in sorted(notlar, key=lambda x: int(x) if x.isdigit() else 0)
    )
    return f'\n\n<section class="sozluk">\n<h2>Notlar</h2>\n<ol>\n{maddeler}\n</ol>\n</section>'


def latin_yazi(metin: str) -> bool:
    duz = html.unescape(re.sub(r"<[^>]+>", " ", metin))
    return bool(re.search(r"[A-Za-zÇĞİÖŞÜçğıöşüÂâÎîÛû]", duz))


def govde_uret(viki: str, baslik: str) -> str:
    viki = toplu.kes_sade(viki)
    notlar = dipnotlar(viki)
    viki = re.sub(r"==+\s*Dipnotlar\s*==+.*?(?=\n==+|\Z)", "", viki, flags=re.S | re.I)
    viki = re.sub(r"<ref\b[^>]*>.*?</ref>", "", viki, flags=re.S | re.I)
    viki = re.sub(r"<ref\b[^>]*/>", "", viki, flags=re.I)
    viki = dipnot_isaret(viki, notlar)
    kolon = kolon_siir(viki)
    if kolon:
        # Künye şablonu durur; şiir kolonları poem içine alınır.
        viki = re.sub(r"(?m)^\s*:.*(?:\n|$)", "", viki)
        viki = viki.rstrip() + "\n" + kolon
    uretilen = toplu.html_wiki(viki, baslik)
    uretilen = re.sub(r"§N(\d+)§", r"(\1)", uretilen)
    if notlar:
        uretilen += notlar_html(notlar)
    return uretilen.strip()


def siir_mi(html_metin: str) -> bool:
    if '<pre class="siir">' not in html_metin:
        return False
    return toplu.kelime(html_metin) >= 4


def url(baslik: str, revid: int) -> str:
    yol = urllib.parse.quote(baslik.replace(" ", "_"), safe="()_/")
    return f"https://tr.wikisource.org/wiki/{yol}?oldid={revid}"


def kisa(baslik: str) -> str:
    return akif.kisa_ad(baslik) or "siir"


def mevcut_slug() -> set[str]:
    return {p.stem for p in (KOK / "src" / "content" / "works").glob("*.json")}


def max_sira() -> int:
    en = 0
    for yol in (KOK / "src" / "content" / "works").glob("*.json"):
        veri = json.loads(yol.read_text(encoding="utf-8"))
        if veri.get("category") == "siir":
            en = max(en, int(veri.get("order") or 0))
    return en


def benzersiz(slug: str, yazar: str, kullanilan: set[str]) -> str:
    if slug not in kullanilan:
        kullanilan.add(slug)
        return slug
    ek = kisa(yazar)
    aday = f"{slug}-{ek}" if ek and not slug.endswith(ek) else slug
    n = 2
    while aday in kullanilan:
        aday = f"{slug}-{ek}-{n}" if ek else f"{slug}-{n}"
        n += 1
    kullanilan.add(aday)
    return aday


def yil_eser(viki: str, seri_yil: int | None, olum: int) -> int | None:
    return toplu.yil_bul(viki, seri_yil, olum)


def yaz(kayitlar: list[dict], havuz: dict) -> None:
    slugs = mevcut_slug()
    sira = max_sira()
    eklenen = []
    supheli: list[tuple[str, str, str]] = []
    kullanilan_hedef: dict[str, str] = {}

    def isle(kisi: dict, oge: dict, seri: str | None) -> None:
        nonlocal sira
        hedef = oge["hedef"]
        kayit = havuz.get(hedef)
        if not kayit or kayit.get("missing") or not kayit.get("wikitext"):
            supheli.append((kisi["ad"], oge.get("etiket") or hedef, "Sayfa yok (kırmızı bağlantı)."))
            return
        gercek = kayit["title"]
        if gercek in kullanilan_hedef:
            supheli.append((kisi["ad"], oge.get("etiket") or gercek, f"Aynı sayfa {kullanilan_hedef[gercek]} adına eklendi."))
            return
        viki = kayit["wikitext"]
        if viki.lstrip().upper().startswith("#YÖNLENDİRME") or viki.lstrip().upper().startswith("#REDIRECT"):
            supheli.append((kisi["ad"], gercek, "Yönlendirme çözülemedi."))
            return
        if indeks_mi(viki, gercek):
            alt = alt_baglar(viki, gercek)
            basliklar = [a["hedef"] for a in alt]
            cek(basliklar, havuz)
            for a in alt:
                a["seri_yil"] = oge.get("seri_yil")
                isle(kisi, a, seri or oge.get("etiket") or gercek.split("/")[-1])
            return
        if cevirmen(viki):
            supheli.append((kisi["ad"], oge.get("etiket") or gercek, f"Başkasının çevirisi ({cevirmen(viki)})."))
            return
        if sade_mi(viki):
            supheli.append((kisi["ad"], oge.get("etiket") or gercek, "Sadeleştirme veya günümüz Türkçesi ibaresi var."))
            return
        baslik = baslik_sec(viki, oge.get("etiket") or gercek.split("/")[-1], kisi["ad"])
        govde = govde_uret(viki, baslik)
        if not latin_yazi(govde):
            supheli.append((kisi["ad"], baslik, "Latin aktarımı yok."))
            return
        if not siir_mi(govde):
            supheli.append((kisi["ad"], baslik, "Şiir değil veya metin çıkmadı (nesir/kısa)."))
            return
        if "{{" in govde or "[[" in govde or "<poem" in govde.lower() or "pagequality" in govde.lower():
            supheli.append((kisi["ad"], baslik, "Viki kalıntısı kaldı, eklenmedi."))
            return
        yil = yil_eser(viki, oge.get("seri_yil"), kisi["yil"])
        latin = yil is not None and yil >= 1929
        slug = benzersiz(kisa(baslik), kisi["ad"], slugs)
        sira += 1
        kullanilan_hedef[gercek] = kisi["ad"]
        eklenen.append(
            {
                "yazar": kisi["ad"],
                "olum": kisi["yil"],
                "baslik": baslik,
                "slug": slug,
                "order": sira,
                "revid": kayit["revid"],
                "sayfa": gercek,
                "url": url(gercek, kayit["revid"]),
                "yayim": toplu.ilk_yayim(viki),
                "seri": seri or oge.get("seri"),
                "latin": latin,
                "govde": govde,
                "kelime": toplu.kelime(govde),
            }
        )

    for kisi in kayitlar:
        print(f"yaz {kisi['ad']} ({len(kisi['baglar'])})", flush=True)
        for oge in kisi["baglar"]:
            isle(kisi, oge, oge.get("seri"))

    # Önceki yarım kalmış çıktıyı bu yazarlar için sil.
    yazarlar = {k["ad"] for k in kayitlar}
    for yol in (KOK / "src" / "content" / "works").glob("*.json"):
        veri = json.loads(yol.read_text(encoding="utf-8"))
        if veri.get("author") in yazarlar and veri.get("sourceRetrieved") == TARIH:
            slug = veri["slug"]
            yol.unlink()
            klasor = KOK / "src" / "content" / "chapters" / slug
            if klasor.exists():
                for cocuk in klasor.glob("*"):
                    cocuk.unlink()
                klasor.rmdir()

    for eser in eklenen:
        klasor = KOK / "src" / "content" / "chapters" / eser["slug"]
        klasor.mkdir(parents=True, exist_ok=True)
        (klasor / "01.md").write_text(
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
            "author": eser["yazar"],
            "authorDeathYear": eser["olum"],
            "translator": None if eser["latin"] else "belirtilmemiş",
            "translatorDeathYear": None,
            "country": "turkiye",
            "category": "siir",
            "order": eser["order"],
            "sourceName": "Vikikaynak",
            "sourceUrl": eser["url"],
            "sourceRevision": eser["revid"],
            "sourceRetrieved": TARIH,
            "originalPublication": eser["yayim"],
        }
        if eser["seri"]:
            kayit["seri"] = eser["seri"]
        if eser["latin"]:
            kayit["yazim"] = "latin"
        (KOK / "src" / "content" / "works" / f"{eser['slug']}.json").write_text(
            json.dumps(kayit, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    (CACHE / "eklenen.json").write_text(json.dumps(eklenen, ensure_ascii=False), encoding="utf-8")
    (CACHE / "supheli.json").write_text(json.dumps(supheli, ensure_ascii=False), encoding="utf-8")
    print(f"EKLENDI {len(eklenen)} supheli {len(supheli)}")


def dene() -> None:
    havuz: dict = {}
    cek(
        [
            "Bana Seni Gerek Seni",
            "Merdiven",
            "Hürriyet Kasidesi",
            "Kasîde-i Bahâriyye der Hakk-ı Müşâriin-ileyh",
        ],
        havuz,
    )
    for ad in havuz:
        k = havuz[ad]
        if k.get("missing"):
            print("YOK", ad)
            continue
        baslik = baslik_sec(k["wikitext"], ad, "")
        govde = govde_uret(k["wikitext"], baslik)
        print("\n====", ad, "BASLIK", baslik, "SIIR", siir_mi(govde), "KELIME", toplu.kelime(govde))
        print(govde[:500])


def main() -> None:
    import sys

    if "--dene" in sys.argv:
        dene()
        return
    havuz_yol = CACHE / "eser-havuz.json"
    havuz = json.loads(havuz_yol.read_text(encoding="utf-8")) if havuz_yol.exists() else {}
    secim = secilecek(kisiler())
    print(f"şair {len(secim)} bağlantı {sum(len(k['baglar']) for k in secim)}", flush=True)
    (CACHE / "secim.json").write_text(
        json.dumps([{k: v for k, v in s.items() if k != "baglar"} | {"bag": len(s["baglar"])} for s in secim], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    hedefler = [b["hedef"] for s in secim for b in s["baglar"]]
    cek(hedefler, havuz)
    havuz_yol.write_text(json.dumps(havuz, ensure_ascii=False), encoding="utf-8")
    yaz(secim, havuz)
    havuz_yol.write_text(json.dumps(havuz, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
