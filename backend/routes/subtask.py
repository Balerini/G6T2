from flask import Blueprint, request, jsonify
from firebase_utils import get_firestore_client
from firebase_admin import firestore

subtask_bp = Blueprint('subtask', __name__)

@subtask_bp.route('/subtasks', methods=['POST'])
def create_subtask():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'deadline', 'status', 'parentTaskId', 'parentProjectId']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Get Firestore client
        db = get_firestore_client()
        
        # Create subtask document
        subtask_data = {
            'name': data['name'],
            'deadline': data['deadline'],
            'status': data['status'],
            'parentTaskId': data['parentTaskId'],
            'parentProjectId': data['parentProjectId'],
            'collaborators': data.get('collaborators', []),
            'attachments': data.get('attachments', []),
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        # Add to Firebase
        _, doc_ref = db.collection('subtasks').add(subtask_data)
        
        return jsonify({
            'message': 'Subtask created successfully',
            'subtaskId': doc_ref.id,
            'data': subtask_data
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@subtask_bp.route('/tasks/<task_id>/subtasks', methods=['GET'])
def get_task_subtasks(task_id):
    try:
        db = get_firestore_client()
        subtasks = db.collection('subtasks').where('parentTaskId', '==', task_id).get()
        
        subtasks_list = []
        for subtask in subtasks:
            subtask_data = subtask.to_dict()
            subtask_data['id'] = subtask.id
            subtasks_list.append(subtask_data)
        
        return jsonify({'subtasks': subtasks_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500