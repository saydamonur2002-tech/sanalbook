#!/usr/bin/env python3
"""tr.wikisource Kişi sayfalarından ölüm yılı 1955 ve öncesi şairleri ayıklar.

Önbellek /tmp/sair-cache altına yazılır. Metin uydurulmaz.
"""

from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://tr.wikisource.org/w/api.php"
UA = (
    "SanalbookBot/1.0 (public-domain literary archive; "
    "https://sanalbook.saydamonur2002.workers.dev)"
)
CACHE = Path("/tmp/sair-cache")
KOK = Path(__file__).resolve().parents[1]

ATLA_NS = {
    "kategori",
    "dosya",
    "file",
    "şablon",
    "sablon",
    "template",
    "kullanıcı",
    "kullanici",
    "user",
    "dizin",
    "sayfa",
    "media",
    "mediawiki",
    "yardım",
    "yardim",
    "özel",
    "ozel",
    "vikisözlük",
    "w",
    "wikipedia",
    "wikt",
    "q",
    "s",
    "vikipedi",
    "module",
    "modül",
}

ATLA_BASLIK = re.compile(
    r"hakkında|hakkinda|dış bağlantı|dis baglanti|kaynakça|kaynakca|ayrıca|ayrica|"
    r"çeviri|ceviri|kendisine|uyarlan|bkz|notlar|dipnot|galeri|bakınız|bakiniz|"
    r"dışbağ|kategoriler",
    re.I,
)
SIIR_BASLIK = re.compile(
    r"şiir|siir|gazel|kaside|kasîde|türkü|turku|mani|mâni|nefes|ilahi|ilâh|koşma|"
    r"kosma|şarkı|sarki|rubai|rüba|beyit|mesnevi|divan|koşuk|kosuk|destan|varsağı|"
    r"semai|semâi|murabba|muhammes|müseddes|tuyuğ|tuyug|şathiye|nutuk değil",
    re.I,
)
NESIR_BASLIK = re.compile(
    r"roman|hikây|hikay|öykü|oyku|tiyatro|oyunlar|makale|mektup|nesir|düzyaz|"
    r"duzyaz|nutuk|hatıra|hatira|vaaz|deneme|nesirleri|düz yaz",
    re.I,
)


def tr_lower(s: str) -> str:
    return s.replace("İ", "i").replace("I", "ı").lower()


def norm(s: str) -> str:
    tab = str.maketrans(
        {
            "â": "a",
            "î": "i",
            "û": "u",
            "Â": "a",
            "Î": "i",
            "Û": "u",
            "ı": "i",
            "İ": "i",
            "I": "i",
            "ş": "s",
            "Ş": "s",
            "ğ": "g",
            "Ğ": "g",
            "ü": "u",
            "Ü": "u",
            "ö": "o",
            "Ö": "o",
            "ç": "c",
            "Ç": "c",
        }
    )
    s = tr_lower(s).translate(tab)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


class Istek:
    def __init__(self) -> None:
        self.son = 0.0

    def al(self, params: dict) -> dict:
        params = {"format": "json", "formatversion": "2", "maxlag": "5", **params}
        sorgu = urllib.parse.urlencode(params, doseq=True)
        url = API + "?" + sorgu
        for deneme in range(6):
            bekle = 1.05 - (time.monotonic() - self.son)
            if bekle > 0:
                time.sleep(bekle)
            istek = urllib.request.Request(url, headers={"User-Agent": UA})
            try:
                self.son = time.monotonic()
                with urllib.request.urlopen(istek, timeout=60) as yanit:
                    kod = yanit.status
                    govde = yanit.read()
            except urllib.error.HTTPError as hata:
                kod = hata.code
                govde = hata.read()
            if kod in {429, 500, 502, 503, 504}:
                time.sleep(2 ** deneme)
                continue
            veri = json.loads(govde)
            if "error" in veri and veri["error"].get("code") == "maxlag":
                time.sleep(5)
                continue
            return veri
        raise SystemExit(f"API yanıt vermedi: {params.get('action')}")


ISTEK = Istek()


