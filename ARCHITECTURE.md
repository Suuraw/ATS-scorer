# ATS-Scorer Architecture Guide

## 📚 Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Data Flow](#data-flow)
4. [Component Details](#component-details)
5. [How Things Work Together](#how-things-work-together)
6. [Technology Stack](#technology-stack)

---

## Overview

**What is ATS-Scorer?**

ATS-Scorer is a FastAPI-based application that helps match resumes with job descriptions by calculating an "ATS score" (Applicant Tracking System score). Think of it as a smart system that reads both a resume and a job description, understands what they mean, and tells you how well they match.

**The Big Picture in Simple Words:**

Imagine you have a resume and a job description. Both are PDF files. This system:
1. **Reads** the PDFs and extracts the text
2. **Understands** the content by breaking it into meaningful sections (like Skills, Experience, Education)
3. **Converts** the text into mathematical representations (embeddings) that capture meaning
4. **Compares** the resume against the job description using AI
5. **Scores** how well they match (0-100 scale)
6. **Identifies** what skills are missing from the resume

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER / CLIENT                            │
│                    (Web Browser / API Client)                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                         │
│                         (app.py)                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐   │
│  │  Parser    │  │ Processing │  │     ATS Score          │   │
│  │  Router    │  │  Router    │  │     Router             │   │
│  └────────────┘  └────────────┘  └────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Helper Modules                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │ file_utils   │  │  processing  │  │ embedding_utils  │     │
│  │  - PDF read  │  │   _pipeline  │  │  - AI scoring    │     │
│  │  - Section   │  │  - Clean     │  │  - Embeddings    │     │
│  │    split     │  │  - Format    │  │  - Similarity    │     │
│  │  - Chunking  │  │              │  │  - Skill gap     │     │
│  └──────────────┘  └──────────────┘  └──────────────────┘     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI/ML Components                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Sentence Transformers (all-mpnet-base-v2)                │  │
│  │  - Converts text to 768-dimensional vectors               │  │
│  │  - Enables semantic similarity comparison                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      File Storage                                │
│  ┌──────────────────┐  ┌──────────────────────────────────┐    │
│  │   resumes/       │  │    data/processed/               │    │
│  │  - PDFs          │  │    - Processed JSONs             │    │
│  │  - Text chunks   │  │    - Ready for comparison        │    │
│  │  - Structured    │  │                                  │    │
│  │    JSONs         │  │                                  │    │
│  └──────────────────┘  └──────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Step-by-Step: How a Resume Gets Scored

**Step 1: Upload Phase**
```
User uploads → resume.pdf + job_description.pdf
                          ↓
              POST /api/parse-resume
                          ↓
              file_utils.py processes
```

**What happens:**
- PDFs are saved to `resumes/` folder
- Text is extracted from each page
- Content is identified and split into sections (Skills, Experience, etc.)
- Each section is broken into smaller "chunks" (1500 characters each)
- Chunks are saved as individual text files
- A structured JSON is created listing all chunks and sections

**Output Example:**
```json
{
  "file_name": "john_doe_resume.pdf",
  "sections": {
    "skills": ["resumes/john_doe_resume_skills_1.txt"],
    "experience": ["resumes/john_doe_resume_experience_1.txt", "..."],
    "education": ["resumes/john_doe_resume_education_1.txt"]
  },
  "metadata": {
    "total_sections": 5,
    "total_chunks": 8
  }
}
```

**Step 2: Processing Phase**
```
Structured JSON created → POST /api/resume/process?file_name=john_doe_resume_structured.json
                                      ↓
                        processing_pipeline.py processes
```

**What happens:**
- Reads the structured JSON
- Loads all text chunks from files
- Cleans the text (removes URLs, normalizes whitespace)
- Combines chunks by section
- Creates a "processed" JSON optimized for embedding

**Output Example:**
```json
{
  "file_name": "john_doe_resume.pdf",
  "processed_sections": [
    {
      "id": "john_doe_resume_skills",
      "section": "skills",
      "text": "python java javascript react node.js aws docker...",
      "metadata": {
        "tokens": 150,
        "processed_at": "2025-11-17T07:00:00"
      }
    }
  ]
}
```

**Step 3: Scoring Phase**
```
Both processed JSONs ready → GET /api/compute-ats-score?resume_filename=...&jd_filename=...
                                           ↓
                            embedding_utils.py computes score
```

**What happens:**

1. **Text Extraction**: Pulls text from each section
2. **Embedding Generation**: 
   - Each section's text is converted to a 768-dimensional vector
   - This vector captures the "meaning" of the text
   - Uses pre-trained AI model (all-mpnet-base-v2)

3. **Section Matching**:
   - Resume "Skills" section → compared to JD "Skills Required" section
   - Resume "Experience" section → compared to JD "Responsibilities" section
   - Uses both semantic similarity (AI understanding) and keyword matching

4. **Weighted Scoring**:
   - Skills: 35% weight
   - Experience: 35% weight
   - Projects: 15% weight
   - Summary: 10% weight
   - Achievements: 5% weight

5. **Skill Gap Analysis**:
   - Extracts specific skills from job description
   - Checks if each skill is present in resume
   - Lists missing skills

**Output Example:**
```json
{
  "ats_score": 78.5,
  "semantic_similarity": 0.785,
  "details": [
    {
      "resume_section": "skills",
      "matched_jd_section": "skills required",
      "semantic_pct": 82.5,
      "keyword_pct": 75.0,
      "blended_pct": 81.4,
      "weight": 0.35
    }
  ],
  "missing_skills": ["kubernetes", "aws lambda"],
  "present_skills": ["python", "docker", "react"],
  "coverage_ratio": 0.85
}
```

---

## Component Details

### 1. **app.py** - The Main Application
**Role:** Entry point of the application

**Simple Explanation:** 
This is like the receptionist of a building. It welcomes users, directs them to the right department (router), and makes sure everything is organized.

**What it does:**
- Starts the FastAPI server
- Registers all API endpoints (routers)
- Provides basic health check endpoint (`GET /`)

---

### 2. **controllers/** - API Endpoint Handlers

#### **parser.py**
**Role:** Handles PDF upload and initial parsing

**Simple Explanation:** 
This is like the mailroom. It receives documents (PDFs), opens them, reads the content, and organizes it into folders.

**Key Functions:**
- `parse_resume_and_jd()`: Accepts resume + JD PDFs, validates format, triggers extraction

**API Endpoint:**
- `POST /api/parse-resume` - Upload PDFs

#### **processing_controller.py**
**Role:** Triggers post-processing of parsed data

**Simple Explanation:**
This is like a data cleaner. It takes the organized content from the mailroom and formats it nicely for comparison.

**Key Functions:**
- `process_resume()`: Takes structured JSON, cleans it, prepares for embedding

**API Endpoint:**
- `POST /api/resume/process?file_name=...` - Process structured JSON

#### **ats_score.py**
**Role:** Computes the final ATS score

**Simple Explanation:**
This is like the evaluator. It takes the cleaned data and uses AI to compare how well the resume matches the job description.

**Key Functions:**
- `compute_ats_score()`: Loads processed JSONs, calls embedding utils, returns score

**API Endpoint:**
- `GET /api/compute-ats-score?resume_filename=...&jd_filename=...` - Get ATS score

---

### 3. **helpers/** - Core Logic Modules

#### **file_utils.py**
**Role:** PDF processing, text extraction, section splitting, chunking

**Simple Explanation:**
This is the document processing specialist. It knows how to:
- Open PDF files and read every word
- Recognize different sections (Skills, Experience, Education)
- Break long text into smaller pieces (chunks)

**Key Functions:**
- `save_uploaded_file()`: Saves uploaded PDF to disk
- `extract_text_from_pdf()`: Extracts and structures resume text
- `extract_jd_from_pdf()`: Extracts and structures job description text
- `split_into_sections()`: Identifies resume sections using keywords
- `chunk_text_for_embeddings()`: Breaks text into 1500-char chunks
- `normalize_text()`: Cleans text (lowercase, remove special chars)

**Section Keywords Recognized:**
- Resume: summary, objective, education, skills, experience, projects, achievements, certifications
- Job Description: responsibilities, requirements, qualifications, skills required, benefits

#### **processing_pipeline.py**
**Role:** Cleans and formats parsed data for embedding

**Simple Explanation:**
This is the quality control department. It takes the raw organized data and makes it perfect for AI processing.

**Key Functions:**
- `clean_text()`: Removes URLs, extra spaces, normalizes format
- `process_resume_json()`: Combines chunks, cleans text, creates final processed JSON
- `batch_process_all()`: Process multiple resumes at once (optional)

#### **embedding_utils.py**
**Role:** AI-powered scoring and skill gap analysis

**Simple Explanation:**
This is the brain of the operation. It uses artificial intelligence to:
- Understand what text means (not just keywords)
- Compare meanings mathematically
- Calculate how well things match

**Key Components:**

1. **Model Configuration:**
   - Uses `sentence-transformers/all-mpnet-base-v2` model
   - Converts text to 768-dimensional vectors
   - Supports GPU acceleration if available

2. **Core Functions:**
   - `embed_text_chunks()`: Converts text → AI vector
   - `safe_cosine()`: Measures similarity between vectors (-1 to 1)
   - `keyword_overlap_pct()`: Measures keyword matching
   - `compute_sectionwise_scores()`: Main scoring logic with section weights
   - `ats_score_from_json()`: Full ATS score computation
   - `semantic_skill_gap()`: Identifies missing skills

3. **Scoring Strategy:**
   - **Semantic Similarity (85%)**: AI-based understanding of meaning
   - **Keyword Overlap (15%)**: Direct keyword matching
   - **Blended Score**: Combines both approaches

4. **Section Mapping:**
   - Resume "skills" → JD "skills required"
   - Resume "experience" → JD "responsibilities"
   - Resume "projects" → JD "projects"
   - Resume "summary" → JD "job description"

---

## How Things Work Together

### Complete Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                     USER UPLOADS FILES                            │
│              resume.pdf + job_description.pdf                     │
└───────────────────────────┬──────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   parser.py   │
                    │  (Controller) │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ file_utils.py │ ← PDF → Text extraction
                    │   (Helper)    │ ← Section splitting
                    └───────┬───────┘ ← Chunking
                            │
                            ▼
                ┌───────────────────────┐
                │  Structured JSON      │
                │  saved to resumes/    │
                └───────┬───────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │ processing_controller │
            │     (Controller)      │
            └───────┬───────────────┘
                    │
                    ▼
            ┌───────────────────┐
            │ processing_       │ ← Clean text
            │ pipeline.py       │ ← Combine chunks
            │    (Helper)       │ ← Format for AI
            └───────┬───────────┘
                    │
                    ▼
        ┌───────────────────────────┐
        │   Processed JSON          │
        │   saved to data/processed │
        └───────┬───────────────────┘
                │
                ▼
        ┌───────────────────┐
        │   ats_score.py    │
        │   (Controller)    │
        └───────┬───────────┘
                │
                ▼
        ┌───────────────────┐
        │ embedding_utils.py│ ← Load AI model
        │     (Helper)      │ ← Generate embeddings
        └───────┬───────────┘ ← Compute similarity
                │             ← Calculate weights
                │             ← Identify skill gaps
                ▼
        ┌───────────────────┐
        │   ATS Score       │
        │   + Details       │
        │   + Missing Skills│
        └───────────────────┘
```

### Example: Complete Request Flow

**User Request:**
```bash
curl -X POST "http://localhost:3000/api/parse-resume" \
  -F "resume=@john_doe.pdf" \
  -F "jobD=@software_engineer_jd.pdf"
```

**Internal Flow:**

1. **FastAPI** receives request → routes to `parser.py`
2. **parser.py** validates PDFs → calls `file_utils.save_uploaded_file()`
3. **file_utils** saves PDFs → calls `extract_text_from_pdf()`
4. **PyMuPDF** reads PDF pages → extracts raw text
5. **file_utils** splits text → identifies sections (Skills, Experience, etc.)
6. **NLTK** tokenizes sentences → creates chunks
7. **file_utils** saves chunks as .txt files → creates structured JSON
8. **parser.py** returns response → user sees structured data

**User processes data:**
```bash
curl -X POST "http://localhost:3000/api/resume/process?file_name=john_doe_structured.json"
```

9. **processing_controller** loads JSON → calls `processing_pipeline.process_resume_json()`
10. **processing_pipeline** reads chunk files → cleans text → combines by section
11. Saves processed JSON to `data/processed/`

**User requests score:**
```bash
curl "http://localhost:3000/api/compute-ats-score?resume_filename=john_doe_processed.json&jd_filename=software_engineer_jd_processed.json"
```

12. **ats_score.py** loads both JSONs → calls `embedding_utils.ats_score_from_json()`
13. **embedding_utils** loads AI model → generates embeddings for each section
14. Compares resume sections to JD sections → calculates weighted score
15. Runs skill gap analysis → identifies missing skills
16. **ats_score.py** returns complete score report

---

## Technology Stack

### Core Framework
- **FastAPI**: Modern Python web framework for building APIs
  - Fast performance (ASGI server)
  - Automatic API documentation (/docs)
  - Type hints and validation

- **Uvicorn**: ASGI server to run FastAPI

### PDF & Text Processing
- **PyMuPDF (fitz)**: Extract text from PDF files
  - Fast and reliable
  - Handles complex PDF layouts

- **NLTK**: Natural Language Toolkit
  - Sentence tokenization
  - Text preprocessing

- **python-multipart**: Handle file uploads in FastAPI

### AI/ML Components
- **Sentence Transformers**: Generate semantic embeddings
  - Model: all-mpnet-base-v2
  - 768-dimensional vectors
  - Pre-trained on large text corpus

- **PyTorch**: Deep learning framework (dependency of sentence-transformers)
  - Handles tensor operations
  - GPU acceleration support

### File & Data Handling
- **JSON**: Structured data storage
- **Python os, re**: File system and regex operations

### Optional (mentioned but not in requirements.txt)
- **python-docx**: For DOCX support (future feature)

---

## Key Design Decisions

### 1. **Why Chunking?**
**Problem:** Long documents exceed embedding model input limits (512 tokens typically)

**Solution:** Break text into 1500-character chunks
- Each chunk is embedded separately
- Chunk embeddings are averaged for section representation
- Maintains semantic meaning while handling long documents

### 2. **Why Section-Based Scoring?**
**Problem:** Resume and JD have different structures

**Solution:** Match related sections
- Resume "Skills" → JD "Skills Required"
- Resume "Experience" → JD "Responsibilities"
- Weighted combination (Skills & Experience = 70% of score)

### 3. **Why Blended Scoring (Semantic + Keywords)?**
**Problem:** Pure semantic similarity might miss exact technical terms

**Solution:** 85% semantic + 15% keyword overlap
- Semantic: Understands "machine learning" ≈ "ML" ≈ "neural networks"
- Keywords: Ensures exact matches like "Python 3.9" are valued

### 4. **Why Separate Processing Steps?**
**Problem:** Processing PDFs and computing scores are expensive

**Solution:** Three-stage pipeline
- Parse once → save structured data
- Process once → save clean data
- Score multiple times → reuse processed data
- Enables caching and optimization

---

## Performance Considerations

### Current Architecture Characteristics:

1. **CPU vs GPU:**
   - Model inference runs on CPU by default
   - GPU support available if CUDA installed
   - GPU provides 5-10x speedup for embeddings

2. **Memory Usage:**
   - Model loading: ~500MB RAM
   - Per-request: ~50-100MB (depends on document size)
   - Embeddings stored in memory during computation

3. **Speed:**
   - PDF parsing: ~1-2 seconds per document
   - Embedding generation: ~0.5-1 second per section
   - Complete scoring: ~3-5 seconds for typical resume + JD

4. **Scaling Limitations:**
   - Single instance, synchronous processing
   - No database (filesystem only)
   - Model loaded per request (could be optimized)

---

## Security & Privacy Notes

1. **Data Storage:**
   - Uploaded files saved to `resumes/` folder
   - Processed data saved to `data/processed/`
   - Both folders in `.gitignore` (not committed to repo)

2. **Personal Information:**
   - Resume data contains PII (Personal Identifiable Information)
   - No encryption at rest currently
   - No access control on stored files

3. **API Security:**
   - No authentication currently
   - No rate limiting
   - Suitable for local/development use only

---

## Future Improvements

Based on the current architecture, potential enhancements:

1. **Database Integration:**
   - Store parsed data in PostgreSQL/MongoDB
   - Enable search and analytics
   - Track scoring history

2. **Caching:**
   - Cache embeddings to avoid recomputation
   - Redis for session storage
   - Model caching across requests

3. **Asynchronous Processing:**
   - Background task queue (Celery)
   - Async PDF processing
   - Parallel embedding generation

4. **API Enhancements:**
   - Authentication (JWT tokens)
   - Rate limiting
   - Batch processing endpoints

5. **Model Improvements:**
   - Fine-tune model on resume/JD data
   - Support multiple embedding models
   - Add re-ranking stage

---

## Summary

**ATS-Scorer** is a well-structured application that:

✅ **Separates concerns**: Controllers handle requests, helpers do heavy lifting

✅ **Pipelines data**: Parse → Process → Score (cacheable stages)

✅ **Uses modern AI**: Semantic embeddings for intelligent matching

✅ **Provides insights**: Not just a score, but skill gap analysis

✅ **Scales vertically**: Can improve with better hardware (GPU)

The architecture is clean, modular, and ready for enhancements like LLM integration, which we'll cover in the LLM Integration Guide!
