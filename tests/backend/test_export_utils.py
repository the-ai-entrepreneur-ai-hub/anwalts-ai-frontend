import io

from export_utils import export_document


SAMPLE_HTML = """
<header><h1>Test Dokument</h1></header>
<p>Dies ist ein <strong>Beispieldokument</strong> mit mehreren Absätzen.</p>
<ul><li>Klausel A</li><li>Klausel B</li></ul>
"""


def test_export_document_pdf_produces_bytes():
    data, filename, media_type = export_document(format="pdf", title="Test Dokument", content=SAMPLE_HTML)
    assert filename.endswith(".pdf")
    assert media_type == "application/pdf"
    assert data[:4] == b"%PDF"


def test_export_document_docx_produces_zip():
    data, filename, media_type = export_document(format="docx", title="Test Dokument", content=SAMPLE_HTML)
    assert filename.endswith(".docx")
    assert media_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    # DOCX files are zipped archives beginning with PK
    assert data[:2] == b"PK"
