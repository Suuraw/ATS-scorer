# Quick Start Guide: Understanding ATS-Scorer

Welcome! This guide helps you quickly understand what ATS-Scorer does and how to extend it.

## 🎯 What Does This App Do?

**In 30 seconds:**
ATS-Scorer is a smart resume analyzer that:
1. **Reads** your resume (PDF) and a job description (PDF)
2. **Understands** the content using AI
3. **Scores** how well they match (0-100)
4. **Identifies** what skills you're missing
5. **Helps** you improve your resume

Think of it as having a career advisor that reads both your resume and the job posting, then tells you: "You're a 78% match! Here's what you're missing: Kubernetes, AWS Lambda."

---

## 📂 Project Structure (Simple View)

```
ATS-scorer/
│
├── app.py                          # 🚪 Main entry point - starts the server
│
├── controllers/                    # 🎮 API endpoints (what users can call)
│   ├── parser.py                   # Upload PDFs
│   ├── processing_controller.py   # Process uploaded data
│   └── ats_score.py                # Get the match score
│
├── helpers/                        # 🛠️ The actual work happens here
│   ├── file_utils.py               # Read PDFs, split into sections
│   ├── processing_pipeline.py     # Clean and format data
│   └── embedding_utils.py          # AI scoring logic
│
├── requirements.txt                # 📦 Python packages needed
│
└── DOCUMENTATION/
    ├── ARCHITECTURE.md             # 📖 Deep dive into how it works
    └── LLM_INTEGRATION_GUIDE.md    # 🤖 How to add AI explanations
```

---

## 🔄 How Data Flows (3 Steps)

### Step 1: Upload & Parse
```
User uploads PDFs → parser.py → file_utils.py → Text extracted & saved
```
**Output:** Text chunks and structured JSON

### Step 2: Process
```
Structured JSON → processing_controller.py → processing_pipeline.py → Cleaned & formatted
```
**Output:** Processed JSON ready for AI

### Step 3: Score
```
Processed JSONs → ats_score.py → embedding_utils.py → AI comparison
```
**Output:** Match score + missing skills

---

## 🧠 How the AI Scoring Works

**Simple Explanation:**

1. **Text to Numbers:** AI converts text into 768 numbers (called "embeddings")
   - "Python developer with 5 years experience" → [0.23, -0.45, 0.67, ...]
   - These numbers capture the "meaning" of the text

2. **Compare Meanings:** Calculate how similar two sets of numbers are
   - Resume Skills [0.23, -0.45, ...] vs JD Requirements [0.25, -0.43, ...]
   - Similarity score: 0.85 (85% match)

3. **Weighted Score:** Different sections have different importance
   - Skills: 35% weight
   - Experience: 35% weight
   - Projects: 15% weight
   - Summary: 10% weight
   - Achievements: 5% weight

4. **Final Score:** Combine weighted scores → 78.5/100

---

## 🚀 Quick Setup (2 minutes)

```bash
# 1. Clone the repo (you probably already did this)
git clone https://github.com/Suuraw/ATS-scorer.git
cd ATS-scorer

# 2. Install Python packages
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Run the server
python app.py

# 4. Open your browser
# Go to: http://localhost:3000/docs
```

---

## 🎮 Try It Out (Example API Calls)

### 1. Upload Resume + Job Description
```bash
curl -X POST "http://localhost:3000/api/parse-resume" \
  -F "resume=@my_resume.pdf" \
  -F "jobD=@job_description.pdf"
```

### 2. Process the Files
```bash
curl -X POST "http://localhost:3000/api/resume/process?file_name=my_resume_structured.json"
curl -X POST "http://localhost:3000/api/resume/process?file_name=job_description_JD_structured.json"
```

### 3. Get Your ATS Score
```bash
curl "http://localhost:3000/api/compute-ats-score?resume_filename=my_resume_processed.json&jd_filename=job_description_JD_processed.json"
```

**Response you'll get:**
```json
{
  "ats_score": 78.5,
  "missing_skills": ["kubernetes", "aws lambda", "terraform"],
  "present_skills": ["python", "docker", "react", "node.js"],
  "coverage_ratio": 0.85,
  "details": [...]
}
```

---

## 🤖 Want to Add AI Explanations?

**Current:** You get numbers: `{"ats_score": 78.5, "missing_skills": ["kubernetes"]}`

