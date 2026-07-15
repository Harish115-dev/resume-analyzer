import pdfplumber
from docx import Document
from docx.oxml.ns import qn
import os


def _extract_from_pdf(filepath):
    full_text = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
    return "\n".join(full_text)


def _is_list_paragraph(paragraph):
    pPr = paragraph._p.find(qn("w:pPr"))
    if pPr is not None and pPr.find(qn("w:numPr")) is not None:
        return True
    if paragraph.style and paragraph.style.name and "List" in paragraph.style.name:
        return True
    return False


def _get_paragraph_hyperlinks(paragraph, document):
    urls = []
    for hyperlink in paragraph._p.findall(qn("w:hyperlink")):
        rId = hyperlink.get(qn("r:id"))
        if rId and rId in document.part.rels:
            urls.append(document.part.rels[rId].target_ref)
    return urls


def _extract_from_docx(filepath):
    full_text = []
    document = Document(filepath)
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        hyperlinks = _get_paragraph_hyperlinks(paragraph, document)

        if not text and not hyperlinks:
            continue

        if _is_list_paragraph(paragraph):
            text = f"- {text}"

        if hyperlinks:
            text = f"{text} {' '.join(hyperlinks)}".strip()

        full_text.append(text)
    return "\n".join(full_text)


def extract_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        return _extract_from_pdf(filepath)
    elif ext == ".docx":
        return _extract_from_docx(filepath)
    else:
        raise ValueError(f"unsupported file type: {ext}")