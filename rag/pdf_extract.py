from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PageText:
    page_number: int  # 1-based
    text: str


def _extract_with_pdfplumber(pdf_path: Path) -> list[PageText]:
    import pdfplumber

    out: list[PageText] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            txt = page.extract_text() or ""
            out.append(PageText(page_number=i, text=txt))
    return out


def _extract_with_pypdf2(pdf_path: Path) -> list[PageText]:
    from PyPDF2 import PdfReader

    out: list[PageText] = []
    reader = PdfReader(str(pdf_path))
    for i, page in enumerate(reader.pages, start=1):
        txt = page.extract_text() or ""
        out.append(PageText(page_number=i, text=txt))
    return out


def extract_pdf_pages(pdf_path: str | Path) -> list[PageText]:
    p = Path(pdf_path)
    if not p.exists():
        raise FileNotFoundError(str(p))

    # Prefer pdfplumber (often better layout extraction); fallback to PyPDF2.
    try:
        pages = _extract_with_pdfplumber(p)
        if any(pt.text.strip() for pt in pages):
            return pages
    except Exception:
        pass

    return _extract_with_pypdf2(p)

