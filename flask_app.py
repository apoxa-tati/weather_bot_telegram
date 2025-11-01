from config import PORT
from flask import Flask


def create_flask_app():
    """Создает и настраивает Flask приложение"""
    app = Flask(__name__)

    @app.route("/")
    def home():
        return {"status": "Bot is running", "service": "Weather Telegram Bot"}

    @app.route("/health")
    def health():
        return {"status": "healthy"}

    @app.route("/ping")
    def ping():
        return "pong"

    return app


def run_flask(app: Flask, port: int = PORT):
    """Запускает Flask приложение"""
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


# Создаем экземпляр приложения
flask_app = create_flask_app()
