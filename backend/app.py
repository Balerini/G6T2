import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_cors import CORS

from firebase_utils import get_firebase_app, get_firestore_client
from routes.project import projects_bp 

def create_app() -> Flask:
    
    load_dotenv()
    
    app = Flask(__name__)

    CORS(app, resources={r"/*": {"origins": ["http://localhost:8080", "http://localhost:8081", "http://127.0.0.1:8080", "http://127.0.0.1:8081"]}}, supports_credentials=True)
    get_firebase_app()

    # Register blueprints here
    # =============== Project routes ===============
    app.register_blueprint(projects_bp)

    # Health routes
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)  # Added debug=True