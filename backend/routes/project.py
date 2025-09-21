from flask import Blueprint, jsonify, request
from firebase_utils import get_firestore_client

projects_bp = Blueprint('projects', __name__)

# =============== GET ALL PROJECTS ===============
@projects_bp.route('/api/projects', methods=['GET'])
def get_all_projects():
    try:
        db = get_firestore_client()
        projects_ref = db.collection('Projects')
        projects = projects_ref.stream()
        
        project_list = []
        for project in projects:
            project_data = project.to_dict()
            project_data['id'] = project.id
            project_list.append(project_data)
            
        return jsonify(project_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500