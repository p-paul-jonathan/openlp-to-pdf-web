from flask import Blueprint
from controllers.upload_controller import index, handle_upload
from controllers.download_controller import get_job_status, get_job_json, download_pdf

web = Blueprint("web", __name__)

@web.route("/", methods=["GET"])
def home():
    return index()

@web.route("/upload", methods=["POST"])
def upload():
    return handle_upload()

# ✅ HTML PAGE
@web.route("/job/<job_id>", methods=["GET"])
def get_job(job_id):
    return get_job_status(job_id)

# ✅ JSON STATUS ENDPOINT (AJAX POLLING)
@web.route("/job/<job_id>/status", methods=["GET"])
def job_status_api(job_id):
    return get_job_json(job_id)

# ✅ FILE DOWNLOAD
@web.route("/job/<job_id>/download", methods=["GET"])
def job_download(job_id):
    return download_pdf(job_id)
