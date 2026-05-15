import json
from services.ollama_service import generate_ai_response

def parse_user_intent(query):
    prompt = f"""
    Convert the user query into JSON.

    Supported actions:
    - search_candidates
    - top_candidates
    - shortlist_candidates
    - reject_candidates
    - generate_jd
    - chat

    Extract:
    - action
    - skills (list)
    - limit (number)
    - status (optional)

    Query: {query}

    Return ONLY valid JSON:
    {{
        "action": "",
        "skills": [],
        "limit": 5,
        "status": ""
    }}
    """

    response = generate_ai_response(prompt)

    try:
        return json.loads(response)
    except:
        return {"action": "chat", "skills": [], "limit": 5}