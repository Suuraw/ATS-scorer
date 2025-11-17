# LLM Integration Guide for ATS-Scorer

## 📚 Table of Contents
1. [Why Add an LLM Layer?](#why-add-an-llm-layer)
2. [LLM Use Cases](#llm-use-cases)
3. [Architecture Options](#architecture-options)
4. [Implementation Guide](#implementation-guide)
5. [Code Examples](#code-examples)
6. [Best Practices](#best-practices)

---

## Why Add an LLM Layer?

### Current System Capabilities
The existing ATS-Scorer can:
- ✅ Parse resumes and job descriptions
- ✅ Calculate semantic similarity scores
- ✅ Identify missing skills
- ✅ Provide numerical metrics

### What's Missing? **Human-Readable Explanations**

**The Problem:**
A user sees: `"ATS Score: 78.5, Missing Skills: ['kubernetes', 'aws lambda']"`

**The Questions:**
- Why did I get 78.5 and not 85?
- How important are these missing skills?
- What should I improve first?
- Can you rewrite my resume bullet points?
- How do I phrase my experience better?

**The Solution: Large Language Models (LLMs)**

LLMs like GPT-4, Claude, or Llama can:
- 🤖 Generate natural language explanations
- 📝 Suggest resume improvements
- 💡 Provide actionable feedback
- ✍️ Rewrite content for better ATS scores
- 🎯 Prioritize recommendations

---

## LLM Use Cases

### 1. **Score Explanation** (Most Important)
**What it does:**
Converts numerical scores into human-readable insights.

**Example:**
```
Input: {"ats_score": 78.5, "missing_skills": ["kubernetes", "aws lambda"]}

Output (LLM Generated):
"Your resume scored 78.5 out of 100, which is a strong match! You align well 
with the job requirements in Python development and Docker experience. However, 
the job specifically requires Kubernetes and AWS Lambda experience, which are 
not evident in your resume. Adding these skills or relevant projects could 
increase your score to 85+. I recommend highlighting any container orchestration 
work you've done, even if not specifically Kubernetes."
```

### 2. **Resume Improvement Suggestions**
**What it does:**
Analyzes resume content and suggests specific improvements.

**Example:**
```
Input: Resume section: "Worked on web applications using React"

Output (LLM Generated):
"Consider rephrasing to: 'Developed responsive web applications using React, 
serving 10,000+ users with 99.9% uptime. Implemented Redux for state management 
and integrated RESTful APIs.' 

This version:
- Uses action verbs (Developed, Implemented)
- Includes quantifiable metrics (10,000+ users, 99.9% uptime)
- Specifies technical details (Redux, RESTful APIs)
- Matches ATS keyword patterns"
```

### 3. **Skill Gap Prioritization**
**What it does:**
Helps users understand which missing skills to learn first.

**Example:**
```
Input: Missing skills: ["kubernetes", "terraform", "jenkins", "grafana"]

Output (LLM Generated):
"Priority Ranking:
1. Kubernetes (Critical): Required skill mentioned 5 times in JD. Core to DevOps 
   role. Learn: Kubernetes basics, pod management, deployments.
2. Jenkins (High): CI/CD automation is essential. Alternatives: GitHub Actions, 
   GitLab CI.
3. Terraform (Medium): Infrastructure-as-code is important but can be learned 
   on the job.
4. Grafana (Low): Monitoring tool, nice to have but not critical."
```

### 4. **Personalized Cover Letter Generation**
**What it does:**
Creates cover letters tailored to the job based on resume + JD match.

**Example:**
```
Input: Resume + Job Description + ATS Score

Output (LLM Generated):
"Dear Hiring Manager,

I am excited to apply for the Senior Software Engineer position. With 5 years 
of experience in Python development and a proven track record in building 
scalable microservices, I am confident I can contribute to your team.

My experience aligns strongly with your requirements:
- Architected microservices handling 1M+ requests/day (matches your scale requirements)
- Led migration to Docker/Kubernetes (matches your containerization needs)
- Implemented CI/CD pipelines reducing deployment time by 60% (matches your DevOps culture)

While I note your requirement for AWS Lambda experience, I have extensive 
experience with similar serverless architectures using Azure Functions, which 
translates directly to AWS Lambda concepts..."
```

### 5. **Interview Preparation Insights**
**What it does:**
Predicts likely interview questions based on JD and resume gaps.

**Example:**
```
Input: JD + Resume + Missing Skills

Output (LLM Generated):
"Likely Interview Questions:

1. 'I see you haven't worked with Kubernetes. How would you approach learning it?'
   Suggested Answer: Highlight your Docker experience and explain how Kubernetes 
   is a natural extension...

2. 'Tell me about a time you scaled a system'
   Prepare: Your microservices project (mention 10x traffic increase handled)...

3. 'What's your experience with AWS?'
   Bridge the gap: Discuss your Azure experience and AWS certifications you're pursuing..."
```

### 6. **Resume Section Rewriting**
**What it does:**
Rewrites resume sections to better match job description language.

**Example:**
```
Input: 
- Resume: "Built websites"
- JD keywords: "full-stack development", "responsive design", "user experience"

Output (LLM Generated):
"Before: Built websites
After: Engineered full-stack web applications with responsive design, optimizing 
user experience across devices and increasing engagement by 40%"
```

### 7. **Skill Translation & Matching**
**What it does:**
Maps candidate's experience to job requirements even with different terminology.

**Example:**
```
Input:
- Resume: "Java Spring Boot REST APIs"
- JD: "Backend microservices development"

Output (LLM Generated):
"✓ Strong Match Detected:
Your 'Java Spring Boot REST APIs' experience directly translates to the job's 
'Backend microservices development' requirement. Spring Boot is specifically 
designed for microservices. Make sure to emphasize:
- Microservice architecture patterns you've used
- Inter-service communication (REST, messaging)
- Service discovery, load balancing
- Database per service pattern"
```

---

## Architecture Options

### Option 1: **Cloud-Based LLM APIs** (Recommended for MVP)

**Providers:**
- OpenAI (GPT-4, GPT-3.5-turbo)
- Anthropic (Claude 3.5)
- Google (Gemini)
- Azure OpenAI

**Pros:**
- ✅ No model hosting required
- ✅ Best quality responses
- ✅ Regular model updates
- ✅ Easy to implement
- ✅ Scales automatically

**Cons:**
- ❌ Costs per API call ($0.001-0.03 per request)
- ❌ Requires internet connection
- ❌ Data sent to third party (privacy concerns)
- ❌ Rate limits

**Best For:**
- Quick prototyping
- Production MVP
- Budget < $100/month for 5000 requests

**Architecture Diagram:**
```
ATS-Scorer Backend
    ↓
[New LLM Service Layer]
    ↓
OpenAI/Claude API
    ↓
Generated Explanations
```

---

### Option 2: **Self-Hosted Open Source LLMs**

**Models:**
- Llama 3.1 (8B, 70B)
- Mistral 7B
- Phi-3 (lightweight)
- Gemma 2

**Hosting Options:**
- Ollama (local development)
- vLLM (production server)
- HuggingFace TGI (Text Generation Inference)
- LiteLLM (unified interface)

**Pros:**
- ✅ No per-request costs (after setup)
- ✅ Complete data privacy
- ✅ No rate limits
- ✅ Customizable/fine-tunable

**Cons:**
- ❌ Requires GPU server ($50-500/month)
- ❌ Model management overhead
- ❌ Slightly lower quality than GPT-4
- ❌ Slower response times

**Best For:**
- Privacy-sensitive data
- High volume usage (>10k requests/month)
- Organizations with GPU infrastructure

**Architecture Diagram:**
```
ATS-Scorer Backend
    ↓
[LLM Service Layer]
    ↓
Local Ollama Server
    ↓
Llama 3.1 Model
    ↓
Generated Explanations
```

---

### Option 3: **Hybrid Approach** (Best of Both Worlds)

**Strategy:**
- Use simple embedding model (current) for scoring
- Use cloud LLM for explanation generation
- Cache LLM responses for common patterns
- Fallback to local model for privacy-critical data

**Architecture Diagram:**
```
                    ATS-Scorer Backend
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
  [Embedding Model]  [LLM Service]    [Cache Layer]
  (sentence-         (Decision        (Redis)
   transformers)      Router)
        │                  │
        │      ┌───────────┼───────────┐
        │      ▼                       ▼
        │  [OpenAI API]         [Local Llama]
        │  (Complex tasks)      (Simple tasks)
        │      │                       │
        └──────┴───────────────────────┘
                        │
                 Final Response
```

---

## Implementation Guide

### Phase 1: Setup (Choose Your LLM Provider)

#### Option A: OpenAI Setup

**Step 1:** Install dependencies
```bash
pip install openai python-dotenv
```

**Step 2:** Update requirements.txt
```txt
# Add these lines to requirements.txt
openai>=1.0.0
python-dotenv>=1.0.0
```

**Step 3:** Create .env file (never commit this!)
```bash
# .env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o-mini  # or gpt-4o for better quality
```

**Step 4:** Add .env to .gitignore
```bash
echo ".env" >> .gitignore
```

#### Option B: Ollama Setup (Local/Free)

**Step 1:** Install Ollama
```bash
# Windows: Download from https://ollama.ai
# Linux/Mac:
curl -fsSL https://ollama.ai/install.sh | sh
```

**Step 2:** Pull a model
```bash
ollama pull llama3.1:8b
```

**Step 3:** Install Python client
```bash
pip install ollama
```

**Step 4:** Update requirements.txt
```txt
# Add this line
ollama>=0.1.0
```

---

### Phase 2: Create LLM Service Module

Create a new file: `helpers/llm_service.py`

```python
# helpers/llm_service.py

import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Choose your provider
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # or "ollama"


# ============================================
# OpenAI Implementation
# ============================================
if LLM_PROVIDER == "openai":
    from openai import OpenAI
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    def generate_completion(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """Generate completion using OpenAI."""
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"


# ============================================
# Ollama Implementation
# ============================================
elif LLM_PROVIDER == "ollama":
    import ollama
    
    MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    
    def generate_completion(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """Generate completion using Ollama."""
        try:
            response = ollama.chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options={"temperature": temperature}
            )
            return response['message']['content']
        except Exception as e:
            return f"Error generating response: {str(e)}"


# ============================================
# High-Level LLM Functions
# ============================================

def explain_ats_score(ats_result: Dict) -> str:
    """
    Generate a human-readable explanation of the ATS score.
    
    Args:
        ats_result: The result from ats_score_from_json()
    
    Returns:
        Natural language explanation
    """
    system_prompt = """You are an expert career coach and ATS (Applicant Tracking System) specialist.
    Your job is to explain resume scores in a helpful, encouraging, and actionable way.
    Focus on what the candidate did well and provide specific, prioritized suggestions for improvement."""
    
    user_prompt = f"""
    A candidate's resume has been scored against a job description. Here are the results:
    
    ATS Score: {ats_result.get('ats_score', 0)}/100
    Semantic Similarity: {ats_result.get('semantic_similarity', 0)}
    
    Section Scores:
    {json.dumps(ats_result.get('details', []), indent=2)}
    
    Missing Skills: {', '.join(ats_result.get('missing_skills', [])[:10])}
    Present Skills: {', '.join(ats_result.get('present_skills', [])[:10])}
    Skill Coverage: {ats_result.get('coverage_ratio', 0)*100}%
    
    Please provide:
    1. A brief, encouraging summary of the overall score
    2. Top 3 strengths (what matched well)
    3. Top 3 areas for improvement (prioritized by impact)
    4. Specific, actionable next steps
    
    Keep the response concise (under 300 words) and motivating.
    """
    
    return generate_completion(system_prompt, user_prompt, temperature=0.7)


def suggest_resume_improvements(resume_section: str, jd_section: str, section_name: str) -> str:
    """
    Suggest improvements for a specific resume section based on JD.
    
    Args:
        resume_section: The candidate's resume section text
        jd_section: The corresponding job description section text
        section_name: Name of the section (e.g., "Skills", "Experience")
    
    Returns:
        Specific improvement suggestions
    """
    system_prompt = """You are an expert resume writer who specializes in optimizing resumes for ATS systems.
    You provide specific, actionable suggestions with before/after examples."""
    
    user_prompt = f"""
    Analyze this resume {section_name} section and suggest improvements to better match the job requirements:
    
    RESUME {section_name.upper()}:
    {resume_section[:500]}...
    
    JOB REQUIREMENTS:
    {jd_section[:500]}...
    
    Provide:
    1. 2-3 specific phrases/bullet points from the resume that could be improved
    2. For each, provide a rewritten version that:
       - Uses stronger action verbs
       - Includes quantifiable metrics where possible
       - Incorporates keywords from the job description
       - Maintains truthfulness (don't invent achievements)
    
    Format as:
    ❌ Before: [original]
    ✅ After: [improved version]
    Why: [brief explanation]
    """
    
    return generate_completion(system_prompt, user_prompt, temperature=0.5)


def prioritize_missing_skills(missing_skills: List[str], jd_text: str) -> str:
    """
    Prioritize which missing skills the candidate should focus on.
    
    Args:
        missing_skills: List of skills missing from resume
        jd_text: Full job description text
    
    Returns:
        Prioritized list with learning recommendations
    """
    system_prompt = """You are a career development advisor who helps candidates prioritize skill development.
    You understand which skills are critical vs. nice-to-have and provide practical learning paths."""
    
    user_prompt = f"""
    A candidate is missing these skills for a job:
    {', '.join(missing_skills[:15])}
    
    Job Description Context:
    {jd_text[:1000]}...
    
    Please:
    1. Categorize skills into: Critical (must-have), Important (should-have), Nice-to-have
    2. For top 5 Critical/Important skills, suggest:
       - Why it matters for this role
       - How long to learn (realistic timeframe)
       - Best free resource to start learning
       - Alternative skills that might compensate
    
    Be encouraging but realistic.
    """
    
    return generate_completion(system_prompt, user_prompt, temperature=0.6)


def generate_cover_letter(resume_data: Dict, jd_data: Dict, ats_result: Dict, company_name: str = "the company") -> str:
    """
    Generate a personalized cover letter based on resume-JD match.
    
    Args:
        resume_data: Processed resume data
        jd_data: Processed job description data
        ats_result: ATS scoring result
        company_name: Name of the company (optional)
    
    Returns:
        Draft cover letter
    """
    system_prompt = """You are an expert cover letter writer. You create compelling, personalized 
    cover letters that highlight relevant experience and address job requirements naturally.
    Your letters are professional yet conversational, specific yet concise (under 400 words)."""
    
    # Extract key info
    resume_sections = {s['section']: s['text'][:300] for s in resume_data.get('processed_sections', [])}
    jd_sections = {s['section']: s['text'][:300] for s in jd_data.get('processed_sections', [])}
    
    user_prompt = f"""
    Write a cover letter for this job application:
    
    CANDIDATE'S EXPERIENCE (highlights):
    Skills: {resume_sections.get('skills', 'N/A')}
    Experience: {resume_sections.get('experience', 'N/A')}
    
    JOB REQUIREMENTS:
    {jd_sections.get('responsibilities', jd_sections.get('general', 'N/A'))}
    
    MATCH ANALYSIS:
    - ATS Score: {ats_result.get('ats_score', 0)}/100
    - Strong matches: {', '.join(ats_result.get('present_skills', [])[:5])}
    - Skills to address: {', '.join(ats_result.get('missing_skills', [])[:3])}
    
    Write a cover letter that:
    1. Opens with enthusiasm and a strong hook
    2. Highlights 2-3 most relevant experiences with specific examples
    3. Addresses skill gaps honestly but positively (e.g., "eager to expand into...")
    4. Closes with confidence and a call to action
    5. Uses "{company_name}" naturally
    
    Maintain professional tone but avoid clichés like "I am writing to apply..."
    """
    
    return generate_completion(system_prompt, user_prompt, temperature=0.7)


def generate_interview_prep(resume_data: Dict, jd_data: Dict, ats_result: Dict) -> str:
    """
    Generate likely interview questions and preparation tips.
    
    Args:
        resume_data: Processed resume data
        jd_data: Processed job description data
        ats_result: ATS scoring result
    
    Returns:
        Interview preparation guide
    """
    system_prompt = """You are an interview coach who helps candidates prepare for technical interviews.
    You predict likely questions based on job requirements and candidate gaps, and provide strategic advice."""
    
    user_prompt = f"""
    Help this candidate prepare for their interview:
    
    JOB REQUIREMENTS:
    {json.dumps([s['text'][:200] for s in jd_data.get('processed_sections', [])[:3]], indent=2)}
    
    CANDIDATE'S BACKGROUND:
    {json.dumps([s['text'][:200] for s in resume_data.get('processed_sections', [])[:3]], indent=2)}
    
    MATCH ANALYSIS:
    - Score: {ats_result.get('ats_score', 0)}/100
    - Strengths: {', '.join(ats_result.get('present_skills', [])[:5])}
    - Gaps: {', '.join(ats_result.get('missing_skills', [])[:5])}
    
    Provide:
    1. 5 most likely technical questions (based on JD requirements)
    2. 3 behavioral questions (based on role type)
    3. 2-3 questions about resume gaps/missing skills
    4. For each question, provide:
       - Why they'll ask this
       - Key points to cover in your answer
       - Example response structure
    
    Be strategic: help them address weaknesses proactively.
    """
    
    return generate_completion(system_prompt, user_prompt, temperature=0.6)


# ============================================
# Utility Functions
# ============================================

def test_llm_connection() -> bool:
    """Test if LLM provider is properly configured."""
    try:
        response = generate_completion(
            "You are a helpful assistant.",
            "Respond with just the word 'SUCCESS' if you can read this.",
            temperature=0
        )
        return "SUCCESS" in response.upper()
    except Exception as e:
        print(f"LLM connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the LLM connection
    print(f"Testing {LLM_PROVIDER} connection...")
    if test_llm_connection():
        print("✅ LLM connection successful!")
    else:
        print("❌ LLM connection failed. Check your configuration.")
```

---

### Phase 3: Add LLM Endpoints to API

Create a new controller: `controllers/llm_insights.py`

```python
# controllers/llm_insights.py

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import os
import json

from helpers.llm_service import (
    explain_ats_score,
    suggest_resume_improvements,
    prioritize_missing_skills,
    generate_cover_letter,
    generate_interview_prep
)
from helpers.embedding_utils import ats_score_with_skill_gap

router = APIRouter(prefix="/llm", tags=["LLM Insights"])
DATA_DIR = os.path.join("data", "processed")


# ============================================
# Pydantic Models for Request Bodies
# ============================================

class ScoreExplanationRequest(BaseModel):
    resume_filename: str
    jd_filename: str


class SectionImprovementRequest(BaseModel):
    resume_section_text: str
    jd_section_text: str
    section_name: str


class CoverLetterRequest(BaseModel):
    resume_filename: str
    jd_filename: str
    company_name: Optional[str] = "the company"


# ============================================
# Endpoints
# ============================================

@router.get("/explain-score")
async def get_score_explanation(
    resume_filename: str = Query(..., description="Processed resume JSON filename"),
    jd_filename: str = Query(..., description="Processed JD JSON filename")
):
    """
    Get a natural language explanation of the ATS score.
    
    This endpoint:
    1. Computes the ATS score
    2. Sends results to LLM
    3. Returns human-readable explanation
    
    Example:
        GET /api/llm/explain-score?resume_filename=john_doe_processed.json&jd_filename=swe_jd_processed.json
    """
    try:
        # Load processed files
        resume_path = os.path.join(DATA_DIR, resume_filename)
        jd_path = os.path.join(DATA_DIR, jd_filename)
        
        if not os.path.exists(resume_path) or not os.path.exists(jd_path):
            raise HTTPException(status_code=404, detail="One or both files not found")
        
        with open(resume_path, "r", encoding="utf-8") as f:
            resume_data = json.load(f)
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_data = json.load(f)
        
        # Compute ATS score with skill gap
        ats_result = ats_score_with_skill_gap(resume_data, jd_data)
        
        # Generate explanation using LLM
        explanation = explain_ats_score(ats_result)
        
        return {
            "message": "Score explanation generated successfully",
            "ats_score": ats_result['ats_score'],
            "explanation": explanation,
            "raw_data": ats_result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/improve-section")
async def improve_resume_section(request: SectionImprovementRequest):
    """
    Get suggestions to improve a specific resume section.
    
    Request body:
    {
        "resume_section_text": "Your resume section content...",
        "jd_section_text": "Job description section content...",
        "section_name": "Skills" or "Experience" etc.
    }
    """
    try:
        suggestions = suggest_resume_improvements(
            request.resume_section_text,
            request.jd_section_text,
            request.section_name
        )
        
        return {
            "message": "Improvement suggestions generated",
            "section": request.section_name,
            "suggestions": suggestions
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/prioritize-skills")
async def get_skill_priorities(
    resume_filename: str = Query(...),
    jd_filename: str = Query(...)
):
    """
    Get a prioritized list of missing skills with learning recommendations.
    """
    try:
        # Load files
        resume_path = os.path.join(DATA_DIR, resume_filename)
        jd_path = os.path.join(DATA_DIR, jd_filename)
        
        with open(resume_path, "r", encoding="utf-8") as f:
            resume_data = json.load(f)
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_data = json.load(f)
        
        # Get missing skills
        ats_result = ats_score_with_skill_gap(resume_data, jd_data)
        missing_skills = ats_result.get('missing_skills', [])
        
        # Get full JD text
        jd_text = " ".join([s['text'] for s in jd_data.get('processed_sections', [])])
        
        # Generate prioritization
        priorities = prioritize_missing_skills(missing_skills, jd_text)
        
        return {
            "message": "Skill prioritization generated",
            "total_missing": len(missing_skills),
            "priorities": priorities
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/generate-cover-letter")
async def create_cover_letter(request: CoverLetterRequest):
    """
    Generate a personalized cover letter based on resume-JD match.
    
    Request body:
    {
        "resume_filename": "john_doe_processed.json",
        "jd_filename": "swe_jd_processed.json",
        "company_name": "TechCorp" (optional)
    }
    """
    try:
        # Load files
        resume_path = os.path.join(DATA_DIR, request.resume_filename)
        jd_path = os.path.join(DATA_DIR, request.jd_filename)
        
        with open(resume_path, "r", encoding="utf-8") as f:
            resume_data = json.load(f)
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_data = json.load(f)
        
        # Get ATS result
        ats_result = ats_score_with_skill_gap(resume_data, jd_data)
        
        # Generate cover letter
        cover_letter = generate_cover_letter(
            resume_data,
            jd_data,
            ats_result,
            request.company_name
        )
        
        return {
            "message": "Cover letter generated",
            "cover_letter": cover_letter,
            "ats_score": ats_result['ats_score']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/interview-prep")
async def get_interview_preparation(
    resume_filename: str = Query(...),
    jd_filename: str = Query(...)
):
    """
    Generate interview preparation guide with likely questions and answers.
    """
    try:
        # Load files
        resume_path = os.path.join(DATA_DIR, resume_filename)
        jd_path = os.path.join(DATA_DIR, jd_filename)
        
        with open(resume_path, "r", encoding="utf-8") as f:
            resume_data = json.load(f)
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_data = json.load(f)
        
        # Get ATS result
        ats_result = ats_score_with_skill_gap(resume_data, jd_data)
        
        # Generate interview prep
        prep_guide = generate_interview_prep(resume_data, jd_data, ats_result)
        
        return {
            "message": "Interview preparation guide generated",
            "preparation_guide": prep_guide,
            "ats_score": ats_result['ats_score']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```

---

### Phase 4: Register LLM Router in Main App

Edit `app.py`:

```python
# app.py
import uvicorn
from fastapi import FastAPI
from controllers import parser, processing_controller, ats_score, llm_insights  # Add llm_insights

app = FastAPI(
    title="ATS Resume Parser API",
    description="FastAPI backend for resume parsing, job description processing, and ATS score evaluation with LLM insights",
    version="2.0.0"  # Updated version
)

@app.get("/")
def say_hello():
    return {"message": "Hello from ATS Parser API with LLM insights!"}

# Register all routers
app.include_router(parser.router, prefix="/api", tags=["Parser"])
app.include_router(processing_controller.router, prefix="/api", tags=["Processing"])
app.include_router(ats_score.router, prefix="/api", tags=["ATS Score"])
app.include_router(llm_insights.router, prefix="/api", tags=["LLM Insights"])  # New!

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=3000, reload=True)
```

---

### Phase 5: Test Your LLM Integration

**Step 1:** Start the server
```bash
python app.py
```

**Step 2:** Visit the docs
```
http://localhost:3000/docs
```

**Step 3:** Test the new endpoints

1. **Explain Score:**
```bash
curl "http://localhost:3000/api/llm/explain-score?resume_filename=john_doe_processed.json&jd_filename=swe_jd_processed.json"
```

2. **Improve Section:**
```bash
curl -X POST "http://localhost:3000/api/llm/improve-section" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_section_text": "Worked on web applications",
    "jd_section_text": "Build scalable microservices with React and Node.js",
    "section_name": "Experience"
  }'
```

3. **Prioritize Skills:**
```bash
curl "http://localhost:3000/api/llm/prioritize-skills?resume_filename=john_doe_processed.json&jd_filename=swe_jd_processed.json"
```

4. **Generate Cover Letter:**
```bash
curl -X POST "http://localhost:3000/api/llm/generate-cover-letter" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_filename": "john_doe_processed.json",
    "jd_filename": "swe_jd_processed.json",
    "company_name": "TechCorp"
  }'
```

---

## Best Practices

### 1. **Prompt Engineering**
✅ **Do:**
- Be specific in system prompts about tone, length, format
- Provide context (resume data, JD, score results)
- Request structured outputs (numbered lists, before/after)
- Set appropriate temperature (0.5-0.7 for factual, 0.7-0.9 for creative)

❌ **Don't:**
- Use vague prompts like "explain this"
- Send entire documents (use summaries/excerpts)
- Expect perfect consistency (LLMs have variability)

### 2. **Cost Management**
✅ **Do:**
- Cache common explanations (e.g., same resume+JD pair)
- Use cheaper models for simple tasks (gpt-4o-mini vs gpt-4o)
- Implement rate limiting
- Monitor token usage

❌ **Don't:**
- Send full documents in every request
- Use expensive models for all tasks
- Allow unlimited API calls

### 3. **Privacy & Security**
✅ **Do:**
- Inform users their data is sent to third-party LLM
- Offer local LLM option for sensitive data
- Anonymize PII before sending to LLM
- Store API keys in environment variables

❌ **Don't:**
- Log LLM requests/responses (may contain PII)
- Commit API keys to git
- Send data to LLM without user consent

### 4. **Error Handling**
✅ **Do:**
- Implement graceful fallbacks
- Retry on transient failures
- Return partial results if LLM fails
- Log errors for debugging

**Example:**
```python
def explain_ats_score_safe(ats_result: Dict) -> str:
    try:
        return explain_ats_score(ats_result)
    except Exception as e:
        # Fallback: return structured data instead
        return f"ATS Score: {ats_result['ats_score']}/100. Missing skills: {', '.join(ats_result['missing_skills'][:5])}"
```

### 5. **Performance Optimization**

**Caching Strategy:**
```python
import hashlib
import json
from functools import lru_cache

def get_cache_key(data: dict) -> str:
    """Generate cache key from data."""
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

# In-memory cache (for development)
explanation_cache = {}

def explain_ats_score_cached(ats_result: Dict) -> str:
    cache_key = get_cache_key(ats_result)
    
    if cache_key in explanation_cache:
        return explanation_cache[cache_key]
    
    explanation = explain_ats_score(ats_result)
    explanation_cache[cache_key] = explanation
    
    return explanation
```

**For production, use Redis:**
```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

def explain_ats_score_cached(ats_result: Dict) -> str:
    cache_key = get_cache_key(ats_result)
    
    # Check cache
    cached = r.get(cache_key)
    if cached:
        return cached.decode()
    
    # Generate new
    explanation = explain_ats_score(ats_result)
    
    # Cache for 1 hour
    r.setex(cache_key, 3600, explanation)
    
    return explanation
```

---

## Summary

**LLM Integration Checklist:**

- [ ] Choose LLM provider (OpenAI/Ollama/other)
- [ ] Install dependencies (`openai` or `ollama`)
- [ ] Create `helpers/llm_service.py` with core functions
- [ ] Create `controllers/llm_insights.py` with API endpoints
- [ ] Register router in `app.py`
- [ ] Set up environment variables (.env file)
- [ ] Test connection with `test_llm_connection()`
- [ ] Implement caching for cost optimization
- [ ] Add error handling and fallbacks
- [ ] Update documentation

**What You'll Gain:**

🎯 **Better User Experience:**
- Natural language explanations instead of numbers
- Actionable recommendations instead of raw data
- Personalized advice based on specific gaps

💼 **New Features:**
- Resume improvement suggestions
- Cover letter generation
- Interview preparation guides
- Skill learning roadmaps

🚀 **Competitive Advantage:**
- AI-powered insights = premium feature
- Differentiation from basic ATS checkers
- Higher user engagement and retention

---

**Next Steps:**
1. Start with OpenAI (easiest to implement)
2. Add the "Explain Score" feature first
3. Gather user feedback
4. Expand to other LLM features based on demand
5. Consider local LLM for scaling

Good luck with your LLM integration! 🚀
