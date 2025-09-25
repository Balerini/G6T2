import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_cors import CORS

from firebase_utils import get_firebase_app, get_firestore_client
from routes.project import projects_bp 
from routes.task import tasks_bp 
from routes.subtask import subtask_bp

def create_app() -> Flask:
    
    load_dotenv()
    
    app = Flask(__name__)

    CORS(app, resources={r"/*": {"origins": ["http://localhost:8080", "http://localhost:8081", "http://127.0.0.1:8080", "http://127.0.0.1:8081"]}}, supports_credentials=True)
    get_firebase_app()

    # Register blueprints here
    # =============== Project routes ===============
    app.register_blueprint(projects_bp)
    
    # =============== Task routes ===============
    app.register_blueprint(tasks_bp)

    # =============== Subtask routes ===============
    app.register_blueprint(subtask_bp, url_prefix='/api')

    # Health routes
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    # User Routes 
    @app.route("/login", methods=["POST"])
    def login():
        payload = request.get_json(silent=True) or {}
        email = payload.get("email")
        password = payload.get("password")
        
        if not email or not password:
            return jsonify({"ok": False, "error": "email and password are required"}), 400

        try:
            # Get Firestore client
            db = get_firestore_client()
            
            users_ref = db.collection('Users')
            all_docs = users_ref.stream()
            docs = []
            
            for doc in all_docs:
                user_data = doc.to_dict()
                if user_data.get('email', '').lower() == email.lower():
                    docs.append(doc)
                    break
            
            for doc in docs:
                user_data = doc.to_dict()
                if user_data.get('password') == password:
                    return jsonify({
                        "ok": True,
                        "message": "Login successful",
                        "user": {
                            "email": email,
                            "id": doc.id,
                            "name": user_data.get('name', ''),
                            "role": user_data.get('role', 'user'),
                            "role_name": user_data.get('role_name', ''),
                            "role_num": user_data.get('role_num', 0),
                            "division_name": user_data.get("division_name", ""),
                        }
                    }), 200
            
            return jsonify({"ok": False, "error": "Invalid email or password"}), 401
            
        except Exception as e:
            return jsonify({"ok": False, "error": f"Database error: {str(e)}"}), 500
        

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
