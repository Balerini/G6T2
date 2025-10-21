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
        print(f"🔥 BACKEND SUBTASK CREATION DEBUG")
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
        
        # Create subtask document with proper structure
        subtask_data = {
            'name': data['name'],
            'description': data.get('description', ''),
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'status': data['status'],
            'priority': data.get('priority', 5), # Default priority is 5 (medium)
            'parent_task_id': data['parent_task_id'],
            'project_id': data['project_id'],
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
@subtask_bp.route('/tasks/<task_id>/subtasks', methods=['GET'])
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
    
# ==================== UPDATE SUBTASK ====================
@subtask_bp.route('/api/subtasks/<subtask_id>', methods=['PUT', 'OPTIONS'])  # Add /api/ prefix and OPTIONS
def update_subtask(subtask_id):
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-Id,X-User-Role')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response, 200
    
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
        
        # Check if subtask exists - USE LOWERCASE COLLECTION
        subtask_ref = db.collection('subtasks').document(subtask_id)  # Changed to lowercase
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
        if 'priority' in data:
            update_data['priority'] = data['priority']
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
            print(f"❌ Subtask {subtask_id} not found")
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
        print(f"✅ Subtask {subtask_id} soft deleted successfully")
        
        return jsonify({
            "message": "Subtask moved to deleted items successfully",
            "subtask_id": subtask_id,
            "is_deleted": True,
            "subtask_name": subtask_data.get('name', 'Unknown Subtask')
        }), 200
        
    except Exception as e:
        print(f"❌ Error soft deleting subtask {subtask_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@subtask_bp.route('/subtasks/test-debug', methods=['GET'])
def test_debug():
    """Simple test to see if subtask routes work"""
    try:
        db = get_firestore_client()
        user_id = request.args.get('userId', 'test')
        
        print(f"🔍 TEST DEBUG: Looking for user {user_id}")
        
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

@subtask_bp.route('/subtasks/debug-everything', methods=['GET'])
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
        print("🔥 DELETED SUBTASKS ROUTE HIT (OWNERSHIP RESTRICTED)!")
        
        db = get_firestore_client()
        user_id = request.args.get("userId")
        
        if not user_id:
            return jsonify({"error": "userId parameter is required"}), 400
        
        print(f"🔍 Looking for deleted subtasks OWNED BY user: {user_id}")
        
        # Query ALL deleted subtasks
        all_deleted_query = db.collection("subtasks").where("is_deleted", "==", True)
        all_deleted_results = all_deleted_query.stream()
        
        subtasks = []
        
        for doc in all_deleted_results:
            subtask = doc.to_dict()
            subtask["id"] = doc.id
            
            # ✅ ONLY include subtasks that the user directly owns
            # ⛔ EXCLUDE cascade deleted subtasks owned by other users
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
                    print(f"✅ INCLUDED CASCADE (user owns subtask): {subtask.get('name', 'Unknown')}")
                else:
                    print(f"✅ INCLUDED DIRECT DELETE: {subtask.get('name', 'Unknown')}")
            
            else:
                # Debug: Show what we're excluding
                if subtask.get('deleted_by_cascade', False):
                    cascade_parent_id = subtask.get('cascade_parent_id')
                    print(f"⛔ EXCLUDED CASCADE (not subtask owner): {subtask.get('name', 'Unknown')} (subtask owner: {subtask.get('owner')}, task: {cascade_parent_id})")
                else:
                    print(f"⛔ EXCLUDED (not owner): {subtask.get('name', 'Unknown')} (owner: {subtask.get('owner')})")
        
        print(f"📊 TOTAL FOUND: {len(subtasks)} deleted subtasks owned by user")
        return jsonify(subtasks), 200

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# =============== RESTORE SUBTASK ===============
@subtask_bp.route('/api/subtasks/<subtask_id>/restore-new', methods=['PUT'])
def restore_subtask_NEW(subtask_id):
    try:
        print(f"🔄 Restoring subtask: {subtask_id}")
        
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
        print(f"💥 Permanently deleting subtask: {subtask_id}")
        
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
    
@subtask_bp.route('/api/tasks/<task_id>/subtasks', methods=['GET'])
def get_subtasks_by_task(task_id):
    """Get all active subtasks for a specific task"""
    try:
        print(f"📋 Getting subtasks for task: {task_id}")
        
        db = get_firestore_client()
        
        # Query subtasks by parent_task_id and not deleted
        subtasks_ref = db.collection('subtasks')
        query = subtasks_ref.where('parent_task_id', '==', task_id).where('is_deleted', '==', False)
        subtasks = query.get()
        
        subtask_list = []
        for doc in subtasks:
            subtask_data = doc.to_dict()
            subtask_data['id'] = doc.id
            
            # Convert Firestore timestamps to ISO format
            for field in ['createdAt', 'updatedAt', 'start_date', 'end_date']:
                if field in subtask_data and subtask_data[field]:
                    try:
                        subtask_data[field] = subtask_data[field].isoformat()
                    except:
                        pass
            
            subtask_list.append(subtask_data)
        
        print(f"✅ Found {len(subtask_list)} subtasks for task {task_id}")
        return jsonify(subtask_list), 200
        
    except Exception as e:
        print(f"❌ Error fetching subtasks: {str(e)}")
        return jsonify({'error': str(e)}), 500
    

# ==================== GET TEAM SUBTASKS FOR MANAGER ====================
@subtask_bp.route('/api/subtasks/team/<manager_id>', methods=['GET'])
def get_team_subtasks(manager_id):
    """Get all subtasks owned by team members under this manager"""
    try:
        print(f"📊 Getting team subtasks for manager: {manager_id}")
        
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
            print(f"ℹ️ No staff members found in division")
            return jsonify([]), 200
        
        # Step 3: Get all subtasks owned by these staff members
        # Firebase 'in' operator can only handle up to 10 items
        all_subtasks = []
        
        # Process in batches of 10
        for i in range(0, len(staff_ids), 10):
            batch_ids = staff_ids[i:i+10]
            print(f"🔍 Querying subtasks for batch {i//10 + 1} ({len(batch_ids)} staff)")
            
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
