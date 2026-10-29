#!/usr/bin/env python3
"""Vikikaynak vikimetnini okuma Markdown'ına çevirir.

Yazar metnini korur. Şablon, kategori ve dipnot başlıkları gibi viki
çerçevesini atar. Satır kaydırmasından bölünmüş ekleri birleştirir.
Vikikaynak kelime açıklamalarını yazar metninden ayrı sözlük notu yapar.
"""

from __future__ import annotations

import html
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "src" / "content" / "chapters"
UA = "SanalbookBot/1.0 (public-domain literary archive)"
API = "https://tr.wikisource.org/w/api.php"

WORKS = [
    {
        "slug": "kasagi",
        "title": "Kaşağı",
        "page": "Kaşağı",
        "order": 1,
    },
    {
        "slug": "forsa",
        "title": "Forsa",
        "page": "Forsa",
        "order": 2,
    },
    {
        "slug": "pembe-incili-kaftan",
        "title": "Pembe İncili Kaftan",
        "page": "Pembe İncili Kaftan",
        "order": 3,
    },
    {
        "slug": "diyet",
        "title": "Diyet",
        "page": "Diyet",
        "order": 4,
    },
    {
        "slug": "bomba",
        "title": "Bomba",
        "page": "Bomba",
        "order": 5,
    },
]

# Vikikaynak <ref> etiketinin böldüğü çekim ekleri. Uzun olan önce.
SUFFIXES = [
    "sını",
    "sini",
    "sunu",
    "sünü",
    "sına",
    "sine",
    "suna",
    "süne",
    "ları",
    "leri",
    "dan",
    "den",
    "tan",
    "ten",
    "sı",
    "si",
    "su",
    "sü",
    "la",
    "le",
    "a",
    "e",
    "ı",
    "i",
    "u",
    "ü",
    "o",
    "ö",
]


