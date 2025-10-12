from flask import Blueprint, jsonify, request
from firebase_utils import get_firestore_client
from firebase_admin import firestore
from datetime import datetime, timedelta
import traceback

dashboard_bp = Blueprint('dashboard', __name__)

# =============== DEBUG ENDPOINT TO CHECK DATA ===============
@dashboard_bp.route('/api/dashboard/debug/user/<user_id>', methods=['GET'])
def debug_user_data(user_id):
    """Debug endpoint to check user and their department's tasks"""
    try:
        db = get_firestore_client()
        
        # Get user info
        user_ref = db.collection('Users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = user_doc.to_dict()
        division_name = user_data.get('division_name')
        
        # Get all users in same division as logged in user
        users_ref = db.collection('Users')
        users_query = users_ref.where('division_name', '==', division_name)
        users = users_query.stream()
        
        department_users = []
        all_tasks_sample = []
        
        for user in users:
            u_data = user.to_dict()
            
            # Count tasks for this user - check both string and array formats
            tasks_query = db.collection('Tasks').where('assigned_to', '==', user.id)
            tasks_list = list(tasks_query.stream())
            task_count_string = len(tasks_list)
            
            # Also try array_contains for array format
            tasks_query_array = db.collection('Tasks').where('assigned_to', 'array_contains', user.id)
            tasks_list_array = list(tasks_query_array.stream())
            task_count_array = len(tasks_list_array)
            
            # Get sample task data for debugging
            if tasks_list:
                sample_task = tasks_list[0].to_dict()
                all_tasks_sample.append({
                    'task_id': tasks_list[0].id,
                    'assigned_to': sample_task.get('assigned_to'),
                    'assigned_to_type': type(sample_task.get('assigned_to')).__name__
                })
            
            department_users.append({
                'id': user.id,
                'name': u_data.get('name'),
                'email': u_data.get('email'),
                'role_name': u_data.get('role_name'),
                'role_num': u_data.get('role_num'),
                'task_count_string_match': task_count_string,
                'task_count_array_match': task_count_array
            })
        
        # Also get a few sample tasks to see their structure
        sample_tasks_ref = db.collection('Tasks').limit(5).stream()
        sample_tasks = []
        for task in sample_tasks_ref:
            task_data = task.to_dict()
            sample_tasks.append({
                'id': task.id,
                'task_name': task_data.get('task_name'),
                'assigned_to': task_data.get('assigned_to'),
                'assigned_to_type': type(task_data.get('assigned_to')).__name__
            })
        
        return jsonify({
            'current_user': {
                'id': user_id,
                'name': user_data.get('name'),
                'division_name': division_name,
                'role_num': user_data.get('role_num')
            },
            'department_users': department_users,
            'sample_tasks': sample_tasks,
            'tasks_found_in_samples': all_tasks_sample
        }), 200
        
    except Exception as e:
        print(f"Debug error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============== HELPER FUNCTION TO GET USER INFO ===============
def get_user_info(user_id):
    """Get user information by user ID"""
    try:
        db = get_firestore_client()
        user_ref = db.collection('Users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return None
        
        return user_doc.to_dict()
    except Exception as e:
        print(f"Error getting user info: {str(e)}")
        return None

# =============== HELPER FUNCTION TO GET DEPARTMENT STAFF ===============
def get_department_staff(division_name, manager_role_num):
    """Get all staff in the same department with role_num >= manager's role_num (subordinates and self)"""
    try:
        db = get_firestore_client()
        users_ref = db.collection('Users')
        
        # Get ALL users in same division first
        users_query = users_ref.where('division_name', '==', division_name)
        users = users_query.stream()
        
        staff_ids = []
        staff_info = {}
        
        for user in users:
            user_data = user.to_dict()
            user_id = user.id
            user_role_num = user_data.get('role_num', 999)
            
            # Convert string role_num to int if needed
            if isinstance(user_role_num, str):
                user_role_num = int(user_role_num)
            
            # Only include users with role_num >= manager's role_num (exclude superiors)
            if user_role_num >= manager_role_num:
                staff_ids.append(user_id)
                staff_info[user_id] = {
                    'name': user_data.get('name', 'Unknown'),
                    'email': user_data.get('email', ''),
                    'role_name': user_data.get('role_name', 'Unknown'),
                    'role_num': user_role_num
                }
                print(f"  - Included: {user_data.get('name')} (ID: {user_id}, Role: {user_data.get('role_name')}, role_num: {user_role_num})")
            else:
                print(f"  - Excluded (superior): {user_data.get('name')} (ID: {user_id}, Role: {user_data.get('role_name')}, role_num: {user_role_num})")
        
        print(f"Found {len(staff_ids)} staff members (role_num >= {manager_role_num}) in '{division_name}' division")
        return staff_ids, staff_info
        
    except Exception as e:
        print(f"Error getting department staff: {str(e)}")
        traceback.print_exc()
        return [], {}

# =============== MANAGERS: COUNT TOTAL NUMBER OF TASKS OF TEAM ===============
@dashboard_bp.route('/api/dashboard/manager/total-tasks/<user_id>', methods=['GET'])
def get_team_total_count_tasks(user_id):
    """Get total number of tasks for manager's team"""
    try:
        # Get manager info
        user_info = get_user_info(user_id)
        if not user_info:
            return jsonify({'error': 'User not found'}), 404
        
        role_num = user_info.get('role_num', 4)
        # Convert to int if it's a string
        if isinstance(role_num, str):
            role_num = int(role_num)
        
        if role_num > 3:
            return jsonify({'error': 'Unauthorized - Manager access only'}), 403
        
        division_name = user_info.get('division_name')
        if not division_name:
            return jsonify({'error': 'Division not found for user'}), 400
        
        manager_role_num = user_info.get('role_num', 4)
        # Convert string to int if needed
        if isinstance(manager_role_num, str):
            manager_role_num = int(manager_role_num)
        
        # Get all staff in the department (subordinates and self only)
        staff_ids, staff_info = get_department_staff(division_name, manager_role_num)
        
        print(f"Manager {user_id} querying tasks for {len(staff_ids)} staff members: {staff_ids}")
        
        if not staff_ids:
            return jsonify({'total_tasks': 0, 'staff_count': 0}), 200
        
        # Count tasks assigned to any staff member in the department
        db = get_firestore_client()
        tasks_ref = db.collection('Tasks')
        
        total_count = 0
        for staff_id in staff_ids:
            # Use array_contains since assigned_to is an array
            tasks_query = tasks_ref.where('assigned_to', 'array_contains', staff_id)
            tasks = tasks_query.stream()
            count = sum(1 for _ in tasks)
            print(f"  Staff {staff_id} ({staff_info.get(staff_id, {}).get('name', 'Unknown')}): {count} tasks")
            total_count += count
        
        print(f"Total tasks found: {total_count}")
        
        return jsonify({
            'total_tasks': total_count,
            'staff_count': len(staff_ids),
            'division_name': division_name
        }), 200
        
    except Exception as e:
        print(f"Error getting total tasks: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============== MANAGERS: COUNT TASKS BY STATUS ===============
@dashboard_bp.route('/api/dashboard/manager/tasks-by-status/<user_id>', methods=['GET'])
def get_team_task_count_by_status(user_id):
    """Get count of tasks by status for manager's team"""
    try:
        # Get manager info
        user_info = get_user_info(user_id)
        if not user_info:
            return jsonify({'error': 'User not found'}), 404
        
        role_num = user_info.get('role_num', 4)
        # Convert to int if it's a string
        if isinstance(role_num, str):
            role_num = int(role_num)
        
        if role_num > 3:
            return jsonify({'error': 'Unauthorized - Manager access only'}), 403
        
        division_name = user_info.get('division_name')
        if not division_name:
            return jsonify({'error': 'Division not found for user'}), 400
        
        manager_role_num = user_info.get('role_num', 4)
        # Convert string to int if needed
        if isinstance(manager_role_num, str):
            manager_role_num = int(manager_role_num)
        
        # Get all staff in the department (subordinates and self only)
        staff_ids, staff_info = get_department_staff(division_name, manager_role_num)
        
        if not staff_ids:
            return jsonify({'tasks_by_status': {}}), 200
        
        # Count tasks by status
        db = get_firestore_client()
        tasks_ref = db.collection('Tasks')
        
        status_counts = {}
        
        for staff_id in staff_ids:
            # Use array_contains since assigned_to is an array
            tasks_query = tasks_ref.where('assigned_to', 'array_contains', staff_id)
            tasks = tasks_query.stream()
            
            for task in tasks:
                task_data = task.to_dict()
                status = task_data.get('task_status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
        
        return jsonify({
            'tasks_by_status': status_counts,
            'division_name': division_name
        }), 200
        
    except Exception as e:
        print(f"Error getting tasks by status: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============== MANAGERS: COUNT AND NAME OF TASKS BY STAFF MEMBER ===============
@dashboard_bp.route('/api/dashboard/manager/tasks-by-staff/<user_id>', methods=['GET'])
def get_team_task_count_by_staff(user_id):
    """Get count of tasks and task details for each staff member in manager's department"""
    try:
        # Get manager info
        user_info = get_user_info(user_id)
        if not user_info:
            return jsonify({'error': 'User not found'}), 404
        
        role_num = user_info.get('role_num', 4)
        # Convert to int if it's a string
        if isinstance(role_num, str):
            role_num = int(role_num)
        
        if role_num > 3:
            return jsonify({'error': 'Unauthorized - Manager access only'}), 403
        
        division_name = user_info.get('division_name')
        if not division_name:
            return jsonify({'error': 'Division not found for user'}), 400
        
        manager_role_num = user_info.get('role_num', 4)
        # Convert string to int if needed
        if isinstance(manager_role_num, str):
            manager_role_num = int(manager_role_num)
        
        # Get all staff in the department (subordinates and self only)
        staff_ids, staff_info = get_department_staff(division_name, manager_role_num)
        
        if not staff_ids:
            return jsonify({'tasks_by_staff': []}), 200
        
        # Get tasks for each staff member with details
        db = get_firestore_client()
        tasks_ref = db.collection('Tasks')
        
        staff_task_data = []
        
        for staff_id in staff_ids:
            # Use array-contains since assigned_to is an array
            tasks_query = tasks_ref.where('assigned_to', 'array_contains', staff_id)
            tasks = tasks_query.stream()
            
            task_list = []
            for task in tasks:
                task_data = task.to_dict()
                task_list.append({
                    'task_id': task.id,
                    'task_name': task_data.get('task_name', 'Untitled'),
                    'task_status': task_data.get('task_status', 'Unknown'),
                    'task_priority': task_data.get('task_priority', 'N/A'),
                    'proj_name': task_data.get('proj_name', ''),
                    'start_date': task_data.get('start_date').isoformat() if task_data.get('start_date') else None,
                    'end_date': task_data.get('end_date').isoformat() if task_data.get('end_date') else None
                })
            
            staff_task_data.append({
                'staff_id': staff_id,
                'staff_name': staff_info[staff_id]['name'],
                'staff_role': staff_info[staff_id]['role_name'],
                'role_num': staff_info[staff_id]['role_num'],
                'task_count': len(task_list),
                'tasks': task_list
            })
        
        # Sort by task count descending
        staff_task_data.sort(key=lambda x: x['task_count'], reverse=True)
        
        return jsonify({
            'tasks_by_staff': staff_task_data,
            'division_name': division_name
        }), 200
        
    except Exception as e:
        print(f"Error getting tasks by staff: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============== MANAGERS: COUNT TASKS BY ITS DIFF PRIORITY ===============
@dashboard_bp.route('/api/dashboard/manager/tasks-by-priority/<user_id>', methods=['GET'])
def get_manager_tasks_by_priority(user_id):
    """Get count of tasks by priority for manager's team"""
    try:
        # Get manager info
        user_info = get_user_info(user_id)
        if not user_info:
            return jsonify({'error': 'User not found'}), 404
        
        role_num = user_info.get('role_num', 4)
        # Convert to int if it's a string
        if isinstance(role_num, str):
            role_num = int(role_num)
        
        if role_num > 3:
            return jsonify({'error': 'Unauthorized - Manager access only'}), 403
        
        division_name = user_info.get('division_name')
        if not division_name:
            return jsonify({'error': 'Division not found for user'}), 400
        
        manager_role_num = user_info.get('role_num', 4)
        # Convert string to int if needed
        if isinstance(manager_role_num, str):
            manager_role_num = int(manager_role_num)
        
        # Get all staff in the department (subordinates and self only)
        staff_ids, staff_info = get_department_staff(division_name, manager_role_num)
        
        if not staff_ids:
            return jsonify({'tasks_by_priority': {'High': 0, 'Medium': 0, 'Low': 0}}), 200
        
        # Helper function to categorize priority
        def get_priority_category(priority_level):
            """Convert priority integer (1-10) to category (High/Medium/Low)"""
            if priority_level is None or priority_level == 'N/A':
                return 'Others'
            
            try:
                num = int(priority_level)
                if num >= 8:
                    return 'High'
                elif num >= 4:
                    return 'Medium'
                else:
                    return 'Low'
            except (ValueError, TypeError):
                return 'Others'
        
        # Count tasks by priority
        db = get_firestore_client()
        tasks_ref = db.collection('Tasks')
        
        # Initialize priority counts
        priority_counts = {
            'High': 0,
            'Medium': 0,
            'Low': 0,
            'Others': 0
        }
        
        for staff_id in staff_ids:
            # Use array_contains since assigned_to is an array
            tasks_query = tasks_ref.where('assigned_to', 'array_contains', staff_id)
            tasks = tasks_query.stream()
            
            for task in tasks:
                task_data = task.to_dict()
                priority_level = task_data.get('priority_level')
                
                # Get the category (High/Medium/Low)
                category = get_priority_category(priority_level)
                priority_counts[category] = priority_counts.get(category, 0) + 1
        
        # Remove 'Unknown' from response if it's 0
        if priority_counts['Others'] == 0:
            del priority_counts['Others']
        
        return jsonify({
            'tasks_by_priority': priority_counts,
            'division_name': division_name
        }), 200
        
    except Exception as e:
        print(f"Error getting tasks by priority: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============== MANAGERS: PENDING TASKS BY AGE AND TASK NAME BASED ON TASK START DATE ===============
@dashboard_bp.route('/api/dashboard/manager/pending-tasks-by-age/<user_id>', methods=['GET'])
def get_manager_pending_tasks_by_age(user_id):
    """Get pending tasks categorized by due date with task details and assignee"""
    try:
        # Get manager info
        user_info = get_user_info(user_id)
        if not user_info:
            return jsonify({'error': 'User not found'}), 404
        
        role_num = user_info.get('role_num', 4)
        # Convert to int if it's a string
        if isinstance(role_num, str):
            role_num = int(role_num)
        
        if role_num > 3:
            return jsonify({'error': 'Unauthorized - Manager access only'}), 403
        
        division_name = user_info.get('division_name')
        if not division_name:
            return jsonify({'error': 'Division not found for user'}), 400
        
        manager_role_num = user_info.get('role_num', 4)
        # Convert string to int if needed
        if isinstance(manager_role_num, str):
            manager_role_num = int(manager_role_num)
        
        # Get all staff in the department (subordinates and self only)
        staff_ids, staff_info = get_department_staff(division_name, manager_role_num)
        
        if not staff_ids:
            return jsonify({'pending_tasks_by_age': {}}), 200
        
        # Get pending tasks
        db = get_firestore_client()
        tasks_ref = db.collection('Tasks')
        
        # Categories for task age with task details
        age_categories = {
            'overdue': [],
            'due_today': [],
            'due_in_1_day': [],
            'due_in_3_days': [],
            'due_in_a_week': [],
            'due_in_2_weeks': [],
            'due_in_a_month': [],
            'due_later': [],
        }
        
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for staff_id in staff_ids:
            # Use array-contains since assigned_to is an array
            tasks_query = tasks_ref.where('assigned_to', 'array_contains', staff_id)
            tasks = tasks_query.stream()
            
            for task in tasks:
                task_data = task.to_dict()
                status = task_data.get('task_status', '')
                
                # # Only count pending tasks (Not Started or In Progress)
                # if status not in ['Not Started', 'In Progress']:
                #     continue
                
                end_date = task_data.get('end_date')
                if not end_date:
                    continue
                
                # Normalize end_date to midnight for comparison
                end_date_normalized = end_date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
                
                # Calculate days difference (positive = future, negative = past)
                days_diff = (end_date_normalized - current_date).days
                
                # Create task detail object
                task_detail = {
                    'task_id': task.id,
                    'task_name': task_data.get('task_name', 'Untitled'),
                    'task_status': status,
                    'priority_level': task_data.get('priority_level', 'N/A'),
                    'assigned_to_id': staff_id,
                    'assigned_to_name': staff_info[staff_id]['name'],
                    'assigned_to_role': staff_info[staff_id]['role_name'],
                    'proj_name': task_data.get('proj_name', ''),
                    'proj_id': task_data.get('proj_ID'),
                    'end_date': end_date.isoformat() if end_date else None,
                    'days_until_due': days_diff
                }
                
                # Categorize by days until due
                if days_diff < 0:
                    age_categories['overdue'].append(task_detail)
                elif days_diff == 0:
                    age_categories['due_today'].append(task_detail)
                elif days_diff == 1:
                    age_categories['due_in_1_day'].append(task_detail)
                elif days_diff <= 3:
                    age_categories['due_in_3_days'].append(task_detail)
                elif days_diff <= 7:
                    age_categories['due_in_a_week'].append(task_detail)
                elif days_diff <= 14:
                    age_categories['due_in_2_weeks'].append(task_detail)
                elif days_diff <= 30:
                    age_categories['due_in_a_month'].append(task_detail)
                elif days_diff > 30: 
                    age_categories['due_later'].append(task_detail)
        
        # Sort tasks within each category by due date (earliest first)
        for category in age_categories:
            age_categories[category].sort(key=lambda x: x['days_until_due'])
        
        # Create summary counts
        summary = {
            'overdue': len(age_categories['overdue']),
            'due_today': len(age_categories['due_today']),
            'due_in_1_day': len(age_categories['due_in_1_day']),
            'due_in_3_days': len(age_categories['due_in_3_days']),
            'due_in_a_week': len(age_categories['due_in_a_week']),
            'due_in_2_weeks': len(age_categories['due_in_2_weeks']),
            'due_in_a_month': len(age_categories['due_in_a_month']),
            'due_later': len(age_categories['due_later']),
        }
        
        return jsonify({
            'pending_tasks_by_age': age_categories,
            'summary': summary,
            'division_name': division_name
        }), 200
        
    except Exception as e:
        print(f"Error getting pending tasks by age: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# =============== NORMAL STAFF WHOSE ROLE_NUM IN DB = 4 ===============

# =============== STAFF: COUNT TOTAL NUMBER OF TASKS ===============
@dashboard_bp.route('/api/dashboard/staff/total-tasks/<user_id>', methods=['GET'])
def get_staff_total_tasks(user_id):
    """Get total number of tasks assigned to a staff member"""
    try:
        print(f"=== STAFF TOTAL TASKS ENDPOINT ===")
        print(f"User ID: {user_id}")
        
        # Get staff info
        user_info = get_user_info(user_id)
        print(f"User info: {user_info}")
        
        if not user_info:
            return jsonify({'error': 'User not found'}), 404
        
        # This endpoint is for staff only (role_num = 4)
        role_num = user_info.get('role_num', 999)
        if isinstance(role_num, str):
            role_num = int(role_num)
        print(f"User role_num: {role_num}")
        
        if role_num != 4:
            return jsonify({'error': f'Unauthorized - Staff access only (your role_num: {role_num})'}), 403
        
        # Count tasks assigned to this staff member
        db = get_firestore_client()
        tasks_ref = db.collection('Tasks')
        
        tasks_query = tasks_ref.where('assigned_to', 'array_contains', user_id)
        tasks = list(tasks_query.stream())
        
        total_count = len(tasks)
        print(f"Total tasks found: {total_count}")
        
        return jsonify({
            'total_tasks': total_count,
            'staff_count': 1
        }), 200
        
    except Exception as e:
        print(f"Error getting staff total tasks: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============== STAFF: COUNT TASKS BY STATUS ===============
@dashboard_bp.route('/api/dashboard/staff/tasks-by-status/<user_id>', methods=['GET'])
def get_staff_tasks_by_status(user_id):
    """Get count of tasks by status for a staff member"""
    try:
        user_info = get_user_info(user_id)
        if not user_info:
            return jsonify({'error': 'User not found'}), 404
        
        role_num = user_info.get('role_num', 999)
        if isinstance(role_num, str):
            role_num = int(role_num)
        
        if role_num != 4:
            return jsonify({'error': 'Unauthorized - Staff access only'}), 403
        
        db = get_firestore_client()
        tasks_ref = db.collection('Tasks')
        
        tasks_query = tasks_ref.where('assigned_to', 'array_contains', user_id)
        tasks = tasks_query.stream()
        
        status_counts = {}
        for task in tasks:
            task_data = task.to_dict()
            status = task_data.get('task_status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return jsonify({'tasks_by_status': status_counts}), 200
        
    except Exception as e:
        print(f"Error getting staff tasks by status: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============== STAFF: COUNT TASKS BY PRIORITY ===============
@dashboard_bp.route('/api/dashboard/staff/tasks-by-priority/<user_id>', methods=['GET'])
def get_staff_tasks_by_priority(user_id):
    """Get count of tasks by priority for a staff member"""
    try:
        user_info = get_user_info(user_id)
        if not user_info:
            return jsonify({'error': 'User not found'}), 404
        
        role_num = user_info.get('role_num', 999)
        if isinstance(role_num, str):
            role_num = int(role_num)
        
        if role_num != 4:
            return jsonify({'error': 'Unauthorized - Staff access only'}), 403
        
        def get_priority_category(priority_level):
            if priority_level is None or priority_level == 'N/A':
                return 'Others'
            try:
                num = int(priority_level)
                if num >= 8:
                    return 'High'
                elif num >= 4:
                    return 'Medium'
                else:
                    return 'Low'
            except (ValueError, TypeError):
                return 'Others'
        
        db = get_firestore_client()
        tasks_ref = db.collection('Tasks')
        
        tasks_query = tasks_ref.where('assigned_to', 'array_contains', user_id)
        tasks = tasks_query.stream()
        
        priority_counts = {'High': 0, 'Medium': 0, 'Low': 0, 'Others': 0}
        
        for task in tasks:
            task_data = task.to_dict()
            priority_level = task_data.get('priority_level')
            category = get_priority_category(priority_level)
            priority_counts[category] = priority_counts.get(category, 0) + 1
        
        if priority_counts['Others'] == 0:
            del priority_counts['Others']
        
        return jsonify({'tasks_by_priority': priority_counts}), 200
        
    except Exception as e:
        print(f"Error getting staff tasks by priority: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# =============== STAFF: PENDING TASKS BY AGE ===============
@dashboard_bp.route('/api/dashboard/staff/pending-tasks-by-age/<user_id>', methods=['GET'])
def get_staff_pending_tasks_by_age(user_id):
    """Get pending tasks categorized by due date for a staff member"""
    try:
        user_info = get_user_info(user_id)
        if not user_info:
            return jsonify({'error': 'User not found'}), 404
        
        role_num = user_info.get('role_num', 999)
        if isinstance(role_num, str):
            role_num = int(role_num)
        
        if role_num != 4:
            return jsonify({'error': 'Unauthorized - Staff access only'}), 403
        
        db = get_firestore_client()
        tasks_ref = db.collection('Tasks')
        
        tasks_query = tasks_ref.where('assigned_to', 'array_contains', user_id)
        tasks = tasks_query.stream()
        
        age_categories = {
            'overdue': [], 'due_today': [], 'due_in_1_day': [], 'due_in_3_days': [],
            'due_in_a_week': [], 'due_in_2_weeks': [], 'due_in_a_month': [], 'due_later': []
        }
        
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for task in tasks:
            task_data = task.to_dict()
            end_date = task_data.get('end_date')
            if not end_date:
                continue
            
            end_date_normalized = end_date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
            days_diff = (end_date_normalized - current_date).days
            
            # Get assigned user names
            assigned_to_names = []
            if task_data.get('assigned_to'):
                for user_id in task_data.get('assigned_to', []):
                    user_doc = db.collection('Users').document(user_id).get()
                    if user_doc.exists:
                        assigned_to_names.append(user_doc.to_dict().get('name', 'Unknown'))
            
            task_detail = {
                'task_id': task.id,
                'task_name': task_data.get('task_name', 'Untitled'),
                'task_status': task_data.get('task_status', 'Unknown'),
                'priority_level': task_data.get('priority_level', 'N/A'),
                'proj_name': task_data.get('proj_name', ''),
                'proj_id': task_data.get('proj_ID'),  # Backend uses proj_ID
                'assigned_to_name': ', '.join(assigned_to_names) if assigned_to_names else 'Unassigned',
                'assigned_to_id': user_id,  # The user this task is assigned to (current user for staff endpoint)
                'end_date': end_date.isoformat() if end_date else None,
                'days_until_due': days_diff
            }
            
            if days_diff < 0:
                age_categories['overdue'].append(task_detail)
            elif days_diff == 0:
                age_categories['due_today'].append(task_detail)
            elif days_diff == 1:
                age_categories['due_in_1_day'].append(task_detail)
            elif days_diff <= 3:
                age_categories['due_in_3_days'].append(task_detail)
            elif days_diff <= 7:
                age_categories['due_in_a_week'].append(task_detail)
            elif days_diff <= 14:
                age_categories['due_in_2_weeks'].append(task_detail)
            elif days_diff <= 30:
                age_categories['due_in_a_month'].append(task_detail)
            else:
                age_categories['due_later'].append(task_detail)
        
        for category in age_categories:
            age_categories[category].sort(key=lambda x: x['days_until_due'])
        
        summary = {
            'overdue': len(age_categories['overdue']),
            'due_today': len(age_categories['due_today']),
            'due_in_1_day': len(age_categories['due_in_1_day']),
            'due_in_3_days': len(age_categories['due_in_3_days']),
            'due_in_a_week': len(age_categories['due_in_a_week']),
            'due_in_2_weeks': len(age_categories['due_in_2_weeks']),
            'due_in_a_month': len(age_categories['due_in_a_month']),
            'due_later': len(age_categories['due_later']),
        }
        
        return jsonify({
            'pending_tasks_by_age': age_categories,
            'summary': summary
        }), 200
        
    except Exception as e:
        print(f"Error getting staff pending tasks by age: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500