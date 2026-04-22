import re
from Main_app.database.skills_database import technical_skills, soft_skills, analytical_skills, get_all_skills

def extract_skills_from_text(text):
    text = text.lower()
    found_skills = []

    for skill in get_all_skills():
        # match full words using regex
        if re.search(r"\b" + re.escape(skill.lower()) + r"\b", text):
            found_skills.append(skill)

    # remove duplicates
    found_skills = list(set(found_skills))

    categorized_skills = {
        "technical": [s for s in found_skills if s in technical_skills],
        "analytical": [s for s in found_skills if s in analytical_skills],
        "soft": [s for s in found_skills if s in soft_skills]
    }

    return categorized_skills
