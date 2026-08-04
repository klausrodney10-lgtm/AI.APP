from pypdf import PdfReader
from PIL import Image
import pytesseract

def read_file(uploaded_file) -> str:
    """Takes a file from st.file_uploader and gives back its text."""
    name = uploaded_file.name.lower()

    # PDF
    if name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)

    # Text files
    if name.endswith(".txt") or name.endswith(".md"):
        return uploaded_file.read().decode("utf-8", errors="ignore")

    # Images (png, jpg, jpeg)
    if name.endswith((".png", ".jpg", ".jpeg")):
        img = Image.open(uploaded_file)
        text = pytesseract.image_to_string(img)
        return text

    return f"Sorry, I can't read {name}. Try a .pdf, .txt, or an image file."
