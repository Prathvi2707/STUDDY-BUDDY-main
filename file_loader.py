from PyPDF2 import PdfReader
from docx import Document


def extract_text_from_pdf(file):
    try:
        pdf_reader = PdfReader(file)
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text() or ""
        return full_text.strip()
    except Exception as e:
        return f"Error reading PDF: {e}"

def extract_text_from_docx(file):
    try:
        document = Document(file)
        text = "\n".join([para.text for para in document.paragraphs])
        return text.strip()
    except Exception as e:
        return f"Error reading DOCX: {e}"


