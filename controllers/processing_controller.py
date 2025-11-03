from fastapi import APIRouter
from helpers.processing_pipeline import process_resume_json
import os

router = APIRouter(prefix="/resume", tags=["Resume Processing"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # root of project
RESUME_DIR = os.path.join(BASE_DIR, "resumes")

@router.post("/process")
def process_resume(file_name: str):
    """
    Triggers post-processing for a given resume JSON file.
    Example: POST /api/resume/process?file_name=Sujay_Kumar_structured.json
    """
    input_path = os.path.join(RESUME_DIR, file_name)

    if not os.path.exists(input_path):
        return {"error": f"File not found: {input_path}"}

    output_path = process_resume_json(input_path)
    return {"message": "Processing complete", "output_file": output_path}
