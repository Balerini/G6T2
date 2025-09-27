from flask import Blueprint, request, jsonify
from firebase_utils import get_firestore_client
from firebase_admin import firestore

subtask_bp = Blueprint('subtask', __name__)

@subtask_bp.route('/subtasks', methods=['POST'])
def create_subtask():
    try:
        data = request.get_json()
        print("=== BACKEND SUBTASK CREATION DEBUG ===")
        print(f"Received subtask data: {data}")
        print(f"Data keys: {list(data.keys()) if data else 'No data'}")
        
        # Validate required fields
        required_fields = ['name', 'start_date', 'end_date', 'status', 'parent_task_id', 'project_id']
        for field in required_fields:
            if field not in data:
                print(f"Missing required field: {field}")
                return jsonify({'error': f'{field} is required'}), 400
        
        # Get Firestore client
        db = get_firestore_client()
        
        # Create subtask document
        subtask_data = {
            'name': data['name'],
            'description': data.get('description', ''),
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'status': data['status'],
            'parent_task_id': data['parent_task_id'],
            'project_id': data['project_id'],
            'assigned_to': data.get('assigned_to', []),
            'attachments': data.get('attachments', []),
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        # Add to Firebase
        print(f"Adding subtask to Firestore: {subtask_data}")
        _, doc_ref = db.collection('subtasks').add(subtask_data)
        print(f"Subtask created successfully with ID: {doc_ref.id}")
        
        # Prepare response data without Firestore sentinels
        response_data = {
            'message': 'Subtask created successfully',
            'subtaskId': doc_ref.id,
            'data': {
                'name': subtask_data['name'],
                'description': subtask_data['description'],
                'start_date': subtask_data['start_date'],
                'end_date': subtask_data['end_date'],
                'status': subtask_data['status'],
                'parent_task_id': subtask_data['parent_task_id'],
                'project_id': subtask_data['project_id'],
                'assigned_to': subtask_data['assigned_to'],
                'attachments': subtask_data['attachments']
            }
        }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        print(f"Error creating subtask: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
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