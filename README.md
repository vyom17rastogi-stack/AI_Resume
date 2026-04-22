# AI Resume Job Matcher (Backend)


## Overview

**AI Resume Job Matcher** is a FastAPI-based backend system that parses, cleans, and prepares resumes for AI-driven job matching.  
It can extract text from **PDF** and **DOCX** resumes, clean and lemmatize content, and preserve key entities like emails, phone numbers, and URLs.

---

## Tech Stack

**Backend:**  
- **Python 3.10+**  
- **FastAPI** – for building APIs  
- **PyPDF2**, **python-docx** – for parsing PDF & DOCX files  
- **NLTK** – for text preprocessing (tokenization, lemmatization, stopword removal)  
- **re (Regex)** – for entity extraction (emails, phones, URLs)  
- **Uvicorn** – ASGI server for FastAPI  

---
## Installation

### Clone the repository
```bash
git clone https://github.com/ShivamDhasmana1/ai_resume_job_matcher.git
cd ai_resume_job_matcher/Backend/Main_app
```

### Create and activate a virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Install dependencies
```bash
pip install -r ../requirements.txt
```

---

## Run the FastAPI Server

```bash
uvicorn main:app --reload
```

Your app will be live at:
```
http://127.0.0.1:8000
```

You can view the interactive Swagger UI docs at:
```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

| Method | Endpoint | Description |
|:------:|:----------|:-------------|
| **GET** | `/` | Health check endpoint |
| **POST** | `/upload-resume/` | Upload and parse resume (PDF/DOCX) |

**Example Response:**
```json
{
  "message": "Successfully parsed and saved to myfile.txt (4583 characters)"
}
```

---

## 🧹 Text Cleaning Workflow

1. **Extract text** from PDF/DOCX using `PyPDF2` or `python-docx`.  
2. **Identify and protect** key entities (emails, phone numbers, URLs).  
3. **Normalize** text: lowercase, remove punctuation, stopwords, and non-alphabetic characters.  
4. **Lemmatize** words to their root forms.  
5. **Reinsert** preserved entities back into the cleaned text.  

---

## Frontend (Prototype)

The frontend interface was **prototyped using [Lovable](https://lovable.dev)**, an AI-based web app builder, to quickly visualize and test the backend integration.  
Future updates may include a fully custom React or Next.js interface for enhanced flexibility and scalability.

---

## License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

---

## Author

**Shivam Dhasmana**  
B.Tech CSE | IMS Engineering College  
Passionate about AI, backend development, and building smart systems.
