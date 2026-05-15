from modules.matcher import calculate_score

def recommend_jobs(candidate_skills, jobs):

    recommendations = []

    if not candidate_skills:
        return []

    candidate_skill_list = [s.strip().lower() for s in candidate_skills.split(",")]

    for job in jobs:

        job_id = job[0]
        job_title = job[1]
        job_skills = job[3]

        if not job_skills:
            continue

        score = calculate_score(job_skills, candidate_skill_list)

        recommendations.append((job_title, score))

    # Sort highest match first
    recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)

    return recommendations[:3]  # Top 3 jobs