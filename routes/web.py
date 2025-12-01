from flask import Blueprint
from controllers.upload_controller import index, handle_upload

web = Blueprint("web", __name__)

@web.route("/", methods=["GET"])
def home():
    return index()


@web.route("/upload", methods=["POST"])
def upload():
    return handle_upload()

