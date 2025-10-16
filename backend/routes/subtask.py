from flask import Blueprint, request, jsonify
from firebase_utils import get_firestore_client
from firebase_admin import firestore

subtask_bp = Blueprint('subtask', __name__)

# ==================== NEW SUBTASK CREATION ====================
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
            'status_history': data.get('status_history', []),
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

# ==================== GET ALL SUBTASKS WITHIN TASK ====================
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
    
# ==================== UPDATE SUBTASK ====================
@subtask_bp.route('/subtasks/<subtask_id>', methods=['PUT'])
def update_subtask(subtask_id):
    try:
        data = request.get_json()
        print(f"=== BACKEND SUBTASK UPDATE DEBUG ===")
        print(f"Updating subtask ID: {subtask_id}")
        print(f"Received update data: {data}")

        # Get user info first, for all updates, not just ownership trf
        current_user_id = request.headers.get('X-User-Id')
        current_user_role = request.headers.get('X-User-Role')

        # Validate user info is provided
        if not current_user_id:
            return jsonify({'error': 'User authentication required - missing user ID'}), 401
        
        if not current_user_role:
            return jsonify({'error': 'User authentication required - missing user role'}), 401
        
        # Validate role is a valid num
        try:
            current_user_role = int(current_user_role)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user role format'}), 400
        
        # Get Firestore client
        db = get_firestore_client()
        
        # Check if subtask exists
        subtask_ref = db.collection('subtasks').document(subtask_id)
        subtask_doc = subtask_ref.get()
        
        if not subtask_doc.exists:
            print(f"Subtask not found: {subtask_id}")
            return jsonify({'error': 'Subtask not found'}), 404
        
        subtask_data = subtask_doc.to_dict()

        # Validate ownership transfer
        if 'owner' in data:
            # Check if current user is the owner
            if str(subtask_data.get('owner')) != str(current_user_id):
                return jsonify({'error': 'Only the subtask owner can transfer ownership'}), 403
            
            # Check if current user is a manager
            if current_user_role != 3:
                return jsonify({'error': 'Only managers can transfer subtask ownership'}), 403
            
            # Check if new owner is in assigned_to list
            new_owner_id = data['owner']
            assigned_to = subtask_data.get('assigned_to', [])
            if str(new_owner_id) not in [str(id) for id in assigned_to]:
                return jsonify({'error': 'New owner must be assigned to the subtask'}), 400
        
        # Store old owner ID BEFORE updating (for email notification)
        old_owner_id = subtask_data.get('owner')
        
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
            update_data['owner'] = data['owner']
        
        
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
        
        # ================== SEND EMAILS FOR OWNER CHANGE ==================
        try:
            new_owner_id = data.get('owner')
            
            print(f"🔍 EMAIL CHECK - new_owner_id: {new_owner_id}")
            print(f"🔍 EMAIL CHECK - old_owner_id: {old_owner_id}")
            print(f"🔍 EMAIL CHECK - Are they different? {old_owner_id != new_owner_id}")
            
            # Check if owner has changed
            if new_owner_id and old_owner_id != new_owner_id:
                print(f"👤 OWNER CHANGE DETECTED: {old_owner_id} → {new_owner_id}")
                from services.email_service import email_service
                
                # Get new owner's info
                print(f"📧 Fetching new owner data for: {new_owner_id}")
                new_owner_doc = db.collection('Users').document(new_owner_id).get()
                
                if new_owner_doc.exists:
                    new_owner_data = new_owner_doc.to_dict()
                    new_owner_email = new_owner_data.get('email')
                    new_owner_name = new_owner_data.get('name', 'User')
                    print(f"✅ New owner found: {new_owner_name} ({new_owner_email})")
                    
                    # Get old owner's info (for CC)
                    old_owner_email = None
                    old_owner_name = 'Previous Owner'
                    if old_owner_id:
                        print(f"📧 Fetching old owner data for: {old_owner_id}")
                        old_owner_doc = db.collection('Users').document(old_owner_id).get()
                        if old_owner_doc.exists:
                            old_owner_data = old_owner_doc.to_dict()
                            old_owner_email = old_owner_data.get('email')
                            old_owner_name = old_owner_data.get('name', 'Previous Owner')
                            print(f"✅ Old owner found: {old_owner_name} ({old_owner_email})")
                    
                    # Prepare subtask details for email
                    subtask_name = updated_subtask.get('name', 'Unknown Subtask')
                    subtask_desc = updated_subtask.get('description', '')
                    
                    # Get parent task name
                    parent_task_name = ''
                    parent_task_id = updated_subtask.get('parent_task_id')
                    if parent_task_id:
                        try:
                            parent_task_doc = db.collection('Tasks').document(parent_task_id).get()
                            if parent_task_doc.exists:
                                parent_task_name = parent_task_doc.to_dict().get('task_name', '')
                        except Exception as e:
                            print(f"⚠️ Could not fetch parent task: {e}")
                    
                    # Get project name
                    project_name = ''
                    project_id = updated_subtask.get('project_id')
                    if project_id:
                        try:
                            project_doc = db.collection('Projects').document(project_id).get()
                            if project_doc.exists:
                                project_name = project_doc.to_dict().get('proj_name', '')
                        except Exception as e:
                            print(f"⚠️ Could not fetch project: {e}")
                    
                    # Get who made the transfer (current user)
                    transferred_by_name = new_owner_name  # Default fallback
                    try:
                        current_user_doc = db.collection('Users').document(current_user_id).get()
                        if current_user_doc.exists:
                            transferred_by_name = current_user_doc.to_dict().get('name', 'Manager')
                    except Exception as e:
                        print(f"⚠️ Could not fetch current user: {e}")
                    
                    # Format dates safely
                    start_date_str = 'Not specified'
                    end_date_str = None
                    
                    if updated_subtask.get('start_date'):
                        start_date_str = updated_subtask['start_date']
                    
                    if updated_subtask.get('end_date'):
                        end_date_str = updated_subtask['end_date']
                    
                    print(f"📧 Preparing to send subtask ownership transfer email...")
                    print(f"   To: {new_owner_email}")
                    print(f"   CC: {old_owner_email}")
                    print(f"   Subtask: {subtask_name}")
                    
                    # Send email to new owner (with old owner CC'd)
                    if new_owner_email:
                        success = email_service.send_subtask_transfer_ownership_email(
                            new_owner_email=new_owner_email,
                            new_owner_name=new_owner_name,
                            old_owner_email=old_owner_email if old_owner_email else '',
                            old_owner_name=old_owner_name,
                            subtask_name=subtask_name,
                            subtask_desc=subtask_desc,
                            parent_task_name=parent_task_name,
                            project_name=project_name,
                            transferred_by_name=transferred_by_name,
                            start_date=start_date_str,
                            end_date=end_date_str
                        )
                        if success:
                            print(f"✅ SUBTASK OWNERSHIP TRANSFER EMAIL SENT to {new_owner_email} (CC: {old_owner_email})")
                        else:
                            print(f"❌ FAILED to send subtask ownership transfer email")
                    else:
                        print(f"⚠️ No email found for new owner {new_owner_id}")
                else:
                    print(f"⚠️ New owner document not found: {new_owner_id}")
            else:
                print(f"⏭️  No owner change detected")
                    
        except Exception as e:
            print(f"❌ Failed to send owner change email: {e}")
            import traceback
            traceback.print_exc()
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Error updating subtask: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500