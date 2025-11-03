import os
import re
import json
from datetime import datetime

def clean_text(text: str) -> str:
    """Cleans text for embedding: removes URLs, extra spaces, etc."""
    text = re.sub(r"http\S+", "", text)  # Remove URLs
    text = re.sub(r"\s+", " ", text).strip()  # Normalize whitespace
    return text


def process_resume_json(input_json_path: str, output_dir: str = "data/processed") -> str:
    """Takes the parsed resume JSON, cleans and prepares it for embedding."""

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    processed_sections = []

    for section, paths in data["sections"].items():
        combined_text = ""
        for path in paths:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as txt_file:
                    content = txt_file.read()
                    combined_text += " " + clean_text(content)
            else:
                print(f"⚠️ Warning: Missing file {path}")

        processed_sections.append({
            "id": f"{data['file_name'].replace('.pdf', '')}_{section}",
            "section": section,
            "text": combined_text.strip(),
            "metadata": {
                "resume_owner": data["file_name"].replace(".pdf", ""),
                "source_files": paths,
                "tokens": len(combined_text.split()),
                "processed_at": datetime.now().isoformat()
            }
        })

    output_data = {
        "file_name": data["file_name"],
        "processed_sections": processed_sections,
        "metadata": {
            "original_json": input_json_path,
            "total_sections": len(processed_sections)
        }
    }

    output_path = os.path.join(output_dir, f"{data['file_name'].replace('.pdf', '')}_processed.json")
    with open(output_path, "w", encoding="utf-8") as out_file:
        json.dump(output_data, out_file, indent=4)

    print(f"✅ Processed resume saved to {output_path}")
    return output_path


def batch_process_all(input_dir: str = "data/resume_jsons", output_dir: str = "data/processed"):
    """Optional: process all resume JSONs in a directory."""
    for file in os.listdir(input_dir):
        if file.endswith(".json"):
            process_resume_json(os.path.join(input_dir, file), output_dir)
