from flask import Blueprint, request, jsonify
from firebase_utils import get_firestore_client
from firebase_admin import firestore

subtask_bp = Blueprint('subtask', __name__)

# ==================== NEW SUBTASK CREATION ====================
@subtask_bp.route('/api/subtasks', methods=['POST', 'OPTIONS'])  # Add /api/ prefix and OPTIONS
def create_subtask():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response, 200
    
    try:
        data = request.get_json()
        print("BACKEND SUBTASK CREATION DEBUG")
        print(f"Received subtask data: {data}")
        
        # Validate required fields
        required_fields = ['name', 'start_date', 'end_date', 'status', 'parent_task_id']
        for field in required_fields:
            if field not in data:
                print(f"Missing required field: {field}")
                return jsonify({'error': f'{field} is required'}), 400

        # project_id is optional (can be null for standalone tasks)
        project_id = data.get('project_id', None)
        
        # Get Firestore client
        db = get_firestore_client()

        # Validate that invited collaborators are from parent task 
        parent_task_id = data['parent_task_id']
        invited_collaborators = data.get('assigned_to', [])
        
        if invited_collaborators:
            # Get parent task to check its collaborators
            parent_task_ref = db.collection('Tasks').document(parent_task_id)
            parent_task_doc = parent_task_ref.get()
            
            if not parent_task_doc.exists:
                return jsonify({'error': 'Parent task not found'}), 404
            
            parent_task_data = parent_task_doc.to_dict()
            parent_task_collaborators = parent_task_data.get('assigned_to', [])
            
            # Convert to strings for comparison
            parent_collaborator_ids = [str(id) for id in parent_task_collaborators]
            
            # Validate each invited collaborator
            for collab_id in invited_collaborators:
                if str(collab_id) not in parent_collaborator_ids:
                    print(f"Collaborator {collab_id} is not in parent task")
                    return jsonify({
                        'error': 'All invited collaborators must be collaborators of the parent task'
                    }), 400
            
            print("All invited collaborators are valid parent task collaborators")
        
        # Create subtask document with proper structure
        subtask_data = {
            'name': data['name'],
            'description': data.get('description', ''),
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'status': data['status'],
            'priority': data.get('priority', 5), # Default priority is 5 (medium)
            'parent_task_id': data['parent_task_id'],
            'project_id': data.get('project_id', None),
            'assigned_to': data.get('assigned_to', []),
            'owner': data.get('owner'),
            'attachments': data.get('attachments', []),
            'status_history': data.get('status_history', []),
            'is_deleted': False,  # Ensure new subtasks are not deleted
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        print(f"Adding subtask to Firestore: {subtask_data}")
        
        # Use lowercase 'subtasks' collection
        doc_ref = db.collection('subtasks').add(subtask_data)
        
        print(f"Subtask created successfully with ID: {doc_ref[1].id}")
        
        # Prepare response data
        response_data = {
            'message': 'Subtask created successfully',
            'subtaskId': doc_ref[1].id,
            'data': {
                'name': subtask_data['name'],
                'description': subtask_data['description'],
                'start_date': subtask_data['start_date'],
                'end_date': subtask_data['end_date'],
                'status': subtask_data['status'],
                'priority': subtask_data['priority'],
                'parent_task_id': subtask_data['parent_task_id'],
                'project_id': subtask_data['project_id'],
                'assigned_to': subtask_data['assigned_to'],
                'owner': subtask_data.get('owner'),
                'attachments': subtask_data['attachments'],
                'is_deleted': False
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
@subtask_bp.route('/api/tasks/<task_id>/subtasks', methods=['GET'])
def get_task_subtasks(task_id):
    try:
        print(f"Fetching subtasks for task_id: {task_id}")
        db = get_firestore_client()
        subtasks = db.collection('subtasks').where('parent_task_id', '==', task_id).get()

        print(f"Found {len(subtasks)} total subtasks")
        
        subtasks_list = []
        for subtask in subtasks:
            subtask_data = subtask.to_dict()
            subtask_data['id'] = subtask.id
            
            # FILTER OUT DELETED SUBTASKS (only show active ones)
            if not subtask_data.get('is_deleted', False):
                subtasks_list.append(subtask_data)
                print(f"  - Active Subtask: {subtask_data.get('name')} (ID: {subtask.id})")
            else:
                print(f"  - Skipped Deleted Subtask: {subtask_data.get('name')} (ID: {subtask.id})")
        
        print(f"Returning {len(subtasks_list)} active subtasks")
        return jsonify({'subtasks': subtasks_list}), 200
        
    except Exception as e:
        print(f"Error fetching subtasks: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@subtask_bp.route('/api/subtasks/<subtask_id>', methods=['GET','PUT', 'OPTIONS'])
def get_or_update_subtask(subtask_id):
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-Id,X-User-Role')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response, 200

    # Handle GET request
    if request.method == 'GET':
        try:
            print(f"📖 Fetching subtask by ID: {subtask_id}")
            db = get_firestore_client()
            subtask_ref = db.collection('subtasks').document(subtask_id)
            subtask_doc = subtask_ref.get()
            
            if not subtask_doc.exists:
                return jsonify({'error': 'Subtask not found'}), 404
            
            subtask_data = subtask_doc.to_dict()
            subtask_data['id'] = subtask_id
            
            if subtask_data.get('is_deleted', False):
                return jsonify({'error': 'Subtask has been deleted'}), 404
            
            collaborator_ids = subtask_data.get('assigned_to', [])
            collaborators_info = []
            
            for collab_id in collaborator_ids:
                user_doc = db.collection('Users').document(collab_id).get()
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    collaborators_info.append({
                        'id': collab_id,
                        'name': user_data.get('name', 'Unknown User'),
                        'email': user_data.get('email', ''),
                        'role_name': user_data.get('role_name', 'Staff')
                    })
                else:
                    collaborators_info.append({
                        'id': collab_id,
                        'name': 'Unknown User',
                        'email': '',
                        'role_name': 'Staff'
                    })
            
            owner_id = subtask_data.get('owner')
            owner_info = None
            if owner_id:
                owner_doc = db.collection('Users').document(owner_id).get()
                if owner_doc.exists:
                    owner_data = owner_doc.to_dict()
                    owner_info = {
                        'id': owner_id,
                        'name': owner_data.get('name', 'Unknown User'),
                        'email': owner_data.get('email', ''),
                        'role_name': owner_data.get('role_name', 'Staff')
                    }
            
            response_data = {
                'id': subtask_id,
                'name': subtask_data.get('name', 'Untitled Subtask'),
                'description': subtask_data.get('description', ''),
                'start_date': subtask_data.get('start_date'),
                'end_date': subtask_data.get('end_date'),
                'status': subtask_data.get('status', 'Unassigned'),
                'priority': subtask_data.get('priority', 5),
                'parent_task_id': subtask_data.get('parent_task_id'),
                'project_id': subtask_data.get('project_id'),
                'owner': owner_id,
                'owner_info': owner_info,
                'assigned_to': collaborator_ids,
                'collaborators': collaborators_info,
                'attachments': subtask_data.get('attachments', []),
                'status_history': subtask_data.get('status_history', []),
                'createdAt': subtask_data.get('createdAt'),
                'updatedAt': subtask_data.get('updatedAt')
            }
            
            for field in ['start_date', 'end_date', 'createdAt', 'updatedAt']:
                if field in response_data and response_data[field]:
                    try:
                        if hasattr(response_data[field], 'isoformat'):
                            response_data[field] = response_data[field].isoformat()
                    except:
                        pass
            
            return jsonify(response_data), 200
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    
    try:
        data = request.get_json()
        print("=== BACKEND SUBTASK UPDATE DEBUG ===")
        print(f"Updating subtask ID: {subtask_id}")
        print(f"Received update data: {data}")

        # Get user info first, for all updates
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
        current_owner = subtask_data.get('owner')
        collaborators = subtask_data.get('assigned_to', [])
        
        # ==================== AUTHORIZATION CHECK ====================
        # Check if user is involved in the subtask (owner or collaborator)
        if current_user_id not in collaborators and current_user_id != current_owner:
            print(f"❌ User {current_user_id} not authorized - not a collaborator or owner")
            return jsonify({'error': 'You are not authorized to edit this subtask'}), 403
        
        # Determine if current user is the owner
        is_owner = (current_user_id == current_owner)
        print(f"🔐 User is owner: {is_owner}")
        
        # ==================== PERMISSION-BASED FIELD FILTERING ====================
        # Define restricted fields (only owner can edit these)
        restricted_fields = ['name', 'start_date', 'end_date', 'priority', 'assigned_to', 'owner']
        
        # If user is NOT owner, filter out restricted fields
        if not is_owner:
            print(f"👤 User is collaborator - filtering restricted fields")
            original_data = data.copy()
            
            # Remove all restricted fields from update
            for field in restricted_fields:
                if field in data:
                    print(f"  ❌ Removing restricted field: {field}")
                    data.pop(field)
            
            # Only allow status and description for collaborators
            allowed_fields = ['status', 'description']
            data = {k: v for k, v in data.items() if k in allowed_fields}
            print(f"✅ Collaborator can only update: {list(data.keys())}")
        
        # ==================== VALIDATION ====================
        # Validate required field: name (if owner is trying to update it)
        if 'name' in data:
            if not data['name'] or len(data['name'].strip()) == 0:
                return jsonify({'error': 'Subtask name is required and cannot be empty'}), 400
        
        # Validate date range (if dates are being updated)
        if 'start_date' in data or 'end_date' in data:
            # Get current or new dates
            start_date_str = data.get('start_date', subtask_data.get('start_date'))
            end_date_str = data.get('end_date', subtask_data.get('end_date'))
            
            if start_date_str and end_date_str:
                try:
                    from datetime import datetime
                    # Handle both string and datetime objects
                    if isinstance(start_date_str, str):
                        start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                    else:
                        start_date = start_date_str
                    
                    if isinstance(end_date_str, str):
                        end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                    else:
                        end_date = end_date_str
                    
                    if end_date < start_date:
                        return jsonify({'error': 'End date must be after start date'}), 400
                except Exception as e:
                    print(f"Date validation error: {e}")
                    return jsonify({'error': 'Invalid date format'}), 400
        
        # ==================== COLLABORATOR VALIDATION (if owner is updating) ====================
        if 'assigned_to' in data and is_owner:
            new_assigned_to = data['assigned_to']
            parent_task_id = subtask_data.get('parent_task_id')
            
            if new_assigned_to and parent_task_id:
                # Get parent task collaborators
                parent_task_ref = db.collection('Tasks').document(parent_task_id)
                parent_task_doc = parent_task_ref.get()
                
                if parent_task_doc.exists:
                    parent_task_data = parent_task_doc.to_dict()
                    parent_collaborators = parent_task_data.get('assigned_to', [])
                    parent_collaborator_ids = [str(id) for id in parent_collaborators]
                    
                    # Validate each new collaborator
                    for collab_id in new_assigned_to:
                        if str(collab_id) not in parent_collaborator_ids:
                            return jsonify({
                                'error': f'Collaborator {collab_id} is not assigned to the parent task'
                            }), 400
                    
                    print("All updated collaborators are valid")
        
        # ==================== OWNERSHIP TRANSFER VALIDATION ====================
        if 'owner' in data and is_owner:
            # Check if current user is a manager
            if current_user_role != 3:
                return jsonify({'error': 'Only managers can transfer subtask ownership'}), 403
            
            # Check if new owner is in assigned_to list
            new_owner_id = data['owner']
            assigned_to = subtask_data.get('assigned_to', [])
            if str(new_owner_id) not in [str(id) for id in assigned_to]:
                return jsonify({'error': 'New owner must be assigned to the subtask'}), 400
            
            # Verify new owner is a collaborator of parent task 
            parent_task_id = subtask_data.get('parent_task_id')
            
            if parent_task_id:
                parent_task_ref = db.collection('Tasks').document(parent_task_id)
                parent_task_doc = parent_task_ref.get()
                
                if parent_task_doc.exists:
                    parent_task_data = parent_task_doc.to_dict()
                    parent_collaborators = parent_task_data.get('assigned_to', [])
                    parent_collaborator_ids = [str(id) for id in parent_collaborators]
                    
                    if str(new_owner_id) not in parent_collaborator_ids:
                        return jsonify({
                            'error': 'New owner must be a collaborator of the parent task'
                        }), 400
        
        # Store old owner ID BEFORE updating (for email notification)
        old_owner_id = subtask_data.get('owner')
        
        # ==================== STATUS HISTORY LOGGING ====================
        if 'status' in data and data['status'] != subtask_data.get('status'):
            print(f"📝 Status change detected: {subtask_data.get('status')} → {data['status']}")
            
            # Get user info for logging
            user_doc = db.collection('Users').document(current_user_id).get()
            user_name = user_doc.to_dict().get('name', 'Unknown User') if user_doc.exists else 'Unknown User'
            
            # Create status history entry
            from datetime import datetime
            status_entry = {
                'old_status': subtask_data.get('status'),
                'new_status': data['status'],
                'changed_by': current_user_id,
                'changed_by_name': user_name,
                'timestamp': datetime.now().isoformat()
            }
            
            # Get existing status history and append
            status_history = subtask_data.get('status_history', [])
            status_history.append(status_entry)
            data['status_history'] = status_history
            
            print(f"✅ Status history entry added: {status_entry}")
        
        # ==================== PREPARE UPDATE DATA ====================
        update_data = {}
        
        # Update only fields that are provided (and allowed based on permissions)
        allowed_update_fields = ['name', 'description', 'start_date', 'end_date', 
                                 'status', 'priority', 'assigned_to', 'attachments', 
                                 'status_history', 'owner']
        
        for field in allowed_update_fields:
            if field in data:
                update_data[field] = data[field]
        
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
                'priority': updated_subtask.get('priority'),
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
                    
                    subtask_name = updated_subtask.get('name', 'Untitled Subtask')
                    print(f"📨 Sending ownership transfer email...")
                    
                    # Send email notification
                    email_service.send_ownership_transfer_email(
                        new_owner_email=new_owner_email,
                        new_owner_name=new_owner_name,
                        old_owner_name=old_owner_name,
                        subtask_name=subtask_name,
                        cc_email=old_owner_email
                    )
                    print(f"✅ Email sent successfully to {new_owner_email}")
                else:
                    print(f"⚠️ New owner user document not found: {new_owner_id}")
            else:
                print("⏭️  No owner change detected")
        
        except Exception as email_error:
            # Don't fail the entire update if email fails
            print(f"⚠️  Email notification failed: {str(email_error)}")
            import traceback
            traceback.print_exc()
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Error updating subtask: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# ==================== GET SINGLE SUBTASK BY ID ====================
# ADD THIS ENDPOINT to backend/routes/subtask.py
# Add it after the get_task_subtasks function (around line 147)

@subtask_bp.route('/api/subtasks/<subtask_id>', methods=['GET', 'OPTIONS'])
def get_subtask_by_id(subtask_id):
    """Get a single subtask by ID with all details"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-Id,X-User-Role')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response, 200
    
    try:
        print(f"📖 Fetching subtask by ID: {subtask_id}")
        
        # Get Firestore client
        db = get_firestore_client()
        
        # Get subtask document
        subtask_ref = db.collection('subtasks').document(subtask_id)
        subtask_doc = subtask_ref.get()
        
        if not subtask_doc.exists:
            print(f"❌ Subtask not found: {subtask_id}")
            return jsonify({'error': 'Subtask not found'}), 404
        
        # Get subtask data
        subtask_data = subtask_doc.to_dict()
        subtask_data['id'] = subtask_id
        
        # Check if subtask is deleted
        if subtask_data.get('is_deleted', False):
            print(f"⚠️ Subtask is deleted: {subtask_id}")
            return jsonify({'error': 'Subtask has been deleted'}), 404
        
        # Get collaborator details (expand user info)
        collaborator_ids = subtask_data.get('assigned_to', [])
        collaborators_info = []
        
        for collab_id in collaborator_ids:
            user_doc = db.collection('Users').document(collab_id).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                collaborators_info.append({
                    'id': collab_id,
                    'name': user_data.get('name', 'Unknown User'),
                    'email': user_data.get('email', ''),
                    'role_name': user_data.get('role_name', 'Staff')
                })
            else:
                collaborators_info.append({
                    'id': collab_id,
                    'name': 'Unknown User',
                    'email': '',
                    'role_name': 'Staff'
                })
        
        # Get owner details
        owner_id = subtask_data.get('owner')
        owner_info = None
        if owner_id:
            owner_doc = db.collection('Users').document(owner_id).get()
            if owner_doc.exists:
                owner_data = owner_doc.to_dict()
                owner_info = {
                    'id': owner_id,
                    'name': owner_data.get('name', 'Unknown User'),
                    'email': owner_data.get('email', ''),
                    'role_name': owner_data.get('role_name', 'Staff')
                }
        
        # Prepare response with all required fields
        response_data = {
            'id': subtask_id,
            'name': subtask_data.get('name', 'Untitled Subtask'),
            'description': subtask_data.get('description', ''),
            'start_date': subtask_data.get('start_date'),
            'end_date': subtask_data.get('end_date'),
            'status': subtask_data.get('status', 'Unassigned'),
            'priority': subtask_data.get('priority', 5),
            'parent_task_id': subtask_data.get('parent_task_id'),
            'project_id': subtask_data.get('project_id'),
            'owner': owner_id,
            'owner_info': owner_info,
            'assigned_to': collaborator_ids,
            'collaborators': collaborators_info,  # Expanded user info
            'attachments': subtask_data.get('attachments', []),
            'status_history': subtask_data.get('status_history', []),
            'createdAt': subtask_data.get('createdAt'),
            'updatedAt': subtask_data.get('updatedAt')
        }
        
        # Convert timestamps to ISO format if needed
        for field in ['start_date', 'end_date', 'createdAt', 'updatedAt']:
            if field in response_data and response_data[field]:
                try:
                    if hasattr(response_data[field], 'isoformat'):
                        response_data[field] = response_data[field].isoformat()
                except:
                    pass
        
        print(f"✅ Subtask fetched successfully: {subtask_data.get('name')}")
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ Error fetching subtask: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ==================== TRANSFER SUBTASK OWNERSHIP ====================
@subtask_bp.route('/api/subtasks/<subtask_id>/transfer-ownership', methods=['PUT', 'OPTIONS'])
def transfer_subtask_ownership(subtask_id):
    """Transfer ownership of a subtask to another collaborator"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-Id,X-User-Role')
        response.headers.add('Access-Control-Allow-Methods', 'PUT,OPTIONS')
        return response, 200
    
    try:
        data = request.get_json()
        current_user_id = request.headers.get('X-User-Id')
        current_user_role = request.headers.get('X-User-Role')
        new_owner_id = data.get('new_owner_id')
        
        if not current_user_id or not new_owner_id:
            return jsonify({'error': 'Missing required fields'}), 400
        
        if not current_user_role:
            return jsonify({'error': 'User role is required'}), 401
        
        try:
            current_user_role = int(current_user_role)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid user role format'}), 400
        
        db = get_firestore_client()
        subtask_ref = db.collection('subtasks').document(subtask_id)
        subtask_doc = subtask_ref.get()
        
        if not subtask_doc.exists:
            return jsonify({'error': 'Subtask not found'}), 404
        
        subtask_data = subtask_doc.to_dict()
        current_owner = subtask_data.get('owner')
        collaborators = subtask_data.get('assigned_to', [])
        
        if current_user_id != current_owner:
            return jsonify({'error': 'Only the current owner can transfer ownership'}), 403
        
        if current_user_role != 3:
            return jsonify({'error': 'Only managers can transfer subtask ownership'}), 403
        
        if new_owner_id not in collaborators:
            return jsonify({'error': 'New owner must be a collaborator of this subtask'}), 400
        
        subtask_ref.update({
            'owner': new_owner_id,
            'updatedAt': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({
            'message': 'Ownership transferred successfully',
            'new_owner': new_owner_id
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
# =============== SOFT DELETE SUBTASK ===============
@subtask_bp.route('/api/subtasks/<subtask_id>/delete', methods=['PUT'])
def soft_delete_subtask(subtask_id):
    try:
        print(f"🗑️ Soft deleting subtask: {subtask_id}")
        
        db = get_firestore_client()
        
        # Get the subtask first
        subtask_ref = db.collection('subtasks').document(subtask_id)
        subtask_doc = subtask_ref.get()
        
        if not subtask_doc.exists:
            print(f"Subtask {subtask_id} not found")
            return jsonify({'error': 'Subtask not found'}), 404
        
        subtask_data = subtask_doc.to_dict()
        
        # Get user ID from request body
        request_data = request.get_json()
        user_id = request_data.get('userId') if request_data else None
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        # VALIDATE: Only subtask owner can delete
        if str(subtask_data.get('owner')) != str(user_id):
            return jsonify({'error': 'Only the subtask owner can delete this subtask'}), 403
        
        # SOFT DELETE: Set is_deleted = True
        update_data = {
            'is_deleted': True,
            'deleted_at': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        subtask_ref.update(update_data)
        print(f"Subtask {subtask_id} soft deleted successfully")
        
        return jsonify({
            "message": "Subtask moved to deleted items successfully",
            "subtask_id": subtask_id,
            "is_deleted": True,
            "subtask_name": subtask_data.get('name', 'Unknown Subtask')
        }), 200
        
    except Exception as e:
        print(f"Error soft deleting subtask {subtask_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@subtask_bp.route('/api/subtasks/test-debug', methods=['GET'])
def test_debug():
    """Simple test to see if subtask routes work"""
    try:
        db = get_firestore_client()
        user_id = request.args.get('userId', 'test')
        
        print(f"TEST DEBUG: Looking for user {user_id}")
        
        # Get ALL subtasks (no filtering)
        all_subtasks = db.collection('subtasks').get()
        
        result = {
            "total_subtasks": len(list(all_subtasks)),
            "test_user_id": user_id,
            "message": "Subtask routes are working!",
            "collection_name": "subtasks"
        }
        
        # Reset the iterator and get deleted ones
        deleted_subtasks = db.collection('subtasks').where('is_deleted', '==', True).get()
        result["deleted_count"] = len(list(deleted_subtasks))
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@subtask_bp.route('/api/subtasks/debug-everything', methods=['GET'])
def debug_everything():
    """Ultimate debug - show EVERYTHING"""
    try:
        db = get_firestore_client()
        
        # Get ALL subtasks, no filtering at all
        all_subtasks = db.collection('subtasks').get()
        
        debug_info = {
            "total_subtasks_found": len(list(all_subtasks)),
            "collection_name": "subtasks",
            "server_working": True,
            "subtasks": []
        }
        
        # Reset iterator and get actual data
        all_docs = db.collection('subtasks').get()
        for doc in all_docs:
            data = doc.to_dict()
            debug_info["subtasks"].append({
                "id": doc.id,
                "name": data.get('name', 'NO NAME'),
                "owner": data.get('owner', 'NO OWNER'),
                "is_deleted": data.get('is_deleted', 'NO IS_DELETED FIELD'),
                "all_field_names": list(data.keys())
            })
        
        return jsonify(debug_info), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "server_working": False,
            "message": "Something is broken"
        }), 500

@subtask_bp.route('/api/test-route-works', methods=['GET'])
def test_route_works():
    return jsonify({"message": "ROUTE WORKS!", "success": True}), 200

# =============== GET DELETED SUBTASKS ===============
@subtask_bp.route('/api/subtasks/deleted-new', methods=['GET'])
def get_deleted_subtasks_NEW():
    """Get deleted subtasks for a user (only subtasks they directly own)"""
    try:
        print("DELETED SUBTASKS ROUTE HIT (OWNERSHIP RESTRICTED)!")
        
        db = get_firestore_client()
        user_id = request.args.get("userId")
        
        if not user_id:
            return jsonify({"error": "userId parameter is required"}), 400
        
        print(f"Looking for deleted subtasks OWNED BY user: {user_id}")
        
        # Query ALL deleted subtasks
        all_deleted_query = db.collection("subtasks").where("is_deleted", "==", True)
        all_deleted_results = all_deleted_query.stream()
        
        subtasks = []
        
        for doc in all_deleted_results:
            subtask = doc.to_dict()
            subtask["id"] = doc.id
            
            # ONLY include subtasks that the user directly owns
            # EXCLUDE cascade deleted subtasks owned by other users
            if subtask.get('owner') == user_id:
                # Convert timestamps to ISO format
                for field in ['deleted_at', 'start_date', 'end_date']:
                    if field in subtask and subtask[field]:
                        try:
                            subtask[field] = subtask[field].isoformat()
                        except:
                            pass
                
                subtasks.append(subtask)
                
                # Debug: Show what type of deletion this was
                if subtask.get('deleted_by_cascade', False):
                    print(f"INCLUDED CASCADE (user owns subtask): {subtask.get('name', 'Unknown')}")
                else:
                    print(f"INCLUDED DIRECT DELETE: {subtask.get('name', 'Unknown')}")
            
            else:
                # Debug: Show what we're excluding
                if subtask.get('deleted_by_cascade', False):
                    cascade_parent_id = subtask.get('cascade_parent_id')
                    print(f"EXCLUDED CASCADE (not subtask owner): {subtask.get('name', 'Unknown')} (subtask owner: {subtask.get('owner')}, task: {cascade_parent_id})")
                else:
                    print(f"EXCLUDED (not owner): {subtask.get('name', 'Unknown')} (owner: {subtask.get('owner')})")
        
        print(f"📊 TOTAL FOUND: {len(subtasks)} deleted subtasks owned by user")
        return jsonify(subtasks), 200

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# =============== RESTORE SUBTASK ===============
@subtask_bp.route('/api/subtasks/<subtask_id>/restore-new', methods=['PUT'])
def restore_subtask_NEW(subtask_id):
    try:
        print(f"Restoring subtask: {subtask_id}")
        
        db = get_firestore_client()
        subtask_ref = db.collection('subtasks').document(subtask_id)
        
        doc = subtask_ref.get()
        if not doc.exists:
            return jsonify({'error': 'Subtask not found'}), 404
        
        # Restore subtask
        subtask_ref.update({
            'is_deleted': False,
            'deleted_at': None,
            'updatedAt': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({"message": "Subtask restored successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =============== PERMANENTLY DELETE SUBTASK ===============
@subtask_bp.route('/api/subtasks/<subtask_id>/permanent-new', methods=['DELETE'])
def permanently_delete_subtask_NEW(subtask_id):
    try:
        print(f"Permanently deleting subtask: {subtask_id}")
        
        db = get_firestore_client()
        subtask_ref = db.collection('subtasks').document(subtask_id)
        
        doc = subtask_ref.get()
        if not doc.exists:
            return jsonify({'error': 'Subtask not found'}), 404
        
        # Hard delete
        subtask_ref.delete()
        
        return jsonify({"message": "Subtask permanently deleted"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== GET TEAM SUBTASKS FOR MANAGER ====================
@subtask_bp.route('/api/subtasks/team/<manager_id>', methods=['GET'])
def get_team_subtasks(manager_id):
    """Get all subtasks owned by team members under this manager"""
    try:
        print(f"Getting team subtasks for manager: {manager_id}")
        
        db = get_firestore_client()
        
        # Step 1: Get the manager's info
        manager_doc = db.collection('Users').document(manager_id).get()
        
        if not manager_doc.exists:
            print(f"Manager not found: {manager_id}")
            return jsonify({'error': 'Manager not found'}), 404
        
        manager_data = manager_doc.to_dict()
        manager_division = manager_data.get('division_name')
        manager_role = manager_data.get('role_num')
        
        print(f"Manager: {manager_data.get('name')} | Division: {manager_division} | Role: {manager_role}")
        
        # Validate that user is actually a manager
        if manager_role not in [2, 3]:  # 2=Director, 3=Manager
            print(f"User is not a manager (role_num: {manager_role})")
            return jsonify({'error': 'User is not authorized to view team subtasks'}), 403
        
        if not manager_division:
            print(f"Manager has no division")
            return jsonify({'error': 'Manager has no division assigned'}), 400
        
        # Step 2: Get all staff in the same division (role_num = 4)
        staff_query = db.collection('Users').where('division_name', '==', manager_division).where('role_num', '==', 4)
        staff_docs = staff_query.get()
        
        # Create a map of user_id -> user_name for quick lookup
        staff_map = {}
        staff_ids = []
        
        for staff_doc in staff_docs:
            staff_data = staff_doc.to_dict()
            staff_id = staff_doc.id
            staff_ids.append(staff_id)
            staff_map[staff_id] = staff_data.get('name', 'Unknown User')
        
        print(f"Found {len(staff_ids)} staff members in {manager_division} division")
        
        if not staff_ids:
            print(f"No staff members found in division")
            return jsonify([]), 200
        
        # Step 3: Get all subtasks owned by these staff members
        # Firebase 'in' operator can only handle up to 10 items
        all_subtasks = []
        
        # Process in batches of 10
        for i in range(0, len(staff_ids), 10):
            batch_ids = staff_ids[i:i+10]
            print(f"Querying subtasks for batch {i//10 + 1} ({len(batch_ids)} staff)")
            
            subtasks_query = db.collection('subtasks').where('owner', 'in', batch_ids).where('is_deleted', '==', False)
            subtasks_docs = subtasks_query.get()
            
            for subtask_doc in subtasks_docs:
                subtask_data = subtask_doc.to_dict()
                
                # Build response object
                owner_id = subtask_data.get('owner')
                subtask_response = {
                    'id': subtask_doc.id,
                    'name': subtask_data.get('name', 'Untitled Subtask'),
                    'ownerName': staff_map.get(owner_id, 'Unknown User'),
                    'owner_id': owner_id,
                    'description': subtask_data.get('description', ''),
                    'start_date': subtask_data.get('start_date'),
                    'end_date': subtask_data.get('end_date'),
                    'status': subtask_data.get('status', 'Unassigned'),
                    'priority': subtask_data.get('priority', 0), # Get priority from subtask
                    'task_id': subtask_data.get('parent_task_id'),
                    'proj_ID': subtask_data.get('project_id'),
                    'assigned_to': subtask_data.get('assigned_to', []),
                    'attachments': subtask_data.get('attachments', [])
                }
                
                # Convert Firestore timestamps to ISO format 
                for field in ['start_date', 'end_date']:
                    if field in subtask_response and subtask_response[field]:
                        try:
                            if hasattr(subtask_response[field], 'isoformat'):
                                subtask_response[field] = subtask_response[field].isoformat()
                        except:
                            pass
                
                all_subtasks.append(subtask_response)
        
        print(f"Found {len(all_subtasks)} total subtasks for {manager_division} team")
        
        return jsonify(all_subtasks), 200
        
    except Exception as e:
        print(f"Error getting team subtasks: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
