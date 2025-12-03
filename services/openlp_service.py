import os
import zipfile
import json
import uuid


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(BASE_DIR)
TMP_DIR = os.path.join(BASE_DIR, "tmp")

def unzip_file(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)


def extract_service_items(service_dir):
    osj_path = os.path.join(service_dir, "service_data.osj")

    if not os.path.exists(osj_path):
        print(f"\n❌ service_data.osj not found at: {osj_path}")
        return []

    with open(osj_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("\n❌ invalid osj format (not a list)")
        return []


    service_items = []
    raw_slides = []

    # index 0 is useless
    for item in data[1:]:
        if isinstance(item, dict) and "serviceitem" in item:
            if item['serviceitem']['header']['name'] == 'songs':
                service_items.append(item["serviceitem"]['data'])

    for song in service_items:
        if isinstance(song, list):
            for slide in song:
                if isinstance(slide, dict) and "raw_slide" in slide:
                    content = slide["raw_slide"].strip()

                    if content:
                        raw_slides.append(content)

    return raw_slides


def extract_openlp_items(job_dir, service_file_path, theme_file_path):
    service_extract_dir = os.path.join(job_dir, 'service')
    theme_extract_dir = os.path.join(job_dir, 'theme')

    os.makedirs(service_extract_dir, exist_ok=True)
    os.makedirs(theme_extract_dir, exist_ok=True)

    unzip_file(service_file_path, service_extract_dir)
    unzip_file(theme_file_path, theme_extract_dir)

    return service_extract_dir, theme_extract_dir

def upload_files_to_tmp(service_file, theme_file):
    job_id = str(uuid.uuid4())

    job_dir = os.path.join(TMP_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    service_file_path = os.path.join(job_dir, service_file.filename)
    theme_file_path = os.path.join(job_dir, theme_file.filename)

    service_file.save(service_file_path)
    theme_file.save(theme_file_path)

    return job_id, service_file_path, theme_file_path

