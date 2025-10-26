#!/usr/bin/env python3
"""
Integration Tests for SCRUM-18: View Deadlines [Manager]
Tests the API endpoint for managers to view team deadlines and task due dates.
Uses real database connections for C2 integration testing.
"""

import unittest
import sys
import os
import json
from datetime import datetime, timedelta, date
from unittest.mock import patch

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import Flask app and Firebase utilities
from app import create_app
from firebase_utils import get_firestore_client

class TestViewDeadlinesManagerIntegration(unittest.TestCase):
    """C2 Integration tests for View Deadlines [Manager] functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        print("=" * 80)
        print("INTEGRATION TESTING - VIEW DEADLINES [MANAGER]")
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
        cls.test_manager_id = "test_manager_deadlines_123"
        cls.test_staff_1_id = "test_staff_deadlines_456"
        cls.test_staff_2_id = "test_staff_deadlines_789"
        cls.test_staff_3_id = "test_staff_deadlines_101"
        
        # Test division name
        cls.test_division = "Test Deadlines Division"
        
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
        """Create test users and tasks with different deadline scenarios"""
        print("Setting up test data...")
        
        # Create test users
        users_data = [
            {
                'id': cls.test_manager_id,
                'name': 'Test Manager Deadlines',
                'email': 'testmanager.deadlines@example.com',
                'role_name': 'Manager',
                'role_num': 2,  # Manager role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_staff_1_id,
                'name': 'Test Staff Deadlines 1',
                'email': 'teststaff1.deadlines@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_staff_2_id,
                'name': 'Test Staff Deadlines 2',
                'email': 'teststaff2.deadlines@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_staff_3_id,
                'name': 'Test Staff Deadlines 3',
                'email': 'teststaff3.deadlines@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            }
        ]
        
        for user_data in users_data:
            user_ref = cls.db.collection('Users').document(user_data['id'])
            user_ref.set(user_data)
        
        # Get current date for calculating deadlines
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Create test tasks with different deadline scenarios
        tasks_data = [
            # Overdue tasks
            {
                'task_name': 'Overdue Task 1',
                'task_desc': 'Task that was due 5 days ago',
                'start_date': current_date - timedelta(days=10),
                'end_date': current_date - timedelta(days=5),  # 5 days overdue
                'task_status': 'Ongoing',
                'priority_level': 9,
                'assigned_to': [cls.test_staff_1_id],
                'owner': cls.test_manager_id,
                'proj_ID': 'test_project_deadlines',
                'is_deleted': False,
                'createdAt': current_date - timedelta(days=10),
                'updatedAt': current_date - timedelta(days=5)
            },
            {
                'task_name': 'Overdue Task 2',
                'task_desc': 'Task that was due 2 days ago',
                'start_date': current_date - timedelta(days=7),
                'end_date': current_date - timedelta(days=2),  # 2 days overdue
                'task_status': 'Under Review',
                'priority_level': 8,
                'assigned_to': [cls.test_staff_2_id],
                'owner': cls.test_manager_id,
                'proj_ID': 'test_project_deadlines',
                'is_deleted': False,
                'createdAt': current_date - timedelta(days=7),
                'updatedAt': current_date - timedelta(days=2)
            },
            
            # Due today
            {
                'task_name': 'Due Today Task 1',
                'task_desc': 'Task due today',
                'start_date': current_date - timedelta(days=3),
                'end_date': current_date,  # Due today
                'task_status': 'Ongoing',
                'priority_level': 10,
                'assigned_to': [cls.test_staff_1_id],
                'owner': cls.test_manager_id,
                'proj_ID': 'test_project_deadlines',
                'is_deleted': False,
                'createdAt': current_date - timedelta(days=3),
                'updatedAt': current_date
            },
            
            # Due in 1 day
            {
                'task_name': 'Due Tomorrow Task 1',
                'task_desc': 'Task due tomorrow',
                'start_date': current_date - timedelta(days=2),
                'end_date': current_date + timedelta(days=1),  # Due tomorrow
                'task_status': 'Unassigned',
                'priority_level': 7,
                'assigned_to': [cls.test_staff_2_id],
                'owner': cls.test_manager_id,
                'proj_ID': 'test_project_deadlines',
                'is_deleted': False,
                'createdAt': current_date - timedelta(days=2),
                'updatedAt': current_date
            },
            
            # Due in 3 days
            {
                'task_name': 'Due in 3 Days Task 1',
                'task_desc': 'Task due in 3 days',
                'start_date': current_date - timedelta(days=1),
                'end_date': current_date + timedelta(days=3),  # Due in 3 days
                'task_status': 'Ongoing',
                'priority_level': 6,
                'assigned_to': [cls.test_staff_3_id],
                'owner': cls.test_manager_id,
                'proj_ID': 'test_project_deadlines',
                'is_deleted': False,
                'createdAt': current_date - timedelta(days=1),
                'updatedAt': current_date
            },
            
            # Due in a week
            {
                'task_name': 'Due in a Week Task 1',
                'task_desc': 'Task due in a week',
                'start_date': current_date,
                'end_date': current_date + timedelta(days=7),  # Due in a week
                'task_status': 'Unassigned',
                'priority_level': 5,
                'assigned_to': [cls.test_staff_1_id, cls.test_staff_2_id],  # Multiple assignees
                'owner': cls.test_manager_id,
                'proj_ID': 'test_project_deadlines',
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            
            # Due in 2 weeks
            {
                'task_name': 'Due in 2 Weeks Task 1',
                'task_desc': 'Task due in 2 weeks',
                'start_date': current_date + timedelta(days=1),
                'end_date': current_date + timedelta(days=14),  # Due in 2 weeks
                'task_status': 'Ongoing',
                'priority_level': 4,
                'assigned_to': [cls.test_staff_3_id],
                'owner': cls.test_manager_id,
                'proj_ID': 'test_project_deadlines',
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            
            # Due in a month
            {
                'task_name': 'Due in a Month Task 1',
                'task_desc': 'Task due in a month',
                'start_date': current_date + timedelta(days=5),
                'end_date': current_date + timedelta(days=30),  # Due in a month
                'task_status': 'Unassigned',
                'priority_level': 3,
                'assigned_to': [cls.test_staff_1_id],
                'owner': cls.test_manager_id,
                'proj_ID': 'test_project_deadlines',
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            
            # Due later (more than a month)
            {
                'task_name': 'Due Later Task 1',
                'task_desc': 'Task due much later',
                'start_date': current_date + timedelta(days=10),
                'end_date': current_date + timedelta(days=60),  # Due in 2 months
                'task_status': 'Ongoing',
                'priority_level': 2,
                'assigned_to': [cls.test_staff_2_id],
                'owner': cls.test_manager_id,
                'proj_ID': 'test_project_deadlines',
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            
            # Completed task (should not appear in pending tasks)
            {
                'task_name': 'Completed Task 1',
                'task_desc': 'Task that is completed',
                'start_date': current_date - timedelta(days=5),
                'end_date': current_date + timedelta(days=2),
                'task_status': 'Completed',
                'priority_level': 8,
                'assigned_to': [cls.test_staff_1_id],
                'owner': cls.test_manager_id,
                'proj_ID': 'test_project_deadlines',
                'is_deleted': False,
                'createdAt': current_date - timedelta(days=5),
                'updatedAt': current_date
            },
            
            # Deleted task (should not appear)
            {
                'task_name': 'Deleted Task 1',
                'task_desc': 'Task that is deleted',
                'start_date': current_date - timedelta(days=3),
                'end_date': current_date + timedelta(days=5),
                'task_status': 'Ongoing',
                'priority_level': 7,
                'assigned_to': [cls.test_staff_2_id],
                'owner': cls.test_manager_id,
                'proj_ID': 'test_project_deadlines',
                'is_deleted': True,  # This should be filtered out
                'createdAt': current_date - timedelta(days=3),
                'updatedAt': current_date
            }
        ]
        
        for i, task_data in enumerate(tasks_data):
            task_ref = cls.db.collection('Tasks').document(f'test_task_deadlines_{i}')
            task_ref.set(task_data)
        
        print(f"Created {len(users_data)} test users and {len(tasks_data)} test tasks")
    
    @classmethod
    def cleanup_test_data(cls):
        """Clean up test data"""
        print("Cleaning up test data...")
        
        # Delete test users
        user_ids = [cls.test_manager_id, cls.test_staff_1_id, cls.test_staff_2_id, cls.test_staff_3_id]
        for user_id in user_ids:
            try:
                cls.db.collection('Users').document(user_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete user {user_id}: {e}")
        
        # Delete test tasks
        for i in range(12):  # We created 12 test tasks
            try:
                cls.db.collection('Tasks').document(f'test_task_deadlines_{i}').delete()
            except Exception as e:
                print(f"Warning: Could not delete task test_task_deadlines_{i}: {e}")
        
        print("Test data cleanup completed")
    
    def test_view_deadlines_manager_basic(self):
        """Test basic functionality of manager viewing team deadlines"""
        print("\n--- Testing basic manager deadline viewing ---")
        
        response = self.app.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Should have the expected structure
        self.assertIn('pending_tasks_by_age', data)
        self.assertIn('summary', data)
        self.assertIn('division_name', data)
        
        # Check division name
        self.assertEqual(data['division_name'], self.test_division)
        
        # Check that we have tasks in different categories
        age_categories = data['pending_tasks_by_age']
        summary = data['summary']
        
        # Should have tasks in multiple categories
        total_tasks = sum(summary.values())
        self.assertGreater(total_tasks, 0, "Should have at least some tasks")
        
        print(f"✅ Found {total_tasks} total pending tasks across all categories")
        print(f"Summary: {summary}")
    
    def test_view_deadlines_categorization(self):
        """Test that tasks are properly categorized by deadline proximity"""
        print("\n--- Testing deadline categorization ---")
        
        response = self.app.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        age_categories = data['pending_tasks_by_age']
        summary = data['summary']
        
        # Check that we have tasks in expected categories
        expected_categories = [
            'overdue', 'due_today', 'due_in_1_day', 'due_in_3_days',
            'due_in_a_week', 'due_in_2_weeks', 'due_in_a_month', 'due_later'
        ]
        
        for category in expected_categories:
            self.assertIn(category, age_categories, f"Should have {category} category")
            self.assertIn(category, summary, f"Summary should include {category}")
            self.assertIsInstance(age_categories[category], list, f"{category} should be a list")
            self.assertIsInstance(summary[category], int, f"{category} summary should be an integer")
        
        # Based on our test data, we should have specific counts
        print(f"Overdue tasks: {summary['overdue']}")
        print(f"Due today: {summary['due_today']}")
        print(f"Due in 1 day: {summary['due_in_1_day']}")
        print(f"Due in 3 days: {summary['due_in_3_days']}")
        print(f"Due in a week: {summary['due_in_a_week']}")
        print(f"Due in 2 weeks: {summary['due_in_2_weeks']}")
        print(f"Due in a month: {summary['due_in_a_month']}")
        print(f"Due later: {summary['due_later']}")
        
        # Should have tasks in multiple categories based on our test data
        self.assertGreater(summary['overdue'], 0, "Should have overdue tasks")
        self.assertGreater(summary['due_today'], 0, "Should have tasks due today")
        self.assertGreater(summary['due_in_1_day'], 0, "Should have tasks due tomorrow")
        
        print("✅ Deadline categorization working correctly")
    
    def test_view_deadlines_task_details(self):
        """Test that task details are properly included"""
        print("\n--- Testing task details inclusion ---")
        
        response = self.app.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        age_categories = data['pending_tasks_by_age']
        
        # Check that tasks have all required fields
        for category_name, tasks in age_categories.items():
            for task in tasks:
                # Required fields
                required_fields = [
                    'task_id', 'task_name', 'task_status', 'priority_level',
                    'assigned_to', 'proj_name', 'proj_id', 'end_date',
                    'days_until_due', 'is_recurring'
                ]
                
                for field in required_fields:
                    self.assertIn(field, task, f"Task in {category_name} should have {field}")
                
                # Check data types
                self.assertIsInstance(task['task_id'], str, "task_id should be string")
                self.assertIsInstance(task['task_name'], str, "task_name should be string")
                self.assertIsInstance(task['assigned_to'], list, "assigned_to should be list")
                self.assertIsInstance(task['days_until_due'], int, "days_until_due should be integer")
                self.assertIsInstance(task['is_recurring'], bool, "is_recurring should be boolean")
                
                # Check assigned_to structure
                for assignee in task['assigned_to']:
                    self.assertIn('id', assignee, "Assignee should have id")
                    self.assertIn('name', assignee, "Assignee should have name")
                    self.assertIn('role', assignee, "Assignee should have role")
        
        print("✅ Task details properly included")
    
    def test_view_deadlines_manager_authorization(self):
        """Test that only managers can access this endpoint"""
        print("\n--- Testing manager authorization ---")
        
        # Test with staff member (should fail)
        response = self.app.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_staff_1_id}')
        self.assertEqual(response.status_code, 403)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Unauthorized', data['error'])
        
        # Test with manager (should succeed)
        response = self.app.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        self.assertEqual(response.status_code, 200)
        
        print("✅ Manager authorization working correctly")
    
    def test_view_deadlines_invalid_manager(self):
        """Test behavior with invalid manager ID"""
        print("\n--- Testing invalid manager ID ---")
        
        invalid_manager_id = "nonexistent_manager_12345"
        response = self.app.get(f'/api/dashboard/manager/pending-tasks-by-age/{invalid_manager_id}')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('User not found', data['error'])
        
        print("✅ Invalid manager ID handled correctly")
    
    def test_view_deadlines_no_division(self):
        """Test behavior when manager has no division"""
        print("\n--- Testing manager with no division ---")
        
        # Create a manager without division
        manager_no_division_id = "test_manager_no_division_999"
        user_data = {
            'id': manager_no_division_id,
            'name': 'Test Manager No Division',
            'email': 'testmanager.nodeadlines@example.com',
            'role_name': 'Manager',
            'role_num': 2,
            'division_name': None  # No division
        }
        
        try:
            user_ref = self.db.collection('Users').document(manager_no_division_id)
            user_ref.set(user_data)
            
            response = self.app.get(f'/api/dashboard/manager/pending-tasks-by-age/{manager_no_division_id}')
            
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIn('Division not found', data['error'])
            
            print("✅ Manager with no division handled correctly")
            
        finally:
            # Clean up
            try:
                self.db.collection('Users').document(manager_no_division_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete test user: {e}")
    
    def test_view_deadlines_no_staff(self):
        """Test behavior when manager has no staff members"""
        print("\n--- Testing manager with no staff ---")
        
        # Create a manager in a different division with no staff
        manager_no_staff_id = "test_manager_no_staff_888"
        user_data = {
            'id': manager_no_staff_id,
            'name': 'Test Manager No Staff',
            'email': 'testmanager.nostaff@example.com',
            'role_name': 'Manager',
            'role_num': 2,
            'division_name': 'Empty Division'  # Different division
        }
        
        try:
            user_ref = self.db.collection('Users').document(manager_no_staff_id)
            user_ref.set(user_data)
            
            response = self.app.get(f'/api/dashboard/manager/pending-tasks-by-age/{manager_no_staff_id}')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            # Should return empty results
            self.assertIn('pending_tasks_by_age', data)
            self.assertIn('summary', data)
            
            # All categories should be empty
            summary = data['summary']
            total_tasks = sum(summary.values())
            self.assertEqual(total_tasks, 0, "Should have no tasks for manager with no staff")
            
            print("✅ Manager with no staff handled correctly")
            
        finally:
            # Clean up
            try:
                self.db.collection('Users').document(manager_no_staff_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete test user: {e}")
    
    def test_view_deadlines_multiple_assignees(self):
        """Test handling of tasks with multiple assignees"""
        print("\n--- Testing tasks with multiple assignees ---")
        
        response = self.app.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        age_categories = data['pending_tasks_by_age']
        
        # Find tasks with multiple assignees
        multi_assignee_tasks = []
        for category_name, tasks in age_categories.items():
            for task in tasks:
                if len(task['assigned_to']) > 1:
                    multi_assignee_tasks.append(task)
        
        # Should have at least one task with multiple assignees (our test data has one)
        self.assertGreater(len(multi_assignee_tasks), 0, "Should have tasks with multiple assignees")
        
        # Check that multiple assignees are properly handled
        for task in multi_assignee_tasks:
            assignees = task['assigned_to']
            self.assertGreater(len(assignees), 1, "Task should have multiple assignees")
            
            # Each assignee should have proper structure
            for assignee in assignees:
                self.assertIn('id', assignee)
                self.assertIn('name', assignee)
                self.assertIn('role', assignee)
        
        print(f"✅ Found {len(multi_assignee_tasks)} tasks with multiple assignees")
    
    def test_view_deadlines_includes_all_statuses(self):
        """Test that tasks of all statuses are included (including completed)"""
        print("\n--- Testing inclusion of tasks with all statuses ---")
        
        response = self.app.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        age_categories = data['pending_tasks_by_age']
        
        # Check that tasks with various statuses are included
        statuses_found = set()
        for category_name, tasks in age_categories.items():
            for task in tasks:
                statuses_found.add(task['task_status'])
        
        print(f"Statuses found: {sorted(statuses_found)}")
        
        # Should include various statuses including completed tasks
        # (Managers need to see completed tasks to track completion patterns)
        expected_statuses = ['Ongoing', 'Unassigned', 'Under Review', 'Completed']
        
        for status in expected_statuses:
            self.assertIn(status, statuses_found, f"Should include {status} tasks")
        
        print("✅ Tasks with all statuses properly included")
    
    def test_view_deadlines_sorting(self):
        """Test that tasks are sorted by due date within each category"""
        print("\n--- Testing task sorting by due date ---")
        
        response = self.app.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        age_categories = data['pending_tasks_by_age']
        
        # Check sorting within each category
        for category_name, tasks in age_categories.items():
            if len(tasks) > 1:
                # Tasks should be sorted by days_until_due (ascending)
                days_until_due = [task['days_until_due'] for task in tasks]
                sorted_days = sorted(days_until_due)
                
                self.assertEqual(days_until_due, sorted_days, 
                               f"Tasks in {category_name} should be sorted by due date")
        
        print("✅ Tasks properly sorted by due date within categories")
    
    def test_view_deadlines_edge_cases(self):
        """Test edge cases for deadline handling"""
        print("\n--- Testing deadline edge cases ---")
        
        response = self.app.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        age_categories = data['pending_tasks_by_age']
        
        # Check edge case values
        for category_name, tasks in age_categories.items():
            for task in tasks:
                days_until_due = task['days_until_due']
                
                # Days until due should be reasonable
                self.assertIsInstance(days_until_due, int, "days_until_due should be integer")
                
                # Check that categorization is correct
                if category_name == 'overdue':
                    self.assertLess(days_until_due, 0, "Overdue tasks should have negative days")
                elif category_name == 'due_today':
                    self.assertEqual(days_until_due, 0, "Due today tasks should have 0 days")
                elif category_name == 'due_in_1_day':
                    self.assertEqual(days_until_due, 1, "Due in 1 day tasks should have 1 day")
                elif category_name == 'due_in_3_days':
                    self.assertIn(days_until_due, [2, 3], "Due in 3 days should be 2-3 days")
                elif category_name == 'due_in_a_week':
                    self.assertIn(days_until_due, range(4, 8), "Due in a week should be 4-7 days")
                elif category_name == 'due_in_2_weeks':
                    self.assertIn(days_until_due, range(8, 15), "Due in 2 weeks should be 8-14 days")
                elif category_name == 'due_in_a_month':
                    self.assertIn(days_until_due, range(15, 31), "Due in a month should be 15-30 days")
                elif category_name == 'due_later':
                    self.assertGreater(days_until_due, 30, "Due later should be > 30 days")
        
        print("✅ Deadline edge cases handled correctly")


if __name__ == '__main__':
    print("=" * 80)
    print("SCRUM-18: VIEW DEADLINES [MANAGER] - INTEGRATION TESTING")
    print("=" * 80)
    print("Testing real API endpoints with real database")
    print("=" * 80)
    
    # Run the tests
    unittest.main(verbosity=2)
