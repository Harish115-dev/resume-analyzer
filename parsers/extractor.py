import pdfplumber
from docx import Document
import os

def _extract_from_pdf(filepath):
    full_text=[]
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text=page.extract_text()
            if text:
                full_text.append(text)
    return "\n".join(full_text)
def _extract_from_docx(filepath):
    full_text=[]
    document= Document(filepath)
    for paragraph in document.paragraphs:
        full_text.append(paragraph.text)
    return "\n".join(full_text)

def extract_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        return _extract_from_pdf(filepath)
    elif ext == ".docx":
        return _extract_from_docx(filepath)
    else :
        raise ValueError(f"unsupported file tye:{ext}")
    



    
