import os

from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from jobs import enqueue
from jobs.uploader_job import UploaderJob
from services.openlp_service import upload_files_to_tmp


def index():
    themes_dir = os.path.join(
        current_app.root_path,
        "public",
        "themes",
    )

    themes = []

    if os.path.isdir(themes_dir):
        for filename in sorted(os.listdir(themes_dir)):
            if filename.lower().endswith(".otz"):
                themes.append({
                    "name": os.path.splitext(filename)[0],
                    "filename": filename,
                })

    return render_template(
        "index.html",
        themes=themes,
    )


def handle_upload():
    service_file = request.files.get("service_file")
    theme_file = request.files.get("theme_file")

    theme_source = request.form.get("theme_source", "default")
    default_theme = request.form.get("default_theme")

    if not service_file:
        flash("Service (.osz) file is required")
        return redirect(url_for("web.home"))

    if theme_source == "default":
        if not default_theme:
            flash("Please select a theme")
            return redirect(url_for("web.home"))

        themes_dir = os.path.join(
            current_app.root_path,
            "public",
            "themes",
        )

        # Prevent path traversal
        if os.path.basename(default_theme) != default_theme:
            flash("Invalid theme")
            return redirect(url_for("web.home"))

        selected_theme_path = os.path.join(
            themes_dir,
            default_theme,
        )

        if not os.path.isfile(selected_theme_path):
            flash("Selected theme was not found")
            return redirect(url_for("web.home"))

        job_id, service_file_path, theme_file_path = upload_files_to_tmp(
            service_file,
            theme_file_path=selected_theme_path,
        )

    else:
        if not theme_file or not theme_file.filename:
            flash("Please upload a theme (.otz) file")
            return redirect(url_for("web.home"))

        job_id, service_file_path, theme_file_path = upload_files_to_tmp(
            service_file,
            theme_file=theme_file,
        )

    enqueue(
        UploaderJob,
        job_id,
        {
            "service_file_path": service_file_path,
            "theme_file_path": theme_file_path,
        },
    )

    return redirect(url_for("web.get_job", job_id=job_id))
