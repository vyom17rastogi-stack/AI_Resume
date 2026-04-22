import re
from difflib import SequenceMatcher
from collections import Counter
from typing import List, Dict, Any

def normalize_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text.lower().strip())

def extract_words(text: str) -> List[str]:
    return re.findall(r"[a-z0-9\+\.#\-]+", text.lower())

def phrase_in_text(phrase: str, text: str) -> bool:
    pattern = r'\b' + re.escape(phrase.lower()) + r'\b'
    return bool(re.search(pattern, text.lower()))

def fuzzy_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def compute_keyword_matches(job_text: str, resume_text: str, top_k:int=50) -> Dict[str, Any]:
    job_words = extract_words(job_text)
    resume_words = extract_words(resume_text)
    job_counts = Counter(job_words)
    most_common = [w for w, _ in job_counts.most_common(top_k)]
    found = []
    for w in most_common:
        if w and phrase_in_text(w, resume_text):
            found.append(w)
    return {
        "job_keywords": most_common,
        "found": found,
        "found_count": len(found),
        "job_count": len(most_common)
    }

def compute_skill_matches(skills_list: List[str], resume_text: str) -> Dict[str, Any]:
    found = []
    fuzzy_matches = []
    rt = resume_text.lower()
    for s in skills_list:
        s_norm = s.lower()
        if phrase_in_text(s_norm, rt):
            found.append(s)
        else:
            maxr = 0.0
            for window in re.findall(r'([a-z0-9\+\.#\- ]{2,60})', rt):
                r = fuzzy_ratio(s_norm, window)
                if r > maxr:
                    maxr = r
            if maxr > 0.85:
                fuzzy_matches.append({"skill": s, "score": maxr})
    return {"found": found, "fuzzy": fuzzy_matches, "found_count": len(found) + len(fuzzy_matches)}

def compute_ats_score(resume_text: str, job_text: str,
                      required_skills: List[str] = None,
                      preferred_skills: List[str] = None) -> Dict[str, Any]:
    resume = normalize_text(resume_text)
    job = normalize_text(job_text)
    required_skills = required_skills or []
    preferred_skills = preferred_skills or []

    req_found = []
    req_missing = []
    for r in required_skills:
        if phrase_in_text(r, resume):
            req_found.append(r)
        else:
            if fuzzy_ratio(r.lower(), resume) > 0.9:
                req_found.append(r)
            else:
                req_missing.append(r)
    req_coverage = (len(req_found) / len(required_skills)) if required_skills else 1.0

    skill_all = list(set(required_skills + preferred_skills))
    skill_match = compute_skill_matches(skill_all, resume)
    required_found = [s for s in skill_match.get("found", []) if s in required_skills]
    preferred_found = [s for s in skill_match.get("found", []) if s in preferred_skills]
    fuzzy_found = skill_match.get("fuzzy", [])

    kw_info = compute_keyword_matches(job, resume)
    keyword_ratio = (kw_info["found_count"] / kw_info["job_count"]) if kw_info["job_count"] else 0.0

    semantic_score = fuzzy_ratio(job, resume)

    weights = {
        "required": 0.40,
        "skills": 0.30,
        "keywords": 0.20,
        "semantic": 0.10
    }

    required_component = req_coverage * 100
    total_skills = len(skill_all) if skill_all else 1
    skills_matched_count = len(required_found) + len(preferred_found) + len(fuzzy_found)
    skills_component = (skills_matched_count / total_skills) * 100

    keywords_component = keyword_ratio * 100
    semantic_component = semantic_score * 100

    final_score = (
        weights["required"] * required_component +
        weights["skills"] * skills_component +
        weights["keywords"] * keywords_component +
        weights["semantic"] * semantic_component
    )

    if required_skills and len(req_missing) > 0:
        penalty = (len(req_missing) / len(required_skills)) * 0.25 * 100
        final_score = max(0.0, final_score - penalty)

    result = {
        "score": round(final_score, 2),
        "breakdown": {
            "required_coverage_pct": round(req_coverage * 100, 2),
            "skills_component_pct": round(skills_component, 2),
            "keywords_component_pct": round(keywords_component, 2),
            "semantic_component_pct": round(semantic_component, 2),
        },
        "details": {
            "required_found": req_found,
            "required_missing": req_missing,
            "skills_found": required_found + preferred_found,
            "fuzzy_skill_matches": fuzzy_found,
            "keyword_matches": kw_info["found"]
        }
    }
    return result