def fetch_wikitext(title: str) -> tuple[str, str, str]:
    params = {
        "action": "query",
        "titles": title,
        "prop": "revisions",
        "rvprop": "content|ids|timestamp",
        "rvslots": "main",
        "format": "json",
        "formatversion": "2",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as response:
        import json

        data = json.load(response)
    page = data["query"]["pages"][0]
    rev = page["revisions"][0]
    return rev["slots"]["main"]["content"], str(rev["revid"]), rev["timestamp"]


def strip_frame(text: str) -> str:
    text = re.sub(r"\{\{eser başlığı.*?\n\}\}", "", text, flags=re.S)
    text = re.sub(r"\{\{Osmanlıca\|[^}]+\}\}", "", text)
    text = re.sub(r"\{\{(?:sayfa başı|dipnot|Dipnot|Kaynakça|eser son)[^}]*\}\}", "", text)
    text = re.sub(r"\[\[Kategori:[^\]]+\]\]", "", text)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    cut = re.search(r"^==+\s*(Dipnotlar|Kaynakça)\s*==+", text, flags=re.M)
    if cut:
        text = text[: cut.start()]
    text = re.sub(r"^==+\s*[^=]+==+\s*$", "", text, flags=re.M)
    return text


def is_ellipsis(text: str) -> bool:
    core = text.replace("—", "").strip()
    return bool(core) and all(ch in ".…· " for ch in core)


def ends_sentence(text: str) -> bool:
    stripped = text.rstrip()
    if not stripped:
        return True
    return stripped[-1] in ".!?…:\"»”"


def join_space(left: str, right: str) -> str:
    left = left.rstrip()
    right = right.lstrip()
    if not left:
        return right
    if not right:
        return left
    return f"{left} {right}"


def normalize_dialogue(text: str) -> str:
    text = text.replace("&mdash;", "—")
    text = re.sub(r"^—\s*", "— ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def paragraphs_from_wiki(text: str) -> list[dict]:
    items: list[dict] = []
    buf: dict | None = None

    def flush() -> None:
        nonlocal buf
        if buf and buf["text"].strip():
            items.append(buf)
        buf = None

    for line in text.splitlines():
        raw = line.rstrip()
        stripped = raw.strip()

        if re.fullmatch(r"<center>\s*🙝?\s*🙟?\s*</center>", stripped) or stripped in {
            "<center>🙝🙟</center>",
        }:
            flush()
            items.append({"kind": "break", "text": ""})
            continue

        dedication = re.fullmatch(r"<div[^>]*>(.*?)</div>", stripped)
        if dedication:
            flush()
            inner = re.sub(r"</?small>", "", dedication.group(1))
            inner = inner.replace("''", "").strip()
            items.append({"kind": "dedication", "text": inner})
            continue

        if stripped == "":
            if buf and buf["kind"] == "prose" and not ends_sentence(buf["text"]):
                buf["pending_blank"] = True
            else:
                flush()
            continue

        if stripped == ":":
            if buf:
                buf["open_wrap"] = True
            continue

        if stripped.startswith(":"):
            content = re.sub(r"^:+", "", stripped).strip()
            if not content:
                if buf:
                    buf["open_wrap"] = True
                continue
            content = normalize_dialogue(content) if content.startswith(("&mdash;", "—")) else content
            if content.startswith("—") or is_ellipsis(content):
                flush()
                buf = {"kind": "speech", "text": content, "open_wrap": False, "pending_blank": False}
                continue
            if buf and (buf.get("open_wrap") or not ends_sentence(buf["text"])):
                buf["text"] = join_space(buf["text"], content)
                buf["open_wrap"] = False
                buf["pending_blank"] = False
                continue
            flush()
            buf = {"kind": "prose", "text": content, "open_wrap": False, "pending_blank": False}
            continue

        if stripped.startswith(("—", "&mdash;")):
            flush()
            buf = {
                "kind": "speech",
                "text": normalize_dialogue(stripped),
                "open_wrap": False,
                "pending_blank": False,
            }
            continue

        if buf and buf["kind"] == "prose" and not buf.get("pending_blank"):
            buf["text"] = join_space(buf["text"], stripped)
            continue

        if buf and buf["kind"] == "prose" and buf.get("pending_blank"):
            if not ends_sentence(buf["text"]) and stripped[:1].islower():
                buf["text"] = join_space(buf["text"], stripped)
                buf["pending_blank"] = False
                continue
            flush()

        if buf:
            flush()
        buf = {"kind": "prose", "text": stripped, "open_wrap": False, "pending_blank": False}

    flush()
    return items


def clean_note(note: str) -> str:
    note = html.unescape(note)
    note = re.sub(r"'''(.+?)'''", r"\1", note)
    note = re.sub(r"''(.+?)''", r"\1", note)
    note = re.sub(r"\)(?=[A-Za-zÇĞİÖŞÜçğıöşü])", ") ", note)
    note = re.sub(r"\s+", " ", note).strip()
    return note


def apply_refs(text: str, notes: list[str]) -> str:
    def repl(match: re.Match[str]) -> str:
        notes.append(clean_note(match.group(1)))
        return f"@@REF{len(notes)}@@"

    return re.sub(r"<ref>(.*?)</ref>", repl, text, flags=re.S)


def wiki_inline(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("&mdash;", "—")
    text = re.sub(r"'''(.+?)'''", r"<strong>\1</strong>", text)
    text = re.sub(r"''(.+?)''", r"<em>\1</em>", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def rejoin_suffixes(text: str) -> str:
    suffix_re = "|".join(re.escape(item) for item in SUFFIXES)
    pattern = re.compile(
        rf"@@REF(\d+)@@\s+({suffix_re})(?=$|[\s,.;:!?…\"»”])"
    )
    return pattern.sub(r"@@REF\1@@\2", text)


def refs_to_html(text: str, slug: str) -> str:
    def repl(match: re.Match[str]) -> str:
        number = match.group(1)
        return (
            f'<sup class="glos"><a href="#not-{slug}-{number}" '
            f'id="ref-{slug}-{number}">{number}</a></sup>'
        )

    return re.sub(r"@@REF(\d+)@@", repl, text)


def render_markdown(slug: str, title: str, items: list[dict]) -> str:
    notes: list[str] = []
    blocks: list[str] = []
    for item in items:
        if item["kind"] == "break":
            blocks.append('<hr class="ayrac" />')
            continue
        if item["kind"] == "dedication":
            dedication = wiki_inline(item["text"])
            blocks.append(f'<p class="ithaf"><em>{dedication}</em></p>')
            continue
        text = apply_refs(item["text"], notes)
        text = wiki_inline(text)
        text = rejoin_suffixes(text)
        text = refs_to_html(text, slug)
        css = "konusma" if item["kind"] == "speech" else "duz"
        blocks.append(f'<p class="{css}">{text}</p>')

    body = "\n\n".join(blocks)
    if notes:
        lis = "\n".join(
            f'<li id="not-{slug}-{index}">{note} <a href="#ref-{slug}-{index}">↑</a></li>'
            for index, note in enumerate(notes, start=1)
        )
        body += f"""

<section class="sozluk">
<h2>Sözlük notları</h2>
<p class="sozluk-aciklama">Bu açıklamalar Vikikaynak aktarımındadır. Yazarın metnine sonradan eklenmiştir; hikâyenin kendisi değildir.</p>
<ol>
{lis}
</ol>
</section>
"""
    frontmatter = f"""---
title: {title}
work: {slug}
order: 1
---

"""
    return frontmatter + body + "\n"


def words(text: str) -> int:
    plain = re.sub(r"<[^>]+>", " ", text)
    plain = re.sub(r"^---.*?---", " ", plain, flags=re.S)
    return len(re.findall(r"\w+", plain, flags=re.UNICODE))


def main() -> None:
    for work in WORKS:
        wikitext, revid, timestamp = fetch_wikitext(work["page"])
        cleaned = strip_frame(wikitext)
        items = paragraphs_from_wiki(cleaned)
        markdown = render_markdown(work["slug"], work["title"], items)
        if "@@REF" in markdown or "{{" in markdown or "<ref>" in markdown or "[[" in markdown:
            raise SystemExit(f"Dönüşüm artığı kaldı: {work['slug']}")
        destination = CHAPTERS / work["slug"] / "01.md"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(markdown, encoding="utf-8")
        print(
            f"{work['slug']}\trev={revid}\t{timestamp}\twords={words(markdown)}\t"
            f"blocks={len(items)}\tfile={destination.relative_to(ROOT)}"
        )


if __name__ == "__main__":
    main()
