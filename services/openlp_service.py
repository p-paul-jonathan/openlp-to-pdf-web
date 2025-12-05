import os
import zipfile
import json
import uuid


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.getenv("TMP_DIR", os.path.join(BASE_DIR, "tmp"))


# -------------------------
# ZIP
# -------------------------

def unzip_file(zip_path, extract_to):
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"ZIP file not found: {zip_path}")

    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"Not a valid ZIP file: {zip_path}")

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
    except Exception as e:
        raise RuntimeError(f"Failed to unzip {zip_path}: {e}")


# -------------------------
# SERVICE FILE
# -------------------------

def extract_service_items(service_dir):
    osj_path = os.path.join(service_dir, "service_data.osj")

    if not os.path.exists(osj_path):
        raise FileNotFoundError(f"service_data.osj not found at {osj_path}")

    try:
        with open(osj_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in service_data.osj: {e}")

    if not isinstance(data, list):
        raise TypeError("Invalid service_data.osj format (expected list)")

    service_items = []
    raw_slides = []

    # index 0 is ignored
    for item in data[1:]:
        if not isinstance(item, dict):
            continue

        service_item = item.get("serviceitem")
        if not service_item:
            continue

        header = service_item.get("header", {})
        if header.get("name") != "songs":
            continue

        data_block = service_item.get("data")
        if not isinstance(data_block, list):
            continue

        service_items.append(data_block)

    if not service_items:
        raise ValueError("No song slides found in service file")

    # Extract raw_slide text
    for song in service_items:
        for slide in song:
            if isinstance(slide, dict) and "raw_slide" in slide:
                content = slide["raw_slide"].strip()
                if content:
                    raw_slides.append(content)

    if not raw_slides:
        raise ValueError("No raw_slide content found in service file")

    return raw_slides


# -------------------------
# OPENLP EXTRACTION
# -------------------------

def extract_openlp_items(job_dir, service_file_path, theme_file_path):
    if not os.path.exists(job_dir):
        raise FileNotFoundError(f"Job directory does not exist: {job_dir}")

    if not os.path.exists(service_file_path):
        raise FileNotFoundError("Service file not provided")

    if not os.path.exists(theme_file_path):
        raise FileNotFoundError("Theme file not provided")

    service_extract_dir = os.path.join(job_dir, "service")
    theme_extract_dir = os.path.join(job_dir, "theme")

    os.makedirs(service_extract_dir, exist_ok=True)
    os.makedirs(theme_extract_dir, exist_ok=True)

    unzip_file(service_file_path, service_extract_dir)
    unzip_file(theme_file_path, theme_extract_dir)

    # Confirm extraction results
    if not os.listdir(service_extract_dir):
        raise RuntimeError("Service ZIP extracted nothing")

    if not os.listdir(theme_extract_dir):
        raise RuntimeError("Theme ZIP extracted nothing")

    return service_extract_dir, theme_extract_dir


# -------------------------
# UPLOAD
# -------------------------

def upload_files_to_tmp(service_file, theme_file):
    if not service_file:
        raise ValueError("Service file missing")

    if not theme_file:
        raise ValueError("Theme file missing")

    job_id = str(uuid.uuid4())
    job_dir = os.path.join(TMP_DIR, job_id)

    os.makedirs(job_dir, exist_ok=True)

    service_file_path = os.path.join(job_dir, service_file.filename)
    theme_file_path = os.path.join(job_dir, theme_file.filename)

    try:
        service_file.save(service_file_path)
        theme_file.save(theme_file_path)
    except Exception as e:
        raise IOError(f"Failed to save uploaded files: {e}")

    if not os.path.exists(service_file_path):
        raise IOError("Service file did not save correctly")

    if not os.path.exists(theme_file_path):
        raise IOError("Theme file did not save correctly")

    return job_id, service_file_path, theme_file_path
