import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_connection
from services.faiss_service import add_to_index, build_index


def run():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, resume_text FROM candidates")
    rows = cur.fetchall()

    for cid, resume in rows:
        if resume:
            add_to_index(cid, resume)

    conn.close()

    build_index()
    print("✅ Embeddings generated and FAISS ready")


if __name__ == "__main__":
    run()