def sablon_govde(metin: str, ad: str) -> str:
    m = re.search(r"\{\{\s*" + re.escape(ad) + r"\b", metin, flags=re.I)
    if not m:
        return ""
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
    return ""


def alanlar(govde: str) -> dict[str, str]:
    """Şablon alanları. \\s eşittir işaretinin satır atlamasını yutmasın."""
    sonuc: dict[str, str] = {}
    metin = govde.replace("\r\n", "\n").replace("\r", "\n")
    if metin.count("\n") < 2 and metin.count("|") > 2:
        parcalar = metin.split("|")
    else:
        parcalar = re.split(r"\n\s*\|", metin)
    for parca in parcalar:
        parca = parca.strip().lstrip("|")
        if "=" not in parca:
            continue
        anahtar, _, deger = parca.partition("=")
        anahtar = tr_lower(anahtar.strip())
        deger = deger.strip()
        if anahtar and anahtar not in sonuc:
            sonuc[anahtar] = deger
    return sonuc


def yil_metin(ham: str) -> tuple[int | None, str]:
    """Kesin miladi yıl ya da belirsizlik nedeni."""
    if not ham or not ham.strip():
        return None, "alan boş"
    duz = re.sub(r"\{\{[^}]*\}\}", " ", ham)
    duz = re.sub(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", r"\1", duz)
    duz = duz.strip()
    k = tr_lower(duz)
    if any(x in k for x in ("yüzyıl", "yuzyil", "yy.", "günümüz", "gunumuz", "bilinmiyor", "yaklaşık", "yaklasik", "civar", "dolay")):
        return None, f"belirsiz: {duz[:80]}"
    if "?" in duz or "？" in duz:
        return None, f"soru işaretli: {duz[:80]}"
    miladi = re.search(r"(?:m\.?\s*|miladi\s*)(\d{3,4})\b", k)
    if miladi:
        yil = int(miladi.group(1))
        if 1 <= yil <= 1955:
            return yil, ""
        if yil >= 1956:
            return yil, ""
    if re.search(r"\bh\.?\s*\d{3,4}\b|hicr[iî]", k) and not re.search(r"miladi|\bm\.?\s*\d{3,4}\b", k):
        return None, f"yalnız hicri: {duz[:80]}"
    yillar = [int(y) for y in re.findall(r"\b(\d{3,4})\b", duz)]
    if len(yillar) == 1:
        return yillar[0], ""
    if len(yillar) > 1:
        return None, f"birden fazla yıl: {duz[:80]}"
    return None, f"yıl yok: {duz[:80]}"


def olum_yili(viki: str, kategoriler: list[str]) -> tuple[int | None, str, str]:
    """(yıl veya None, kaynak, belirsizlik). Yıl 1956+ da döner; eleme sonra."""
    govde = ""
    for ad in ("Kişi", "Kisi", "kişi"):
        govde = sablon_govde(viki, ad)
        if govde:
            break
    if not govde:
        govde = viki[:4000]
    alan = alanlar(govde)
    for anahtar in ("ölümyılı", "olumyili", "ölüm yılı", "ölüm tarihi", "ölüm", "death"):
        if anahtar in alan and alan[anahtar]:
            yil, neden = yil_metin(alan[anahtar])
            if yil:
                return yil, anahtar, ""
            if neden and neden != "alan boş":
                # tarih aralığı: 1483-1556
                aralik = re.findall(r"\b(\d{3,4})\b", alan[anahtar])
                if len(aralik) == 2 and "yüzyıl" not in tr_lower(alan[anahtar]) and "?" not in alan[anahtar]:
                    return int(aralik[-1]), anahtar + " aralığı", ""
                return None, anahtar, neden
    if "tarih" in alan and re.search(r"\d{3,4}\s*[-–—]\s*\d{3,4}", alan["tarih"]):
        yillar = re.findall(r"\b(\d{3,4})\b", alan["tarih"])
        if "?" not in alan["tarih"] and "yüzyıl" not in tr_lower(alan["tarih"]):
            return int(yillar[-1]), "tarih aralığı", ""
    kat_yil = []
    for kat in kategoriler:
        m = re.search(r"(\d{3,4})\s*(?:yılında|yılı'|de|te|'de|'te|'da|'ta)\s*ölen", tr_lower(kat))
        if not m:
            m = re.search(r"(\d{3,4}) yılında ölen", kat)
        if m:
            kat_yil.append(int(m.group(1)))
    kat_yil = sorted(set(kat_yil))
    if len(kat_yil) == 1:
        return kat_yil[0], "kategori", ""
    if len(kat_yil) > 1:
        return None, "kategori", f"çelişen kategoriler: {kat_yil}"
    return None, "", "ölüm yılı alanı yok"


def ns_mi(hedef: str) -> bool:
    if ":" not in hedef:
        return False
    onek = tr_lower(hedef.split(":", 1)[0].strip())
    return onek in ATLA_NS or onek.startswith("w")


def baglantilar(viki: str) -> list[dict]:
    bolum = "giriş"
    sonuc = []
    gorulen = set()
    for satir in viki.splitlines():
        bas = re.match(r"^(=+)\s*(.+?)\s*\1\s*$", satir.strip())
        if bas:
            bolum = bas.group(2).strip()
            continue
        if "{{" in satir and not satir.strip().startswith(("*", "#")):
            continue
        aday = False
        if satir.strip().startswith(("*", "#")):
            aday = True
        elif re.fullmatch(r"\s*\[\[[^\]]+\]\]\s*", satir):
            aday = True
        if not aday:
            continue
        for m in re.finditer(r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]", satir):
            hedef = m.group(1).strip().replace("_", " ")
            if not hedef or ns_mi(hedef):
                continue
            if hedef.startswith("#"):
                continue
            etiket = (m.group(2) or hedef).strip()
            anahtar = hedef
            if anahtar in gorulen:
                continue
            gorulen.add(anahtar)
            sonuc.append({"hedef": hedef, "etiket": etiket, "bolum": bolum})
    return sonuc


def sair_sinyali(viki: str, kategoriler: list[str], baglar: list[dict]) -> list[str]:
    nedenler = []
    for kat in kategoriler:
        if re.search(r"şair|ozan|âşık|aşık|halk edebiyat|divan edebiyat|tasavvuf", tr_lower(kat)):
            nedenler.append(f"kategori: {kat}")
            break
    govde = ""
    for ad in ("Kişi", "Kisi"):
        govde = sablon_govde(viki, ad)
        if govde:
            break
    alan = alanlar(govde) if govde else {}
    for anahtar in ("meslek", "mesleği", "uğraş", "uğraşı", "tanım", "açıklama"):
        deger = alan.get(anahtar, "")
        if re.search(r"şair|ozan|âşık|aşık", tr_lower(deger)):
            nedenler.append(f"{anahtar}: {deger[:80]}")
    giris = viki.split("\n==", 1)[0]
    if re.search(r"şair|şâir|ozan|âşık|aşık", tr_lower(giris)):
        nedenler.append("girişte şair/ozan/âşık")
    for bag in baglar:
        if SIIR_BASLIK.search(bag["bolum"]) and not NESIR_BASLIK.search(bag["bolum"]):
            nedenler.append(f"bölüm: {bag['bolum']}")
            break
    return nedenler


def sitedekiler() -> list[str]:
    works = KOK / "src" / "content" / "works"
    adlar = set()
    for yol in works.glob("*.json"):
        veri = json.loads(yol.read_text(encoding="utf-8"))
        adlar.add(veri.get("author") or "")
    return sorted(adlar)


def sitede_var(ad: str, sitede: list[str]) -> str | None:
    na = set(norm(ad).split())
    for mevcut in sitede:
        nb = set(norm(mevcut).split())
        if not na or not nb:
            continue
        if na == nb:
            return mevcut
        kisa, uzun = (na, nb) if len(na) <= len(nb) else (nb, na)
        if len(kisa) >= 2 and kisa <= uzun:
            return mevcut
    return None


def tum_kisiler() -> list[dict]:
    sayfalar = []
    devam = None
    while True:
        params = {
            "action": "query",
            "list": "allpages",
            "apnamespace": "100",
            "aplimit": "500",
            "apfilterredir": "nonredirects",
        }
        if devam:
            params["apcontinue"] = devam
        veri = ISTEK.al(params)
        sayfalar.extend(veri["query"]["allpages"])
        devam = veri.get("continue", {}).get("apcontinue")
        if not devam:
            break
    return sayfalar


def icerik_cek(basliklar: list[str]) -> dict[str, dict]:
    sonuc: dict[str, dict] = {}
    for i in range(0, len(basliklar), 15):
        parca = basliklar[i : i + 15]
        veri = ISTEK.al(
            {
                "action": "query",
                "prop": "revisions|categories",
                "rvprop": "content|ids",
                "rvslots": "main",
                "cllimit": "max",
                "titles": "|".join(parca),
            }
        )
        for sayfa in veri["query"]["pages"]:
            if sayfa.get("missing"):
                sonuc[sayfa["title"]] = {"missing": True, "title": sayfa["title"]}
                continue
            rev = (sayfa.get("revisions") or [{}])[0]
            slot = (rev.get("slots") or {}).get("main") or {}
            kategoriler = [c["title"].split(":", 1)[-1] for c in sayfa.get("categories") or []]
            sonuc[sayfa["title"]] = {
                "missing": False,
                "title": sayfa["title"],
                "pageid": sayfa.get("pageid"),
                "revid": rev.get("revid"),
                "wikitext": slot.get("content") or "",
                "kategoriler": kategoriler,
            }
        print(f"  kişi {min(i + 15, len(basliklar))}/{len(basliklar)}", flush=True)
    return sonuc


def ozet_yaz(sayfalar: dict) -> None:
    sitede = sitedekiler()
    ozet = []
    for baslik, sayfa in sayfalar.items():
        if sayfa.get("missing"):
            continue
        ad = baslik.split(":", 1)[-1]
        viki = sayfa.get("wikitext") or ""
        kat = sayfa.get("kategoriler") or []
        yil, kaynak, belirsiz = olum_yili(viki, kat)
        baglar = baglantilar(viki)
        sinyaller = sair_sinyali(viki, kat, baglar)
        ozet.append(
            {
                "ad": ad,
                "baslik": baslik,
                "revid": sayfa.get("revid"),
                "yil": yil,
                "yil_kaynak": kaynak,
                "belirsiz": belirsiz,
                "sair": bool(sinyaller),
                "sinyaller": sinyaller,
                "sitede": sitede_var(ad, sitede),
                "bag": len(baglar),
                "bolumler": sorted({b["bolum"] for b in baglar}),
            }
        )
    (CACHE / "ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=2), encoding="utf-8")
    sair = [o for o in ozet if o["sair"]]
    kesin = [o for o in sair if isinstance(o["yil"], int) and o["yil"] <= 1955 and not o["sitede"]]
    belirsiz = [o for o in sair if not isinstance(o["yil"], int)]
    yeni = [o for o in sair if isinstance(o["yil"], int) and o["yil"] >= 1956]
    sitede_olan = [o for o in sair if o["sitede"]]
    print(
        f"şair {len(sair)} eklenecek {len(kesin)} belirsiz {len(belirsiz)} "
        f"1956+ {len(yeni)} sitede {len(sitede_olan)} kişi {len(ozet)}"
    )
    for o in sorted(kesin, key=lambda x: (-(x["bag"]), x["ad"])):
        print(f"  {o['yil']} {o['bag']:3} {o['ad']}")


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    hazir = CACHE / "kisi-sayfalar.json"
    if hazir.exists() and "--yeniden" not in __import__("sys").argv:
        print("önbellekten", flush=True)
        ozet_yaz(json.loads(hazir.read_text(encoding="utf-8")))
        return
    print("Kişi listesi", flush=True)
    liste = tum_kisiler()
    (CACHE / "kisi-liste.json").write_text(
        json.dumps(liste, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  {len(liste)} sayfa", flush=True)
    basliklar = [s["title"] for s in liste]
    print("Kişi metinleri", flush=True)
    sayfalar = icerik_cek(basliklar)
    (CACHE / "kisi-sayfalar.json").write_text(
        json.dumps(sayfalar, ensure_ascii=False), encoding="utf-8"
    )
    ozet_yaz(sayfalar)


if __name__ == "__main__":
    main()
