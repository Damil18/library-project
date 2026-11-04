"""Application entry point."""
from flask import Flask, jsonify

from books.routes import bp as books_bp
from core.config import Config
from core.db import close_db, init_db
from core.exceptions import AppError


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if isinstance(config, dict):
        app.config.update(config)
    elif config is not None:
        app.config.from_object(config)

    app.register_blueprint(books_bp)

    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"error": str(error)}), error.status_code

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
