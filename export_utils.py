"""
Utility helpers for exporting generated documents to DOCX and PDF.

The PDF pipeline now uses WeasyPrint to render semantic HTML into
print-quality PDFs that meet European typography and accessibility
expectations.
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from html import escape, unescape
from typing import List, Tuple

import bleach  # type: ignore
from docx import Document  # type: ignore
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT  # type: ignore
from docx.shared import Pt  # type: ignore
from weasyprint import HTML  # type: ignore

__all__ = [
    "export_document",
]


@dataclass
class ExportResult:
    data: bytes
    filename: str
    media_type: str


ALLOWED_HTML_TAGS = [
    "p",
    "br",
    "strong",
    "em",
    "u",
    "ul",
    "ol",
    "li",
    "blockquote",
    "h1",
    "h2",
    "h3",
    "h4",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "hr",
    "span",
]

ALLOWED_HTML_ATTRS = {
    "th": ["colspan", "rowspan", "scope"],
    "td": ["colspan", "rowspan"],
    "table": ["class"],
    "span": ["class"],
}

PDF_BASE_STYLES = """
@page {
  size: A4;
  margin: 25mm 20mm 25mm 20mm;
}
body {
  font-family: "Noto Serif", "Times New Roman", serif;
  font-size: 11pt;
  line-height: 1.55;
  color: #1f2933;
}
h1 {
  font-size: 18pt;
  margin: 0 0 14pt;
  text-align: center;
  font-weight: 600;
  color: #0f172a;
}
h2 {
  font-size: 15pt;
  margin: 18pt 0 8pt;
  color: #0f172a;
}
h3 {
  font-size: 13pt;
  margin: 16pt 0 8pt;
  color: #334155;
}
p {
  margin: 0 0 8pt;
}
ul, ol {
  margin: 0 0 8pt 18pt;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin: 10pt 0 14pt;
}
thead {
  background: #eef2ff;
}
th, td {
  border: 0.6pt solid #cbd5f5;
  padding: 6pt 8pt;
  vertical-align: top;
  font-size: 10.5pt;
}
blockquote {
  border-left: 3pt solid #c7d2fe;
  padding-left: 10pt;
  margin: 10pt 0;
  color: #475569;
  font-style: italic;
}
hr {
  border: none;
  border-top: 0.8pt solid #e2e8f0;
  margin: 18pt 0;
}
"""


def export_document(*, format: str, title: str, content: str) -> Tuple[bytes, str, str]:
    """Export a document in the requested format."""
    normalized_format = (format or "docx").lower()
    safe_title = title.strip() or "Rechtsdokument"
    plain_text = normalise_plain_text(content)

    if normalized_format == "pdf":
        sanitized_html = sanitize_html_for_pdf(content)
        result = export_pdf(title=safe_title, html=sanitized_html)
    elif normalized_format == "docx":
        result = export_docx(title=safe_title, text=plain_text)
    else:
        raise ValueError(f"Unsupported export format: {format}")

    return result.data, result.filename, result.media_type


def normalise_plain_text(html: str | None) -> str:
    """Convert HTML from the editor into plain text paragraphs."""
    if not html:
        return ""

    text = html
    replacements = {
        r"(?i)<\s*/\s*p\s*>": "\n\n",
        r"(?i)<\s*br\s*/?\s*>": "\n",
        r"(?i)<\s*/\s*li\s*>": "\n",
        r"(?i)<\s*h[1-6][^>]*>": "\n\n",
        r"(?i)<\s*/\s*h[1-6]\s*>": "\n\n",
    }
    for pattern, value in replacements.items():
        text = re.sub(pattern, value, text)

    text = re.sub(r"(?is)<\s*li[^>]*>", "• ", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\u00a0", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def sanitize_html_for_pdf(html: str | None) -> str:
    if not html:
        return "<p>(kein Inhalt)</p>"

    cleaned = bleach.clean(
        html,
        tags=ALLOWED_HTML_TAGS,
        attributes=ALLOWED_HTML_ATTRS,
        strip=True
    )
    cleaned = re.sub(r"\s+\n", "\n", cleaned)
    cleaned = cleaned.strip()
    return cleaned or "<p>(kein Inhalt)</p>"


def export_docx(*, title: str, text: str) -> ExportResult:
    document = Document()
    normal_style = document.styles["Normal"]
    normal_style.font.name = "Arial"
    normal_style.font.size = Pt(11)

    heading = document.add_heading(title, level=1)
    heading.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    for paragraph in split_paragraphs(text):
        p = document.add_paragraph(paragraph)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.space_before = Pt(0)

    buffer = io.BytesIO()
    document.save(buffer)
    filename = f"{slugify(title)}.docx"
    return ExportResult(
        data=buffer.getvalue(),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


def export_pdf(*, title: str, html: str) -> ExportResult:
    document_html = f"""
    <!DOCTYPE html>
    <html lang="de">
      <head>
        <meta charset="utf-8" />
        <title>{escape(title)}</title>
        <style>
          {PDF_BASE_STYLES}
        </style>
      </head>
      <body>
        <header style="text-align:center;border-bottom:1px solid #e2e8f0;padding-bottom:12pt;margin-bottom:18pt">
          <h1>{escape(title)}</h1>
        </header>
        {html}
      </body>
    </html>
    """

    pdf_bytes = HTML(string=document_html).write_pdf()
    filename = f"{slugify(title)}.pdf"
    return ExportResult(data=pdf_bytes, filename=filename, media_type="application/pdf")


def split_paragraphs(text: str) -> List[str]:
    if not text:
        return []
    return [segment.strip() for segment in text.split("\n\n") if segment.strip()]


def slugify(value: str, fallback: str = "dokument") -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    value = re.sub(r"[\s_-]+", "-", value).strip("-")
    return value or fallback
