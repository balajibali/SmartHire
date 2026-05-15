import faiss
import numpy as np
import threading
from database.db import get_connection
from services.embedding_service import (
    text_to_vector,
    to_bytes,
    from_bytes
)

# =========================
# 🌍 GLOBALS
# =========================
_index = None

_id_map = []

_dim = None

_lock = threading.Lock()


# =========================
# 🧹 NORMALIZE VECTOR
# =========================
def normalize_vector(vec):

    try:

        norm = np.linalg.norm(vec)

        if norm == 0:
            return vec

        return vec / norm

    except:
        return vec


# =========================
# 🔧 BUILD FULL INDEX
# =========================
def build_index():

    global _index
    global _id_map
    global _dim

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                embedding
            FROM candidates
            WHERE embedding IS NOT NULL
        """)

        rows = cur.fetchall()

        conn.close()

        if not rows:

            _index = None

            _id_map = []

            return

        vectors = []

        ids = []

        for cid, blob in rows:

            try:

                vec = from_bytes(blob)

                if vec is not None:

                    vec = vec.astype(
                        "float32"
                    )

                    vec = normalize_vector(
                        vec
                    )

                    vectors.append(vec)

                    ids.append(cid)

            except Exception as e:

                print(
                    "Vector Load Error:",
                    e
                )

        if not vectors:

            _index = None

            _id_map = []

            return

        X = np.vstack(vectors).astype(
            "float32"
        )

        _dim = X.shape[1]

        # =========================
        # ⚡ COSINE SIMILARITY
        # =========================
        _index = faiss.IndexFlatIP(
            _dim
        )

        _index.add(X)

        _id_map = ids

        print(
            f"FAISS Index Built: "
            f"{len(_id_map)} vectors"
        )

    except Exception as e:

        print(
            "Build Index Error:",
            e
        )


# =========================
# 🚀 ADD SINGLE VECTOR
# =========================
def add_to_index(
    candidate_id,
    resume_text
):

    global _index
    global _id_map
    global _dim

    try:

        if not resume_text:
            return

        vec = text_to_vector(
            resume_text
        )

        if vec is None:
            return

        vec = vec.astype(
            "float32"
        )

        vec = normalize_vector(vec)

        # =========================
        # 💾 SAVE TO DB
        # =========================
        conn = get_connection()

        cur = conn.cursor()

        cur.execute(
            """
            UPDATE candidates
            SET embedding=?
            WHERE id=?
            """,
            (
                to_bytes(vec),
                candidate_id
            )
        )

        conn.commit()

        conn.close()

        # =========================
        # 🔧 BUILD INDEX
        # =========================
        with _lock:

            if _index is None:

                build_index()

                return

            # =========================
            # ⚡ FAST INSERT
            # =========================
            _index.add(
                np.array([vec])
            )

            _id_map.append(
                candidate_id
            )

        print(
            f"Candidate Indexed: "
            f"{candidate_id}"
        )

    except Exception as e:

        print(
            "Add To Index Error:",
            e
        )


# =========================
# 🔍 SEARCH SIMILAR
# =========================
def search_similar(
    job_desc,
    top_k=50
):

    global _index
    global _id_map

    try:

        if not job_desc:
            return []

        # =========================
        # 🔧 AUTO BUILD
        # =========================
        if _index is None:

            build_index()

        if _index is None:
            return []

        # =========================
        # 🧠 QUERY VECTOR
        # =========================
        query_vec = text_to_vector(
            job_desc
        )

        if query_vec is None:
            return []

        query_vec = query_vec.astype(
            "float32"
        )

        query_vec = normalize_vector(
            query_vec
        )

        query_vec = np.array([
            query_vec
        ]).astype("float32")

        # =========================
        # 🔍 SEARCH
        # =========================
        D, I = _index.search(
            query_vec,
            min(
                top_k,
                len(_id_map)
            )
        )

        results = []

        for score, idx in zip(
            D[0],
            I[0]
        ):

            try:

                if (
                    idx >= 0
                    and
                    idx < len(_id_map)
                ):

                    results.append({

                        "candidate_id":
                        _id_map[idx],

                        "similarity":
                        round(
                            float(score) * 100,
                            2
                        )
                    })

            except:
                pass

        return results

    except Exception as e:

        print(
            "Search Error:",
            e
        )

        return []


# =========================
# 🧠 SEMANTIC SEARCH
# =========================
def semantic_search(
    query,
    limit=10
):

    try:

        results = search_similar(
            query,
            top_k=limit
        )

        return results

    except Exception as e:

        print(
            "Semantic Search Error:",
            e
        )

        return []


# =========================
# 🧹 RESET INDEX
# =========================
def reset_index():

    global _index
    global _id_map
    global _dim

    _index = None

    _id_map = []

    _dim = None

    print(
        "FAISS Index Reset"
    )


# =========================
# 📊 INDEX STATS
# =========================
def get_index_stats():

    try:

        total = len(_id_map)

        return {

            "indexed_candidates":
            total,

            "dimension":
            _dim,

            "index_ready":
            _index is not None
        }

    except:

        return {

            "indexed_candidates": 0,

            "dimension": None,

            "index_ready": False
        }