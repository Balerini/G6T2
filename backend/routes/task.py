from flask import Blueprint, jsonify, request
from firebase_utils import get_firestore_client
from firebase_admin import firestore
from datetime import datetime
import traceback
import pytz
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.notification_service import notification_service


tasks_bp = Blueprint('tasks', __name__)

# =============== CREATE TASK ===============
@tasks_bp.route('/api/tasks', methods=['POST'])
def create_task():
    try:
        task_data = request.get_json()
        print("=== BACKEND TASK CREATION DEBUG ===")
        print(f"Received task data: {task_data}")
        print(f"Priority level received: {task_data.get('priority_level')}")  # Changed to priority_level
        
        # Validate required fields
        required_fields = ['task_name', 'start_date', 'priority_level']  # Changed to priority_level
        for field in required_fields:
            if not task_data.get(field):
                return jsonify({'error': f'Required field missing: {field}'}), 400

        # Validate priority level range
        try:
            priority_level = int(task_data.get('priority_level'))  # Changed variable name
            if priority_level < 1 or priority_level > 10:
                return jsonify({'error': 'Priority level must be between 1 and 10'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Priority level must be a valid number between 1 and 10'}), 400

        # Get Firestore client
        db = get_firestore_client()

        # Get creator ID early so we can use it throughout
        owner_id = task_data.get('owner', '')

        # Convert date strings to datetime objects with Singapore timezone
        sg_tz = pytz.timezone('Asia/Singapore')
        
        start_date = datetime.strptime(task_data['start_date'], '%Y-%m-%d')
        start_date = sg_tz.localize(start_date)
        
        end_date = None
        if task_data.get('end_date'):
            end_date = datetime.strptime(task_data['end_date'], '%Y-%m-%d')
            # Set end time to end of day in Singapore timezone
            end_date = sg_tz.localize(end_date.replace(hour=23, minute=59, second=59))

        # Get project ID from project name if provided
        proj_id = None
        if task_data.get('proj_name'):
            # Find the project by name to get its ID
            projects_ref = db.collection('Projects')
            projects_query = projects_ref.where('proj_name', '==', task_data.get('proj_name')).limit(1)
            project_docs = list(projects_query.stream())
            if project_docs:
                proj_id = project_docs[0].id
                print(f"Found project ID {proj_id} for project name: {task_data.get('proj_name')}")
            else:
                print(f"Warning: Project not found for name: {task_data.get('proj_name')}")
                # List all available projects for debugging
                all_projects = projects_ref.stream()
                print("Available projects:")
                for proj in all_projects:
                    proj_data = proj.to_dict()
                    print(f"  - ID: {proj.id}, Name: {proj_data.get('proj_name', 'No name')}")
        else:
            print("No project name provided in task data")

        # Prepare task data for Firestore
        firestore_task_data = {
            'proj_name': task_data.get('proj_name', ''),
            'proj_ID': proj_id,
            'task_name': task_data['task_name'],
            'task_desc': task_data.get('task_desc', ''),
            'start_date': start_date,
            'end_date': end_date,
            'owner': owner_id,
            'assigned_to': task_data.get('assigned_to', []), 
            'attachments': task_data.get('attachments', []),
            'task_status': task_data.get('task_status'),
            'priority_level': priority_level,  
            'hasSubtasks': task_data.get('hasSubtasks', False),
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }

        # Add document to Firestore
        print(f"Adding task to Firestore: {firestore_task_data}")
        print(f"Creating task: {firestore_task_data['task_name']} with assigned_to: {task_data.get('assigned_to', [])}")  # FIXED THIS LINE
        doc_ref = db.collection('Tasks').add(firestore_task_data)
        task_id = doc_ref[1].id
        print(f"Task created successfully with ID: {task_id}")

        # Prepare response data
        response_data = firestore_task_data.copy()
        response_data['id'] = task_id
        response_data['start_date'] = start_date.isoformat()
        if end_date:
            response_data['end_date'] = end_date.isoformat()
        response_data['createdAt'] = datetime.now(sg_tz).isoformat()
        response_data['updatedAt'] = datetime.now(sg_tz).isoformat()
        response_data['proj_ID'] = proj_id

        # ================== SEND EMAILS TO ASSIGNED USERS ==================
        try:
            from email_service import email_service

            # Get creator's info (for the "owner" field)
            creator_name = 'Unknown User'
            if owner_id:
                creator_doc = db.collection('Users').document(owner_id).get()
                creator_name = creator_doc.to_dict().get('name', 'Unknown User') if creator_doc.exists else 'Unknown User'

            # Send emails to each assigned user (except creator)
            assigned_users = task_data.get('assigned_to', [])  # FIXED THIS LINE
            for user_id in assigned_users:  # FIXED THIS LINE
                if user_id == owner_id:
                    continue

                user_doc = db.collection('Users').document(user_id).get()
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    to_email = user_data.get('email')
                    user_name = user_data.get('name', 'User')

                    if to_email:
                        email_service.send_task_assignment_email(
                            to_email=to_email,
                            user_name=user_name,
                            task_name=firestore_task_data['task_name'],
                            task_desc=firestore_task_data.get('task_desc', ''),
                            project_name=firestore_task_data.get('proj_name', ''),
                            creator_name=creator_name,
                            start_date=str(firestore_task_data['start_date'].date()),
                            end_date=str(firestore_task_data['end_date'].date()) if firestore_task_data.get('end_date') else None,
                            priority_level=firestore_task_data.get('priority_level', '')  
                        )
                    else:
                        print(f"⚠️ No email found for user {user_id}")
        except Exception as e:
            print(f"❌ Failed to send email notifications: {e}")

        # ================== CREATE NOTIFICATIONS FOR STAFF ==================
        try:
            # Notify assigned staff members about task assignment
            assigned_users = task_data.get('assigned_to', [])
            if assigned_users:
                notification_task_data = {
                    'task_name': firestore_task_data['task_name'],
                    'task_ID': task_id,
                    'id': task_id,
                    'proj_ID': proj_id
                }
                notification_service.notify_task_assigned(notification_task_data, assigned_users)
                print(f"✅ Notifications created for {len(assigned_users)} assigned users")
        except Exception as e:
            print(f"❌ Failed to create notifications: {e}")

        return jsonify(response_data), 201

    except ValueError as e:
        return jsonify({'error': f'Invalid date format. Use YYYY-MM-DD: {str(e)}'}), 400
    except Exception as e:
        print(f"Error creating task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@tasks_bp.route("/api/tasks", methods=["GET"])
def get_tasks():
    try:
        db = get_firestore_client()
        print("entered app.py")
        user_id = request.args.get("userId")
        tasks_ref = db.collection("Tasks")

        if user_id:
            query = tasks_ref.where("assigned_to", "array_contains", user_id)
            results = query.stream()
        else:
            results = tasks_ref.stream()

        tasks = []
        for doc in results:
            task = doc.to_dict()
            task["id"] = doc.id
            tasks.append(task)
            print(doc.id)

        return jsonify(tasks), 200

    except Exception as e:
        print("Error fetching tasks:", e)
        return jsonify({"error": str(e)}), 500

# =============== GET SINGLE TASK ===============
@tasks_bp.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    try:
        db = get_firestore_client()
        doc_ref = db.collection('Tasks').document(task_id)
        doc = doc_ref.get()

        if doc.exists:
            task_data = doc.to_dict()
            task_data['id'] = doc.id
            
            # Convert timestamps to ISO format
            if 'start_date' in task_data and task_data['start_date']:
                task_data['start_date'] = task_data['start_date'].isoformat()
            if 'end_date' in task_data and task_data['end_date']:
                task_data['end_date'] = task_data['end_date'].isoformat()
            if 'createdAt' in task_data and task_data['createdAt']:
                task_data['createdAt'] = task_data['createdAt'].isoformat()
            if 'updatedAt' in task_data and task_data['updatedAt']:
                task_data['updatedAt'] = task_data['updatedAt'].isoformat()

            return jsonify(task_data), 200
        else:
            return jsonify({'error': 'Task not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============== UPDATE TASK ===============
@tasks_bp.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """
    Update a task.

    URL Param:
      task_id: Either Firestore document id or business task_ID.

    Body (JSON): Partial update. Recognized fields include
      - proj_ID, task_ID, task_name, task_desc
      - start_date (YYYY-MM-DD)
      - end_date   (YYYY-MM-DD)
      - task_status
      - assigned_to (array)
      - status_log: optional array with a single entry
          { changed_by, timestamp (ISO), new_status }

    Notes:
      - Dates are converted to Firestore timestamps (end date set to end-of-day)
      - If task_id is not a valid document id, resolves by task_ID (and proj_ID if provided)
      - status_log is appended (ArrayUnion) instead of overwriting
    """
    try:
        print(f"\n🔧 === UPDATE TASK CALLED === Task ID: {task_id}")
        update_data = request.get_json()
        print(f"📦 Update data received: {list(update_data.keys())}")
        db = get_firestore_client()
        
        # Handle date conversion if dates are being updated with Singapore timezone
        sg_tz = pytz.timezone('Asia/Singapore')
        
        if 'start_date' in update_data and update_data['start_date']:
            start_date = datetime.strptime(update_data['start_date'], '%Y-%m-%d')
            update_data['start_date'] = sg_tz.localize(start_date)
        
        if 'end_date' in update_data and update_data['end_date']:
            end_date = datetime.strptime(update_data['end_date'], '%Y-%m-%d')
            update_data['end_date'] = sg_tz.localize(end_date.replace(hour=23, minute=59, second=59))

        # Add updated timestamp
        update_data['updatedAt'] = firestore.SERVER_TIMESTAMP

        tasks_col = db.collection('Tasks')

        # Try to resolve by Firestore document id first
        doc_ref = tasks_col.document(task_id)
        doc = doc_ref.get()

        # If not found, try to resolve by business task_ID (and proj_ID if provided)
        if not doc.exists:
            query = tasks_col.where('task_ID', '==', task_id)
            # Narrow by proj_ID if available in payload
            proj_id = update_data.get('proj_ID')
            if proj_id:
                query = query.where('proj_ID', '==', proj_id)
            results = list(query.stream())
            if not results and proj_id:
                # fallback: try without proj filter in case payload proj_ID mismatches
                results = list(tasks_col.where('task_ID', '==', task_id).stream())
            if not results:
                return jsonify({'error': 'Task not found'}), 404
            doc_ref = results[0].reference

        # Get the OLD document data BEFORE updating (for notification comparison)
        old_doc = doc_ref.get()
        old_assigned_to = old_doc.to_dict().get('assigned_to', []) if old_doc.exists else []
        
        # If status_log present, append rather than overwrite
        status_log_update = None
        if 'status_log' in update_data and isinstance(update_data['status_log'], list) and update_data['status_log']:
            try:
                entry = update_data['status_log'][0]
                status_log_update = firestore.ArrayUnion([entry])
            except Exception:
                status_log_update = None
            # remove from direct update to avoid overwrite
            update_data.pop('status_log', None)

        # Apply the update
        if update_data:
            doc_ref.update(update_data)
        if status_log_update is not None:
            doc_ref.update({'status_log': status_log_update})

        # Get updated document for response
        updated_doc = doc_ref.get()
        if updated_doc.exists:
            response_data = updated_doc.to_dict()
            response_data['id'] = updated_doc.id
            
            # Convert timestamps for response
            if 'start_date' in response_data and response_data['start_date']:
                response_data['start_date'] = response_data['start_date'].isoformat()
            if 'end_date' in response_data and response_data['end_date']:
                response_data['end_date'] = response_data['end_date'].isoformat()
            if 'updatedAt' in response_data and response_data['updatedAt']:
                response_data['updatedAt'] = response_data['updatedAt'].isoformat()
            if 'createdAt' in response_data and response_data['createdAt']:
                response_data['createdAt'] = response_data['createdAt'].isoformat()

            # ================== CREATE NOTIFICATIONS FOR TASK UPDATES ==================
            try:
                print(f"🔔 NOTIFICATION BLOCK REACHED")
                
                # Get the NEW assigned_to list (after update)
                # old_assigned_to was captured before the update above
                new_assigned_to = response_data.get('assigned_to', [])
                
                # Determine what ACTUALLY changed by comparing old vs new values
                # Exclude only true metadata/system fields
                metadata_fields = ['updatedAt', 'createdAt', 'status_log', 'id', 'task_ID', 'proj_ID']
                old_values_dict = old_doc.to_dict() if old_doc.exists else {}
                
                actually_changed = []
                for key in update_data.keys():
                    if key in metadata_fields:
                        continue
                    
                    old_val = old_values_dict.get(key)
                    new_val = update_data.get(key)
                    
                    # Compare values (handle different types)
                    if key == 'assigned_to':
                        # For lists, sort and compare
                        old_sorted = sorted(old_val) if old_val else []
                        new_sorted = sorted(new_val) if new_val else []
                        if old_sorted != new_sorted:
                            actually_changed.append(key)
                            print(f"   ✓ {key} changed: {old_sorted} → {new_sorted}")
                    elif key in ['start_date', 'end_date']:
                        # For dates, compare the calendar date only (ignore time and timezone)
                        old_date = old_val.date() if old_val and hasattr(old_val, 'date') else None
                        new_date = new_val.date() if new_val and hasattr(new_val, 'date') else None
                        
                        if old_date != new_date:
                            actually_changed.append(key)
                            print(f"   ✓ {key} changed: {old_date} → {new_date}")
                    elif old_val != new_val:
                        actually_changed.append(key)
                        print(f"   ✓ {key} changed: '{old_val}' (type: {type(old_val).__name__}) → '{new_val}' (type: {type(new_val).__name__})")
                
                updated_fields = actually_changed
                assignment_changed = 'assigned_to' in updated_fields
                other_fields_changed = [f for f in updated_fields if f != 'assigned_to']
                
                print(f"   All update_data keys: {list(update_data.keys())}")
                print(f"   Actually changed fields: {updated_fields}")
                print(f"   Assignment changed: {assignment_changed}")
                print(f"   Other fields changed: {other_fields_changed}")
                print(f"   Old assigned_to: {old_assigned_to}")
                print(f"   New assigned_to: {new_assigned_to}")
                
                notification_task_data = {
                    'task_name': response_data.get('task_name', 'Unknown Task'),
                    'task_ID': response_data.get('task_ID'),
                    'id': updated_doc.id,
                    'proj_ID': response_data.get('proj_ID')
                }
                
                # Prepare old and new values for changed fields
                old_values = old_doc.to_dict() if old_doc.exists else {}
                new_values = response_data
                
                # SCENARIO 1: Assignment changed - notify NEWLY added users about assignment
                if assignment_changed and new_assigned_to:
                    newly_assigned = [user for user in new_assigned_to if user not in old_assigned_to]
                    already_assigned = [user for user in new_assigned_to if user in old_assigned_to]
                    
                    # Notify newly assigned users
                    if newly_assigned:
                        print(f"🎯 Notifying {len(newly_assigned)} NEWLY assigned users")
                        notification_service.notify_task_assigned(notification_task_data, newly_assigned)
                        print(f"✅ Task assignment notifications sent to: {newly_assigned}")
                    
                    # If other fields also changed, notify already assigned users about updates
                    if other_fields_changed and already_assigned:
                        print(f"🎯 Notifying {len(already_assigned)} ALREADY assigned users about updates")
                        notification_service.notify_task_updated(notification_task_data, already_assigned, other_fields_changed, old_values, new_values)
                        print(f"✅ Task update notifications sent to: {already_assigned}")
                
                # SCENARIO 2: Other fields changed WITHOUT assignment change - notify ALL current assignees
                elif other_fields_changed and new_assigned_to:
                    print(f"🎯 Notifying {len(new_assigned_to)} users about task details update (no assignment change)")
                    notification_service.notify_task_updated(notification_task_data, new_assigned_to, other_fields_changed, old_values, new_values)
                    print(f"✅ Task update notifications sent")
                else:
                    print(f"⏭️  No notifications needed (no changes or no assignees)")
                
            except Exception as e:
                print(f"❌ Failed to create update notifications: {e}")
                import traceback
                traceback.print_exc()

            return jsonify(response_data), 200
        else:
            return jsonify({'error': 'Task not found after update'}), 404

    except ValueError as e:
        return jsonify({'error': f'Invalid date format. Use YYYY-MM-DD: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============== DELETE TASK ===============
@tasks_bp.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        db = get_firestore_client()
        doc_ref = db.collection('Tasks').document(task_id)
        
        # Check if document exists before deleting
        doc = doc_ref.get()
        if not doc.exists:
            return jsonify({'error': 'Task not found'}), 404
        
        # Delete document
        doc_ref.delete()

        return jsonify({'message': 'Task deleted successfully', 'id': task_id}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============== GET TASKS BY PROJECT ID ===============
@tasks_bp.route('/api/projects/<proj_id>/tasks', methods=['GET'])
def get_tasks_by_project(proj_id):
    try:
        db = get_firestore_client()
        tasks_ref = db.collection('Tasks')
        # Query tasks by project ID
        query = tasks_ref.where('proj_ID', '==', proj_id)
        tasks = query.stream()
        
        task_list = []
        for task in tasks:
            task_data = task.to_dict()
            task_data['id'] = task.id
            
            # Convert timestamps to ISO format
            if 'start_date' in task_data and task_data['start_date']:
                task_data['start_date'] = task_data['start_date'].isoformat()
            if 'end_date' in task_data and task_data['end_date']:
                task_data['end_date'] = task_data['end_date'].isoformat()
            if 'createdAt' in task_data and task_data['createdAt']:
                task_data['createdAt'] = task_data['createdAt'].isoformat()
            if 'updatedAt' in task_data and task_data['updatedAt']:
                task_data['updatedAt'] = task_data['updatedAt'].isoformat()
            
            task_list.append(task_data)
            
        return jsonify(task_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============== GET ALL USERS FOR DROPDOWN ===============
@tasks_bp.route('/api/users', methods=['GET'])
def get_users():
    try:
        db = get_firestore_client()
        users_ref = db.collection('Users')  # Adjust collection name as needed
        users = users_ref.stream()
        
        user_list = []
        for user in users:
            user_data = user.to_dict()
            # Only return necessary fields for dropdown
            user_info = {
                'id': user.id,
                'name': user_data.get('name', ''),
                'email': user_data.get('email', '')  # Optional: include email for better identification
            }
            user_list.append(user_info)
        
        # Sort users by name for better UX
        user_list.sort(key=lambda x: x['name'].lower())
        
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# =============== GET ALL PROJECTS FOR DROPDOWN ===============
# @tasks_bp.route('/api/projects', methods=['GET'])
# def get_all_projects():
#     try:
#         db = get_firestore_client()
#         projects_ref = db.collection('Projects')  # Adjust collection name as needed
#         projects = projects_ref.stream()
        
#         project_list = []
#         for project in projects:
#             project_data = project.to_dict()
#             # Only return necessary fields for dropdown
#             project_info = {
#                 'id': project.id,
#                 'proj_id': project_data.get('proj_ID', project.id),  # Use proj_id field
#                 'name': project_data.get('name', '') or project_data.get('project_name', ''),  # Adjust field name
#                 'description': project_data.get('description', '')  # Optional
#             }
#             project_list.append(project_info)
        
#         # Sort projects by name for better UX
#         project_list.sort(key=lambda x: x['name'].lower() if x['name'] else '')
        
#         return jsonify(project_list), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
@tasks_bp.route('/api/projects', methods=['GET'])
def get_all_projects():
    try:
        db = get_firestore_client()
        projects_ref = db.collection('Projects')  # Make sure this collection name is correct
        projects = projects_ref.stream()
        
        project_list = []
        for project in projects:
            project_data = project.to_dict()
            print(f"Project document ID: {project.id}")
            print(f"Project data: {project_data}")
            
            # Be very defensive about field access
            project_info = {
                'id': project.id,
                'proj_ID': project_data.get('proj_ID') or project_data.get('proj_id') or project.id,
                'name': project_data.get('name') or project_data.get('project_name') or f'Project {project.id}',
                'description': project_data.get('description') or ''
            }
            
            print(f"Processed project_info: {project_info}")
            project_list.append(project_info)
        
        print(f"Final project_list: {project_list}")
        return jsonify(project_list), 200
    except Exception as e:
        print(f"Error in get_all_projects: {str(e)}")
        return jsonify({'error': str(e)}), 500
