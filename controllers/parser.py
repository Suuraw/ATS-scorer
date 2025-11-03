# app/controllers/parser.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from helpers.file_utils import save_uploaded_file, extract_text_from_pdf, extract_jd_from_pdf

router = APIRouter()

@router.post("/parse-resume")
async def parse_resume_and_jd(
    resume: UploadFile = File(...),
    jobD: UploadFile = File(...)
):
    """
    Accept both Resume and Job Description PDFs,
    extract text, split into sections, chunk, and return structured data.
    """
    # --- Validate file types ---
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Resume must be a PDF.")
    if not jobD.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Job Description must be a PDF.")

    try:
        # --- Save uploaded PDFs ---
        resume_path = save_uploaded_file(resume)
        jd_path = save_uploaded_file(jobD)

        # --- Extract structured text ---
        resume_data = extract_text_from_pdf(resume_path)
        jd_data = extract_jd_from_pdf(jd_path)

        # --- Response ---
        return {
            "resume": {
                "filename": resume.filename,
                "parsed": resume_data
            },
            "job_description": {
                "filename": jobD.filename,
                "parsed": jd_data
            },
            "summary": {
                "resume_sections": list(resume_data["sections"].keys()),
                "jd_sections": list(jd_data["sections"].keys())
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process files: {str(e)}")
