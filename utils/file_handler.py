import PyPDF2
import re
import io


# =========================
# 🧹 CLEAN TEXT
# =========================
def clean_resume_text(text):

    if not text:
        return ""

    # REMOVE EXTRA SPACES
    text = re.sub(r"\s+", " ", text)

    # REMOVE MULTIPLE NEWLINES
    text = re.sub(r"\n+", "\n", text)

    # REMOVE NON-PRINTABLE CHARS
    text = re.sub(
        r"[^\x20-\x7E\n]",
        " ",
        text
    )

    # TRIM
    text = text.strip()

    return text


# =========================
# 📄 EXTRACT TEXT FROM PDF
# =========================
def extract_text_from_pdf(file):

    text = ""

    try:

        # =========================
        # 📦 READ FILE SAFELY
        # =========================
        if hasattr(file, "read"):

            file_bytes = file.read()

            file_stream = io.BytesIO(file_bytes)

        else:

            file_stream = file

        # =========================
        # 📖 LOAD PDF
        # =========================
        pdf = PyPDF2.PdfReader(file_stream)

        # =========================
        # 📄 EXTRACT PAGE TEXT
        # =========================
        for page_num, page in enumerate(pdf.pages):

            try:

                page_text = (
                    page.extract_text() or ""
                )

                if page_text:

                    text += (
                        page_text + "\n"
                    )

            except Exception as page_error:

                print(
                    f"Page {page_num} Error:",
                    page_error
                )

        # =========================
        # 🧹 CLEAN TEXT
        # =========================
        text = clean_resume_text(text)

    except Exception as e:

        print("PDF Error:", e)

        text = ""

    return text


# =========================
# 📂 HANDLE MULTIPLE FILES
# =========================
def process_uploaded_files(files):

    results = []

    if not files:
        return results

    for file in files:

        try:

            # =========================
            # 📄 EXTRACT TEXT
            # =========================
            text = extract_text_from_pdf(file)

            # =========================
            # 📊 FILE META
            # =========================
            file_size = 0

            try:

                file_size = len(
                    file.getvalue()
                )

            except:
                pass

            # =========================
            # 💾 RESULT
            # =========================
            results.append({

                "filename": getattr(
                    file,
                    "name",
                    "unknown.pdf"
                ),

                "text": text,

                "chars": len(text),

                "words": len(text.split()),

                "size_kb": round(
                    file_size / 1024,
                    2
                ),

                "success": bool(text)
            })

        except Exception as e:

            results.append({

                "filename": getattr(
                    file,
                    "name",
                    "unknown.pdf"
                ),

                "text": "",

                "chars": 0,

                "words": 0,

                "size_kb": 0,

                "success": False,

                "error": str(e)
            })

    return results