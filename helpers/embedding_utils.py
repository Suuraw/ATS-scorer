import re
import os
from typing import Dict, List, Tuple, Optional

import numpy as np
import torch
from sentence_transformers import SentenceTransformer, util

# -------------------------
# Configuration
# -------------------------
MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
CHUNK_WORD_SIZE = 180
KEYWORD_BLEND = 0.15

SECTION_MAPPING = {
    "summary": ["job description", "responsibilities", "qualifications"],
    "skills": ["skills required", "skills", "requirements"],
    "experience": ["responsibilities", "qualifications", "experience"],
    "projects": ["responsibilities", "projects"],
    "achievements": ["qualifications", "responsibilities", "experience"]
}

SECTION_WEIGHTS = {
    "skills": 0.35,
    "experience": 0.35,
    "projects": 0.15,
    "summary": 0.1,
    "achievements": 0.05
}

# -------------------------
# Model load (global)
# -------------------------
_device = "cuda" if torch.cuda.is_available() else "cpu"
_model = SentenceTransformer(MODEL_NAME, device=_device)

# -------------------------
# Utilities
# -------------------------
def clean_text(text: str) -> str:
    """Minimal cleaning: lowercase, remove URLs, extra spaces, keep useful punctuation."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s\.\-\+#]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def chunk_text_words(text: str, chunk_size: int = CHUNK_WORD_SIZE) -> List[str]:
    words = text.split()
    if not words:
        return []
    if len(words) <= chunk_size:
        return [" ".join(words)]
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]


def embed_text_chunks(text: str, chunk_size: int = CHUNK_WORD_SIZE) -> torch.Tensor:
    """Chunk long text, embed, return mean embedding tensor."""
    chunks = chunk_text_words(text, chunk_size)
    if not chunks:
        dim = _model.get_sentence_embedding_dimension()
        return torch.zeros(dim, device=_device)
    embeddings = _model.encode(chunks, convert_to_tensor=True, show_progress_bar=False)
    if embeddings.dim() == 1:
        return embeddings
    return torch.mean(embeddings, dim=0)


def safe_cosine(a: torch.Tensor, b: torch.Tensor) -> float:
    """Compute cosine similarity safely."""
    if a is None or b is None:
        return 0.0
    if torch.norm(a) == 0 or torch.norm(b) == 0:
        return 0.0
    sim = util.cos_sim(a, b).item()
    return max(-1.0, min(1.0, float(sim)))


def tokenize_keywords(text: str) -> List[str]:
    """Basic keyword tokenizer."""
    if not text:
        return []
    cleaned = re.sub(r"[^\w\+\#\-]", " ", text)
    return [t.strip().lower() for t in cleaned.split() if len(t.strip()) > 1]


def keyword_overlap_pct(resume_text: str, jd_text: str) -> float:
    """Keyword overlap ratio with JD as denominator."""
    r_tokens = set(tokenize_keywords(resume_text))
    j_tokens = set(tokenize_keywords(jd_text))
    if not j_tokens:
        return 0.0
    return len(r_tokens.intersection(j_tokens)) / len(j_tokens)


# -------------------------
# Core Scoring Logic
# -------------------------
def extract_sections_map(data: Dict) -> Dict[str, str]:
    """Turn processed_sections array into {section_lower: cleaned_text}."""
    out = {}
    for s in data.get("processed_sections", []):
        sec = (s.get("section") or "").lower().strip()
        text = s.get("text") or ""
        cleaned = clean_text(text)
        if cleaned:
            out[sec] = cleaned
    return out


def compute_sectionwise_scores(resume_data: Dict, jd_data: Dict, use_keyword_blend: bool = True) -> Tuple[float, List[Dict]]:
    """Compute weighted section-wise ATS similarity (with fallback JD matching)."""
    resume_sections = extract_sections_map(resume_data)
    jd_sections = extract_sections_map(jd_data)

    if not resume_sections or not jd_sections:
        return 0.0, []

    # Precompute global JD embedding (for fallback)
    jd_all_text = " ".join(jd_sections.values())
    jd_all_emb = embed_text_chunks(jd_all_text)

    details, total_weight, weighted_sum = [], 0.0, 0.0

    for r_section, jd_targets in SECTION_MAPPING.items():
        r_text = resume_sections.get(r_section, "")
        weight = SECTION_WEIGHTS.get(r_section, 0.0)

        if not r_text:
            details.append({
                "resume_section": r_section,
                "matched_jd_section": None,
                "semantic_pct": 0.0,
                "keyword_pct": 0.0,
                "weight": weight,
                "blended_pct": 0.0
            })
            continue

        r_emb = embed_text_chunks(r_text)
        best_sem_sim, best_j_sec, best_keyword_pct = -1.0, None, 0.0

        # Check section-to-section mappings first
        for j_sec in jd_targets:
            j_text = jd_sections.get(j_sec, "")
            if not j_text:
                continue
            j_emb = embed_text_chunks(j_text)
            sem_sim = safe_cosine(r_emb, j_emb)
            sem_sim_norm = (sem_sim + 1.0) / 2.0
            if sem_sim_norm > best_sem_sim:
                best_sem_sim = sem_sim_norm
                best_j_sec = j_sec
                best_keyword_pct = keyword_overlap_pct(r_text, j_text)

        # 🔁 Fallback: global JD comparison if no direct section match
        if best_j_sec is None or best_sem_sim < 0.3:  # only trigger if weak or no match
            sem_sim_global = safe_cosine(r_emb, jd_all_emb)
            sem_sim_global_norm = (sem_sim_global + 1.0) / 2.0
            if sem_sim_global_norm > best_sem_sim:
                best_sem_sim = sem_sim_global_norm
                best_j_sec = "all_jd"
                best_keyword_pct = keyword_overlap_pct(r_text, jd_all_text)

        # Blending logic
        blended = (1.0 - KEYWORD_BLEND) * best_sem_sim + KEYWORD_BLEND * best_keyword_pct if use_keyword_blend else best_sem_sim

        weighted_sum += blended * weight
        total_weight += weight

        details.append({
            "resume_section": r_section,
            "matched_jd_section": best_j_sec,
            "semantic_pct": round(best_sem_sim * 100, 2),
            "keyword_pct": round(best_keyword_pct * 100, 2),
            "weight": weight,
            "blended_pct": round(blended * 100, 2)
        })

    overall_pct = round((weighted_sum / total_weight) * 100, 2) if total_weight > 0 else 0.0
    return overall_pct, details


def ats_score_from_json(resume_data: Dict, jd_data: Dict, use_keyword_blend: bool = True) -> Dict:
    """Compute core ATS score."""
    overall_pct, details = compute_sectionwise_scores(resume_data, jd_data, use_keyword_blend)
    resume_sections = extract_sections_map(resume_data)
    jd_sections = extract_sections_map(jd_data)

    resume_length = sum(len(t.split()) for t in resume_sections.values())
    jd_length = sum(len(t.split()) for t in jd_sections.values())

    return {
        "ats_score": overall_pct,
        "semantic_similarity": round(overall_pct / 100.0, 4),
        "resume_length": resume_length,
        "jd_length": jd_length,
        "details": details
    }


# ============================================================
#  🧠 Skill / Requirement Gap Analysis
# ============================================================
def extract_jd_skills(jd_data: Dict) -> List[str]:
    """Extract candidate skills or requirement terms from the JD."""
    jd_sections = extract_sections_map(jd_data)
    combined_text = " ".join(jd_sections.values())

    candidates = re.split(r"[,/\n]", combined_text)
    candidates = [c.strip().lower() for c in candidates if len(c.strip()) > 1]

    blacklist = {"experience", "responsibilities", "degree", "team", "problem", "knowledge", "development"}
    filtered = []
    for c in candidates:
        if any(word in c for word in blacklist):
            continue
        if len(c.split()) > 5:
            continue
        filtered.append(c)
    return list(set(filtered))


def semantic_skill_gap(resume_data: Dict, jd_data: Dict, threshold: float = 0.6) -> Dict:
    """Identify missing or weakly covered JD skills."""
    jd_skills = extract_jd_skills(jd_data)
    resume_sections = extract_sections_map(resume_data)

    if not jd_skills or not resume_sections:
        return {
            "missing_skills": [],
            "present_skills": [],
            "coverage_ratio": 0.0,
            "total_jd_skills": len(jd_skills)
        }

    resume_embeds = [embed_text_chunks(sec_text) for sec_text in resume_sections.values()]
    present_skills, missing_skills = [], []

    for skill in jd_skills:
        skill_emb = embed_text_chunks(skill)
        sims = [safe_cosine(skill_emb, r_emb) for r_emb in resume_embeds]
        max_sim = max(sims) if sims else 0.0
        entry = {"skill": skill, "similarity": round(max_sim, 3)}

        if max_sim >= threshold:
            present_skills.append(entry)
        else:
            missing_skills.append(entry)

    coverage_ratio = round(len(present_skills) / max(1, len(jd_skills)), 2)

    return {
        "missing_skills": sorted(missing_skills, key=lambda x: x["similarity"]),
        "present_skills": sorted(present_skills, key=lambda x: -x["similarity"]),
        "coverage_ratio": coverage_ratio,
        "total_jd_skills": len(jd_skills)
    }


def ats_score_with_skill_gap(resume_data: Dict, jd_data: Dict, use_keyword_blend: bool = True) -> Dict:
    """
    Extended ATS scoring with semantic skill gap detection.
    Adds missing/present skill data directly into the main response.
    """
    base_result = ats_score_from_json(resume_data, jd_data, use_keyword_blend)
    skill_gap = semantic_skill_gap(resume_data, jd_data, threshold=0.6)

    return {
        **base_result,
        "missing_skills": [s["skill"] for s in skill_gap["missing_skills"]],
        "present_skills": [s["skill"] for s in skill_gap["present_skills"]],
        "missing_skill_count": len(skill_gap["missing_skills"]),
        "present_skill_count": len(skill_gap["present_skills"]),
        "coverage_ratio": skill_gap["coverage_ratio"],
        "skill_gap_analysis": skill_gap
    }


# -------------------------
# Optional: CLI Test
# -------------------------
if __name__ == "__main__":
    import json
    a = json.load(open("data/processed/Sujay Kumar_structured.json", "r", encoding="utf-8"))
    b = json.load(open("data/processed/Full_Stack_Developer_Job_Description_JD_structured.json", "r", encoding="utf-8"))
    print(json.dumps(ats_score_with_skill_gap(a, b), indent=2))
