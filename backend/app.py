import os
import hashlib
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_cors import CORS
from firebase_admin import firestore

from firebase_utils import get_firebase_app, get_firestore_client
from routes.project import projects_bp 
from routes.task import tasks_bp 
from routes.subtask import subtask_bp
from routes.dashboard import dashboard_bp
from services.notification_service import notification_service

def validate_password(password):
    """Validate password requirements"""
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return "Password must be less than 128 characters"
    
    # Check for at least one uppercase letter
    if not any(c.isupper() for c in password):
        return "Password must contain at least one uppercase letter"
    
    # Check for at least one lowercase letter
    if not any(c.islower() for c in password):
        return "Password must contain at least one lowercase letter"
    
    # Check for at least one digit
    if not any(c.isdigit() for c in password):
        return "Password must contain at least one number"
    
    # Check for at least one special character
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return "Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)"
    
    return None

def hash_password(password):
    """Hash password using SHA-256 with salt"""
    salt = os.urandom(32)  # Generate random salt
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt + password_hash  # Store salt + hash together

def verify_password(stored_password, provided_password):
    """Verify a password against its hash"""
    try:
        # Convert hex string back to bytes
        stored_password_bytes = bytes.fromhex(stored_password)
        salt = stored_password_bytes[:32]  # First 32 bytes are salt
        stored_hash = stored_password_bytes[32:]  # Rest is hash
        
        # Hash the provided password with the same salt
        provided_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        
        # Compare hashes
        return stored_hash == provided_hash
    except Exception:
        return False

