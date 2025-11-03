# helpers/file_utils.py

import os
import re
import json
import fitz  # PyMuPDF
import nltk

# --- Ensure required NLTK tokenizers are available ---
for resource in ["punkt", "punkt_tab"]:
    try:
        nltk.data.find(f"tokenizers/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)

# ----------------------------
# Config
# ----------------------------
UPLOAD_DIR = "resumes"
CHUNK_SIZE = 1500
SECTION_HEADERS = [
    "summary", "objective", "education", "skills",
    "experience", "professional experience", "projects",
    "key projects", "achievements", "certifications",
    "publications", "extracurricular"
]

JD_HEADERS = [
    "about the role", "job description", "responsibilities", "requirements",
    "qualifications", "skills required", "key skills", "nice to have",
    "what we offer", "benefits", "who you are", "desired experience"
]

# -----------------------------------------------------
# Save uploaded file
# -----------------------------------------------------
def save_uploaded_file(file) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return file_path

# -----------------------------------------------------
# Normalize and clean text
# -----------------------------------------------------
def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s\.,@\-']", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# -----------------------------------------------------
# Split resume into sections
# -----------------------------------------------------
def split_into_sections(text: str) -> dict:
    sections = {}
    current_section = "general"
    sections[current_section] = []

    for line in text.splitlines():
        line_clean = line.strip().lower()
        if not line_clean:
            continue

        if any(header in line_clean for header in SECTION_HEADERS):
            current_section = next((h for h in SECTION_HEADERS if h in line_clean), "general")
            sections[current_section] = []
        else:
            sections[current_section].append(line.strip())

    for key in sections:
        joined = " ".join(sections[key])
        sections[key] = normalize_text(joined)
    return sections

# -----------------------------------------------------
# Chunk text
# -----------------------------------------------------
def chunk_text_for_embeddings(text: str, max_length=CHUNK_SIZE) -> list:
    sentences = nltk.sent_tokenize(text)
    chunks, current = [], ""

    for sent in sentences:
        if len(current) + len(sent) < max_length:
            current += " " + sent
        else:
            chunks.append(current.strip())
            current = sent
    if current:
        chunks.append(current.strip())

    return chunks

# -----------------------------------------------------
# Extract and structure RESUME
# -----------------------------------------------------
def extract_text_from_pdf(file_path: str) -> dict:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    try:
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text("text")
    except Exception as e:
        raise RuntimeError(f"Error reading PDF: {e}")

    if not text.strip():
        raise ValueError("No text found in the uploaded PDF.")

    sections = split_into_sections(text)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    saved_files, chunk_metadata = {}, []

    for section, content in sections.items():
        if not content:
            continue

        chunks = chunk_text_for_embeddings(content)
        section_name = re.sub(r"[^a-zA-Z0-9_]", "_", section)
        section_files = []

        for i, chunk in enumerate(chunks):
            fname = f"{base_name}_{section_name}_{i+1}.txt"
            text_path = os.path.join(UPLOAD_DIR, fname)
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(chunk)
            section_files.append(text_path)

            chunk_metadata.append({
                "section": section,
                "chunk_index": i + 1,
                "text_path": text_path,
                "text_preview": chunk[:200] + ("..." if len(chunk) > 200 else "")
            })

        saved_files[section] = section_files

    structured_output = {
        "file_name": os.path.basename(file_path),
        "sections": saved_files,
        "metadata": {
            "total_sections": len(saved_files),
            "total_chunks": sum(len(v) for v in saved_files.values()),
            "chunks": chunk_metadata
        }
    }

    json_path = os.path.join(UPLOAD_DIR, f"{base_name}_structured.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(structured_output, f, indent=4, ensure_ascii=False)

    return structured_output

# -----------------------------------------------------
# Extract and structure JOB DESCRIPTION
# -----------------------------------------------------
def extract_jd_from_pdf(file_path: str) -> dict:
    """
    Extracts JD text, identifies main sections (if any),
    chunks for embeddings, and saves structured data.
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    try:
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text("text")
    except Exception as e:
        raise RuntimeError(f"Error reading JD PDF: {e}")

    if not text.strip():
        raise ValueError("No text found in the JD PDF.")

    # Identify JD-like sections
    sections = {}
    current_section = "general"
    sections[current_section] = []

    for line in text.splitlines():
        line_clean = line.strip().lower()
        if not line_clean:
            continue
        if any(header in line_clean for header in JD_HEADERS):
            current_section = next((h for h in JD_HEADERS if h in line_clean), "general")
            sections[current_section] = []
        else:
            sections[current_section].append(line.strip())

    for key in sections:
        joined = " ".join(sections[key])
        sections[key] = normalize_text(joined)

    # Chunk & save
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    saved_files, chunk_metadata = {}, []

    for section, content in sections.items():
        if not content:
            continue

        chunks = chunk_text_for_embeddings(content)
        section_name = re.sub(r"[^a-zA-Z0-9_]", "_", section)
        section_files = []

        for i, chunk in enumerate(chunks):
            fname = f"{base_name}_{section_name}_{i+1}.txt"
            text_path = os.path.join(UPLOAD_DIR, fname)
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(chunk)
            section_files.append(text_path)

            chunk_metadata.append({
                "section": section,
                "chunk_index": i + 1,
                "text_path": text_path,
                "text_preview": chunk[:200] + ("..." if len(chunk) > 200 else "")
            })

        saved_files[section] = section_files

    structured_output = {
        "file_name": os.path.basename(file_path),
        "sections": saved_files,
        "metadata": {
            "total_sections": len(saved_files),
            "total_chunks": sum(len(v) for v in saved_files.values()),
            "chunks": chunk_metadata
        }
    }

    json_path = os.path.join(UPLOAD_DIR, f"{base_name}_JD_structured.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(structured_output, f, indent=4, ensure_ascii=False)

    return structured_output
