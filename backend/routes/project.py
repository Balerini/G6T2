from flask import Blueprint, jsonify, request
from firebase_utils import get_firestore_client
from firebase_admin import firestore
from datetime import datetime
import traceback

projects_bp = Blueprint('projects', __name__)

# =============== GET ALL PROJECTS WITH TASKS ===============
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
            
            # Get tasks for this project
            proj_id = project_data.get('proj_ID') or project_data.get('proj_id')
            if proj_id:  # Only query tasks if proj_id exists
                tasks_ref = db.collection('Tasks')
                tasks_query = tasks_ref.where('proj_ID', '==', proj_id)
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
            else:
                project_data['tasks'] = []
            
            project_list.append(project_data)
            
        return jsonify(project_list), 200
    except Exception as e:
        print(f"Error fetching projects: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============== GET SINGLE PROJECT WITH TASKS ===============
@projects_bp.route('/api/projects/<project_id>', methods=['GET'])
def get_project_with_tasks(project_id):
    try:
        db = get_firestore_client()
        
        # Try to get project by document ID first
        doc_ref = db.collection('Projects').document(project_id)
        doc = doc_ref.get()

        if not doc.exists:
            # If not found by document ID, try to find by proj_ID field
            projects_ref = db.collection('Projects')
            projects_query = projects_ref.where('proj_ID', '==', project_id).limit(1)
            projects = list(projects_query.stream())
            
            if not projects:
                return jsonify({'error': 'Project not found'}), 404
            
            doc = projects[0]
            
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

        # Get tasks for this project
        proj_id = project_data.get('proj_ID') or project_data.get('proj_id') or project_id
        tasks_ref = db.collection('Tasks')
        tasks_query = tasks_ref.where('proj_ID', '==', proj_id)
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
        return jsonify({'error': str(e)}), 500

# =============== GET SPECIFIC TASK IN PROJECT ===============
@projects_bp.route('/api/projects/<project_id>/tasks/<task_id>', methods=['GET'])
def get_project_task(project_id, task_id):
    try:
        db = get_firestore_client()
        
        # Get the project first
        project_ref = db.collection('Projects').document(project_id)
        project_doc = project_ref.get()
        
        if not project_doc.exists:
            # Try finding by proj_ID
            projects_ref = db.collection('Projects')
            projects_query = projects_ref.where('proj_ID', '==', project_id).limit(1)
            projects = list(projects_query.stream())
            
            if not projects:
                return jsonify({'error': 'Project not found'}), 404
            
            project_doc = projects[0]
            
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

        # Get the specific task
        tasks_ref = db.collection('Tasks')
        
        # Try to find task by task_ID first
        tasks_query = tasks_ref.where('task_ID', '==', task_id).limit(1)
        tasks = list(tasks_query.stream())
        
        if not tasks:
            # If not found by task_ID, try by document ID
            task_doc_ref = db.collection('Tasks').document(task_id)
            task_doc = task_doc_ref.get()
            
            if not task_doc.exists:
                return jsonify({'error': 'Task not found'}), 404
                
            task_data = task_doc.to_dict()
            task_data['id'] = task_doc.id
        else:
            task = tasks[0]
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
        
        # Return both project and task data
        return jsonify({
            'project': project_data,
            'task': task_data
        }), 200

    except Exception as e:
        print(f"Error fetching project task: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============== GET USERS ===============
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
        return jsonify({'error': str(e)}), 500

# =============== GET PROJECT TASKS ===============
@projects_bp.route('/api/projects/<project_id>/tasks', methods=['GET'])
def get_project_tasks(project_id):
    try:
        db = get_firestore_client()
        
        # First get the project to get the proj_ID
        project_ref = db.collection('Projects').document(project_id)
        project_doc = project_ref.get()
        
        proj_id = project_id  # Default to the provided ID
        
        if project_doc.exists:
            project_data = project_doc.to_dict()
            proj_id = project_data.get('proj_ID') or project_data.get('proj_id') or project_id
        else:
            # Try to find project by proj_ID field
            projects_ref = db.collection('Projects')
            projects_query = projects_ref.where('proj_ID', '==', project_id).limit(1)
            projects = list(projects_query.stream())
            
            if projects:
                project_data = projects[0].to_dict()
                proj_id = project_data.get('proj_ID') or project_data.get('proj_id') or project_id
        
        # Get tasks for this project
        tasks_ref = db.collection('Tasks')
        tasks_query = tasks_ref.where('proj_ID', '==', proj_id)
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
            
        return jsonify(task_list), 200
        
    except Exception as e:
        print(f"Error fetching project tasks: {str(e)}")
        return jsonify({'error': str(e)}), 500