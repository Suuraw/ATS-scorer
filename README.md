# ATS Resume Parser API

Lightweight FastAPI-based project to parse resumes and job descriptions (PDF), prepare chunks for embeddings, and compute an ATS-style similarity score between a resume and a job description.

## 📚 Documentation

**New to this project?** Start here:
- 🚀 **[QUICK_START.md](./QUICK_START.md)** - Quick overview and setup (5 min read)
- 🏗️ **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Detailed explanation of how everything works
- 🤖 **[LLM_INTEGRATION_GUIDE.md](./LLM_INTEGRATION_GUIDE.md)** - Step-by-step guide to add AI-powered explanations

---

## Project structure

- `app.py` - FastAPI application and router registration.
- `controllers/` - API routers
  - `parser.py` - Endpoint to upload both resume and job description PDFs and return structured JSON.
  - `processing_controller.py` - Endpoint to trigger post-processing from a structured resume JSON (uses files saved under `resumes/`).
  - `ats_score.py` - Endpoint to compute ATS similarity between two processed JSON files in `data/processed`.
- `helpers/` - Utility modules
  - `file_utils.py` - PDF extraction, section splitting, chunking and saving text files + structured JSON.
  - `processing_pipeline.py` - Post-processing of the structured JSON into a single processed JSON used for embeddings.
- `resumes/` - Uploaded PDFs, intermediate text chunks and structured JSONs (gitignored).
- `data/processed/` - Processed JSON outputs (gitignored).
- `requirements.txt` - Python package dependencies.

## .gitignore notes

The repository includes a `.gitignore` that excludes runtime and large data folders:

- `__pycache__/` - compiled Python files.
- `.venv` - local virtual environment.
- `resumes` - uploaded PDFs and intermediate text chunks (keeps private resume data out of VCS).
- `data` - processed outputs and other generated data.

This is intentional: resume files, intermediate chunks, and processed data are not checked into git.

## Frameworks & key dependencies

- FastAPI - web framework for building the API.
- Uvicorn - ASGI server used to run the app.
- PyMuPDF (`fitz`) - PDF reading/extraction.
- python-docx - (if DOCX support is added/needed).
- python-multipart - for file uploads in FastAPI.
- nltk - sentence tokenization and chunking.
- sentence-transformers - embeddings / similarity (may pull heavy dependencies such as PyTorch).

See `requirements.txt` for the exact packages listed.

Notes about heavy packages:

- `sentence-transformers` can pull `torch` which is large. On Windows, pip will try to install a compatible wheel but if it fails you may need to install a prebuilt torch wheel from https://pytorch.org/.
- `PyMuPDF` sometimes requires Microsoft Visual C++ Redistributable on Windows. If `pip install PyMuPDF` fails, install the Visual C++ redistributable from Microsoft.

## Quick start (Windows)

Prerequisites:

- Python 3.8+ installed and on PATH.
- Recommended: 4+ GB free RAM for model-related packages, more if using sentence-transformers locally.

Open a terminal (PowerShell, CMD, or Git Bash). Commands below are shown for all three major shells.

1. Create and activate a virtual environment

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Command Prompt (cmd.exe):

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

Git Bash / bash.exe:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

2. Upgrade pip and install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `sentence-transformers` installation fails due to `torch`, follow instructions on https://pytorch.org/ to install a compatible `torch` wheel first, for example (CPU-only):

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers
```

3. (Optional) Ensure NLTK resources are available

The code tries to download required NLTK tokenizers automatically. If you see errors around tokenizers, run:

```python
python -c "import nltk; nltk.download('punkt')"
```

4. Run the API

You can run the app using the built-in uvicorn call in `app.py`:

```bash
python app.py
```

or run uvicorn directly for more control:

```bash
uvicorn app:app --host 0.0.0.0 --port 3000 --reload
```

The API will be available at: http://127.0.0.1:3000

Open the interactive docs at: http://127.0.0.1:3000/docs

## Endpoints (examples)

1. Health / root

GET /

2. Upload resume + job description (parser)

POST /api/parse-resume

- Content-Type: multipart/form-data
- Body: `resume` (file, PDF), `jobD` (file, PDF)

Example curl (Git Bash / Linux / WSL):

```bash
curl -X POST "http://127.0.0.1:3000/api/parse-resume" \
  -F "resume=@C:/path/to/your_resume.pdf" \
  -F "jobD=@C:/path/to/job_description.pdf"
```

The endpoint returns structured JSON files and also writes chunk text files and a structured JSON into the `resumes/` folder.

3. Post-process a structured resume JSON

POST /api/resume/process?file_name=<structured_json_filename>

Example:

```
POST /api/resume/process?file_name=Sujay_Kumar_structured.json
```

This will take the structured JSON (in `resumes/`) and create a processed JSON under `data/processed/`.

4. Compute ATS score

GET /api/compute-ats-score?resume_filename=<processed_resume.json>&jd_filename=<processed_jd.json>

Default values are provided in the code. Response includes computed similarity result.

## Windows-specific troubleshooting

- PyMuPDF install errors: install the Microsoft Visual C++ Redistributable.
- sentence-transformers / torch: use CPU wheel from PyTorch website if pip fails.
- File access issues: make sure your terminal has permission to read/write the `resumes/` and `data/` folders.

## Security & privacy

- This project stores uploaded resumes and job descriptions inside the `resumes/` directory by design. Keep that directory out of VCS (already in `.gitignore`).
- Do not commit personal/resume data to the repo.

## Next steps / improvements to consider

- Add a small test suite (pytest) to validate parser and pipeline.
- Add Dockerfile and docker-compose for reproducible local runs.
- Add optional model download step or use a hosted embedding API to avoid heavy local installs.

---

If you'd like, I can now:

- run a quick import check to confirm there are no syntax errors,
- or add a small example script that shows how to call the endpoints programmatically.
