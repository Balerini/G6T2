import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

from firebase_utils import get_firebase_app, get_firestore_client
from routes.auth import auth_bp


def create_app() -> Flask:
    
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
    app = Flask(__name__)

    CORS(app, resources={r"/*": {"origins": ["http://localhost:8080"]}}, supports_credentials=True)
    get_firebase_app()

    app.register_blueprint(auth_bp)

    @app.get("/health")
    def health() -> tuple:
        return jsonify({"status": "ok"}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))