def create_app() -> Flask:
    
    load_dotenv()
    
    app = Flask(__name__)

    CORS(app, resources={r"/*": {"origins": ["http://localhost:8080", "http://localhost:8081", "http://127.0.0.1:8080", "http://127.0.0.1:8081"]}}, supports_credentials=True)
    get_firebase_app()
    
    # Log all incoming requests
    @app.before_request
    def log_request():
        print(f"\n🌐 {request.method} {request.path}")

    # Register blueprints here
    # =============== Project routes ===============
    app.register_blueprint(projects_bp)
    
    # =============== Task routes ===============
    app.register_blueprint(tasks_bp)

    # =============== Subtask routes ===============
    app.register_blueprint(subtask_bp, url_prefix='/api')

    # =============== Dashboard routes ===============
    app.register_blueprint(dashboard_bp)

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
                stored_password = user_data.get('password', '')
                
                # Check if password is hashed (new users) or plain text (old users)
                if len(stored_password) > 32 and ':' not in stored_password:
                    # New hashed password
                    if verify_password(stored_password, password):
                        return jsonify({
                            "ok": True,
                            "message": "Login successful",
                            "user": {
                                "email": email,
                                "id": doc.id,
                                "name": user_data.get('name', ''),
                                "role_name": user_data.get('role_name', 'Staff'),
                                "role_name": user_data.get('role_name', ''),
                                "role_num": user_data.get('role_num', 0),
                                "division_name": user_data.get("division_name", ""),
                            }
                        }), 200
                else:
                    # Old plain text password (for backward compatibility)
                    if user_data.get('password') == password:
                        return jsonify({
                            "ok": True,
                            "message": "Login successful",
                            "user": {
                                "email": email,
                                "id": doc.id,
                                "name": user_data.get('name', ''),
                                "role_name": user_data.get('role_name', 'Staff'),
                                "role_name": user_data.get('role_name', ''),
                                "role_num": user_data.get('role_num', 0),
                                "division_name": user_data.get("division_name", ""),
                            }
                        }), 200
            
            return jsonify({"ok": False, "error": "Invalid email or password"}), 401
            
        except Exception as e:
            return jsonify({"ok": False, "error": f"Database error: {str(e)}"}), 500

    @app.route("/register", methods=["POST"])
    def register():
        payload = request.get_json(silent=True) or {}
        name = payload.get("name")
        email = payload.get("email")
        password = payload.get("password")
        division_name = payload.get("division_name")
        
        # Validate required fields
        if not all([name, email, password, division_name]):
            return jsonify({"ok": False, "error": "All fields are required"}), 400

        # Basic validation
        if len(name.strip()) < 2:
            return jsonify({"ok": False, "error": "Name must be at least 2 characters"}), 400
        
        # Password validation
        password_errors = validate_password(password)
        if password_errors:
            return jsonify({"ok": False, "error": password_errors}), 400
        
        # Auto-determine role from email
        email_lower = email.lower()
        if 'director' in email_lower:
            role = 'director'
        elif 'manager' in email_lower:
            role = 'manager'
        else:
            role = 'staff'
        
        # Validate department
        valid_departments = [
            "Sales",
            "Consultancy", 
            "System Solutioning",
            "Engineering Operation",
            "HR and Admin",
            "Finance",
            "IT"
        ]
        if division_name not in valid_departments:
            return jsonify({"ok": False, "error": "Invalid department selected"}), 400

        try:
            # Get Firestore client
            db = get_firestore_client()
            
            # Check if user already exists
            users_ref = db.collection('Users')
            existing_users = users_ref.where('email', '==', email.lower().strip()).stream()
            
            if list(existing_users):
                return jsonify({"ok": False, "error": "Email already exists"}), 409
            
            # Hash the password
            hashed_password = hash_password(password)
            
            # Create user document
            user_data = {
                'division_name': division_name.strip(),
                'email': email.lower().strip(),
                'name': name.strip(),
                'password': hashed_password.hex(),  # Convert bytes to hex string for storage
                'role_name': role.capitalize(),
                'role_num': 4 if role == "staff" else 2 if role == "director" else 3 if role == "manager" else 1
            }
            
            # Add user to Firestore
            doc_ref = users_ref.add(user_data)
            
            return jsonify({
                "ok": True,
                "message": "Registration successful",
                "user": {
                    "name": name.strip(),
                    "email": email.lower().strip(),
                    "role_name": role.capitalize(),
                    "role_num": 4 if role == "staff" else 2 if role == "director" else 3 if role == "manager" else 1,
                    "division_name": division_name.strip()
                }
            }), 201
            
        except Exception as e:
            return jsonify({"ok": False, "error": f"Database error: {str(e)}"}), 500
    
    # =============== NOTIFICATION ROUTES ===============
    
    @app.route("/api/notifications/<user_id>", methods=["GET"])
    def get_notifications(user_id):
        """Get notifications for a user"""
        try:
            unread_only = request.args.get('unread_only', 'false').lower() == 'true'
            limit = int(request.args.get('limit', 50))
            
            notifications = notification_service.get_user_notifications(
                user_id=user_id,
                unread_only=unread_only,
                limit=limit
            )
            
            return jsonify({
                "ok": True,
                "notifications": notifications
            }), 200
            
        except Exception as e:
            print(f"Error getting notifications: {str(e)}")
            return jsonify({"ok": False, "error": str(e)}), 500
    
    @app.route("/api/notifications/<notification_id>/read", methods=["PUT"])
    def mark_notification_read(notification_id):
        """Mark a notification as read"""
        try:
            success = notification_service.mark_as_read(notification_id)
            
            if success:
                return jsonify({"ok": True, "message": "Notification marked as read"}), 200
            else:
                return jsonify({"ok": False, "error": "Notification not found"}), 404
                
        except Exception as e:
            print(f"Error marking notification as read: {str(e)}")
            return jsonify({"ok": False, "error": str(e)}), 500
    
    @app.route("/api/notifications/<user_id>/mark-all-read", methods=["PUT"])
    def mark_all_notifications_read(user_id):
        """Mark all notifications as read for a user"""
        try:
            count = notification_service.mark_all_as_read(user_id)
            
            return jsonify({
                "ok": True,
                "message": f"Marked {count} notifications as read"
            }), 200
            
        except Exception as e:
            print(f"Error marking all notifications as read: {str(e)}")
            return jsonify({"ok": False, "error": str(e)}), 500
    
    @app.route("/api/notifications/<notification_id>", methods=["DELETE"])
    def delete_notification(notification_id):
        """Delete a notification"""
        try:
            success = notification_service.delete_notification(notification_id)
            
            if success:
                return jsonify({"ok": True, "message": "Notification deleted"}), 200
            else:
                return jsonify({"ok": False, "error": "Notification not found"}), 404
                
        except Exception as e:
            print(f"Error deleting notification: {str(e)}")
            return jsonify({"ok": False, "error": str(e)}), 500
    
    @app.route("/api/notifications/check-deadlines", methods=["POST"])
    def check_deadlines():
        """Check for upcoming deadlines and create notifications"""
        try:
            notification_service.notify_upcoming_deadlines()
            
            return jsonify({
                "ok": True,
                "message": "Deadline check completed"
            }), 200
            
        except Exception as e:
            print(f"Error checking deadlines: {str(e)}")
            return jsonify({"ok": False, "error": str(e)}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
