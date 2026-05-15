import sqlite3
import os
from contextlib import closing

# =========================
# 📁 DATABASE PATH
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_NAME = os.path.join(
    BASE_DIR,
    "database.db"
)


# =========================
# 🔌 CONNECTION (UPGRADED)
# =========================
def get_connection():

    conn = sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    conn.execute(
        "PRAGMA journal_mode=WAL"
    )

    conn.execute(
        "PRAGMA synchronous=NORMAL"
    )

    conn.execute(
        "PRAGMA temp_store=MEMORY"
    )

    conn.execute(
        "PRAGMA cache_size=-64000"
    )

    return conn


# =========================
# 🏗 INIT DATABASE
# =========================
def init_db():

    conn = get_connection()

    cursor = conn.cursor()

    # =========================
    # 👤 USERS
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        email TEXT UNIQUE,

        password TEXT,

        is_verified INTEGER DEFAULT 0,

        created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # =========================
    # 📄 JOBS
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        title TEXT,

        description TEXT,

        skills TEXT,

        experience TEXT,

        deadline TEXT,

        created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (user_id)
        REFERENCES users(id)
    )
    """)

    # =========================
    # 👥 CANDIDATES
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        job_id INTEGER,

        name TEXT,

        email TEXT,

        phone TEXT,

        resume_text TEXT,

        resume_file BLOB,

        status TEXT DEFAULT 'Applied',

        score REAL DEFAULT 0,

        embedding BLOB,

        ai_summary TEXT,

        skills TEXT,

        experience TEXT,

        created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (job_id)
        REFERENCES jobs(id)
    )
    """)

    # =========================
    # 🌍 GLOBAL CANDIDATES
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS global_candidates (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,

        email TEXT UNIQUE,

        phone TEXT,

        resume_text TEXT,

        skills TEXT,

        ai_summary TEXT,

        created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # =========================
    # 🔧 SAFE MIGRATIONS
    # =========================
    safe_add_column(
        cursor,
        "candidates",
        "embedding",
        "BLOB"
    )

    safe_add_column(
        cursor,
        "candidates",
        "phone",
        "TEXT"
    )

    safe_add_column(
        cursor,
        "candidates",
        "skills",
        "TEXT"
    )

    safe_add_column(
        cursor,
        "candidates",
        "experience",
        "TEXT"
    )

    safe_add_column(
        cursor,
        "candidates",
        "ai_summary",
        "TEXT"
    )

    safe_add_column(
        cursor,
        "global_candidates",
        "phone",
        "TEXT"
    )

    safe_add_column(
        cursor,
        "global_candidates",
        "skills",
        "TEXT"
    )

    safe_add_column(
        cursor,
        "global_candidates",
        "ai_summary",
        "TEXT"
    )

    # =========================
    # ⚡ INDEXES
    # =========================
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_jobs_user
        ON jobs(user_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_candidates_job
        ON candidates(job_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_candidates_email
        ON candidates(email)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_candidates_status
        ON candidates(status)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_global_email
        ON global_candidates(email)
    """)

    conn.commit()

    conn.close()


# =========================
# 🔧 SAFE COLUMN ADD
# =========================
def safe_add_column(
    cursor,
    table,
    column,
    col_type
):

    cursor.execute(
        f"PRAGMA table_info({table})"
    )

    columns = [
        col[1]
        for col in cursor.fetchall()
    ]

    if column not in columns:

        cursor.execute(
            f"""
            ALTER TABLE {table}
            ADD COLUMN {column} {col_type}
            """
        )


# =========================
# 👤 USER FUNCTIONS
# =========================
def create_user(email, password):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users
        (email, password)
        VALUES (?, ?)
        """,
        (
            email.strip().lower(),
            password
        )
    )

    conn.commit()

    conn.close()


def get_user(email):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE LOWER(email)=?
        """,
        (email.strip().lower(),)
    )

    user = cursor.fetchone()

    conn.close()

    return user


def verify_user(email):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET is_verified=1
        WHERE LOWER(email)=?
        """,
        (email.strip().lower(),)
    )

    conn.commit()

    conn.close()


# =========================
# 📄 JOB FUNCTIONS
# =========================
def create_job(
    user_id,
    title,
    description,
    skills,
    experience,
    deadline
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO jobs (
            user_id,
            title,
            description,
            skills,
            experience,
            deadline
        )

        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        title.strip(),
        description.strip(),
        skills,
        experience,
        deadline
    ))

    job_id = cursor.lastrowid

    conn.commit()

    conn.close()

    return job_id


