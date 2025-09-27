from flask import Blueprint, jsonify, request
from firebase_utils import get_firestore_client
from firebase_admin import firestore
from datetime import datetime
import traceback

projects_bp = Blueprint('projects', __name__)

# =============== HELPER FUNCTION FOR DEPARTMENT FILTERING ===============
def get_users_from_same_division(division_name):
    """Get all user IDs from the same division"""
    try:
        db = get_firestore_client()
        users_ref = db.collection('Users')
        users_query = users_ref.where('division_name', '==', division_name)
        users = users_query.stream()
        
        user_ids = []
        for user in users:
            user_ids.append(user.id)
        
        print(f"Found {len(user_ids)} users in {division_name} division")
        return user_ids
    except Exception as e:
        print(f"Error getting users from division {division_name}: {str(e)}")
        return []

# =============== GET FILTERED PROJECTS BY DIVISION ===============
@projects_bp.route('/api/projects/filtered/<division_name>', methods=['GET'])
def get_filtered_projects_by_division(division_name):
    """Get projects filtered by division - only shows projects where current user is a collaborator"""
    try:
        db = get_firestore_client()
        
        # Get current user ID from query parameters
        current_user_id = request.args.get('user_id')
        if not current_user_id:
            print("No user ID provided in query parameters")
            return jsonify({'error': 'User ID required'}), 400
        
        print(f"Filtering projects for division: {division_name}, user: {current_user_id}")
        
        # Get all projects
        projects_ref = db.collection('Projects')
        all_projects = projects_ref.stream()
        
        filtered_projects = []
        
        for project in all_projects:
            project_data = project.to_dict()
            project_data['id'] = project.id
            
            # Check if current user is a collaborator of this project
            collaborators = project_data.get('collaborators', [])
            is_user_collaborator = current_user_id in collaborators
            
            if is_user_collaborator:
                print(f"Project {project_data.get('proj_name', 'Unknown')} included - user is collaborator")
                
                # Convert timestamps to ISO format
                if 'start_date' in project_data and project_data['start_date']:
                    project_data['start_date'] = project_data['start_date'].isoformat()
                if 'end_date' in project_data and project_data['end_date']:
                    project_data['end_date'] = project_data['end_date'].isoformat()
                if 'createdAt' in project_data and project_data['createdAt']:
                    project_data['createdAt'] = project_data['createdAt'].isoformat()
                if 'updatedAt' in project_data and project_data['updatedAt']:
                    project_data['updatedAt'] = project_data['updatedAt'].isoformat()
                
                # Get all tasks for this project (since user is a collaborator)
                project_doc_id = project.id
                tasks_ref = db.collection('Tasks')
                tasks_query = tasks_ref.where('proj_ID', '==', project_doc_id)
                tasks = tasks_query.stream()
                
                task_list = []
                for task in tasks:
                    task_data = task.to_dict()
                    task_data['id'] = task.id
                    
                    # Convert task timestamps
                    if 'start_date' in task_data and task_data['start_date']:
                        task_data['start_date'] = task_data['start_date'].isoformat()
                    if 'end_date' in task_data and task_data['end_date']:
                        task_data['end_date'] = task_data['end_date'].isoformat()
                    if 'createdAt' in task_data and task_data['createdAt']:
                        task_data['createdAt'] = task_data['createdAt'].isoformat()
                    if 'updatedAt' in task_data and task_data['updatedAt']:
                        task_data['updatedAt'] = task_data['updatedAt'].isoformat()
                    
                    task_list.append(task_data)
                
                project_data['tasks'] = task_list
                filtered_projects.append(project_data)
            else:
                print(f"Project {project_data.get('proj_name', 'Unknown')} excluded - user is not collaborator")
        
        print(f"Returning {len(filtered_projects)} filtered projects for user {current_user_id}")
        return jsonify(filtered_projects), 200
        
    except Exception as e:
        print(f"Error fetching filtered projects: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============== GET FILTERED USERS BY DIVISION ===============
@projects_bp.route('/api/users/filtered/<division_name>', methods=['GET'])
def get_filtered_users_by_division(division_name):
    """Get users filtered by division"""
    try:
        db = get_firestore_client()
        
        print(f"Filtering users for division: {division_name}")
        
        users_ref = db.collection('Users')
        users_query = users_ref.where('division_name', '==', division_name)
        users = users_query.stream()
        
        user_list = []
        for user in users:
            user_data = user.to_dict()
            user_data['id'] = user.id
            
            # Convert timestamps to ISO format for JSON serialization
            if 'createdAt' in user_data and user_data['createdAt']:
                user_data['createdAt'] = user_data['createdAt'].isoformat()
            if 'updatedAt' in user_data and user_data['updatedAt']:
                user_data['updatedAt'] = user_data['updatedAt'].isoformat()
            
            user_list.append(user_data)
        
        print(f"Returning {len(user_list)} filtered users for {division_name}")
        return jsonify(user_list), 200
        
    except Exception as e:
        print(f"Error fetching filtered users: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============== GET ALL PROJECTS (EXISTING) ===============
@projects_bp.route('/api/projects', methods=['GET'])
def get_all_projects_with_tasks():
    try:
        db = get_firestore_client()
        
        # Get all projects
        projects_ref = db.collection('Projects')
        projects = projects_ref.stream()
        
        project_list = []
        for project in projects:
            project_data = project.to_dict()
            project_data['id'] = project.id
            
            # Convert timestamps to ISO format for JSON serialization
            if 'start_date' in project_data and project_data['start_date']:
                project_data['start_date'] = project_data['start_date'].isoformat()
            if 'end_date' in project_data and project_data['end_date']:
                project_data['end_date'] = project_data['end_date'].isoformat()
            if 'createdAt' in project_data and project_data['createdAt']:
                project_data['createdAt'] = project_data['createdAt'].isoformat()
            if 'updatedAt' in project_data and project_data['updatedAt']:
                project_data['updatedAt'] = project_data['updatedAt'].isoformat()
            
            # Get tasks for this project using document ID
            project_doc_id = project.id
            tasks_ref = db.collection('Tasks')
            tasks_query = tasks_ref.where('proj_ID', '==', project_doc_id)
            tasks = tasks_query.stream()
            
            task_list = []
            for task in tasks:
                task_data = task.to_dict()
                task_data['id'] = task.id
                
                # Convert task timestamps
                if 'start_date' in task_data and task_data['start_date']:
                    task_data['start_date'] = task_data['start_date'].isoformat()
                if 'end_date' in task_data and task_data['end_date']:
                    task_data['end_date'] = task_data['end_date'].isoformat()
                if 'createdAt' in task_data and task_data['createdAt']:
                    task_data['createdAt'] = task_data['createdAt'].isoformat()
                if 'updatedAt' in task_data and task_data['updatedAt']:
                    task_data['updatedAt'] = task_data['updatedAt'].isoformat()
                
                task_list.append(task_data)
            
            project_data['tasks'] = task_list
            project_list.append(project_data)
            
        return jsonify(project_list), 200
    except Exception as e:
        print(f"Error fetching projects: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============== GET SINGLE PROJECT WITH TASKS (EXISTING) ===============
@projects_bp.route('/api/projects/<project_id>', methods=['GET'])
def get_project_with_tasks(project_id):
    try:
        db = get_firestore_client()
        
        # Get project by document ID
        doc_ref = db.collection('Projects').document(project_id)
        doc = doc_ref.get()

        if not doc.exists:
            return jsonify({'error': 'Project not found'}), 404
            
        project_data = doc.to_dict()
        project_data['id'] = doc.id
        
        # Convert timestamps to ISO format
        if 'start_date' in project_data and project_data['start_date']:
            project_data['start_date'] = project_data['start_date'].isoformat()
        if 'end_date' in project_data and project_data['end_date']:
            project_data['end_date'] = project_data['end_date'].isoformat()
        if 'createdAt' in project_data and project_data['createdAt']:
            project_data['createdAt'] = project_data['createdAt'].isoformat()
        if 'updatedAt' in project_data and project_data['updatedAt']:
            project_data['updatedAt'] = project_data['updatedAt'].isoformat()

        # Get tasks for this project using the document ID
        tasks_ref = db.collection('Tasks')
        tasks_query = tasks_ref.where('proj_ID', '==', project_id)
        tasks = tasks_query.stream()
        
        task_list = []
        for task in tasks:
            task_data = task.to_dict()
            task_data['id'] = task.id
            
            # Convert task timestamps
            if 'start_date' in task_data and task_data['start_date']:
                task_data['start_date'] = task_data['start_date'].isoformat()
            if 'end_date' in task_data and task_data['end_date']:
                task_data['end_date'] = task_data['end_date'].isoformat()
            if 'createdAt' in task_data and task_data['createdAt']:
                task_data['createdAt'] = task_data['createdAt'].isoformat()
            if 'updatedAt' in task_data and task_data['updatedAt']:
                task_data['updatedAt'] = task_data['updatedAt'].isoformat()
            
            task_list.append(task_data)
        
        project_data['tasks'] = task_list
        return jsonify(project_data), 200

    except Exception as e:
        print(f"Error fetching project: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
# =============== GET PROJECT WITH TASKS (EXISTING) ===============
@projects_bp.route('/api/projects/<project_id>/tasks', methods=['GET'])
def get_project_tasks(project_id):
    try:
        db = get_firestore_client()
                
        # Verify the project exists
        project_ref = db.collection('Projects').document(project_id)
        project_doc = project_ref.get()
        
        if not project_doc.exists:
            return jsonify({'error': 'Project not found'}), 404

        project_data = project_doc.to_dict()
        project_data['id'] = project_doc.id

        # Convert timestamps in project
        if 'start_date' in project_data and project_data['start_date']:
            project_data['start_date'] = project_data['start_date'].isoformat()
        if 'end_date' in project_data and project_data['end_date']:
            project_data['end_date'] = project_data['end_date'].isoformat()
        if 'createdAt' in project_data and project_data['createdAt']:
            project_data['createdAt'] = project_data['createdAt'].isoformat()
        if 'updatedAt' in project_data and project_data['updatedAt']:
            project_data['updatedAt'] = project_data['updatedAt'].isoformat()

        # Query tasks for this project using document ID
        tasks_ref = db.collection('Tasks')
        tasks_query = tasks_ref.where('proj_ID', '==', project_id).stream()
        
        task_list = []
        task_count = 0
        
        for task in tasks_query:
            task_count += 1
            task_data = task.to_dict()
            task_data['id'] = task.id
            
            # Convert timestamps in tasks
            if 'start_date' in task_data and task_data['start_date']:
                task_data['start_date'] = task_data['start_date'].isoformat()
            if 'end_date' in task_data and task_data['end_date']:
                task_data['end_date'] = task_data['end_date'].isoformat()
            if 'createdAt' in task_data and task_data['createdAt']:
                task_data['createdAt'] = task_data['createdAt'].isoformat()
            if 'updatedAt' in task_data and task_data['updatedAt']:
                task_data['updatedAt'] = task_data['updatedAt'].isoformat()

            task_list.append(task_data)
        
        # If no tasks found, let's check if there are ANY tasks in the Tasks collection
        if len(task_list) == 0:
            all_tasks_query = tasks_ref.limit(5).stream()  # Just get first 5 for debugging
            for task in all_tasks_query:
                task_data = task.to_dict()

        # Return project with tasks
        response = {
            **project_data,
            "tasks": task_list
        }

        return jsonify(response), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============== GET SPECIFIC TASK IN PROJECT (EXISTING) ===============
@projects_bp.route('/api/projects/<project_id>/tasks/<task_id>', methods=['GET'])
def get_specific_project_task(project_id, task_id):
    try:
        db = get_firestore_client()
        
        # Get the project first
        project_ref = db.collection('Projects').document(project_id)
        project_doc = project_ref.get()
        
        if not project_doc.exists:
            return jsonify({'error': 'Project not found'}), 404
            
        project_data = project_doc.to_dict()
        project_data['id'] = project_doc.id
        
        # Convert project timestamps
        if 'start_date' in project_data and project_data['start_date']:
            project_data['start_date'] = project_data['start_date'].isoformat()
        if 'end_date' in project_data and project_data['end_date']:
            project_data['end_date'] = project_data['end_date'].isoformat()
        if 'createdAt' in project_data and project_data['createdAt']:
            project_data['createdAt'] = project_data['createdAt'].isoformat()
        if 'updatedAt' in project_data and project_data['updatedAt']:
            project_data['updatedAt'] = project_data['updatedAt'].isoformat()

        # Get the specific task by document ID
        task_doc_ref = db.collection('Tasks').document(task_id)
        task_doc = task_doc_ref.get()
        
        if not task_doc.exists:
            return jsonify({'error': 'Task not found'}), 404
            
        task_data = task_doc.to_dict()
        task_data['id'] = task_doc.id
        
        # Verify the task belongs to this project
        if task_data.get('proj_ID') != project_id:
            return jsonify({'error': 'Task does not belong to this project'}), 404
        
        # Convert task timestamps
        if 'start_date' in task_data and task_data['start_date']:
            task_data['start_date'] = task_data['start_date'].isoformat()
        if 'end_date' in task_data and task_data['end_date']:
            task_data['end_date'] = task_data['end_date'].isoformat()
        if 'createdAt' in task_data and task_data['createdAt']:
            task_data['createdAt'] = task_data['createdAt'].isoformat()
        if 'updatedAt' in task_data and task_data['updatedAt']:
            task_data['updatedAt'] = task_data['updatedAt'].isoformat()
        
        # Return both project and task data
        return jsonify({
            'project': project_data,
            'task': task_data
        }), 200

    except Exception as e:
        print(f"Error fetching project task: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============== GET USERS (EXISTING) ===============
@projects_bp.route('/api/users', methods=['GET'])
def get_all_users():
    try:
        db = get_firestore_client()
        users_ref = db.collection('Users')
        users = users_ref.stream()
        
        user_list = []
        for user in users:
            user_data = user.to_dict()
            user_data['id'] = user.id
            
            # Convert timestamps to ISO format for JSON serialization
            if 'createdAt' in user_data and user_data['createdAt']:
                user_data['createdAt'] = user_data['createdAt'].isoformat()
            if 'updatedAt' in user_data and user_data['updatedAt']:
                user_data['updatedAt'] = user_data['updatedAt'].isoformat()
            
            user_list.append(user_data)
            
        return jsonify(user_list), 200
    except Exception as e:
        print(f"Error fetching users: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============== CREATE PROJECT ===============
@projects_bp.route('/api/projects', methods=['POST'])
def create_project():
    """Create a new project"""
    try:
        db = get_firestore_client()
        
        # Get request data
        project_data = request.get_json()
        
        if not project_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['proj_name', 'start_date', 'end_date', 'created_by', 'division_name']
        for field in required_fields:
            if field not in project_data or not project_data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate project name
        if len(project_data['proj_name'].strip()) < 3:
            return jsonify({'error': 'Project name must be at least 3 characters'}), 400
        
        # Validate dates
        try:
            start_date = datetime.fromisoformat(project_data['start_date'].replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(project_data['end_date'].replace('Z', '+00:00'))
            
            # Check if start date is not in the past (allow today)
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if start_date.replace(tzinfo=None) < today:
                return jsonify({'error': 'Start date cannot be in the past'}), 400
            
            # Check if end date is after start date
            if end_date <= start_date:
                return jsonify({'error': 'End date must be after start date'}), 400
                
        except ValueError as e:
            return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
        
        # Get creator ID
        creator_id = project_data['created_by']
        
        # Ensure collaborators includes the creator
        collaborators = project_data.get('collaborators', [])
        if creator_id not in collaborators:
            collaborators.append(creator_id)
        
        # Prepare project data for Firestore
        firestore_data = {
            'proj_name': project_data['proj_name'].strip(),
            'proj_desc': project_data.get('proj_desc', '').strip(),
            'start_date': start_date,
            'end_date': end_date,
            'proj_status': 'Not Started',  # Default status for new projects
            'created_by': creator_id,
            'division_name': project_data['division_name'],
            'collaborators': collaborators,  # 👈 INCLUDES CREATOR
            'createdAt': firestore.SERVER_TIMESTAMP,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        print(f"Creating project: {firestore_data['proj_name']} with collaborators: {collaborators}")
        
        # Add project to Firestore
        doc_ref = db.collection('Projects').add(firestore_data)
        project_id = doc_ref[1].id
        
        # Get the created project back with the ID
        created_project = doc_ref[1].get().to_dict()
        created_project['id'] = project_id
        
        # Convert timestamps back to ISO format for response
        if 'start_date' in created_project and created_project['start_date']:
            created_project['start_date'] = created_project['start_date'].isoformat()
        if 'end_date' in created_project and created_project['end_date']:
            created_project['end_date'] = created_project['end_date'].isoformat()
        if 'createdAt' in created_project and created_project['createdAt']:
            created_project['createdAt'] = created_project['createdAt'].isoformat()
        if 'updatedAt' in created_project and created_project['updatedAt']:
            created_project['updatedAt'] = created_project['updatedAt'].isoformat()
        
        print(f"Project created successfully with ID: {project_id}")
        
        return jsonify({
            'message': 'Project created successfully',
            'project': created_project
        }), 201
        
    except Exception as e:
        print(f"Error creating project: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============== UPDATE PROJECT ===============
@projects_bp.route('/api/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    """Update an existing project"""
    try:
        db = get_firestore_client()
        
        # Check if project exists
        doc_ref = db.collection('Projects').document(project_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get request data
        update_data = request.get_json()
        
        if not update_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Prepare update data
        firestore_update = {
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        # Update project name if provided
        if 'proj_name' in update_data:
            if len(update_data['proj_name'].strip()) < 3:
                return jsonify({'error': 'Project name must be at least 3 characters'}), 400
            firestore_update['proj_name'] = update_data['proj_name'].strip()
        
        # Update description if provided
        if 'proj_desc' in update_data:
            firestore_update['proj_desc'] = update_data['proj_desc'].strip()
        
        # Update dates if provided
        if 'start_date' in update_data or 'end_date' in update_data:
            existing_data = doc.to_dict()
            
            try:
                start_date = None
                end_date = None
                
                if 'start_date' in update_data:
                    start_date = datetime.fromisoformat(update_data['start_date'].replace('Z', '+00:00'))
                    firestore_update['start_date'] = start_date
                else:
                    start_date = existing_data.get('start_date')
                
                if 'end_date' in update_data:
                    end_date = datetime.fromisoformat(update_data['end_date'].replace('Z', '+00:00'))
                    firestore_update['end_date'] = end_date
                else:
                    end_date = existing_data.get('end_date')
                
                # Validate dates
                if start_date and end_date and end_date <= start_date:
                    return jsonify({'error': 'End date must be after start date'}), 400
                    
            except ValueError as e:
                return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
        
        # Update status if provided
        if 'proj_status' in update_data:
            valid_statuses = ['Not Started', 'In Progress', 'Completed', 'On Hold']
            if update_data['proj_status'] in valid_statuses:
                firestore_update['proj_status'] = update_data['proj_status']
        
        # Update the document
        doc_ref.update(firestore_update)
        
        # Get updated project
        updated_doc = doc_ref.get()
        updated_project = updated_doc.to_dict()
        updated_project['id'] = project_id
        
        # Convert timestamps for response
        if 'start_date' in updated_project and updated_project['start_date']:
            updated_project['start_date'] = updated_project['start_date'].isoformat()
        if 'end_date' in updated_project and updated_project['end_date']:
            updated_project['end_date'] = updated_project['end_date'].isoformat()
        if 'createdAt' in updated_project and updated_project['createdAt']:
            updated_project['createdAt'] = updated_project['createdAt'].isoformat()
        if 'updatedAt' in updated_project and updated_project['updatedAt']:
            updated_project['updatedAt'] = updated_project['updatedAt'].isoformat()
        
        print(f"Project {project_id} updated successfully")
        
        return jsonify({
            'message': 'Project updated successfully',
            'project': updated_project
        }), 200
        
    except Exception as e:
        print(f"Error updating project: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# =============== DELETE PROJECT ===============
@projects_bp.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project and all its associated tasks"""
    try:
        db = get_firestore_client()
        
        # Check if project exists
        project_ref = db.collection('Projects').document(project_id)
        project_doc = project_ref.get()
        
        if not project_doc.exists:
            return jsonify({'error': 'Project not found'}), 404
        
        project_data = project_doc.to_dict()
        project_name = project_data.get('proj_name', 'Unknown')
        
        # Get all tasks associated with this project
        tasks_ref = db.collection('Tasks')
        tasks_query = tasks_ref.where('proj_ID', '==', project_id)
        tasks = tasks_query.stream()
        
        # Delete all associated tasks
        deleted_task_count = 0
        for task in tasks:
            task.reference.delete()
            deleted_task_count += 1
        
        # Delete the project
        project_ref.delete()
        
        print(f"Project '{project_name}' and {deleted_task_count} associated tasks deleted successfully")
        
        return jsonify({
            'message': f'Project "{project_name}" and {deleted_task_count} associated tasks deleted successfully'
        }), 200
        
    except Exception as e:
        print(f"Error deleting project: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500