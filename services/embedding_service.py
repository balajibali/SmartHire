import numpy as np
from sentence_transformers import SentenceTransformer
import threading
import hashlib

# =========================
# 🌍 GLOBALS
# =========================
_model = None

_model_lock = threading.Lock()

_embedding_cache = {}

MODEL_NAME = "all-MiniLM-L6-v2"

EMBEDDING_DIMENSION = 384


# =========================
# 🚀 LOAD MODEL ONCE
# =========================
def load_model():

    global _model

    try:

        with _model_lock:

            if _model is None:

                print(
                    f"Loading Embedding Model: "
                    f"{MODEL_NAME}"
                )

                _model = SentenceTransformer(
                    MODEL_NAME
                )

        return _model

    except Exception as e:

        print(
            "Model Load Error:",
            e
        )

        return None


# =========================
# 🧹 CLEAN TEXT
# =========================
def clean_text(text):

    if not text:
        return ""

    try:

        text = str(text)

        text = text.replace(
            "\n",
            " "
        )

        text = text.replace(
            "\r",
            " "
        )

        text = " ".join(
            text.split()
        )

        return text.strip()

    except:
        return ""


# =========================
# 🔑 TEXT HASH
# =========================
def get_text_hash(text):

    try:

        return hashlib.md5(
            text.encode("utf-8")
        ).hexdigest()

    except:
        return None


# =========================
# 🧠 TEXT TO VECTOR
# =========================
def text_to_vector(text: str):

    try:

        if not text:
            return None

        text = clean_text(text)

        if not text:
            return None

        # =========================
        # ⚡ CACHE
        # =========================
        text_hash = get_text_hash(text)

        if (
            text_hash
            and
            text_hash in _embedding_cache
        ):

            return _embedding_cache[
                text_hash
            ]

        # =========================
        # 🚀 LOAD MODEL
        # =========================
        model = load_model()

        if model is None:
            return None

        # =========================
        # 🧠 GENERATE EMBEDDING
        # =========================
        vec = model.encode(
            [text],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False
        )[0].astype("float32")

        # =========================
        # ⚡ CACHE VECTOR
        # =========================
        if text_hash:

            if len(_embedding_cache) > 500:

                # REMOVE OLD CACHE
                first_key = next(
                    iter(_embedding_cache)
                )

                del _embedding_cache[
                    first_key
                ]

            _embedding_cache[
                text_hash
            ] = vec

        return vec

    except Exception as e:

        print(
            "Embedding Error:",
            e
        )

        return None


# =========================
# 💾 VECTOR → BYTES
# =========================
def to_bytes(vec: np.ndarray):

    try:

        if vec is None:
            return None

        return vec.astype(
            "float32"
        ).tobytes()

    except Exception as e:

        print(
            "To Bytes Error:",
            e
        )

        return None


# =========================
# 📦 BYTES → VECTOR
# =========================
def from_bytes(blob: bytes):

    try:

        if not blob:
            return None

        vec = np.frombuffer(
            blob,
            dtype="float32"
        )

        return vec

    except Exception as e:

        print(
            "From Bytes Error:",
            e
        )

        return None


# =========================
# 📊 COSINE SIMILARITY
# =========================
def cosine_similarity(
    vec1,
    vec2
):

    try:

        if (
            vec1 is None
            or
            vec2 is None
        ):
            return 0

        vec1 = np.array(vec1)

        vec2 = np.array(vec2)

        similarity = np.dot(
            vec1,
            vec2
        ) / (
            np.linalg.norm(vec1)
            *
            np.linalg.norm(vec2)
        )

        return round(
            float(similarity) * 100,
            2
        )

    except Exception as e:

        print(
            "Similarity Error:",
            e
        )

        return 0


# =========================
# 🔍 SEMANTIC MATCH SCORE
# =========================
def semantic_match_score(
    text1,
    text2
):

    try:

        vec1 = text_to_vector(
            text1
        )

        vec2 = text_to_vector(
            text2
        )

        return cosine_similarity(
            vec1,
            vec2
        )

    except Exception as e:

        print(
            "Semantic Match Error:",
            e
        )

        return 0


# =========================
# 📊 MODEL INFO
# =========================
def get_embedding_info():

    return {

        "model_name":
        MODEL_NAME,

        "dimension":
        EMBEDDING_DIMENSION,

        "cache_size":
        len(_embedding_cache),

        "loaded":
        _model is not None
    }


# =========================
# 🧹 CLEAR CACHE
# =========================
def clear_embedding_cache():

    global _embedding_cache

    _embedding_cache = {}

    print(
        "Embedding Cache Cleared"
    )