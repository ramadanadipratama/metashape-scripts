#!/usr/bin/env python3
"""Build an ebook in books/<slug>/ into books/<slug>/dist/<slug>.docx.

Stand-in for the `npm run build -- <slug>` step described in the ebook skill:
  python3 tools/build_ebook.py <slug>

Reads book.json (title, subtitle, author, language, chapters[]) and the
chapter Markdown files, adds a title page and a table of contents, numbers the
chapters ("Bab 1: ..."), starts every chapter on a new page and puts page
numbers in the footer. Requires pandoc.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOOTER_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
    '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
    '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
    '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
    '<w:r><w:t>1</w:t></w:r>'
    '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
    '</w:p></w:ftr>'
)


def make_reference_docx(path: Path) -> None:
    """Pandoc's default reference.docx with chapter page breaks and a page-number footer."""
    tmp = path.with_suffix(".tmp.docx")
    subprocess.run(["pandoc", "-o", str(tmp), "--print-default-data-file", "reference.docx"], check=True)
    with zipfile.ZipFile(tmp) as zin, zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/styles.xml":
                s = data.decode("utf-8")
                # Every chapter (Heading 1) starts on a new page.
                s = re.sub(r'(<w:style w:type="paragraph" w:styleId="Heading1">.*?<w:pPr>)',
                           r'\1<w:pageBreakBefore/>', s, count=1, flags=re.S)
                # Character style for English terms: italic + teal.
                s = s.replace("</w:styles>",
                              '<w:style w:type="character" w:customStyle="1" w:styleId="IstilahInggris">'
                              '<w:name w:val="Istilah Inggris"/><w:rPr><w:i/><w:iCs/><w:color w:val="1B7F6E"/></w:rPr>'
                              '</w:style></w:styles>', 1)
                # Character style for abbreviations: bold + black.
                s = s.replace("</w:styles>",
                              '<w:style w:type="character" w:customStyle="1" w:styleId="Singkatan">'
                              '<w:name w:val="Singkatan"/><w:rPr><w:b/><w:bCs/><w:color w:val="000000"/></w:rPr>'
                              '</w:style></w:styles>', 1)
                data = s.encode("utf-8")
            elif item.filename == "word/_rels/document.xml.rels":
                s = data.decode("utf-8").replace(
                    "</Relationships>",
                    '<Relationship Id="rIdFtr1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/></Relationships>')
                data = s.encode("utf-8")
            elif item.filename == "[Content_Types].xml":
                s = data.decode("utf-8").replace(
                    "</Types>",
                    '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>')
                data = s.encode("utf-8")
            elif item.filename == "word/document.xml":
                s = data.decode("utf-8")
                # A4 page, 2,5 cm margins, page number in the footer.
                sect = ('<w:sectPr><w:footerReference w:type="default" r:id="rIdFtr1"/>'
                        '<w:pgSz w:w="11906" w:h="16838"/>'
                        '<w:pgMar w:top="1417" w:right="1417" w:bottom="1417" w:left="1417" '
                        'w:header="709" w:footer="709" w:gutter="0"/></w:sectPr>')
                s = re.sub(r"<w:sectPr\s*/>|<w:sectPr>.*?</w:sectPr>", sect, s, count=1, flags=re.S)
                if 'xmlns:r=' not in s:
                    s = s.replace("<w:document ", '<w:document xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" ', 1)
                data = s.encode("utf-8")
            zout.writestr(item, data)
        zout.writestr("word/footer1.xml", FOOTER_XML)
    tmp.unlink()


def chapter_files(book: Path, meta: dict) -> list:
    if meta.get("chapters"):
        return [book / "chapters" / c for c in meta["chapters"]]
    return sorted((book / "chapters").glob("*.md"), key=lambda p: p.name)


EN_STYLE = "Istilah Inggris"
ABBR_STYLE = "Singkatan"


def load_terms(book: Path, name: str = "english-terms.txt") -> list:
    f = book / name
    if not f.exists():
        return []
    terms = [ln.strip() for ln in f.read_text(encoding="utf-8").splitlines()]
    return sorted({t for t in terms if t and not t.startswith("#")}, key=len, reverse=True)


