import requests


# =========================
# ⚙️ OLLAMA CONFIG
# =========================
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

DEFAULT_MODEL = "llama3"

DEFAULT_OPTIONS = {
    "num_predict": 250,   # ⚡ reduced slightly to avoid timeout
    "temperature": 0.6
}


# =========================
# 🧹 CLEAN RESPONSE
# =========================
def clean_response(text):

    if not text:
        return ""

    text = str(text).strip()

    text = text.replace("<think>", "")
    text = text.replace("</think>", "")

    return text.strip()


# =========================
# ✂️ SAFE PROMPT (NEW)
# =========================
def trim_prompt(prompt, max_chars=4000):
    """
    Prevents Ollama timeout by limiting prompt size
    """
    if len(prompt) > max_chars:
        return prompt[:max_chars]
    return prompt


# =========================
# 🚀 GENERATE AI RESPONSE
# =========================
def generate_ai_response(
    prompt,
    model=DEFAULT_MODEL,
    timeout=120   # ⚡ reduced for faster failure recovery
):

    if not prompt or not prompt.strip():
        return "Empty prompt"

    # 🔥 NEW: trim long prompts
    prompt = trim_prompt(prompt)

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": DEFAULT_OPTIONS
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=timeout
        )

        if response.status_code == 200:

            data = response.json()

            ai_text = data.get("response", "")

            ai_text = clean_response(ai_text)

            if not ai_text:
                return "AI returned empty response"

            return ai_text

        return f"AI Error: {response.status_code}"

    except requests.exceptions.Timeout:
        return "⏳ AI took too long. Try shorter query."

    except requests.exceptions.ConnectionError:
        return "❌ Ollama not running. Start it using: ollama serve"

    except Exception as e:
        return f"Ollama Error: {str(e)}"


# =========================
# 💬 CHAT RESPONSE (IMPROVED MEMORY HANDLING)
# =========================
def generate_chat_response(
    user_message,
    context="",
    model=DEFAULT_MODEL
):

    # 🔥 trim context to avoid overload
    context = trim_prompt(context, 2000)

    prompt = f"""
You are an intelligent AI Recruitment Assistant.

Rules:
- Be precise
- Help hiring decisions
- Use context if available
- Avoid hallucination

Context:
{context}

User Question:
{user_message}
"""

    return generate_ai_response(prompt, model)


# =========================
# 🧠 JD GENERATOR
# =========================
def generate_job_description(
    title,
    skills="",
    experience=""
):

    prompt = f"""
Generate a professional ATS-friendly Job Description.

Role:
{title}

Skills Required:
{skills}

Experience Required:
{experience}

Format:
- Job Overview
- Responsibilities
- Required Skills
- Preferred Skills
- Qualifications
- Tools/Technologies
- Soft Skills
"""

    return generate_ai_response(prompt)


# =========================
# 📊 RESUME ANALYZER
# =========================
def analyze_resume(
    resume_text,
    job_description=""
):

    prompt = f"""
You are an expert HR recruiter.

Analyze this resume:

Resume:
{resume_text}

Job Description:
{job_description}

Return:
- Summary
- Strengths
- Weaknesses
- Skill Match
- Recommendation
- Fit Score (0-100)
"""

    return generate_ai_response(prompt)


# =========================
# 🎯 CANDIDATE MATCHING
# =========================
def match_candidate(
    resume_text,
    job_description
):

    prompt = f"""
Compare resume with job description.

Job:
{job_description}

Resume:
{resume_text}

Return ONLY:
- Match Percentage
- Matching Skills
- Missing Skills
- Final Recommendation
"""

    return generate_ai_response(prompt)


# =========================
# 📧 EMAIL GENERATOR
# =========================
def generate_email(
    purpose,
    candidate_name=""
):

    prompt = f"""
Generate professional HR email.

Purpose:
{purpose}

Candidate:
{candidate_name}

Make it formal and concise.
"""

    return generate_ai_response(prompt)


# =========================
# 🌐 OLLAMA HEALTH CHECK
# =========================
def check_ollama():

    try:
        response = requests.get(
            "http://127.0.0.1:11434",
            timeout=5
        )

        return response.status_code == 200

    except:
        return False