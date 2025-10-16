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
        print("BACKEND TASK CREATION DEBUG")
        print(f"Received task data: {task_data}")
        print(f"Priority level received: {task_data.get('priority_level')}")  # Changed to priority_level

        # TITLE: CREATE TASK
        # Validate required fields
        required_fields = ['task_name', 'start_date', 'priority_level']  # Changed to priority_level
        for field in required_fields:
            if not task_data.get(field):
                return jsonify({"error": f"Required field missing: {field}"}), 400

        # TITLE: Validate required fields
        # Validate priority level range
        try:
            priority_level = int(task_data.get('priority_level'))  # Changed variable name
            if priority_level < 1 or priority_level > 10:
                return jsonify({"error": "Priority level must be between 1 and 10"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Priority level must be a valid number between 1 and 10"}), 400

        # TITLE: Validate priority level range
        # Get Firestore client
        db = get_firestore_client()

        # TITLE: Get Firestore client
        # Get creator ID early so we can use it throughout
        owner_id = task_data.get('owner', '')

        # TITLE: Get creator ID early so we can use it throughout
        # Convert date strings to datetime objects with Singapore timezone
        sg_tz = pytz.timezone('Asia/Singapore')
        start_date = datetime.strptime(task_data['start_date'], '%Y-%m-%d')
        start_date = sg_tz.localize(start_date)
        
        end_date = None
        if task_data.get('end_date'):
            end_date = datetime.strptime(task_data['end_date'], '%Y-%m-%d')
            # TITLE: Convert date strings to datetime objects with Singapore timezone
            end_date = sg_tz.localize(end_date.replace(hour=23, minute=59, second=59))

        # TITLE: Set end time to end of day in Singapore timezone
        # Get project ID from project name if provided
        proj_id = None
        if task_data.get('proj_name'):
            # TITLE: Get project ID from project name if provided
            projects_ref = db.collection('Projects')
            projects_query = projects_ref.where('proj_name', '==', task_data.get('proj_name')).limit(1)
            project_docs = list(projects_query.stream())
            
            if project_docs:
                proj_id = project_docs[0].id
                print(f"Found project ID: {proj_id} for project name: {task_data.get('proj_name')}")
            else:
                print(f"Warning: Project not found for name: {task_data.get('proj_name')}")
                # TITLE: Find the project by name to get its ID
                all_projects = projects_ref.stream()
                print("Available projects:")
                for proj in all_projects:
                    proj_data = proj.to_dict()
                    print(f" - ID: {proj.id}, Name: {proj_data.get('proj_name', 'No name')}")
        else:
            print("No project name provided in task data")
            # TITLE: List all available projects for debugging

        # TITLE: Prepare task data for Firestore
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
            'is_deleted': task_data.get('is_deleted', False),  # ADD THIS LINE
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }

        print(f"Adding task to Firestore: {firestore_task_data}")
        print(f"Creating task '{firestore_task_data['task_name']}' with assigned_to: {task_data.get('assigned_to', [])}")  # FIXED THIS LINE

        # TITLE: Add document to Firestore
        doc_ref = db.collection('Tasks').add(firestore_task_data)
        task_id = doc_ref[1].id
        print(f"Task created successfully with ID: {task_id}")

        # TITLE: Prepare response data
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
            from backend.services.email_service import email_service

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
        return jsonify({"error": f"Invalid date format. Use YYYY-MM-DD: {str(e)}"}), 400
    except Exception as e:
        print(f"Error creating task: {str(e)}")
        return jsonify({"error": str(e)}), 500

@tasks_bp.route("/api/tasks", methods=["GET"])
def get_tasks():
    try:
        db = get_firestore_client()
        print("entered app.py")
        user_id = request.args.get("userId")
        tasks_ref = db.collection("Tasks")

        tasks = []

        if user_id:
            assigned_query = tasks_ref.where("assigned_to", "array_contains", user_id)
            assigned_results = assigned_query.stream()

            owner_query = tasks_ref.where("owner", "==", user_id)
            owner_results = owner_query.stream()

            seen_ids = set()
            for doc in assigned_results:
                if doc.id not in seen_ids:
                    task = doc.to_dict()
                    task["id"] = doc.id
                    
                    # ADD THIS: Filter out deleted tasks
                    if not task.get('is_deleted', False):
                        tasks.append(task)
                        seen_ids.add(doc.id)

            for doc in owner_results:
                if doc.id not in seen_ids:
                    task = doc.to_dict()
                    task["id"] = doc.id
                    
                    # ADD THIS: Filter out deleted tasks
                    if not task.get('is_deleted', False):
                        tasks.append(task)
                        seen_ids.add(doc.id)

        else:
            # If no user_id provided, return all tasks
            results = tasks_ref.stream()
            for doc in results:
                task = doc.to_dict()
                task["id"] = doc.id
                
                # ADD THIS: Filter out deleted tasks
                if not task.get('is_deleted', False):
                    tasks.append(task)

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
      - Sends email to new owner and CC's old owner when ownership changes
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
        # Check both 'owner_id' and 'owner' fields for flexibility
        old_owner_id = old_doc.to_dict().get('owner_id') or old_doc.to_dict().get('owner') if old_doc.exists else None
        
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

            # ================== SEND EMAILS FOR OWNER CHANGE ==================
            try:
                # Check both 'owner_id' and 'owner' fields (depending on your frontend)
                new_owner_id = update_data.get('owner_id') or update_data.get('owner')
                
                print(f"🔍 EMAIL CHECK - Raw update_data: {update_data}")
                print(f"🔍 EMAIL CHECK - update_data.get('owner'): {update_data.get('owner')}")
                print(f"🔍 EMAIL CHECK - update_data.get('owner_id'): {update_data.get('owner_id')}")
                print(f"🔍 EMAIL CHECK - new_owner_id (final): {new_owner_id}")
                print(f"🔍 EMAIL CHECK - old_owner_id from old_doc: {old_owner_id}")
                print(f"🔍 EMAIL CHECK - Are they different? {old_owner_id != new_owner_id}")
                print(f"🔍 EMAIL CHECK - Is new_owner_id truthy? {bool(new_owner_id)}")
                
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
                        
                        # Prepare task details for email
                        task_name = response_data.get('task_name', 'Unknown Task')
                        task_desc = response_data.get('task_desc', '')
                        project_name = response_data.get('proj_name', '')
                        
                        # Get who made the transfer (from request context or use new owner as fallback)
                        transferred_by_name = new_owner_name  # You can enhance this with actual user context
                        
                        # Format dates safely
                        start_date_str = 'Not specified'
                        end_date_str = None
                        
                        if 'start_date' in response_data and response_data['start_date']:
                            try:
                                start_date_str = datetime.fromisoformat(response_data['start_date']).strftime('%Y-%m-%d')
                            except:
                                start_date_str = str(response_data['start_date'])[:10]
                        
                        if 'end_date' in response_data and response_data['end_date']:
                            try:
                                end_date_str = datetime.fromisoformat(response_data['end_date']).strftime('%Y-%m-%d')
                            except:
                                end_date_str = str(response_data['end_date'])[:10]
                        
                        print(f"📧 Preparing to send ownership transfer email...")
                        print(f"   To: {new_owner_email}")
                        print(f"   CC: {old_owner_email}")
                        print(f"   Task: {task_name}")
                        
                        # Send email to new owner (with old owner CC'd)
                        if new_owner_email:
                            success = email_service.send_task_transfer_ownership_email(
                                new_owner_email=new_owner_email,
                                new_owner_name=new_owner_name,
                                old_owner_email=old_owner_email if old_owner_email else '',
                                old_owner_name=old_owner_name,
                                task_name=task_name,
                                task_desc=task_desc,
                                project_name=project_name,
                                transferred_by_name=transferred_by_name,
                                start_date=start_date_str,
                                end_date=end_date_str
                            )
                            if success:
                                print(f"✅ OWNERSHIP TRANSFER EMAIL SENT to {new_owner_email} (CC: {old_owner_email})")
                            else:
                                print(f"❌ FAILED to send ownership transfer email")
                        else:
                            print(f"⚠️ No email found for new owner {new_owner_id}")
                    else:
                        print(f"⚠️ New owner document not found: {new_owner_id}")
                else:
                    print(f"⏭️  No owner change detected (both are {new_owner_id})")
                        
            except Exception as e:
                print(f"❌ Failed to send owner change email: {e}")
                import traceback
                traceback.print_exc()

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

@tasks_bp.route('/api/tasks/<task_id>/delete', methods=['PUT'])  # Note: PUT, not DELETE
def soft_delete_task(task_id):
    try:
        db = get_firestore_client()
        
        # UPDATE the document (NOT delete it)
        task_ref = db.collection('Tasks').document(task_id)
        task_ref.update({  # Using UPDATE, not DELETE
            'is_deleted': True,        # Set flag to True
            'deleted_at': firestore.SERVER_TIMESTAMP,  # Add timestamp
            'updatedAt': firestore.SERVER_TIMESTAMP
        })
        
        print(f"Task {task_id} soft deleted (is_deleted = True)")
        
        return jsonify({
            "message": "Task moved to deleted items",
            "task_id": task_id,
            "is_deleted": True
        }), 200
        
    except Exception as e:
        print(f"Error soft deleting task: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
# =============== GET DELETED TASKS ===============
@tasks_bp.route('/api/tasks/deleted', methods=['GET'])
def get_deleted_tasks():
    """Get all deleted tasks (where is_deleted = True)"""
    try:
        print("📋 === GET DELETED TASKS ===")
        
        db = get_firestore_client()
        user_id = request.args.get('userId')
        
        if not user_id:
            return jsonify({"error": "userId parameter is required"}), 400
        
        # Query for deleted tasks where user is owner or assigned
        tasks_ref = db.collection('Tasks')
        query = tasks_ref.where('is_deleted', '==', True)
        
        tasks = []
        seen_ids = set()
        
        # Get tasks where user is assigned
        try:
            assigned_query = query.where('assignedto', 'array_contains', user_id)
            for doc in assigned_query.stream():
                if doc.id not in seen_ids:
                    task_data = doc.to_dict()
                    task_data['id'] = doc.id
                    
                    # Convert timestamps to ISO format
                    if 'deleted_at' in task_data and task_data['deleted_at']:
                        task_data['deleted_at'] = task_data['deleted_at'].isoformat()
                    if 'startdate' in task_data and task_data['startdate']:
                        task_data['startdate'] = task_data['startdate'].isoformat()
                    if 'enddate' in task_data and task_data['enddate']:
                        task_data['enddate'] = task_data['enddate'].isoformat()
                    
                    tasks.append(task_data)
                    seen_ids.add(doc.id)
        except Exception as e:
            print(f"Error querying assigned tasks: {e}")
        
        # Get tasks where user is owner
        try:
            owner_query = query.where('owner', '==', user_id)
            for doc in owner_query.stream():
                if doc.id not in seen_ids:
                    task_data = doc.to_dict()
                    task_data['id'] = doc.id
                    
                    # Convert timestamps to ISO format
                    if 'deleted_at' in task_data and task_data['deleted_at']:
                        task_data['deleted_at'] = task_data['deleted_at'].isoformat()
                    if 'startdate' in task_data and task_data['startdate']:
                        task_data['startdate'] = task_data['startdate'].isoformat()
                    if 'enddate' in task_data and task_data['enddate']:
                        task_data['enddate'] = task_data['enddate'].isoformat()
                    
                    tasks.append(task_data)
                    seen_ids.add(doc.id)
        except Exception as e:
            print(f"Error querying owned tasks: {e}")
        
        print(f"📊 Found {len(tasks)} deleted tasks for user {user_id}")
        return jsonify(tasks), 200
        
    except Exception as e:
        print(f"❌ Error fetching deleted tasks: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =============== GET DELETED SUBTASKS ===============
@tasks_bp.route('/api/subtasks/deleted', methods=['GET'])
def get_deleted_subtasks():
    """Get all deleted subtasks (where is_deleted = True)"""
    try:
        print("📋 === GET DELETED SUBTASKS ===")
        
        db = get_firestore_client()
        user_id = request.args.get('userId')
        
        if not user_id:
            return jsonify({"error": "userId parameter is required"}), 400
        
        # Query for deleted subtasks where user is assigned or owns the parent task
        subtasks_ref = db.collection('Subtasks')
        query = subtasks_ref.where('is_deleted', '==', True)
        
        subtasks = []
        seen_ids = set()
        
        # Get subtasks where user is assigned
        try:
            assigned_query = query.where('assignedto', 'array_contains', user_id)
            for doc in assigned_query.stream():
                if doc.id not in seen_ids:
                    subtask_data = doc.to_dict()
                    subtask_data['id'] = doc.id
                    
                    # Convert timestamps to ISO format
                    if 'deleted_at' in subtask_data and subtask_data['deleted_at']:
                        subtask_data['deleted_at'] = subtask_data['deleted_at'].isoformat()
                    if 'startdate' in subtask_data and subtask_data['startdate']:
                        subtask_data['startdate'] = subtask_data['startdate'].isoformat()
                    if 'enddate' in subtask_data and subtask_data['enddate']:
                        subtask_data['enddate'] = subtask_data['enddate'].isoformat()
                    
                    # Get parent task name if available
                    if 'task_id' in subtask_data:
                        try:
                            parent_task = db.collection('Tasks').document(subtask_data['task_id']).get()
                            if parent_task.exists:
                                parent_data = parent_task.to_dict()
                                subtask_data['parent_task_name'] = parent_data.get('taskname', 'Unknown Task')
                        except Exception as e:
                            print(f"Error getting parent task: {e}")
                    
                    subtasks.append(subtask_data)
                    seen_ids.add(doc.id)
        except Exception as e:
            print(f"Error querying assigned subtasks: {e}")
        
        # Get subtasks where user owns the parent task
        # This is more complex as we need to join subtasks with tasks
        try:
            # Get all user's tasks first
            user_tasks = db.collection('Tasks').where('owner', '==', user_id).stream()
            user_task_ids = [task.id for task in user_tasks]
            
            # Then get deleted subtasks for those tasks
            for task_id in user_task_ids:
                subtask_query = query.where('task_id', '==', task_id)
                for doc in subtask_query.stream():
                    if doc.id not in seen_ids:
                        subtask_data = doc.to_dict()
                        subtask_data['id'] = doc.id
                        
                        # Convert timestamps to ISO format
                        if 'deleted_at' in subtask_data and subtask_data['deleted_at']:
                            subtask_data['deleted_at'] = subtask_data['deleted_at'].isoformat()
                        if 'startdate' in subtask_data and subtask_data['startdate']:
                            subtask_data['startdate'] = subtask_data['startdate'].isoformat()
                        if 'enddate' in subtask_data and subtask_data['enddate']:
                            subtask_data['enddate'] = subtask_data['enddate'].isoformat()
                        
                        # Get parent task name
                        try:
                            parent_task = db.collection('Tasks').document(task_id).get()
                            if parent_task.exists:
                                parent_data = parent_task.to_dict()
                                subtask_data['parent_task_name'] = parent_data.get('taskname', 'Unknown Task')
                        except Exception as e:
                            print(f"Error getting parent task: {e}")
                        
                        subtasks.append(subtask_data)
                        seen_ids.add(doc.id)
        except Exception as e:
            print(f"Error querying owned subtasks: {e}")
        
        print(f"📊 Found {len(subtasks)} deleted subtasks for user {user_id}")
        return jsonify(subtasks), 200
        
    except Exception as e:
        print(f"❌ Error fetching deleted subtasks: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =============== RESTORE TASK ===============
@tasks_bp.route('/api/tasks/<task_id>/restore', methods=['PUT'])
def restore_task(task_id):
    """
    Restore a soft-deleted task by setting is_deleted = False
    """
    try:
        print(f"🔄 Restoring task: {task_id}")
        
        db = get_firestore_client()
        doc_ref = db.collection('Tasks').document(task_id)
        
        # Check if document exists
        doc = doc_ref.get()
        if not doc.exists:
            print(f"❌ Task {task_id} not found")
            return jsonify({'error': 'Task not found'}), 404
        
        # Get current task data
        task_data = doc.to_dict()
        
        # Check if task is actually deleted
        if not task_data.get('is_deleted', False):
            return jsonify({'error': 'Task is not deleted'}), 400
        
        print(f"📝 Restoring task: {task_data.get('taskname', 'Unknown')}")
        
        # RESTORE: Set is_deleted back to False
        update_data = {
            'is_deleted': False,
            'deleted_at': None,  # Clear the deleted timestamp
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref.update(update_data)
        print(f"✅ Task {task_id} restored successfully")
        
        return jsonify({
            "message": "Task restored successfully",
            "task_id": task_id,
            "is_deleted": False,
            "task_name": task_data.get('taskname', 'Unknown Task')
        }), 200
        
    except Exception as e:
        print(f"❌ Error restoring task {task_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =============== RESTORE SUBTASK ===============
@tasks_bp.route('/api/subtasks/<subtask_id>/restore', methods=['PUT'])
def restore_subtask(subtask_id):
    """
    Restore a soft-deleted subtask by setting is_deleted = False
    """
    try:
        print(f"🔄 Restoring subtask: {subtask_id}")
        
        db = get_firestore_client()
        doc_ref = db.collection('Subtasks').document(subtask_id)
        
        # Check if document exists
        doc = doc_ref.get()
        if not doc.exists:
            print(f"❌ Subtask {subtask_id} not found")
            return jsonify({'error': 'Subtask not found'}), 404
        
        # Get current subtask data
        subtask_data = doc.to_dict()
        
        # Check if subtask is actually deleted
        if not subtask_data.get('is_deleted', False):
            return jsonify({'error': 'Subtask is not deleted'}), 400
        
        print(f"📝 Restoring subtask: {subtask_data.get('subtaskname', 'Unknown')}")
        
        # RESTORE: Set is_deleted back to False
        update_data = {
            'is_deleted': False,
            'deleted_at': None,  # Clear the deleted timestamp
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref.update(update_data)
        print(f"✅ Subtask {subtask_id} restored successfully")
        
        return jsonify({
            "message": "Subtask restored successfully",
            "subtask_id": subtask_id,
            "is_deleted": False,
            "subtask_name": subtask_data.get('subtaskname', 'Unknown Subtask')
        }), 200
        
    except Exception as e:
        print(f"❌ Error restoring subtask {subtask_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =============== PERMANENTLY DELETE TASK ===============
@tasks_bp.route('/api/tasks/<task_id>/permanent', methods=['DELETE'])
def permanently_delete_task(task_id):
    """
    Permanently delete a task (actually remove from database)
    """
    try:
        print(f"💥 Permanently deleting task: {task_id}")
        
        db = get_firestore_client()
        doc_ref = db.collection('Tasks').document(task_id)
        
        # Check if document exists
        doc = doc_ref.get()
        if not doc.exists:
            print(f"❌ Task {task_id} not found")
            return jsonify({'error': 'Task not found'}), 404
        
        # Get current task data for logging
        task_data = doc.to_dict()
        print(f"💥 Permanently deleting task: {task_data.get('taskname', 'Unknown')}")
        
        # HARD DELETE: Actually remove the document
        doc_ref.delete()
        print(f"✅ Task {task_id} permanently deleted")
        
        return jsonify({
            "message": "Task permanently deleted",
            "task_id": task_id
        }), 200
        
    except Exception as e:
        print(f"❌ Error permanently deleting task {task_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =============== PERMANENTLY DELETE SUBTASK ===============
@tasks_bp.route('/api/subtasks/<subtask_id>/permanent', methods=['DELETE'])
def permanently_delete_subtask(subtask_id):
    """
    Permanently delete a subtask (actually remove from database)
    """
    try:
        print(f"💥 Permanently deleting subtask: {subtask_id}")
        
        db = get_firestore_client()
        doc_ref = db.collection('Subtasks').document(subtask_id)
        
        # Check if document exists
        doc = doc_ref.get()
        if not doc.exists:
            print(f"❌ Subtask {subtask_id} not found")
            return jsonify({'error': 'Subtask not found'}), 404
        
        # Get current subtask data for logging
        subtask_data = doc.to_dict()
        print(f"💥 Permanently deleting subtask: {subtask_data.get('subtaskname', 'Unknown')}")
        
        # HARD DELETE: Actually remove the document
        doc_ref.delete()
        print(f"✅ Subtask {subtask_id} permanently deleted")
        
        return jsonify({
            "message": "Subtask permanently deleted",
            "subtask_id": subtask_id
        }), 200
        
    except Exception as e:
        print(f"❌ Error permanently deleting subtask {subtask_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500
