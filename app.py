import os
from flask import Flask, render_template, request
from routes import web


def create_app():
    app = Flask(__name__)

    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    tmp_dir = os.environ.get("TMP_DIR", os.path.join(base_dir, "tmp"))
    os.makedirs(tmp_dir, exist_ok=True)

    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    app.register_blueprint(web)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404


    @app.errorhandler(500)
    def internal_error(e):
        return render_template("error.html"), 500


    @app.errorhandler(Exception)
    def unhandled_exception(e):
        if debug:
            return render_template("error.html", error=str(e)), 500
        else:
            return render_template("error.html"), 500

    return app

if __name__ == "__main__":
    app = create_app()

    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    app.run(host=host, port=port, debug=debug)
