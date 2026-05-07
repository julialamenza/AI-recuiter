from io import BytesIO

from docx import Document
from pypdf import PdfReader


def extract_text_from_bytes(content: bytes, mime_type: str) -> str:
    mt = (mime_type or "").lower().split(";")[0].strip()
    if mt == "application/pdf":
        reader = PdfReader(BytesIO(content))
        parts: list[str] = []
        for page in reader.pages:
            t = page.extract_text() or ""
            parts.append(t)
        return "\n".join(parts).strip()
    if mt in (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ):
        doc = Document(BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs if p.text).strip()
    if mt in ("text/plain", "application/octet-stream"):
        return content.decode("utf-8", errors="replace").strip()
    raise ValueError(f"Unsupported MIME type for text extraction: {mime_type}")
