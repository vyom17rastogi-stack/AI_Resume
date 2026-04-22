from fastapi import FastAPI, File, UploadFile
import PyPDF2
import docx
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from Main_app.clean_text_module import clean_text
from Main_app.core.extract_skills import extract_skills_from_text
from Main_app.database.job_database import jobs
from Main_app.database.job_descriptions import job_descriptions
from Main_app.core.ai_matcher import ai_match_jobs
from Main_app.ats_scorer import compute_ats_score
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body
from typing import Optional

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    filename = file.filename

    if not (filename.endswith(".pdf") or filename.endswith(".docx")):
        return {"error": "Only PDF or DOCX files are supported."}

    temp_path = f"temp_{filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    text = ""
    if filename.endswith(".pdf"):
        with open(temp_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text() or ""
    else:
        doc = docx.Document(temp_path)
        text = "\n".join([p.text for p in doc.paragraphs])

    cleaned_output = clean_text(text)
    cleaned_text = cleaned_output["cleaned_text"]

    skills = extract_skills_from_text(cleaned_text)
    ai_matches = ai_match_jobs(cleaned_text, jobs)

    output_text_path = OUTPUT_DIR / "myfile.txt"
    output_matches_path = OUTPUT_DIR / "ai_job_matches.txt"
    
    with open(output_text_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    with open(output_matches_path, "w", encoding="utf-8") as f:
        for match in ai_matches:
            f.write(f"{match['job_title']} ({match['company']}) - {match['match_score']}%\n")

    os.remove(temp_path)

    return {
        "message": "Resume processed and AI job matches found",
        "cleaned_text": cleaned_text,
        "emails": cleaned_output["emails"],
        "phones": cleaned_output["phones"],
        "urls": cleaned_output["urls"],
        "skills": skills,
        "ai_job_matches": ai_matches
    }


@app.post("/analyze-resume/")
async def analyze_resume(data: dict):
    insights = [
        {
            "category": "Grammar & Clarity",
            "suggestions": ["Use active voice", "Fix typos in experience section"],
            "priority": "high"
        }
    ]
    return {"insights": insights}

@app.post("/score-resume/")
async def score_resume(
    resume_text: str = Body(..., example="cleaned resume text here"),
    job_description: str = Body(..., example="Job description text here"),
    required_skills: Optional[list] = Body(None, example=["python","fastapi"]),
    preferred_skills: Optional[list] = Body(None, example=["aws","docker"])
):
    result = compute_ats_score(resume_text, job_description, required_skills or [], preferred_skills or [])
    return {"message": "OK", "ats_result": result}


@app.get("/jobs/")
async def list_jobs():
    return {"jobs": [
        {
            "id": j.get("id"),
            "title": j.get("title"),
            "company": j.get("company"),
            "required_skills": j.get("required_skills", []),
            "preferred_skills": j.get("preferred_skills", [])
        }
        for j in jobs
    ]}


@app.post("/score-resume-all-jobs/")
async def score_resume_all_jobs(data: dict = Body(...)):
    resume_text = data.get("resume_text", "")
    if not resume_text:
        return {"error": "resume_text required"}

    results = []
    for j in jobs:
        job_id = j.get("id")
        jd = job_descriptions.get(job_id, "")
        required = j.get("required_skills", [])
        preferred = j.get("preferred_skills", [])
        ats = compute_ats_score(resume_text, jd, required, preferred)
        results.append({
            "id": job_id,
            "title": j.get("title"),
            "company": j.get("company"),
            "ats_result": ats
        })

    return {"message": "OK", "results": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
