#!/usr/bin/env python3
"""
Integration Tests for SCRUM-52,66: My Tasks Priority [All]
Tests the API endpoint for getting user's tasks with priority information.
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

class TestMyTasksPriorityIntegration(unittest.TestCase):
    """C2 Integration tests for My Tasks Priority functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        print("=" * 80)
        print("INTEGRATION TESTING - MY TASKS PRIORITY [ALL]")
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
        cls.test_user_id = "test_user_priority_123"
        cls.test_manager_id = "test_manager_priority_456"
        cls.test_staff_id = "test_staff_priority_789"
        
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
        """Create test users and tasks with different priority levels"""
        print("Setting up test data...")
        
        # Create test users
        users_data = [
            {
                'id': cls.test_user_id,
                'name': 'Test User Priority',
                'email': 'testuser.priority@example.com',
                'role_name': 'Staff',
                'role_num': 4,
                'division_name': 'Test Division'
            },
            {
                'id': cls.test_manager_id,
                'name': 'Test Manager Priority',
                'email': 'testmanager.priority@example.com',
                'role_name': 'Manager',
                'role_num': 2,
                'division_name': 'Test Division'
            },
            {
                'id': cls.test_staff_id,
                'name': 'Test Staff Priority',
                'email': 'teststaff.priority@example.com',
                'role_name': 'Staff',
                'role_num': 4,
                'division_name': 'Test Division'
            }
        ]
        
        for user_data in users_data:
            user_ref = cls.db.collection('Users').document(user_data['id'])
            user_ref.set(user_data)
        
        # Create test tasks with different priority levels
        tasks_data = [
            {
                'task_name': 'High Priority Task 1',
                'task_desc': 'Task with priority level 9 (High)',
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=7),
                'task_status': 'Ongoing',
                'priority_level': 9,  # High priority
                'assigned_to': [cls.test_user_id],
                'owner': cls.test_user_id,
                'proj_ID': 'test_project_priority',
                'is_deleted': False,
                'createdAt': datetime.now(),
                'updatedAt': datetime.now()
            },
            {
                'task_name': 'Medium Priority Task 1',
                'task_desc': 'Task with priority level 5 (Medium)',
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=14),
                'task_status': 'Unassigned',
                'priority_level': 5,  # Medium priority
                'assigned_to': [cls.test_user_id],
                'owner': cls.test_user_id,
                'proj_ID': 'test_project_priority',
                'is_deleted': False,
                'createdAt': datetime.now(),
                'updatedAt': datetime.now()
            },
            {
                'task_name': 'Low Priority Task 1',
                'task_desc': 'Task with priority level 2 (Low)',
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=30),
                'task_status': 'Completed',
                'priority_level': 2,  # Low priority
                'assigned_to': [cls.test_user_id],
                'owner': cls.test_user_id,
                'proj_ID': 'test_project_priority',
                'is_deleted': False,
                'createdAt': datetime.now(),
                'updatedAt': datetime.now()
            },
            {
                'task_name': 'High Priority Task 2',
                'task_desc': 'Another high priority task',
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=3),
                'task_status': 'Under Review',
                'priority_level': 10,  # High priority
                'assigned_to': [cls.test_user_id, cls.test_staff_id],
                'owner': cls.test_manager_id,
                'proj_ID': 'test_project_priority',
                'is_deleted': False,
                'createdAt': datetime.now(),
                'updatedAt': datetime.now()
            },
            {
                'task_name': 'Medium Priority Task 2',
                'task_desc': 'Another medium priority task',
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=21),
                'task_status': 'Ongoing',
                'priority_level': 6,  # Medium priority
                'assigned_to': [cls.test_staff_id],
                'owner': cls.test_staff_id,
                'proj_ID': 'test_project_priority',
                'is_deleted': False,
                'createdAt': datetime.now(),
                'updatedAt': datetime.now()
            },
            {
                'task_name': 'Deleted Task',
                'task_desc': 'This task should not appear in results',
                'start_date': datetime.now(),
                'end_date': datetime.now() + timedelta(days=7),
                'task_status': 'Ongoing',
                'priority_level': 8,
                'assigned_to': [cls.test_user_id],
                'owner': cls.test_user_id,
                'proj_ID': 'test_project_priority',
                'is_deleted': True,  # This should be filtered out
                'createdAt': datetime.now(),
                'updatedAt': datetime.now()
            }
        ]
        
        for i, task_data in enumerate(tasks_data):
            task_ref = cls.db.collection('Tasks').document(f'test_task_priority_{i}')
            task_ref.set(task_data)
        
        print(f"Created {len(users_data)} test users and {len(tasks_data)} test tasks")
    
    @classmethod
    def cleanup_test_data(cls):
        """Clean up test data"""
        print("Cleaning up test data...")
        
        # Delete test users
        user_ids = [cls.test_user_id, cls.test_manager_id, cls.test_staff_id]
        for user_id in user_ids:
            try:
                cls.db.collection('Users').document(user_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete user {user_id}: {e}")
        
        # Delete test tasks
        for i in range(6):  # We created 6 test tasks
            try:
                cls.db.collection('Tasks').document(f'test_task_priority_{i}').delete()
            except Exception as e:
                print(f"Warning: Could not delete task test_task_priority_{i}: {e}")
        
        print("Test data cleanup completed")
    
    def test_get_my_tasks_with_priority_basic(self):
        """Test basic functionality of getting user's tasks with priority"""
        print("\n--- Testing basic my tasks with priority ---")
        
        response = self.app.get(f'/api/tasks?userId={self.test_user_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Should return tasks assigned to or owned by the user
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0, "Should return at least one task")
        
        # Check that all returned tasks have priority information
        for task in data:
            self.assertIn('priority_level', task, "Task should have priority_level field")
            self.assertIn('task_name', task, "Task should have task_name field")
            self.assertIn('task_status', task, "Task should have task_status field")
            
            # Priority should be a valid number between 1-10
            priority = task['priority_level']
            self.assertIsInstance(priority, (int, str), "Priority should be a number")
            if isinstance(priority, str):
                priority = int(priority)
            self.assertGreaterEqual(priority, 1, "Priority should be >= 1")
            self.assertLessEqual(priority, 10, "Priority should be <= 10")
        
        print(f"✅ Found {len(data)} tasks with priority information")
    
    def test_get_my_tasks_priority_categorization(self):
        """Test that tasks are properly categorized by priority levels"""
        print("\n--- Testing priority categorization ---")
        
        response = self.app.get(f'/api/tasks?userId={self.test_user_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Categorize tasks by priority
        high_priority = []  # 8-10
        medium_priority = []  # 4-7
        low_priority = []  # 1-3
        
        for task in data:
            priority = task['priority_level']
            if isinstance(priority, str):
                priority = int(priority)
            
            if priority >= 8:
                high_priority.append(task)
            elif priority >= 4:
                medium_priority.append(task)
            else:
                low_priority.append(task)
        
        # Verify we have tasks in different priority categories
        print(f"High priority tasks (8-10): {len(high_priority)}")
        print(f"Medium priority tasks (4-7): {len(medium_priority)}")
        print(f"Low priority tasks (1-3): {len(low_priority)}")
        
        # Should have at least one task in each category based on our test data
        self.assertGreater(len(high_priority), 0, "Should have high priority tasks")
        self.assertGreater(len(medium_priority), 0, "Should have medium priority tasks")
        self.assertGreater(len(low_priority), 0, "Should have low priority tasks")
        
        # Verify specific priority values
        high_priorities = [int(task['priority_level']) for task in high_priority]
        medium_priorities = [int(task['priority_level']) for task in medium_priority]
        low_priorities = [int(task['priority_level']) for task in low_priority]
        
        self.assertTrue(all(p >= 8 for p in high_priorities), "High priority tasks should be >= 8")
        self.assertTrue(all(4 <= p <= 7 for p in medium_priorities), "Medium priority tasks should be 4-7")
        self.assertTrue(all(1 <= p <= 3 for p in low_priorities), "Low priority tasks should be 1-3")
        
        print("✅ Priority categorization working correctly")
    
    def test_get_my_tasks_priority_filtering_by_status(self):
        """Test filtering tasks by status while maintaining priority information"""
        print("\n--- Testing status filtering with priority ---")
        
        # Test different status filters
        status_tests = [
            ('Ongoing', 'Ongoing'),
            ('Unassigned', 'Unassigned'),
            ('Completed', 'Completed'),
            ('Under Review', 'Under Review'),
            ('active', ['Unassigned', 'Ongoing', 'Under Review']),  # Status group
        ]
        
        for status_filter, expected_statuses in status_tests:
            response = self.app.get(f'/api/tasks?userId={self.test_user_id}&status={status_filter}')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            if isinstance(expected_statuses, str):
                expected_statuses = [expected_statuses]
            
            # All returned tasks should match the status filter
            for task in data:
                task_status = task.get('task_status', '')
                self.assertIn(task_status, expected_statuses, 
                            f"Task status '{task_status}' should match filter '{status_filter}'")
                
                # Priority should still be present
                self.assertIn('priority_level', task, "Priority should be present even with status filtering")
            
            print(f"✅ Status filter '{status_filter}': {len(data)} tasks")
    
    def test_get_my_tasks_priority_no_user_id(self):
        """Test behavior when no userId is provided"""
        print("\n--- Testing no userId parameter ---")
        
        response = self.app.get('/api/tasks')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Should return all tasks (not user-specific)
        self.assertIsInstance(data, list)
        print(f"✅ No userId: returned {len(data)} total tasks")
    
    def test_get_my_tasks_priority_invalid_user_id(self):
        """Test behavior with invalid userId"""
        print("\n--- Testing invalid userId ---")
        
        invalid_user_id = "nonexistent_user_12345"
        response = self.app.get(f'/api/tasks?userId={invalid_user_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Should return empty list for non-existent user
        self.assertEqual(len(data), 0, "Should return empty list for non-existent user")
        print("✅ Invalid userId handled correctly")
    
    def test_get_my_tasks_priority_assigned_vs_owned(self):
        """Test that tasks are returned for both assigned and owned tasks"""
        print("\n--- Testing assigned vs owned tasks ---")
        
        # Test with user who has both assigned and owned tasks
        response = self.app.get(f'/api/tasks?userId={self.test_user_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        assigned_tasks = []
        owned_tasks = []
        
        for task in data:
            # Check if user is in assigned_to array
            assigned_to = task.get('assigned_to', [])
            if self.test_user_id in assigned_to:
                assigned_tasks.append(task)
            
            # Check if user is the owner
            if task.get('owner') == self.test_user_id:
                owned_tasks.append(task)
        
        print(f"Assigned tasks: {len(assigned_tasks)}")
        print(f"Owned tasks: {len(owned_tasks)}")
        
        # Should have both assigned and owned tasks
        self.assertGreater(len(assigned_tasks), 0, "Should have assigned tasks")
        self.assertGreater(len(owned_tasks), 0, "Should have owned tasks")
        
        # All tasks should have priority information
        for task in assigned_tasks + owned_tasks:
            self.assertIn('priority_level', task, "All tasks should have priority information")
        
        print("✅ Both assigned and owned tasks returned with priority")
    
    def test_get_my_tasks_priority_excludes_deleted(self):
        """Test that deleted tasks are excluded from results"""
        print("\n--- Testing exclusion of deleted tasks ---")
        
        response = self.app.get(f'/api/tasks?userId={self.test_user_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check that no deleted tasks are returned
        for task in data:
            is_deleted = task.get('is_deleted', False)
            self.assertFalse(is_deleted, "Deleted tasks should not be returned")
        
        print("✅ Deleted tasks properly excluded")
    
    def test_get_my_tasks_priority_edge_cases(self):
        """Test edge cases for priority handling"""
        print("\n--- Testing priority edge cases ---")
        
        # Test with user who has tasks with edge case priority values
        response = self.app.get(f'/api/tasks?userId={self.test_user_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        priorities_found = set()
        for task in data:
            priority = task['priority_level']
            if isinstance(priority, str):
                priority = int(priority)
            priorities_found.add(priority)
        
        print(f"Priority values found: {sorted(priorities_found)}")
        
        # Should have various priority levels
        self.assertGreater(len(priorities_found), 1, "Should have multiple priority levels")
        
        # All priorities should be valid (1-10)
        for priority in priorities_found:
            self.assertGreaterEqual(priority, 1, f"Priority {priority} should be >= 1")
            self.assertLessEqual(priority, 10, f"Priority {priority} should be <= 10")
        
        print("✅ Priority edge cases handled correctly")
    
    def test_get_my_tasks_priority_response_format(self):
        """Test that response format includes all necessary fields"""
        print("\n--- Testing response format ---")
        
        response = self.app.get(f'/api/tasks?userId={self.test_user_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        if data:  # Only test if we have data
            task = data[0]
            
            # Required fields for priority functionality
            required_fields = [
                'id', 'task_name', 'task_status', 'priority_level',
                'assigned_to', 'owner', 'start_date', 'end_date'
            ]
            
            for field in required_fields:
                self.assertIn(field, task, f"Task should have {field} field")
            
            # Priority should be a valid number
            priority = task['priority_level']
            self.assertIsInstance(priority, (int, str), "Priority should be a number")
            
            # Assigned_to should be a list
            assigned_to = task['assigned_to']
            self.assertIsInstance(assigned_to, list, "assigned_to should be a list")
            
            print("✅ Response format is correct")
        else:
            print("⚠️ No tasks found to test response format")


if __name__ == '__main__':
    print("=" * 80)
    print("SCRUM-52,66: MY TASKS PRIORITY [ALL] - INTEGRATION TESTING")
    print("=" * 80)
    print("Testing real API endpoints with real database")
    print("=" * 80)
    
    # Run the tests
    unittest.main(verbosity=2)
