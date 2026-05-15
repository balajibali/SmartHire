import re


# =========================
# 🔹 SKILL VARIATIONS
# =========================
SKILL_MAP = {

    # =========================
    # 💻 PROGRAMMING
    # =========================
    "python": ["python"],

    "java": ["java"],

    "c++": ["c++", "cpp"],

    "c": [" c "],

    "c#": ["c#", "csharp"],

    "javascript": [
        "javascript",
        "js"
    ],

    "typescript": [
        "typescript",
        "ts"
    ],

    "sql": [
        "sql",
        "mysql",
        "postgresql",
        "sqlite"
    ],

    "mongodb": [
        "mongodb",
        "mongo"
    ],

    # =========================
    # 🌐 FRONTEND
    # =========================
    "html": ["html"],

    "css": ["css"],

    "react": [
        "react",
        "reactjs",
        "react.js"
    ],

    "next.js": [
        "next.js",
        "nextjs"
    ],

    "vue": [
        "vue",
        "vuejs"
    ],

    "angular": [
        "angular"
    ],

    "tailwind": [
        "tailwind",
        "tailwindcss"
    ],

    "bootstrap": [
        "bootstrap"
    ],

    # =========================
    # ⚙️ BACKEND
    # =========================
    "django": ["django"],

    "flask": ["flask"],

    "fastapi": ["fastapi"],

    "node": [
        "node",
        "nodejs",
        "node.js"
    ],

    "express": [
        "express",
        "expressjs"
    ],

    "spring boot": [
        "spring boot"
    ],

    # =========================
    # ☁️ CLOUD & DEVOPS
    # =========================
    "aws": [
        "aws",
        "amazon web services"
    ],

    "azure": ["azure"],

    "gcp": [
        "gcp",
        "google cloud"
    ],

    "docker": ["docker"],

    "kubernetes": [
        "kubernetes",
        "k8s"
    ],

    "jenkins": ["jenkins"],

    "git": ["git", "github"],

    "linux": ["linux"],

    # =========================
    # 🤖 AI / ML
    # =========================
    "machine learning": [
        "machine learning",
        "ml"
    ],

    "deep learning": [
        "deep learning",
        "dl"
    ],

    "data science": [
        "data science",
        "data scientist"
    ],

    "nlp": [
        "nlp",
        "natural language processing"
    ],

    "computer vision": [
        "computer vision"
    ],

    "tensorflow": [
        "tensorflow"
    ],

    "pytorch": [
        "pytorch"
    ],

    "langchain": [
        "langchain"
    ],

    "llamaindex": [
        "llamaindex"
    ],

    "huggingface": [
        "huggingface",
        "transformers"
    ],

    "prompt engineering": [
        "prompt engineering",
        "prompt engineer"
    ],

    "rag": [
        "rag",
        "retrieval augmented generation"
    ],

    "vector database": [
        "vector db",
        "vector database",
        "pinecone",
        "faiss",
        "chroma"
    ],

    "ollama": [
        "ollama"
    ],

    "openai": [
        "openai",
        "gpt"
    ],

    # =========================
    # 📊 DATA TOOLS
    # =========================
    "excel": ["excel"],

    "power bi": [
        "power bi",
        "powerbi"
    ],

    "tableau": ["tableau"],

    "pandas": ["pandas"],

    "numpy": ["numpy"],

    "matplotlib": ["matplotlib"],

    # =========================
    # 🧠 SOFT SKILLS
    # =========================
    "communication": [
        "communication",
        "communication skills"
    ],

    "teamwork": [
        "teamwork",
        "team work"
    ],

    "leadership": [
        "leadership"
    ],

    "problem solving": [
        "problem solving",
        "problem-solving"
    ],

    "critical thinking": [
        "critical thinking"
    ],

    "time management": [
        "time management"
    ]
}


# =========================
# 🧹 CLEAN TEXT
# =========================
def normalize_text(text):

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================
# 🔍 EXTRACT SKILLS
# =========================
def extract_skills(text):

    if not text:
        return []

    text = normalize_text(text)

    found_skills = set()

    for main_skill, variations in SKILL_MAP.items():

        for variant in variations:

            try:

                # =========================
                # 🔥 SAFE REGEX
                # =========================
                pattern = (
                    rf"\b{re.escape(variant)}\b"
                )

                if re.search(pattern, text):

                    found_skills.add(main_skill)

                    break

            except:
                pass

    return sorted(
        list(found_skills)
    )


# =========================
# 📊 SKILL MATCH SCORE
# =========================
def calculate_skill_match(
    required_skills,
    candidate_skills
):

    if not required_skills:
        return 0

    required_set = set([
        s.lower().strip()
        for s in required_skills
    ])

    candidate_set = set([
        s.lower().strip()
        for s in candidate_skills
    ])

    matched = (
        required_set
        &
        candidate_set
    )

    score = (
        len(matched)
        /
        max(len(required_set), 1)
    ) * 100

    return round(score, 2)


# =========================
# 🧠 EXTRACT EXPERIENCE
# =========================
def extract_experience(text):

    if not text:
        return None

    text = normalize_text(text)

    matches = re.findall(
        r"(\d+)\+?\s*years?",
        text
    )

    if matches:

        try:

            years = max([
                int(x)
                for x in matches
            ])

            return years

        except:
            pass

    return None