**With LLM:** You get advice: 
> "Great match! You scored 78.5/100. Your Python and Docker skills align perfectly with the job. To boost your score, consider adding Kubernetes experience - it's mentioned 3 times in the job description. Try completing a Kubernetes tutorial or highlighting any container orchestration work you've done."

**How to add this?**
👉 See **[LLM_INTEGRATION_GUIDE.md](./LLM_INTEGRATION_GUIDE.md)** for complete instructions!

**Quick preview:**
1. Choose an AI provider (OpenAI, Ollama, etc.)
2. Add one file: `helpers/llm_service.py` (provided in guide)
3. Add one controller: `controllers/llm_insights.py` (provided in guide)
4. Get AI-powered explanations!

---

## 📚 Want to Learn More?

### For Understanding the System:
👉 **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Complete explanation of:
- How each component works
- Data flow diagrams
- Technology choices
- Design decisions
- Performance characteristics

### For Adding AI Features:
👉 **[LLM_INTEGRATION_GUIDE.md](./LLM_INTEGRATION_GUIDE.md)** - Step-by-step guide for:
- Adding natural language explanations
- Resume improvement suggestions
- Cover letter generation
- Interview preparation tips
- Complete code examples (copy-paste ready!)

---

## 🔧 Tech Stack (What's Under the Hood)

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Framework** | FastAPI | Handle HTTP requests |
| **Server** | Uvicorn | Run the FastAPI app |
| **PDF Reading** | PyMuPDF | Extract text from PDFs |
| **Text Processing** | NLTK | Split text into sentences |
| **AI Model** | Sentence-Transformers | Convert text → numbers for comparison |
| **Math** | PyTorch | Handle AI calculations |

---

## 💡 Common Questions

### Q: Do I need GPU for this?
**A:** No! It works on CPU (slower but functional). GPU makes it 5-10x faster if available.

### Q: How accurate is the scoring?
**A:** The AI similarity is quite good (85-90% accurate), but it's not perfect. It understands semantic meaning ("machine learning" ≈ "ML") but may miss some context.

### Q: Can I use this for hundreds of resumes?
**A:** Currently, it's designed for one-at-a-time processing. For batch processing, you'd need to add:
- Database (instead of file storage)
- Job queue (for parallel processing)
- Caching (for faster repeated comparisons)

### Q: Is my data private?
**A:** Yes, everything runs locally. Files are stored in the `resumes/` and `data/` folders (not committed to git). If you add LLM integration with cloud APIs, that data would be sent to the LLM provider.

### Q: How much does it cost to run?
**A:** 
- **Without LLM:** Free! (just your computer's electricity)
- **With cloud LLM (OpenAI):** ~$0.001-0.01 per resume analysis
- **With local LLM (Ollama):** Free! (but needs more powerful computer)

---

## 🛣️ Roadmap / Future Ideas

Based on the current architecture, here are natural extensions:

1. ✅ **LLM Integration** (guide available!)
   - Natural language explanations
   - Resume improvement suggestions

2. 🔲 **Web UI** (not implemented)
   - Drag-and-drop file upload
   - Visual score display
   - Side-by-side comparison

3. 🔲 **Database Integration** (not implemented)
   - Store analysis history
   - Track improvements over time
   - Compare multiple JDs

4. 🔲 **Batch Processing** (not implemented)
   - Process multiple resumes at once
   - Rank candidates

5. 🔲 **Resume Builder** (not implemented)
   - Template-based resume generation
   - ATS-optimized formatting
   - Real-time score updates as you type

---

## 🤝 Contributing

Want to improve ATS-Scorer? Here's how:

1. **Found a bug?** Open an issue
2. **Want to add a feature?** Check the roadmap, then create a PR
3. **Improved the docs?** PRs welcome!

**Good first contributions:**
- Add tests (currently no test suite!)
- Improve section detection keywords
- Add support for DOCX files
- Create a simple web UI
- Optimize embedding caching

---

## 📖 Summary

**ATS-Scorer in one sentence:**
> Upload a resume + job description → get an AI-powered match score + missing skills analysis.

**Ready to dive deeper?**
- 🏗️ [ARCHITECTURE.md](./ARCHITECTURE.md) - How everything works
- 🤖 [LLM_INTEGRATION_GUIDE.md](./LLM_INTEGRATION_GUIDE.md) - Add AI explanations

**Questions?** Open an issue on GitHub!

---

*Last updated: 2025-11-17*