def style_english(text: str, terms: list, abbrs: list = ()) -> str:
    """Mark English terms (and text already in *italics*) with the "Istilah Inggris" style,
    and abbreviations (outside headings) with the "Singkatan" style."""
    if not terms and not abbrs:
        return text
    keep = []

    def protect(m):
        keep.append(m.group(0))
        return f"\x00{len(keep) - 1}\x00"

    span = lambda t: f'[{t}]{{custom-style="{EN_STYLE}"}}'
    text = re.sub(r"```.*?```", protect, text, flags=re.S)          # code blocks
    text = re.sub(r"`[^`\n]+`", protect, text)                      # inline code
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)(\{[^}]*\})?", protect, text)  # images
    text = re.sub(r"\]\([^)]*\)", protect, text)                   # link targets
    # Text already in *italics* (not **bold**) -> styled span
    def mark(t):
        keep.append(span(t))
        return f"\x00{len(keep) - 1}\x00"

    italic = lambda m: mark(m.group(1))

    text = re.sub(r"(?<!\*)\*(?![\s*])([^*\n]+?)(?<![\s*])\*(?!\*)", italic, text)
    if terms:
        pat = re.compile(r"(?<!\w)(" + "|".join(re.escape(t) for t in terms) + r")(?!\w)", re.I)
        text = pat.sub(lambda m: mark(m.group(1)), text)
    if abbrs:
        ab = re.compile(r"(?<![\w])(" + "|".join(re.escape(t) for t in abbrs) + r")(?![\w])")
        bold = lambda m: f'[{m.group(1)}]{{custom-style="{ABBR_STYLE}"}}'
        text = "\n".join(ln if ln.lstrip().startswith("#") else ab.sub(bold, ln) for ln in text.split("\n"))
    return re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], text)


def compress_image(src: Path, dst_dir: Path) -> Path:
    """Shrink an illustration to a JPEG (max 1600 px wide) so the .docx stays small."""
    try:
        from PIL import Image
    except ImportError:
        return src
    dst = dst_dir / (src.stem + ".jpg")
    with Image.open(src) as im:
        im = im.convert("RGB")
        if im.width > 1600:
            im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
        im.save(dst, "JPEG", quality=85, optimize=True)
    return dst


def build(slug: str) -> Path:
    book = ROOT / "books" / slug
    meta = json.loads((book / "book.json").read_text(encoding="utf-8"))
    files = chapter_files(book, meta)
    if not files:
        sys.exit(f"Tidak ada bab di {book / 'chapters'}")

    parts, toc, missing = [], [], []
    terms = load_terms(book)
    abbrs = load_terms(book, "abbreviations.txt")
    workdir = tempfile.TemporaryDirectory()
    imgdir = Path(workdir.name)
    for n, f in enumerate(files, 1):
        text = f.read_text(encoding="utf-8")
        m = re.match(r"#\s+(.+)", text)
        title = m.group(1).strip() if m else f.stem
        toc.append(f"Bab {n}. {title}")
        text = re.sub(r"^#\s+.+$", f"# Bab {n}: {title}", text, count=1, flags=re.M)

        def img(match):
            alt, rel = match.group(1), match.group(2)
            p = (f.parent / rel).resolve()
            if not p.exists():
                missing.append(rel)
                return ""
            return f"![{alt}]({compress_image(p, imgdir)}){{width=100%}}"

        text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", img, text)
        parts.append(style_english(text, terms, abbrs))

    # Appendices (books/<slug>/appendix/*.md): added after the chapters, not numbered.
    for f in sorted((book / "appendix").glob("*.md"), key=lambda p: p.name):
        text = f.read_text(encoding="utf-8")
        m = re.match(r"#\s+(.+)", text)
        toc.append(None if not m else m.group(1).strip())
        text = re.sub(r"^(#\s+.+)$", r"\1 {.unnumbered}", text, count=1, flags=re.M)
        parts.append(style_english(text, terms, abbrs))

    head = "---\n" + json.dumps({
        "title": meta.get("title", slug),
        "subtitle": meta.get("subtitle", ""),
        "author": meta.get("author", ""),
        "lang": meta.get("language", "id"),
    }, ensure_ascii=False) + "\n---\n\n"
    toc_md = "# Daftar Isi {.unnumbered}\n\n" + "\n".join(f"- {line}" for line in toc if line) + "\n\n"
    md = head + toc_md + "\n\n".join(parts)

    dist = book / "dist"
    dist.mkdir(exist_ok=True)
    out = dist / f"{slug}.docx"
    with tempfile.TemporaryDirectory() as td:
        ref = Path(td) / "reference.docx"
        make_reference_docx(ref)
        src = Path(td) / "book.md"
        src.write_text(md, encoding="utf-8")
        subprocess.run(["pandoc", str(src), "-f", "markdown", "-t", "docx",
                        "--reference-doc", str(ref), "-o", str(out)], check=True)
    workdir.cleanup()
    for rel in missing:
        print(f"Peringatan: gambar tidak ditemukan, dilewati: {rel}")
    print(out)
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Pakai: python3 tools/build_ebook.py <slug>")
    build(sys.argv[1])
