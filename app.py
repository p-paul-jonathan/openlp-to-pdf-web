import os
from flask import Flask
from routes import web

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(BASE_DIR, "tmp")


def create_app():
    app = Flask(__name__)
    app.secret_key = "openlp-secret"  # change in prod

    # Ensure tmp exists
    os.makedirs(TMP_DIR, exist_ok=True)

    # Register routes
    app.register_blueprint(web)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
