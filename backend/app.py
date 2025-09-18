import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_cors import CORS

from firebase_utils import get_firebase_app, get_firestore_client

def create_app() -> Flask:
    
    load_dotenv()
    
    app = Flask(__name__)

    CORS(app, resources={r"/*": {"origins": ["http://localhost:8080"]}}, supports_credentials=True)
    get_firebase_app()

    # Health routes
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

   
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))