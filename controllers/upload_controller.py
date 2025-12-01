import os
import uuid
from flask import render_template, request, redirect, url_for, flash

from services.openlp_service import unzip_file, extract_service_items


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(BASE_DIR)  # go up from /controllers to root
TMP_DIR = os.path.join(BASE_DIR, "tmp")


def index():
    return render_template("index.html")


def handle_upload():
    service_file = request.files.get("service_file")
    theme_file = request.files.get("theme_file")

    if not service_file or not theme_file:
        flash("Both service (.osz) and theme (.otz) files are required")
        return redirect(url_for("web.index"))

    # Generate unique ID
    unique_id = str(uuid.uuid4())

    # Create tmp/<unique_id> directory
    workdir = os.path.join(TMP_DIR, unique_id)
    os.makedirs(workdir, exist_ok=True)

    # Save uploaded files
    service_path = os.path.join(workdir, service_file.filename)
    theme_path = os.path.join(workdir, theme_file.filename)

    service_file.save(service_path)
    theme_file.save(theme_path)

    # Create extract directories
    service_extract_dir = os.path.join(workdir, "service")
    theme_extract_dir = os.path.join(workdir, "theme")

    os.makedirs(service_extract_dir, exist_ok=True)
    os.makedirs(theme_extract_dir, exist_ok=True)

    # Unzip
    unzip_file(service_path, service_extract_dir)
    unzip_file(theme_path, theme_extract_dir)

    # Extract service items
    service_items = extract_service_items(service_extract_dir)

    return f"""
    <h2>Files uploaded and extracted successfully</h2>
    <p><strong>Job ID:</strong> {unique_id}</p>
    <p><strong>Working directory:</strong> {workdir}</p>
    <p><strong>Service items found:</strong> {len(service_items)}</p>
    """

