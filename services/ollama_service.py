
import requests


# =========================
# OLLAMA CONFIG
# =========================
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

DEFAULT_MODEL = "llama3"

DEFAULT_OPTIONS = {
    "num_predict": 500,
    "temperature": 0.5
}


# =========================
# CLEAN RESPONSE
# =========================
def clean_response(text):

    if not text:
        return ""

    text = str(text).strip()

    text = text.replace("<think>", "")
    text = text.replace("</think>", "")

    return text.strip()


# =========================
# TRIM PROMPT
# =========================
def trim_prompt(prompt, max_chars=12000):

    if not prompt:
        return ""

    if len(prompt) > max_chars:
        return prompt[:max_chars]

    return prompt


# =========================
# GENERATE AI RESPONSE
# =========================
def generate_ai_response(
    prompt,
    model=DEFAULT_MODEL,
    timeout=180
):

    if not prompt:
        return "Empty prompt"

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

            ai_text = data.get(
                "response",
                ""
            )

            ai_text = clean_response(
                ai_text
            )

            if not ai_text:
                return "AI returned empty response"

            return ai_text

        return f"AI Error: {response.status_code}"

    except requests.exceptions.Timeout:

        return (
            "AI request timed out. "
            "Try again with a shorter query."
        )

    except requests.exceptions.ConnectionError:

        return (
            "Ollama is not running.\n"
            "Start it using:\n\n"
            "ollama serve"
        )

    except Exception as e:

        return f"Ollama Error: {str(e)}"


# =========================
# CHAT RESPONSE
# =========================
def generate_chat_response(
    user_message,
    context="",
    model=DEFAULT_MODEL
):

    context = trim_prompt(
        context,
        8000
    )

    question = user_message.lower()

    # =====================
    # JOB DESCRIPTION MODE
    # =====================

    if any(
        keyword in question
        for keyword in [
            "job description",
            "generate jd",
            "create jd",
            "jd for",
            "write jd"
        ]
    ):

        prompt = f"""
You are an expert HR recruiter.

Create a professional ATS-friendly
Job Description.

Request:

{user_message}

Include:

1. Job Overview
2. Responsibilities
3. Required Skills
4. Preferred Skills
5. Qualifications
6. Tools & Technologies
7. Soft Skills
8. Benefits

Return professional format.
"""

    # =====================
    # DATABASE MODE
    # =====================

    else:

        prompt = f"""
You are an ATS Recruitment Assistant.

STRICT RULES:

1. Use ONLY information
   present in DATABASE CONTEXT.

2. Never invent candidates.

3. Never invent jobs.

4. Never invent skills.

5. Never invent experience.

6. Never invent scores.

7. If data is unavailable say:

   No matching data found in database.

8. When candidate matches are found:

   - Show candidate name
   - Skills
   - Experience
   - Status
   - Score

9. When jobs match:

   Show all available job details.

DATABASE CONTEXT:

{context}

USER QUESTION:

{user_message}

ANSWER:
"""

    return generate_ai_response(
        prompt,
        model=model,
        timeout=180
    )


# =========================
# JOB DESCRIPTION
# =========================
def generate_job_description(
    title,
    skills="",
    experience=""
):

    prompt = f"""
Generate a professional ATS-friendly
Job Description.

Role:
{title}

Required Skills:
{skills}

Experience:
{experience}

Include:

1. Overview
2. Responsibilities
3. Required Skills
4. Preferred Skills
5. Qualifications
6. Tools
7. Benefits
"""

    return generate_ai_response(
        prompt
    )


# =========================
# RESUME ANALYZER
# =========================
def analyze_resume(
    resume_text,
    job_description=""
):

    prompt = f"""
You are an expert recruiter.

Resume:

{resume_text}

Job Description:

{job_description}

Provide:

1. Summary
2. Strengths
3. Weaknesses
4. Skill Match
5. Missing Skills
6. Recommendation
7. Fit Score (0-100)
"""

    return generate_ai_response(
        prompt
    )


# =========================
# CANDIDATE MATCHING
# =========================
def match_candidate(
    resume_text,
    job_description
):

    prompt = f"""
Compare the candidate resume
against the job description.

JOB DESCRIPTION:

{job_description}

RESUME:

{resume_text}

Return:

1. Match Percentage
2. Matching Skills
3. Missing Skills
4. Recommendation
"""

    return generate_ai_response(
        prompt
    )


# =========================
# EMAIL GENERATOR
# =========================
def generate_email(
    purpose,
    candidate_name=""
):

    prompt = f"""
Generate a professional HR email.

Purpose:

{purpose}

Candidate:

{candidate_name}

Keep it concise,
formal and professional.
"""

    return generate_ai_response(
        prompt
    )


# =========================
# OLLAMA HEALTH CHECK
# =========================
def check_ollama():

    try:

        response = requests.get(
            "http://127.0.0.1:11434",
            timeout=5
        )

        return (
            response.status_code == 200
        )

    except:

        return False

