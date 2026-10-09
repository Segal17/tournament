"""Точка входа Flask-приложения турнира."""

from flask import Flask

from config import Config


def create_app() -> Flask:
    """Создаёт и настраивает приложение."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Регистрируем основной блюпринт
    from routes.main import main_bp

    app.register_blueprint(main_bp, url_prefix="")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="127.0.0.1", port=5000)
