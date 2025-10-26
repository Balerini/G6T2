"""
Project utility functions for unit testing.
Contains pure functions extracted from routes/project.py for C1 unit testing.
"""

def is_project_completed_pure(tasks_data):
    """
    Pure function to check if all tasks and subtasks in a project are completed.
    Takes tasks data directly instead of database queries.
    Returns True if project should be hidden, False otherwise.
    """
    # If no tasks exist, project is not complete
    if not tasks_data:
        return False
    
    # Check if all tasks are completed
    for task_data in tasks_data:
        # Skip deleted tasks
        if task_data.get('is_deleted', False):
            continue
        
        # If any task is not completed, project is not complete
        if task_data.get('task_status') != 'Completed':
            return False
        
        # Check subtasks if they exist
        subtasks = task_data.get('subtasks', [])
        if subtasks is not None:
            for subtask in subtasks:
                # Skip deleted subtasks
                if subtask.get('is_deleted', False):
                    continue
                    
                # If any subtask is not completed, project is not complete
                if subtask.get('status') != 'Completed':
                    return False
    
    return True


def is_project_completed(project_id, db):
    """
    Check if all tasks and subtasks in a project are completed.
    Returns True if project should be hidden, False otherwise.
    """
    try:
        # Get all tasks for this project
        tasks_ref = db.collection('Tasks')
        tasks_query = tasks_ref.where('proj_ID', '==', project_id)
        tasks = list(tasks_query.stream())
        
        # If no tasks exist, project is not complete
        if not tasks:
            return False
        
        # Check if all tasks are completed
        for task_doc in tasks:
            task_data = task_doc.to_dict()
            
            # Skip deleted tasks
            if task_data.get('is_deleted', False):
                continue
            
            # If any task is not completed, project is not complete
            if task_data.get('task_status') != 'Completed':
                return False
            
            # Check subtasks if they exist
            subtasks = task_data.get('subtasks', [])
            for subtask in subtasks:
                # Skip deleted subtasks
                if subtask.get('is_deleted', False):
                    continue
                    
                # If any subtask is not completed, project is not complete
                if subtask.get('status') != 'Completed':
                    return False
        
        return True
    except Exception as e:
        print(f"Error checking project completion: {str(e)}")
        return False
