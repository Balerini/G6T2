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
    """Get projects filtered by division - only shows projects where collaborators are from same division"""
    try:
        db = get_firestore_client()
        
        print(f"Filtering projects for division: {division_name}")
        
        # Get all user IDs from the same division
        same_division_user_ids = get_users_from_same_division(division_name)
        
        if not same_division_user_ids:
            print(f"No users found in division {division_name}")
            return jsonify([]), 200
        
        # Get all projects
        projects_ref = db.collection('Projects')
        all_projects = projects_ref.stream()
        
        filtered_projects = []
        
        for project in all_projects:
            project_data = project.to_dict()
            project_data['id'] = project.id
            
            # Check if any collaborator is from the same division
            collaborators = project_data.get('collaborators', [])
            has_same_division_collaborator = any(
                collab_id in same_division_user_ids for collab_id in collaborators
            )
            
            if has_same_division_collaborator:
                print(f"Project {project_data.get('proj_name', 'Unknown')} included for {division_name}")
                
                # Convert timestamps to ISO format
                if 'start_date' in project_data and project_data['start_date']:
                    project_data['start_date'] = project_data['start_date'].isoformat()
                if 'end_date' in project_data and project_data['end_date']:
                    project_data['end_date'] = project_data['end_date'].isoformat()
                if 'createdAt' in project_data and project_data['createdAt']:
                    project_data['createdAt'] = project_data['createdAt'].isoformat()
                if 'updatedAt' in project_data and project_data['updatedAt']:
                    project_data['updatedAt'] = project_data['updatedAt'].isoformat()
                
                # Get filtered tasks for this project
                project_doc_id = project.id
                tasks_ref = db.collection('Tasks')
                tasks_query = tasks_ref.where('proj_ID', '==', project_doc_id)
                tasks = tasks_query.stream()
                
                task_list = []
                for task in tasks:
                    task_data = task.to_dict()
                    task_data['id'] = task.id
                    
                    # Include all tasks for projects that have collaborators from the same division
                    # (removed the restrictive task-level filtering)
                    
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
        
        print(f"Returning {len(filtered_projects)} filtered projects for {division_name}")
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