def get_jobs_by_user(user_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM jobs
        WHERE user_id=?
        ORDER BY created_at DESC
    """, (user_id,))

    data = cursor.fetchall()

    conn.close()

    return data


def get_job_by_id(job_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM jobs
        WHERE id=?
    """, (job_id,))

    job = cursor.fetchone()

    conn.close()

    return job


def delete_job(job_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM jobs
        WHERE id=?
    """, (job_id,))

    conn.commit()

    conn.close()


# =========================
# 👥 CANDIDATE FUNCTIONS
# =========================
def add_candidate(
    job_id,
    name,
    email,
    resume_text,
    resume_file=None,
    score=0,
    phone=None,
    skills=None,
    experience=None
):

    conn = get_connection()

    cursor = conn.cursor()

    # =========================
    # 🚫 DUPLICATE CHECK
    # =========================
    cursor.execute("""
        SELECT id
        FROM candidates
        WHERE job_id=?
        AND LOWER(email)=?
    """, (
        job_id,
        email.strip().lower()
    ))

    exists = cursor.fetchone()

    if exists:

        conn.close()

        return exists[0]

    # =========================
    # 💾 INSERT
    # =========================
    cursor.execute("""
        INSERT INTO candidates (

            job_id,
            name,
            email,
            phone,
            resume_text,
            resume_file,
            score,
            skills,
            experience

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job_id,
        name.strip(),
        email.strip().lower(),
        phone,
        resume_text,
        resume_file,
        score,
        skills,
        experience
    ))

    candidate_id = cursor.lastrowid

    conn.commit()

    conn.close()

    # =========================
    # 🧠 FAISS INDEX
    # =========================
    if resume_text:

        try:

            from services.faiss_service import (
                add_to_index
            )

            add_to_index(
                candidate_id,
                resume_text
            )

        except:
            pass

    return candidate_id


def get_candidates_by_job(job_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM candidates
        WHERE job_id=?
        ORDER BY score DESC
    """, (job_id,))

    data = cursor.fetchall()

    conn.close()

    return data


def get_shortlisted_candidates(job_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM candidates
        WHERE job_id=?
        AND LOWER(status)='shortlisted'
        ORDER BY score DESC
    """, (job_id,))

    data = cursor.fetchall()

    conn.close()

    return data


def update_candidate_status(
    candidate_id,
    status
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE candidates
        SET status=?
        WHERE id=?
    """, (
        status.capitalize(),
        candidate_id
    ))

    conn.commit()

    conn.close()


def update_candidate_score(
    candidate_id,
    score
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE candidates
        SET score=?
        WHERE id=?
    """, (
        score,
        candidate_id
    ))

    conn.commit()

    conn.close()


# =========================
# 🌍 GLOBAL CANDIDATES
# =========================
def get_all_global_candidates():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            resume_text,
            skills,
            ai_summary

        FROM global_candidates

        ORDER BY created_at DESC
    """)

    data = cursor.fetchall()

    conn.close()

    return data


def add_global_candidate(
    name,
    email,
    resume_text,
    phone=None,
    skills=None,
    ai_summary=None
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM global_candidates
        WHERE LOWER(email)=?
    """, (email.strip().lower(),))

    exists = cursor.fetchone()

    if not exists:

        cursor.execute("""
            INSERT INTO global_candidates (

                name,
                email,
                phone,
                resume_text,
                skills,
                ai_summary

            )

            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name.strip(),
            email.strip().lower(),
            phone,
            resume_text,
            skills,
            ai_summary
        ))

    conn.commit()

    conn.close()


# =========================
# 📊 STATS
# =========================
def count_all_shortlisted(user_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)

        FROM candidates

        WHERE job_id IN (
            SELECT id
            FROM jobs
            WHERE user_id=?
        )

        AND LOWER(status)='shortlisted'
    """, (user_id,))

    count = cursor.fetchone()[0]

    conn.close()

    return count


def count_all_pending(user_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)

        FROM candidates

        WHERE job_id IN (
            SELECT id
            FROM jobs
            WHERE user_id=?
        )

        AND LOWER(status)='applied'
    """, (user_id,))

    count = cursor.fetchone()[0]

    conn.close()

    return count


# =========================
# 🔍 SEARCH FUNCTIONS
# =========================
def search_candidates(keyword):

    conn = get_connection()

    cursor = conn.cursor()

    like_query = f"%{keyword.lower()}%"

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            skills,
            score

        FROM candidates

        WHERE LOWER(name) LIKE ?
        OR LOWER(email) LIKE ?
        OR LOWER(resume_text) LIKE ?
        OR LOWER(skills) LIKE ?

        ORDER BY score DESC
    """, (
        like_query,
        like_query,
        like_query,
        like_query
    ))

    data = cursor.fetchall()

    conn.close()

    return data