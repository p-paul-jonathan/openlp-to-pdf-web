from flask import Blueprint
from controllers.upload_controller import index, handle_upload
from controllers.download_controller import get_job_status

web = Blueprint("web", __name__)

@web.route("/", methods=["GET"])
def home():
    return index()


@web.route("/upload", methods=["POST"])
def upload():
    return handle_upload()


@web.route('/job/:id', methods=["GET"])
def get_job():
    return get_job_status()
