from fastapi import APIRouter, HTTPException, Query
import os, json
from helpers.embedding_utils import ats_score_from_json

router = APIRouter()
DATA_DIR = os.path.join("data", "processed")


@router.get("/compute-ats-score")
async def compute_ats_score(
    resume_filename: str = Query("software-engineer-resume_processed.json"),
    jd_filename: str = Query("Full_Stack_Developer_Job_Description_processed.json")
):
    """
    Compute ATS similarity score between processed resume and JD JSONs.
    Allows passing custom filenames for flexibility.
    """
    try:
        resume_path = os.path.join(DATA_DIR, resume_filename)
        jd_path = os.path.join(DATA_DIR, jd_filename)

        if not os.path.exists(resume_path) or not os.path.exists(jd_path):
            raise HTTPException(
                status_code=404,
                detail=f"One or both files not found in {DATA_DIR}"
            )

        with open(resume_path, "r", encoding="utf-8") as f:
            resume_data = json.load(f)
        with open(jd_path, "r", encoding="utf-8") as f:
            jd_data = json.load(f)

        result = ats_score_from_json(resume_data, jd_data)

        return {"message": "ATS score computed successfully", "data": result}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in processed files.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing ATS score: {str(e)}")
