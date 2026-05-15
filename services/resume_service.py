import re
from PyPDF2 import PdfReader


def extract_text(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        text += page.extract_text()

    return text


# 🔥 NEW: Extract Email
def extract_email(text):
    match = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", text)
    return match[0] if match else "Not Found"


# 🔥 NEW: Extract Phone
def extract_phone(text):
    match = re.findall(r"\+?\d[\d\s\-]{8,15}", text)
    return match[0] if match else "Not Found"


# 🔥 NEW: Extract Name (simple logic)
def extract_name(text):
    lines = text.strip().split("\n")
    return lines[0] if lines else "Unknown"