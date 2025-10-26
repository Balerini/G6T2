#!/usr/bin/env python3
"""
Integration Tests for SCRUM-75: View Standalone Task
Tests the API endpoints for viewing individual tasks (standalone and project tasks).
Uses real database connections for C2 integration testing.
"""

import unittest
import sys
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import Flask app and Firebase utilities
from app import create_app
from firebase_utils import get_firestore_client

class TestViewStandaloneTaskIntegration(unittest.TestCase):
    """C2 Integration tests for View Standalone Task functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        print("=" * 80)
        print("INTEGRATION TESTING - VIEW STANDALONE TASK")
        print("=" * 80)
        print("Testing real API endpoints with real database")
        print("=" * 80)
        
        # Set up Flask test client
        app = create_app()
        cls.app = app.test_client()
        cls.app_context = app.app_context()
        cls.app_context.push()
        
        # Get Firestore client
        cls.db = get_firestore_client()
        
        # Test user IDs (these should exist in your test database)
        cls.test_user_1_id = "test_user_standalone_123"
        cls.test_user_2_id = "test_user_standalone_456"
        cls.test_user_3_id = "test_user_standalone_789"
        cls.test_manager_id = "test_manager_standalone_101"
        cls.test_nonexistent_user_id = "test_nonexistent_standalone_202"
        
        # Test division name
        cls.test_division = "Test Standalone Division"
        
        # Create test data
        cls.setup_test_data()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        cls.cleanup_test_data()
        cls.app_context.pop()
        print("=" * 80)
        print("INTEGRATION TESTING COMPLETED")
        print("=" * 80)
    
    @classmethod
    def setup_test_data(cls):
        """Create test users, standalone tasks, and project tasks for testing"""
        print("Setting up test data...")
        
        # Create test users
        users_data = [
            {
                'id': cls.test_user_1_id,
                'name': 'Test User Standalone 1',
                'email': 'testuser1.standalone@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_user_2_id,
                'name': 'Test User Standalone 2',
                'email': 'testuser2.standalone@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_user_3_id,
                'name': 'Test User Standalone 3',
                'email': 'testuser3.standalone@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_manager_id,
                'name': 'Test Manager Standalone',
                'email': 'testmanager.standalone@example.com',
                'role_name': 'Manager',
                'role_num': 3,  # Manager role
                'division_name': cls.test_division
            }
        ]
        
        for user_data in users_data:
            user_ref = cls.db.collection('Users').document(user_data['id'])
            user_ref.set(user_data)
        
        # Create test project for project tasks
        current_date = datetime.now()
        project_data = {
            'proj_name': 'Test Standalone Project',
            'proj_desc': 'Test project for standalone task testing',
            'start_date': current_date + timedelta(days=1),
            'end_date': current_date + timedelta(days=30),
            'owner': cls.test_manager_id,
            'division_name': cls.test_division,
            'collaborators': [cls.test_manager_id, cls.test_user_1_id, cls.test_user_2_id],
            'proj_status': 'In Progress',
            'is_deleted': False,
            'createdAt': current_date,
            'updatedAt': current_date
        }
        
        project_ref = cls.db.collection('Projects').document('test_project_standalone_123')
        project_ref.set(project_data)
        cls.test_project_id = 'test_project_standalone_123'
        
        # Create standalone tasks (no project)
        standalone_tasks_data = [
            {
                'id': 'test_standalone_task_1',
                'task_name': 'Personal Learning Task',
                'task_desc': 'Learn new technology for personal development',
                'start_date': current_date + timedelta(days=1),
                'end_date': current_date + timedelta(days=7),
                'task_status': 'In Progress',
                'priority_level': 2,
                'proj_ID': None,  # Standalone task
                'owner': cls.test_user_1_id,
                'assigned_to': [cls.test_user_1_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            {
                'id': 'test_standalone_task_2',
                'task_name': 'Team Meeting Preparation',
                'task_desc': 'Prepare materials for team meeting',
                'start_date': current_date + timedelta(days=2),
                'end_date': current_date + timedelta(days=5),
                'task_status': 'Not Started',
                'priority_level': 3,
                'proj_ID': None,  # Standalone task
                'owner': cls.test_user_2_id,
                'assigned_to': [cls.test_user_2_id, cls.test_user_3_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            {
                'id': 'test_standalone_task_3',
                'task_name': 'Completed Personal Task',
                'task_desc': 'A task that has been completed',
                'start_date': current_date - timedelta(days=5),
                'end_date': current_date - timedelta(days=1),
                'task_status': 'Completed',
                'priority_level': 1,
                'proj_ID': None,  # Standalone task
                'owner': cls.test_user_3_id,
                'assigned_to': [cls.test_user_3_id],
                'is_deleted': False,
                'createdAt': current_date - timedelta(days=10),
                'updatedAt': current_date - timedelta(days=1)
            },
            {
                'id': 'test_standalone_task_4',
                'task_name': 'Deleted Standalone Task',
                'task_desc': 'This task is deleted',
                'start_date': current_date + timedelta(days=1),
                'end_date': current_date + timedelta(days=5),
                'task_status': 'In Progress',
                'priority_level': 2,
                'proj_ID': None,  # Standalone task
                'owner': cls.test_user_1_id,
                'assigned_to': [cls.test_user_1_id],
                'is_deleted': True,  # This task should be excluded
                'createdAt': current_date,
                'updatedAt': current_date
            }
        ]
        
        # Create project tasks (part of project)
        project_tasks_data = [
            {
                'id': 'test_project_task_1',
                'task_name': 'Project Development Task',
                'task_desc': 'Develop feature for the project',
                'start_date': current_date + timedelta(days=3),
                'end_date': current_date + timedelta(days=10),
                'task_status': 'In Progress',
                'priority_level': 2,
                'proj_ID': cls.test_project_id,  # Project task
                'owner': cls.test_manager_id,
                'assigned_to': [cls.test_user_1_id, cls.test_user_2_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            {
                'id': 'test_project_task_2',
                'task_name': 'Project Testing Task',
                'task_desc': 'Test the developed feature',
                'start_date': current_date + timedelta(days=8),
                'end_date': current_date + timedelta(days=15),
                'task_status': 'Not Started',
                'priority_level': 3,
                'proj_ID': cls.test_project_id,  # Project task
                'owner': cls.test_user_1_id,
                'assigned_to': [cls.test_user_2_id, cls.test_user_3_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            }
        ]
        
        # Create all tasks
        all_tasks = standalone_tasks_data + project_tasks_data
        for task_data in all_tasks:
            task_ref = cls.db.collection('Tasks').document(task_data['id'])
            task_ref.set(task_data)
        
        print(f"Created {len(users_data)} test users, 1 test project, and {len(all_tasks)} test tasks")
        print(f"Standalone tasks: {len(standalone_tasks_data)}, Project tasks: {len(project_tasks_data)}")
    
    @classmethod
    def cleanup_test_data(cls):
        """Clean up test data"""
        print("Cleaning up test data...")
        
        # Delete test tasks
        task_ids = [
            'test_standalone_task_1', 'test_standalone_task_2', 'test_standalone_task_3', 'test_standalone_task_4',
            'test_project_task_1', 'test_project_task_2'
        ]
        for task_id in task_ids:
            try:
                cls.db.collection('Tasks').document(task_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete task {task_id}: {e}")
        
        # Delete test users
        user_ids = [cls.test_user_1_id, cls.test_user_2_id, cls.test_user_3_id, cls.test_manager_id]
        for user_id in user_ids:
            try:
                cls.db.collection('Users').document(user_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete user {user_id}: {e}")
        
        # Delete test project
        try:
            cls.db.collection('Projects').document(cls.test_project_id).delete()
        except Exception as e:
            print(f"Warning: Could not delete project {cls.test_project_id}: {e}")
        
        print("Test data cleanup completed")
    
    def test_view_all_tasks_for_user(self):
        """Test viewing all tasks for a specific user"""
        print("\n--- Testing view all tasks for user ---")
        
        # Test with user 1 (should have multiple tasks)
        response = self.app.get(f'/api/tasks?userId={self.test_user_1_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Should be a list of tasks
        self.assertIsInstance(data, list)
        
        # User 1 should have tasks (assigned_to and owner)
        self.assertGreater(len(data), 0, "User 1 should have tasks")
        
        # Check task structure
        for task in data:
            self.assertIn('id', task)
            self.assertIn('task_name', task)
            self.assertIn('task_desc', task)
            self.assertIn('task_status', task)
            self.assertIn('priority_level', task)
            self.assertIn('proj_ID', task)
            self.assertIn('owner', task)
            self.assertIn('assigned_to', task)
            self.assertIn('start_date', task)
            self.assertIn('end_date', task)
            self.assertIn('createdAt', task)
            self.assertIn('updatedAt', task)
            
            # Verify user is either owner or assigned to task
            is_owner = task['owner'] == self.test_user_1_id
            is_assigned = self.test_user_1_id in task.get('assigned_to', [])
            self.assertTrue(is_owner or is_assigned, f"User should be owner or assigned to task {task['id']}")
            
            # Verify task is not deleted
            self.assertFalse(task.get('is_deleted', False), f"Task {task['id']} should not be deleted")
        
        print(f"✅ Successfully retrieved {len(data)} tasks for user 1")
    
    def test_view_individual_task(self):
        """Test viewing individual task details"""
        print("\n--- Testing view individual task ---")
        
        task_id = 'test_standalone_task_1'
        response = self.app.get(f'/api/tasks/{task_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check task information
        self.assertEqual(data['id'], task_id)
        self.assertEqual(data['task_name'], 'Personal Learning Task')
        self.assertEqual(data['task_desc'], 'Learn new technology for personal development')
        self.assertEqual(data['task_status'], 'In Progress')
        self.assertEqual(data['priority_level'], 2)
        self.assertIsNone(data['proj_ID'], "Should be standalone task (no project)")
        self.assertEqual(data['owner'], self.test_user_1_id)
        
        # Check assigned_to is an array
        self.assertIsInstance(data['assigned_to'], list)
        self.assertIn(self.test_user_1_id, data['assigned_to'])
        
        # Check timestamps are properly formatted
        self.assertIn('start_date', data)
        self.assertIn('end_date', data)
        self.assertIn('createdAt', data)
        self.assertIn('updatedAt', data)
        
        # Verify timestamps are ISO format strings
        for field in ['start_date', 'end_date', 'createdAt', 'updatedAt']:
            if data[field]:
                self.assertIsInstance(data[field], str)
                self.assertTrue('T' in data[field] or len(data[field]) == 10)
        
        print("✅ Successfully retrieved individual task details")
    
    def test_view_project_task(self):
        """Test viewing task that belongs to a project"""
        print("\n--- Testing view project task ---")
        
        task_id = 'test_project_task_1'
        response = self.app.get(f'/api/tasks/{task_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check task information
        self.assertEqual(data['id'], task_id)
        self.assertEqual(data['task_name'], 'Project Development Task')
        self.assertEqual(data['task_desc'], 'Develop feature for the project')
        self.assertEqual(data['task_status'], 'In Progress')
        self.assertEqual(data['priority_level'], 2)
        self.assertEqual(data['proj_ID'], self.test_project_id, "Should be project task")
        self.assertEqual(data['owner'], self.test_manager_id)
        
        # Check assigned_to is an array with multiple users
        self.assertIsInstance(data['assigned_to'], list)
        self.assertIn(self.test_user_1_id, data['assigned_to'])
        self.assertIn(self.test_user_2_id, data['assigned_to'])
        
        print("✅ Successfully retrieved project task details")
    
    def test_filter_tasks_by_status(self):
        """Test filtering tasks by status"""
        print("\n--- Testing task status filtering ---")
        
        # Test filtering by specific status
        response = self.app.get(f'/api/tasks?userId={self.test_user_1_id}&status=In Progress')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # All returned tasks should have "In Progress" status
        for task in data:
            self.assertEqual(task['task_status'], 'In Progress')
        
        print(f"✅ Found {len(data)} tasks with 'In Progress' status")
        
        # Test filtering by multiple statuses
        response = self.app.get(f'/api/tasks?userId={self.test_user_2_id}&status=Not Started&status=Completed')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # All returned tasks should have either "Not Started" or "Completed" status
        for task in data:
            self.assertIn(task['task_status'], ['Not Started', 'Completed'])
        
        print(f"✅ Found {len(data)} tasks with 'Not Started' or 'Completed' status")
        
        # Test filtering by "all" (should return all tasks)
        response = self.app.get(f'/api/tasks?userId={self.test_user_3_id}&status=all')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Should return all tasks for user (no status filtering)
        self.assertGreaterEqual(len(data), 0)
        
        print(f"✅ Found {len(data)} tasks with 'all' status filter")
    
    def test_filter_tasks_by_active_status(self):
        """Test filtering tasks by active status group"""
        print("\n--- Testing active status group filtering ---")
        
        # Test filtering by "active" status group
        response = self.app.get(f'/api/tasks?userId={self.test_user_1_id}&status=active')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # All returned tasks should have active statuses
        active_statuses = {'active', 'unassigned', 'ongoing', 'under review', 'in progress', 'not started'}
        for task in data:
            self.assertIn(task['task_status'].lower(), active_statuses)
        
        print(f"✅ Found {len(data)} tasks with active status")
    
    def test_view_tasks_without_user_filter(self):
        """Test viewing all tasks without user filter"""
        print("\n--- Testing view all tasks without user filter ---")
        
        response = self.app.get('/api/tasks')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Should be a list of tasks
        self.assertIsInstance(data, list)
        
        # Should include both standalone and project tasks
        standalone_count = sum(1 for task in data if task.get('proj_ID') is None)
        project_count = sum(1 for task in data if task.get('proj_ID') is not None)
        
        print(f"✅ Found {len(data)} total tasks: {standalone_count} standalone, {project_count} project tasks")
        
        # Verify no deleted tasks are included
        for task in data:
            self.assertFalse(task.get('is_deleted', False), f"Task {task['id']} should not be deleted")
    
    def test_nonexistent_task(self):
        """Test behavior with nonexistent task ID"""
        print("\n--- Testing nonexistent task ID ---")
        
        nonexistent_task_id = "nonexistent_standalone_task_12345"
        
        response = self.app.get(f'/api/tasks/{nonexistent_task_id}')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Task not found', data['error'])
        
        print("✅ Nonexistent task ID handled correctly")
    
    def test_nonexistent_user(self):
        """Test behavior with nonexistent user ID"""
        print("\n--- Testing nonexistent user ID ---")
        
        response = self.app.get(f'/api/tasks?userId={self.test_nonexistent_user_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Should return empty list for nonexistent user
        self.assertEqual(data, [])
        
        print("✅ Nonexistent user ID handled correctly")
    
    def test_deleted_tasks_excluded(self):
        """Test that deleted tasks are excluded from results"""
        print("\n--- Testing deleted tasks exclusion ---")
        
        # Get tasks for user 1 (who owns the deleted task)
        response = self.app.get(f'/api/tasks?userId={self.test_user_1_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify deleted task is not included
        task_names = [task['task_name'] for task in data]
        self.assertNotIn('Deleted Standalone Task', task_names)
        
        # Verify all returned tasks are not deleted
        for task in data:
            self.assertFalse(task.get('is_deleted', False), f"Task {task['id']} should not be deleted")
        
        print("✅ Deleted tasks properly excluded from results")
    
    def test_task_assignment_scenarios(self):
        """Test different task assignment scenarios"""
        print("\n--- Testing task assignment scenarios ---")
        
        # Test user who is both owner and assigned to tasks
        response = self.app.get(f'/api/tasks?userId={self.test_user_1_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # User 1 should have tasks where they are owner or assigned
        for task in data:
            is_owner = task['owner'] == self.test_user_1_id
            is_assigned = self.test_user_1_id in task.get('assigned_to', [])
            self.assertTrue(is_owner or is_assigned, f"User should be owner or assigned to task {task['id']}")
        
        # Test user who is only assigned to tasks (not owner)
        response = self.app.get(f'/api/tasks?userId={self.test_user_3_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # User 3 should have tasks where they are assigned
        for task in data:
            is_owner = task['owner'] == self.test_user_3_id
            is_assigned = self.test_user_3_id in task.get('assigned_to', [])
            self.assertTrue(is_owner or is_assigned, f"User should be owner or assigned to task {task['id']}")
        
        print("✅ Task assignment scenarios handled correctly")
    
    def test_standalone_vs_project_tasks(self):
        """Test distinction between standalone and project tasks"""
        print("\n--- Testing standalone vs project tasks ---")
        
        # Get all tasks for user 1
        response = self.app.get(f'/api/tasks?userId={self.test_user_1_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        standalone_tasks = [task for task in data if task.get('proj_ID') is None]
        project_tasks = [task for task in data if task.get('proj_ID') is not None]
        
        # Should have both types of tasks
        self.assertGreater(len(standalone_tasks), 0, "Should have standalone tasks")
        self.assertGreater(len(project_tasks), 0, "Should have project tasks")
        
        # Verify standalone tasks have no project ID
        for task in standalone_tasks:
            self.assertIsNone(task.get('proj_ID'), f"Task {task['id']} should be standalone")
        
        # Verify project tasks have project ID
        for task in project_tasks:
            self.assertIsNotNone(task.get('proj_ID'), f"Task {task['id']} should be project task")
            self.assertEqual(task.get('proj_ID'), self.test_project_id)
        
        print(f"✅ Found {len(standalone_tasks)} standalone tasks and {len(project_tasks)} project tasks")
    
    def test_task_timestamp_formatting(self):
        """Test that timestamps are properly formatted in ISO format"""
        print("\n--- Testing timestamp formatting ---")
        
        task_id = 'test_standalone_task_1'
        response = self.app.get(f'/api/tasks/{task_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check timestamp fields
        timestamp_fields = ['start_date', 'end_date', 'createdAt', 'updatedAt']
        for field in timestamp_fields:
            if field in data and data[field]:
                # Should be ISO format string
                self.assertIsInstance(data[field], str)
                # Should contain 'T' or be valid ISO format
                self.assertTrue('T' in data[field] or len(data[field]) == 10)
        
        print("✅ Timestamp formatting verified")
    
    def test_task_data_completeness(self):
        """Test that task data includes all required fields"""
        print("\n--- Testing task data completeness ---")
        
        task_id = 'test_standalone_task_2'
        response = self.app.get(f'/api/tasks/{task_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check all required fields are present
        required_fields = [
            'id', 'task_name', 'task_desc', 'task_status', 'priority_level',
            'proj_ID', 'owner', 'assigned_to', 'start_date', 'end_date',
            'createdAt', 'updatedAt'
        ]
        
        for field in required_fields:
            self.assertIn(field, data, f"Required field '{field}' should be present")
        
        # Check data types
        self.assertIsInstance(data['assigned_to'], list)
        self.assertIsInstance(data['priority_level'], int)
        self.assertIsInstance(data['task_status'], str)
        
        print("✅ Task data completeness verified")
    
    def test_multiple_assignment_tasks(self):
        """Test tasks assigned to multiple users"""
        print("\n--- Testing multiple assignment tasks ---")
        
        # Get tasks for user 2 (who has multi-assigned tasks)
        response = self.app.get(f'/api/tasks?userId={self.test_user_2_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Find multi-assigned tasks
        multi_assigned_tasks = [task for task in data if len(task.get('assigned_to', [])) > 1]
        
        self.assertGreater(len(multi_assigned_tasks), 0, "Should have multi-assigned tasks")
        
        for task in multi_assigned_tasks:
            assigned_to = task.get('assigned_to', [])
            self.assertGreater(len(assigned_to), 1, f"Task {task['id']} should have multiple assignees")
            self.assertIn(self.test_user_2_id, assigned_to, f"User 2 should be assigned to task {task['id']}")
        
        print(f"✅ Found {len(multi_assigned_tasks)} multi-assigned tasks")
    
    def test_task_status_variations(self):
        """Test different task status variations"""
        print("\n--- Testing task status variations ---")
        
        # Get all tasks for user 3 (who has completed tasks)
        response = self.app.get(f'/api/tasks?userId={self.test_user_3_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Should have tasks with different statuses
        statuses = set(task['task_status'] for task in data)
        self.assertGreater(len(statuses), 0, "Should have tasks with different statuses")
        
        # Verify status values are valid
        valid_statuses = {'Not Started', 'In Progress', 'Completed', 'On Hold', 'Cancelled'}
        for task in data:
            self.assertIn(task['task_status'], valid_statuses, f"Task {task['id']} has invalid status")
        
        print(f"✅ Found tasks with statuses: {', '.join(statuses)}")


if __name__ == '__main__':
    print("=" * 80)
    print("SCRUM-75: VIEW STANDALONE TASK - INTEGRATION TESTING")
    print("=" * 80)
    print("Testing real API endpoints with real database")
    print("=" * 80)
    
    # Run the tests
    unittest.main(verbosity=2)
