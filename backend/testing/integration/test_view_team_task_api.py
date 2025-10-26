#!/usr/bin/env python3
"""
REAL Integration Tests - View Team Task API [Manager]
Tests manager's ability to view team tasks via API with REAL database integration.
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


class TestViewTeamTaskAPI(unittest.TestCase):
    """REAL Integration tests for manager viewing team tasks with real database"""
    
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
        
        # Create staff user from different department
        other_staff_data = {
            'name': f'Test Other Staff {self.timestamp}',
            'email': f'otherstaff.{self.timestamp}@company.com',
            'role_name': 'Staff',
            'role_num': 4,
            'division_name': 'Sales Department',
            'created_at': datetime.now().isoformat()
        }
        
        other_staff_ref = self.db.collection('Users').add(other_staff_data)
        self.test_other_staff_id = other_staff_ref[1].id
        self.test_user_ids.append(self.test_other_staff_id)
    
    def setup_test_tasks(self):
        """Create real test tasks in the database"""
        # Calculate future dates for validation
        future_start = datetime.now() + timedelta(days=1)
        future_end = datetime.now() + timedelta(days=30)
        
        # Create project for tasks
        project_data = {
            'proj_name': f'Test Project {self.timestamp}',
            'proj_desc': 'Test project for team task viewing',
            'start_date': future_start.strftime('%Y-%m-%d'),
            'end_date': future_end.strftime('%Y-%m-%d'),
            'owner': self.test_manager_id,
            'division_name': 'IT Department',
            'collaborators': [self.test_manager_id, self.test_staff1_id, self.test_staff2_id]
        }
        
        project_ref = self.db.collection('Projects').add(project_data)
        self.test_project_id = project_ref[1].id
        self.test_project_ids.append(self.test_project_id)
        
        # Task 1: Assigned to staff1
        task1_data = {
            'task_name': f'Team Task 1 {self.timestamp}',
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
        
        # Task 2: Assigned to staff2
        task2_data = {
            'task_name': f'Team Task 2 {self.timestamp}',
            'task_desc': 'Task assigned to staff 2',
            'start_date': future_start.strftime('%Y-%m-%d'),
            'end_date': future_end.strftime('%Y-%m-%d'),
            'task_status': 'Completed',
            'priority_level': 2,
            'proj_ID': self.test_project_id,
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff2_id],
            'created_at': datetime.now().isoformat(),
            'is_deleted': False
        }
        
        task2_ref = self.db.collection('Tasks').add(task2_data)
        self.test_task2_id = task2_ref[1].id
        self.test_task_ids.append(self.test_task2_id)
        
        # Task 3: Assigned to both staff members
        task3_data = {
            'task_name': f'Team Task 3 {self.timestamp}',
            'task_desc': 'Task assigned to both staff members',
            'start_date': future_start.strftime('%Y-%m-%d'),
            'end_date': future_end.strftime('%Y-%m-%d'),
            'task_status': 'Not Started',
            'priority_level': 1,
            'proj_ID': self.test_project_id,
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff1_id, self.test_staff2_id],
            'created_at': datetime.now().isoformat(),
            'is_deleted': False
        }
        
        task3_ref = self.db.collection('Tasks').add(task3_data)
        self.test_task3_id = task3_ref[1].id
        self.test_task_ids.append(self.test_task3_id)
        
        # Task 4: Assigned to other department staff (should not be visible to manager)
        task4_data = {
            'task_name': f'Other Dept Task {self.timestamp}',
            'task_desc': 'Task assigned to other department staff',
            'start_date': future_start.strftime('%Y-%m-%d'),
            'end_date': future_end.strftime('%Y-%m-%d'),
            'task_status': 'In Progress',
            'priority_level': 3,
            'proj_ID': self.test_project_id,
            'owner': self.test_manager_id,
            'assigned_to': [self.test_other_staff_id],
            'created_at': datetime.now().isoformat(),
            'is_deleted': False
        }
        
        task4_ref = self.db.collection('Tasks').add(task4_data)
        self.test_task4_id = task4_ref[1].id
        self.test_task_ids.append(self.test_task4_id)
    
    def test_manager_view_team_tasks_via_main_endpoint(self):
        """Test manager viewing team tasks via main /api/tasks endpoint with REAL database"""
        # Test manager viewing tasks assigned to their team members
        response = self.client.get(f'/api/tasks?userId={self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # Manager should see tasks they own and tasks assigned to them
        # Since manager owns all tasks, they should see all tasks
        self.assertGreaterEqual(len(response_data), 3)  # At least 3 team tasks
        
        # Verify task data structure
        for task in response_data:
            self.assertIn('id', task)
            self.assertIn('task_name', task)
            self.assertIn('task_status', task)
            self.assertIn('assigned_to', task)
            self.assertIn('owner', task)
    
    def test_manager_view_team_tasks_by_staff_member(self):
        """Test manager viewing tasks assigned to specific staff member with REAL database"""
        # Test viewing tasks assigned to staff1
        response = self.client.get(f'/api/tasks?userId={self.test_staff1_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # Staff1 should see tasks assigned to them
        staff1_tasks = [task for task in response_data if self.test_staff1_id in task.get('assigned_to', [])]
        self.assertGreaterEqual(len(staff1_tasks), 2)  # At least 2 tasks assigned to staff1
        
        # Verify all tasks are assigned to staff1
        for task in staff1_tasks:
            self.assertIn(self.test_staff1_id, task.get('assigned_to', []))
    
    def test_manager_dashboard_team_task_count(self):
        """Test manager dashboard team task count endpoint with REAL database"""
        response = self.client.get(f'/api/dashboard/manager/total-tasks/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('total_tasks', response_data)
        self.assertIn('staff_count', response_data)
        
        # Should have tasks for team members
        self.assertGreaterEqual(response_data['total_tasks'], 3)  # At least 3 team tasks
        self.assertGreaterEqual(response_data['staff_count'], 2)  # At least 2 staff members
    
    def test_manager_dashboard_team_tasks_by_status(self):
        """Test manager dashboard team tasks by status endpoint with REAL database"""
        response = self.client.get(f'/api/dashboard/manager/tasks-by-status/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, dict)
        
        # Should have status breakdown
        self.assertIn('In Progress', response_data)
        self.assertIn('Completed', response_data)
        self.assertIn('Not Started', response_data)
        
        # Verify counts are reasonable
        self.assertGreaterEqual(response_data['In Progress'], 1)
        self.assertGreaterEqual(response_data['Completed'], 1)
        self.assertGreaterEqual(response_data['Not Started'], 1)
    
    def test_manager_dashboard_team_tasks_by_staff(self):
        """Test manager dashboard team tasks by staff endpoint with REAL database"""
        response = self.client.get(f'/api/dashboard/manager/tasks-by-staff/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, dict)
        
        # Should have staff breakdown
        self.assertIn(self.test_staff1_id, response_data)
        self.assertIn(self.test_staff2_id, response_data)
        
        # Verify counts are reasonable
        self.assertGreaterEqual(response_data[self.test_staff1_id], 2)  # Staff1 has at least 2 tasks
        self.assertGreaterEqual(response_data[self.test_staff2_id], 2)  # Staff2 has at least 2 tasks
    
    def test_manager_dashboard_team_tasks_by_priority(self):
        """Test manager dashboard team tasks by priority endpoint with REAL database"""
        response = self.client.get(f'/api/dashboard/manager/tasks-by-priority/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, dict)
        
        # Should have priority breakdown
        self.assertIn('1', response_data)  # High priority
        self.assertIn('2', response_data)  # Medium priority
        self.assertIn('3', response_data)  # Low priority
        
        # Verify counts are reasonable
        self.assertGreaterEqual(response_data['1'], 1)  # At least 1 high priority task
        self.assertGreaterEqual(response_data['2'], 1)  # At least 1 medium priority task
        self.assertGreaterEqual(response_data['3'], 1)  # At least 1 low priority task
    
    def test_manager_view_team_tasks_with_status_filter(self):
        """Test manager viewing team tasks with status filter with REAL database"""
        # Test viewing only "In Progress" tasks
        response = self.client.get(f'/api/tasks?userId={self.test_manager_id}&status=In Progress')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # All returned tasks should have "In Progress" status
        for task in response_data:
            self.assertEqual(task.get('task_status'), 'In Progress')
    
    def test_manager_view_team_tasks_with_multiple_status_filter(self):
        """Test manager viewing team tasks with multiple status filters with REAL database"""
        # Test viewing "In Progress" and "Completed" tasks
        response = self.client.get(f'/api/tasks?userId={self.test_manager_id}&status=In Progress&status=Completed')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # All returned tasks should have either "In Progress" or "Completed" status
        allowed_statuses = {'In Progress', 'Completed'}
        for task in response_data:
            self.assertIn(task.get('task_status'), allowed_statuses)
    
    def test_unauthorized_user_access_manager_endpoints(self):
        """Test unauthorized user trying to access manager endpoints with REAL database"""
        # Test staff user trying to access manager dashboard
        response = self.client.get(f'/api/dashboard/manager/total-tasks/{self.test_staff1_id}')
        
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('Unauthorized', response_data['error'])
    
    def test_nonexistent_user_access_manager_endpoints(self):
        """Test nonexistent user trying to access manager endpoints with REAL database"""
        fake_user_id = 'nonexistent_user_id'
        
        response = self.client.get(f'/api/dashboard/manager/total-tasks/{fake_user_id}')
        
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('User not found', response_data['error'])
    
    def test_manager_view_team_tasks_timeline(self):
        """Test manager viewing team tasks timeline with REAL database"""
        response = self.client.get(f'/api/dashboard/manager/tasks-timeline/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # Should have timeline data
        if response_data:  # If there are tasks
            for timeline_item in response_data:
                self.assertIn('date', timeline_item)
                self.assertIn('tasks', timeline_item)
                self.assertIsInstance(timeline_item['tasks'], list)
    
    def test_manager_view_pending_tasks_by_age(self):
        """Test manager viewing pending tasks by age with REAL database"""
        response = self.client.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, dict)
        
        # Should have age categories
        expected_categories = ['overdue', 'due_today', 'due_this_week', 'due_later']
        for category in expected_categories:
            self.assertIn(category, response_data)
            self.assertIsInstance(response_data[category], int)


if __name__ == '__main__':
    print("=" * 80)
    print("REAL INTEGRATION TESTING - VIEW TEAM TASK API [MANAGER]")
    print("=" * 80)
    print("Testing manager's ability to view team tasks with REAL database integration")
    print("Tests Flask app + business logic + real database")
    print("=" * 80)
    
    # Run with verbose output
    unittest.main(verbosity=2)
