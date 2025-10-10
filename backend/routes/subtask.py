from flask import Blueprint, request, jsonify
from firebase_utils import get_firestore_client
from firebase_admin import firestore

subtask_bp = Blueprint('subtask', __name__)

@subtask_bp.route('/subtasks', methods=['POST'])
def create_subtask():
    try:
        data = request.get_json()
        print(f"=== BACKEND SUBTASK CREATION DEBUG ===")
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
            'owner': data.get('owner'),
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
                'owner': subtask_data.get('owner'),
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
        print(f"Fetching subtasks for task_id: {task_id}")
        db = get_firestore_client()
        subtasks = db.collection('subtasks').where('parent_task_id', '==', task_id).get()

        print(f"Found {len(subtasks)} subtasks")
        
        subtasks_list = []
        for subtask in subtasks:
            subtask_data = subtask.to_dict()
            subtask_data['id'] = subtask.id
            subtasks_list.append(subtask_data)
            print(f"  - Subtask: {subtask_data.get('name')} (ID: {subtask.id})")
        
        return jsonify({'subtasks': subtasks_list}), 200
        
    except Exception as e:
        print(f"Error fetching subtasks: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@subtask_bp.route('/subtasks/<subtask_id>', methods=['PUT'])
def update_subtask(subtask_id):
    try:
        data = request.get_json()
        print(f"=== BACKEND SUBTASK UPDATE DEBUG ===")
        print(f"Updating subtask ID: {subtask_id}")
        print(f"Received update data: {data}")
        
        # Get Firestore client
        db = get_firestore_client()
        
        # Check if subtask exists
        subtask_ref = db.collection('subtasks').document(subtask_id)
        subtask_doc = subtask_ref.get()
        
        if not subtask_doc.exists:
            print(f"Subtask not found: {subtask_id}")
            return jsonify({'error': 'Subtask not found'}), 404
        
        # Prepare update data
        update_data = {}
        
        # Update only fields that are provided
        if 'name' in data:
            update_data['name'] = data['name']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'start_date' in data:
            update_data['start_date'] = data['start_date']
        if 'end_date' in data:
            update_data['end_date'] = data['end_date']
        if 'status' in data:
            update_data['status'] = data['status']
        if 'assigned_to' in data:
            update_data['assigned_to'] = data['assigned_to']
        if 'attachments' in data:
            update_data['attachments'] = data['attachments']
        if 'status_history' in data:
            update_data['status_history'] = data['status_history']
        if 'owner' in data:
            update_data['owner'] = git sdata['owner']
        
        
        # Always update the timestamp
        update_data['updatedAt'] = firestore.SERVER_TIMESTAMP
        
        print(f"Updating subtask with data: {update_data}")
        
        # Update in Firestore
        subtask_ref.update(update_data)
        
        # Get updated subtask
        updated_subtask = subtask_ref.get().to_dict()
        updated_subtask['id'] = subtask_id
        
        print(f"Subtask updated successfully: {subtask_id}")
        
        # Prepare response data
        response_data = {
            'message': 'Subtask updated successfully',
            'subtaskId': subtask_id,
            'data': {
                'id': subtask_id,
                'name': updated_subtask.get('name'),
                'description': updated_subtask.get('description'),
                'start_date': updated_subtask.get('start_date'),
                'end_date': updated_subtask.get('end_date'),
                'status': updated_subtask.get('status'),
                'parent_task_id': updated_subtask.get('parent_task_id'),
                'project_id': updated_subtask.get('project_id'),
                'assigned_to': updated_subtask.get('assigned_to', []),
                'owner': updated_subtask.get('owner'),
                'attachments': updated_subtask.get('attachments', []),
                'status_history': updated_subtask.get('status_history', [])
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Error updating subtask: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500