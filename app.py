import os
from flask import Flask, render_template
from dotenv import load_dotenv
from routes import web

# Load .env variables at startup
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Secret key
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")

    # TMP dir
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tmp_dir = os.getenv("TMP_DIR", os.path.join(base_dir, "tmp"))
    os.makedirs(tmp_dir, exist_ok=True)

    # Debug mode flag
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # Register routes
    app.register_blueprint(web)

    # ----------------------------
    # Error Handlers
    # ----------------------------

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        if debug:
            return render_template("error.html", error=str(e)), 500
        return render_template("error.html"), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        if debug:
            return render_template("error.html", error=str(e)), 500
        return render_template("error.html"), 500

    return app


if __name__ == "__main__":
    app = create_app()

    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    app.run(host=host, port=port, debug=debug)
