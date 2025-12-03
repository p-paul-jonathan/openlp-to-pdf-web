from flask import render_template, request, redirect, url_for, flash

from jobs import enqueue
from jobs.uploader_job import UploaderJob
from services.openlp_service import upload_files_to_tmp

def index():
    return render_template("index.html")

def handle_upload():
    service_file = request.files.get("service_file")
    theme_file = request.files.get("theme_file")

    if not service_file or not theme_file:
        flash("Both service (.osz) and theme (.otz) files are required")
        return redirect(url_for("web.index"))

    job_id, service_file_path, theme_file_path = upload_files_to_tmp(service_file, theme_file)

    enqueue(
        UploaderJob,
        job_id,
        {
            "service_file_path": service_file_path,
            "theme_file_path": theme_file_path
        }
    )
    return f"""
    <h2>Files uploaded and extracted successfully</h2>

    """

