import PyPDF2
import docx

def parse_file(path):
    """
    Extracts text from PDF or DOCX file.
    Returns raw text.
    """
    if path.lower().endswith(".pdf"):
        text = ""
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text

    elif path.lower().endswith(".docx"):
        doc = docx.Document(path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

    else:
        raise ValueError("Unsupported file format")
