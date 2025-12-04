import os
from flask import Flask
from routes import web


def create_app():
    app = Flask(__name__)

    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    tmp_dir = os.environ.get("TMP_DIR", os.path.join(base_dir, "tmp"))

    os.makedirs(tmp_dir, exist_ok=True)

    app.register_blueprint(web)

    return app


if __name__ == "__main__":
    app = create_app()

    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    app.run(host=host, port=port, debug=debug)
