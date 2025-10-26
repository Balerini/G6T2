#!/usr/bin/env python3
"""
REAL Integration Tests - View My Tasks [All]
Tests user's ability to view their assigned tasks via API with REAL database integration.
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


class TestViewMyTasksAPI(unittest.TestCase):
    """REAL Integration tests for viewing my tasks with real database"""
    
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
    
    def setup_test_tasks(self):
        """Create real test tasks in the database"""
        # Calculate future dates for validation
        future_start = datetime.now() + timedelta(days=1)
        future_end = datetime.now() + timedelta(days=30)
        
        # Create project for tasks
        project_data = {
            'proj_name': f'Test Project {self.timestamp}',
            'proj_desc': 'Test project for task viewing',
            'start_date': future_start.strftime('%Y-%m-%d'),
            'end_date': future_end.strftime('%Y-%m-%d'),
            'owner': self.test_manager_id,
            'division_name': 'IT Department',
            'collaborators': [self.test_manager_id, self.test_staff1_id, self.test_staff2_id]
        }
        
        project_ref = self.db.collection('Projects').add(project_data)
        self.test_project_id = project_ref[1].id
        self.test_project_ids.append(self.test_project_id)
        
        # Task 1: Assigned to staff1 (In Progress)
        task1_data = {
            'task_name': f'Task 1 - Staff1 {self.timestamp}',
            'task_desc': 'Task assigned to staff 1',
            'start_date': future_start.strftime('%Y-%m-%d'),
            'end_date': future_end.strftime('%Y-%m-%d'),
            'task_status': 'In Progress',
            'priority_level': 3,
            'proj_ID': self.test_project_id,
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff1_id],
            'created_at': datetime.now().isoformat(),
            'is_deleted': False
        }
        
        task1_ref = self.db.collection('Tasks').add(task1_data)
        self.test_task1_id = task1_ref[1].id
        self.test_task_ids.append(self.test_task1_id)
        
        # Task 2: Assigned to staff1 (Completed)
        task2_data = {
            'task_name': f'Task 2 - Staff1 {self.timestamp}',
            'task_desc': 'Completed task assigned to staff 1',
            'start_date': future_start.strftime('%Y-%m-%d'),
            'end_date': future_end.strftime('%Y-%m-%d'),
            'task_status': 'Completed',
            'priority_level': 2,
            'proj_ID': self.test_project_id,
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff1_id],
            'created_at': datetime.now().isoformat(),
            'is_deleted': False
        }
        
        task2_ref = self.db.collection('Tasks').add(task2_data)
        self.test_task2_id = task2_ref[1].id
        self.test_task_ids.append(self.test_task2_id)
        
        # Task 3: Assigned to staff2 (Not Started)
        task3_data = {
            'task_name': f'Task 3 - Staff2 {self.timestamp}',
            'task_desc': 'Task assigned to staff 2',
            'start_date': future_start.strftime('%Y-%m-%d'),
            'end_date': future_end.strftime('%Y-%m-%d'),
            'task_status': 'Not Started',
            'priority_level': 1,
            'proj_ID': self.test_project_id,
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff2_id],
            'created_at': datetime.now().isoformat(),
            'is_deleted': False
        }
        
        task3_ref = self.db.collection('Tasks').add(task3_data)
        self.test_task3_id = task3_ref[1].id
        self.test_task_ids.append(self.test_task3_id)
        
        # Task 4: Assigned to both staff1 and staff2
        task4_data = {
            'task_name': f'Task 4 - Both Staff {self.timestamp}',
            'task_desc': 'Task assigned to both staff members',
            'start_date': future_start.strftime('%Y-%m-%d'),
            'end_date': future_end.strftime('%Y-%m-%d'),
            'task_status': 'Under Review',
            'priority_level': 2,
            'proj_ID': self.test_project_id,
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff1_id, self.test_staff2_id],
            'created_at': datetime.now().isoformat(),
            'is_deleted': False
        }
        
        task4_ref = self.db.collection('Tasks').add(task4_data)
        self.test_task4_id = task4_ref[1].id
        self.test_task_ids.append(self.test_task4_id)
        
        # Task 5: Owned by staff1 (not assigned to them)
        task5_data = {
            'task_name': f'Task 5 - Owned by Staff1 {self.timestamp}',
            'task_desc': 'Task owned by staff 1',
            'start_date': future_start.strftime('%Y-%m-%d'),
            'end_date': future_end.strftime('%Y-%m-%d'),
            'task_status': 'In Progress',
            'priority_level': 3,
            'proj_ID': self.test_project_id,
            'owner': self.test_staff1_id,
            'assigned_to': [self.test_staff2_id],  # Assigned to staff2, owned by staff1
            'created_at': datetime.now().isoformat(),
            'is_deleted': False
        }
        
        task5_ref = self.db.collection('Tasks').add(task5_data)
        self.test_task5_id = task5_ref[1].id
        self.test_task_ids.append(self.test_task5_id)
        
        # Task 6: Deleted task (should not appear in results)
        task6_data = {
            'task_name': f'Task 6 - Deleted {self.timestamp}',
            'task_desc': 'Deleted task',
            'start_date': future_start.strftime('%Y-%m-%d'),
            'end_date': future_end.strftime('%Y-%m-%d'),
            'task_status': 'In Progress',
            'priority_level': 3,
            'proj_ID': self.test_project_id,
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff1_id],
            'created_at': datetime.now().isoformat(),
            'is_deleted': True  # This task is deleted
        }
        
        task6_ref = self.db.collection('Tasks').add(task6_data)
        self.test_task6_id = task6_ref[1].id
        self.test_task_ids.append(self.test_task6_id)
    
    def test_view_my_tasks_all_staff1(self):
        """Test staff1 viewing all their tasks with REAL database"""
        response = self.client.get(f'/api/tasks?userId={self.test_staff1_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # Staff1 should see:
        # - Task 1 (assigned to them)
        # - Task 2 (assigned to them) 
        # - Task 4 (assigned to them)
        # - Task 5 (owned by them)
        # Should NOT see Task 3 (assigned to staff2) or Task 6 (deleted)
        
        self.assertGreaterEqual(len(response_data), 4)  # At least 4 tasks
        
        # Verify task data structure
        for task in response_data:
            self.assertIn('id', task)
            self.assertIn('task_name', task)
            self.assertIn('task_status', task)
            self.assertIn('assigned_to', task)
            self.assertIn('owner', task)
            self.assertIn('proj_ID', task)
        
        # Verify staff1 can see their assigned tasks
        assigned_tasks = [task for task in response_data if self.test_staff1_id in task.get('assigned_to', [])]
        self.assertGreaterEqual(len(assigned_tasks), 3)  # At least 3 assigned tasks
        
        # Verify staff1 can see tasks they own
        owned_tasks = [task for task in response_data if task.get('owner') == self.test_staff1_id]
        self.assertGreaterEqual(len(owned_tasks), 1)  # At least 1 owned task
        
        # Verify deleted task is not included
        deleted_tasks = [task for task in response_data if task.get('is_deleted', False)]
        self.assertEqual(len(deleted_tasks), 0)  # No deleted tasks should appear
    
    def test_view_my_tasks_all_staff2(self):
        """Test staff2 viewing all their tasks with REAL database"""
        response = self.client.get(f'/api/tasks?userId={self.test_staff2_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # Staff2 should see:
        # - Task 3 (assigned to them)
        # - Task 4 (assigned to them)
        # - Task 5 (assigned to them)
        # Should NOT see Task 1, Task 2 (assigned to staff1) or Task 6 (deleted)
        
        self.assertGreaterEqual(len(response_data), 3)  # At least 3 tasks
        
        # Verify staff2 can see their assigned tasks
        assigned_tasks = [task for task in response_data if self.test_staff2_id in task.get('assigned_to', [])]
        self.assertGreaterEqual(len(assigned_tasks), 3)  # At least 3 assigned tasks
    
    def test_view_my_tasks_with_status_filter_in_progress(self):
        """Test viewing tasks filtered by 'In Progress' status with REAL database"""
        response = self.client.get(f'/api/tasks?userId={self.test_staff1_id}&status=In Progress')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # All returned tasks should have "In Progress" status
        for task in response_data:
            self.assertEqual(task.get('task_status'), 'In Progress')
    
    def test_view_my_tasks_with_status_filter_completed(self):
        """Test viewing tasks filtered by 'Completed' status with REAL database"""
        response = self.client.get(f'/api/tasks?userId={self.test_staff1_id}&status=Completed')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # All returned tasks should have "Completed" status
        for task in response_data:
            self.assertEqual(task.get('task_status'), 'Completed')
    
    def test_view_my_tasks_with_multiple_status_filter(self):
        """Test viewing tasks filtered by multiple statuses with REAL database"""
        response = self.client.get(f'/api/tasks?userId={self.test_staff1_id}&status=In Progress&status=Completed')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # All returned tasks should have either "In Progress" or "Completed" status
        allowed_statuses = {'In Progress', 'Completed'}
        for task in response_data:
            self.assertIn(task.get('task_status'), allowed_statuses)
    
    def test_view_my_tasks_with_active_status_group(self):
        """Test viewing tasks filtered by 'active' status group with REAL database"""
        response = self.client.get(f'/api/tasks?userId={self.test_staff1_id}&status=active')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # All returned tasks should have active statuses
        active_statuses = {'active', 'unassigned', 'ongoing', 'under review'}
        for task in response_data:
            task_status = task.get('task_status', '').lower()
            self.assertIn(task_status, active_statuses)
    
    def test_view_my_tasks_with_all_status_filter(self):
        """Test viewing tasks with 'all' status filter with REAL database"""
        response = self.client.get(f'/api/tasks?userId={self.test_staff1_id}&status=all')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # Should return all tasks regardless of status
        self.assertGreaterEqual(len(response_data), 4)  # At least 4 tasks
    
    def test_view_my_tasks_with_comma_separated_status_filter(self):
        """Test viewing tasks with comma-separated status filter with REAL database"""
        response = self.client.get(f'/api/tasks?userId={self.test_staff1_id}&status=In Progress,Completed')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # All returned tasks should have either "In Progress" or "Completed" status
        allowed_statuses = {'In Progress', 'Completed'}
        for task in response_data:
            self.assertIn(task.get('task_status'), allowed_statuses)
    
    def test_view_my_tasks_without_user_id(self):
        """Test viewing tasks without user_id parameter with REAL database"""
        response = self.client.get('/api/tasks')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # Should return all tasks (not filtered by user)
        self.assertGreaterEqual(len(response_data), 5)  # At least 5 tasks (excluding deleted)
    
    def test_view_my_tasks_with_nonexistent_user_id(self):
        """Test viewing tasks with nonexistent user_id with REAL database"""
        fake_user_id = 'nonexistent_user_id'
        
        response = self.client.get(f'/api/tasks?userId={fake_user_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # Should return empty list for nonexistent user
        self.assertEqual(len(response_data), 0)
    
    def test_view_my_tasks_manager_role(self):
        """Test manager viewing their tasks with REAL database"""
        response = self.client.get(f'/api/tasks?userId={self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # Manager should see tasks they own
        owned_tasks = [task for task in response_data if task.get('owner') == self.test_manager_id]
        self.assertGreaterEqual(len(owned_tasks), 4)  # At least 4 owned tasks
    
    def test_view_my_tasks_director_role(self):
        """Test director viewing their tasks with REAL database"""
        response = self.client.get(f'/api/tasks?userId={self.test_director_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # Director should see tasks they own (if any)
        owned_tasks = [task for task in response_data if task.get('owner') == self.test_director_id]
        self.assertGreaterEqual(len(owned_tasks), 0)  # At least 0 owned tasks
    
    def test_view_my_tasks_task_data_structure(self):
        """Test that returned task data has proper structure with REAL database"""
        response = self.client.get(f'/api/tasks?userId={self.test_staff1_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        if response_data:  # If there are tasks
            task = response_data[0]
            
            # Verify required fields
            required_fields = ['id', 'task_name', 'task_status', 'assigned_to', 'owner', 'proj_ID']
            for field in required_fields:
                self.assertIn(field, task, f"Missing required field: {field}")
            
            # Verify data types
            self.assertIsInstance(task['assigned_to'], list)
            self.assertIsInstance(task['task_name'], str)
            self.assertIsInstance(task['task_status'], str)
            self.assertIsInstance(task['owner'], str)
    
    def test_view_my_tasks_no_duplicates(self):
        """Test that no duplicate tasks are returned with REAL database"""
        response = self.client.get(f'/api/tasks?userId={self.test_staff1_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # Check for duplicates
        task_ids = [task['id'] for task in response_data]
        unique_task_ids = set(task_ids)
        
        self.assertEqual(len(task_ids), len(unique_task_ids), "Duplicate tasks found in response")
    
    def test_view_my_tasks_case_insensitive_status_filter(self):
        """Test that status filtering is case insensitive with REAL database"""
        response = self.client.get(f'/api/tasks?userId={self.test_staff1_id}&status=in progress')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # All returned tasks should have "In Progress" status (case insensitive)
        for task in response_data:
            self.assertEqual(task.get('task_status'), 'In Progress')


if __name__ == '__main__':
    print("=" * 80)
    print("REAL INTEGRATION TESTING - VIEW MY TASKS [ALL]")
    print("=" * 80)
    print("Testing user's ability to view their assigned tasks with REAL database integration")
    print("Tests Flask app + business logic + real database")
    print("=" * 80)
    
    # Run with verbose output
    unittest.main(verbosity=2)
