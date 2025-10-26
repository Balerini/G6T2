#!/usr/bin/env python3
"""
Integration Tests for SCRUM-8: View Team's Tasks
Tests the API endpoints for managers to view their team's tasks.
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

class TestViewTeamTasksIntegration(unittest.TestCase):
    """C2 Integration tests for View Team's Tasks functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        print("=" * 80)
        print("INTEGRATION TESTING - VIEW TEAM'S TASKS")
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
        cls.test_manager_id = "test_manager_team_123"
        cls.test_staff_1_id = "test_staff_team_456"
        cls.test_staff_2_id = "test_staff_team_789"
        cls.test_staff_3_id = "test_staff_team_101"
        cls.test_non_manager_id = "test_non_manager_202"
        
        # Test division name
        cls.test_division = "Test Team Division"
        
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
        """Create test users, projects, and tasks for team task viewing testing"""
        print("Setting up test data...")
        
        # Create test users
        users_data = [
            {
                'id': cls.test_manager_id,
                'name': 'Test Manager Team',
                'email': 'testmanager.team@example.com',
                'role_name': 'Manager',
                'role_num': 3,  # Manager role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_staff_1_id,
                'name': 'Test Staff Team 1',
                'email': 'teststaff1.team@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_staff_2_id,
                'name': 'Test Staff Team 2',
                'email': 'teststaff2.team@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_staff_3_id,
                'name': 'Test Staff Team 3',
                'email': 'teststaff3.team@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_non_manager_id,
                'name': 'Test Non Manager',
                'email': 'testnonmanager.team@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role (not manager)
                'division_name': cls.test_division
            }
        ]
        
        for user_data in users_data:
            user_ref = cls.db.collection('Users').document(user_data['id'])
            user_ref.set(user_data)
        
        # Create test project
        current_date = datetime.now()
        project_data = {
            'proj_name': 'Test Team Project',
            'proj_desc': 'Test project for team task viewing',
            'start_date': current_date + timedelta(days=1),
            'end_date': current_date + timedelta(days=30),
            'owner': cls.test_manager_id,
            'division_name': cls.test_division,
            'collaborators': [cls.test_manager_id, cls.test_staff_1_id, cls.test_staff_2_id, cls.test_staff_3_id],
            'proj_status': 'In Progress',
            'is_deleted': False,
            'createdAt': current_date,
            'updatedAt': current_date
        }
        
        project_ref = cls.db.collection('Projects').document('test_project_team_123')
        project_ref.set(project_data)
        cls.test_project_id = 'test_project_team_123'
        
        # Create test tasks with different statuses, priorities, and assignments
        tasks_data = [
            {
                'id': 'test_task_team_1',
                'task_name': 'High Priority Task',
                'task_desc': 'A high priority task for staff 1',
                'start_date': current_date + timedelta(days=2),
                'end_date': current_date + timedelta(days=5),
                'task_status': 'In Progress',
                'priority_level': 9,  # High priority
                'proj_ID': cls.test_project_id,
                'owner': cls.test_staff_1_id,
                'assigned_to': [cls.test_staff_1_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            {
                'id': 'test_task_team_2',
                'task_name': 'Completed Task',
                'task_desc': 'A completed task for staff 2',
                'start_date': current_date + timedelta(days=1),
                'end_date': current_date + timedelta(days=3),
                'task_status': 'Completed',
                'priority_level': 5,  # Medium priority
                'proj_ID': cls.test_project_id,
                'owner': cls.test_staff_2_id,
                'assigned_to': [cls.test_staff_2_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            {
                'id': 'test_task_team_3',
                'task_name': 'Not Started Task',
                'task_desc': 'A not started task for staff 3',
                'start_date': current_date + timedelta(days=5),
                'end_date': current_date + timedelta(days=10),
                'task_status': 'Not Started',
                'priority_level': 2,  # Low priority
                'proj_ID': cls.test_project_id,
                'owner': cls.test_staff_3_id,
                'assigned_to': [cls.test_staff_3_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            {
                'id': 'test_task_team_4',
                'task_name': 'Multi-Assigned Task',
                'task_desc': 'A task assigned to multiple staff members',
                'start_date': current_date + timedelta(days=3),
                'end_date': current_date + timedelta(days=8),
                'task_status': 'In Progress',
                'priority_level': 7,  # High priority
                'proj_ID': cls.test_project_id,
                'owner': cls.test_manager_id,
                'assigned_to': [cls.test_staff_1_id, cls.test_staff_2_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            {
                'id': 'test_task_team_5',
                'task_name': 'Overdue Task',
                'task_desc': 'An overdue task for staff 1',
                'start_date': current_date - timedelta(days=5),
                'end_date': current_date - timedelta(days=2),  # Overdue
                'task_status': 'In Progress',
                'priority_level': 8,  # High priority
                'proj_ID': cls.test_project_id,
                'owner': cls.test_staff_1_id,
                'assigned_to': [cls.test_staff_1_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            {
                'id': 'test_task_team_6',
                'task_name': 'Manager Task',
                'task_desc': 'A task assigned to the manager',
                'start_date': current_date + timedelta(days=1),
                'end_date': current_date + timedelta(days=7),
                'task_status': 'Not Started',
                'priority_level': 6,  # Medium priority
                'proj_ID': cls.test_project_id,
                'owner': cls.test_manager_id,
                'assigned_to': [cls.test_manager_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            }
        ]
        
        for task_data in tasks_data:
            task_ref = cls.db.collection('Tasks').document(task_data['id'])
            task_ref.set(task_data)
        
        print(f"Created {len(users_data)} test users, 1 test project, and {len(tasks_data)} test tasks")
    
    @classmethod
    def cleanup_test_data(cls):
        """Clean up test data"""
        print("Cleaning up test data...")
        
        # Delete test tasks
        task_ids = ['test_task_team_1', 'test_task_team_2', 'test_task_team_3', 'test_task_team_4', 'test_task_team_5', 'test_task_team_6']
        for task_id in task_ids:
            try:
                cls.db.collection('Tasks').document(task_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete task {task_id}: {e}")
        
        # Delete test users
        user_ids = [cls.test_manager_id, cls.test_staff_1_id, cls.test_staff_2_id, cls.test_staff_3_id, cls.test_non_manager_id]
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
    
    def test_view_team_tasks_by_staff(self):
        """Test viewing team tasks grouped by staff member"""
        print("\n--- Testing team tasks by staff ---")
        
        response = self.app.get(f'/api/dashboard/manager/tasks-by-staff/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check response structure
        self.assertIn('tasks_by_staff', data)
        self.assertIn('division_name', data)
        self.assertEqual(data['division_name'], self.test_division)
        
        # Check that we have staff members
        staff_data = data['tasks_by_staff']
        self.assertGreater(len(staff_data), 0, "Should have staff members")
        
        # Check that staff are sorted by task count (descending)
        task_counts = [staff['task_count'] for staff in staff_data]
        self.assertEqual(task_counts, sorted(task_counts, reverse=True), "Staff should be sorted by task count")
        
        # Verify staff members are included
        staff_names = [staff['staff_name'] for staff in staff_data]
        self.assertIn('Test Staff Team 1', staff_names)
        self.assertIn('Test Staff Team 2', staff_names)
        self.assertIn('Test Staff Team 3', staff_names)
        
        # Check task details for each staff member
        for staff in staff_data:
            self.assertIn('staff_id', staff)
            self.assertIn('staff_name', staff)
            self.assertIn('staff_role', staff)
            self.assertIn('role_num', staff)
            self.assertIn('task_count', staff)
            self.assertIn('tasks', staff)
            
            # Check task structure
            for task in staff['tasks']:
                self.assertIn('task_id', task)
                self.assertIn('task_name', task)
                self.assertIn('task_status', task)
                self.assertIn('task_priority', task)
                self.assertIn('proj_name', task)
        
        print(f"✅ Successfully retrieved tasks for {len(staff_data)} staff members")
    
    def test_view_team_tasks_by_status(self):
        """Test viewing team tasks grouped by status"""
        print("\n--- Testing team tasks by status ---")
        
        response = self.app.get(f'/api/dashboard/manager/tasks-by-status/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check response structure
        self.assertIn('tasks_by_status', data)
        self.assertIn('division_name', data)
        self.assertEqual(data['division_name'], self.test_division)
        
        # Check status counts
        status_counts = data['tasks_by_status']
        self.assertIsInstance(status_counts, dict)
        
        # Verify we have the expected statuses
        expected_statuses = ['In Progress', 'Completed', 'Not Started']
        for status in expected_statuses:
            if status in status_counts:
                self.assertGreater(status_counts[status], 0, f"Should have {status} tasks")
        
        print(f"✅ Status breakdown: {status_counts}")
    
    def test_view_team_tasks_by_priority(self):
        """Test viewing team tasks grouped by priority"""
        print("\n--- Testing team tasks by priority ---")
        
        response = self.app.get(f'/api/dashboard/manager/tasks-by-priority/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check response structure
        self.assertIn('tasks_by_priority', data)
        self.assertIn('division_name', data)
        self.assertEqual(data['division_name'], self.test_division)
        
        # Check priority counts
        priority_counts = data['tasks_by_priority']
        self.assertIsInstance(priority_counts, dict)
        
        # Verify we have the expected priority categories (based on actual API response)
        expected_priorities = ['High', 'Medium', 'Low']
        for priority in expected_priorities:
            self.assertIn(priority, priority_counts, f"Should have {priority} priority category")
        
        # Check that we have some high priority tasks (priority >= 8)
        self.assertGreater(priority_counts['High'], 0, "Should have high priority tasks")
        
        print(f"✅ Priority breakdown: {priority_counts}")
    
    def test_view_team_total_tasks(self):
        """Test viewing total number of team tasks"""
        print("\n--- Testing total team tasks count ---")
        
        response = self.app.get(f'/api/dashboard/manager/total-tasks/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check response structure
        self.assertIn('total_tasks', data)
        self.assertIn('division_name', data)
        self.assertEqual(data['division_name'], self.test_division)
        
        # Check that we have tasks
        total_tasks = data['total_tasks']
        self.assertGreater(total_tasks, 0, "Should have tasks")
        self.assertIsInstance(total_tasks, int)
        
        print(f"✅ Total team tasks: {total_tasks}")
    
    def test_view_team_pending_tasks_by_age(self):
        """Test viewing team pending tasks categorized by age"""
        print("\n--- Testing pending tasks by age ---")
        
        response = self.app.get(f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check response structure
        self.assertIn('pending_tasks_by_age', data)
        self.assertIn('division_name', data)
        self.assertEqual(data['division_name'], self.test_division)
        
        # Check age categories
        age_categories = data['pending_tasks_by_age']
        self.assertIsInstance(age_categories, dict)
        
        # Verify we have the expected age categories (based on actual API response)
        expected_categories = ['overdue', 'due_today', 'due_in_1_day', 'due_in_3_days', 'due_in_a_week', 'due_in_2_weeks', 'due_in_a_month', 'due_later']
        for category in expected_categories:
            self.assertIn(category, age_categories, f"Should have {category} category")
        
        # Check that we have some overdue tasks
        overdue_tasks = age_categories['overdue']
        self.assertGreater(len(overdue_tasks), 0, "Should have overdue tasks")
        
        print(f"✅ Pending tasks by age: {len(age_categories['overdue'])} overdue, {len(age_categories['due_today'])} due today")
    
    def test_view_team_tasks_timeline(self):
        """Test viewing team tasks timeline for Gantt chart"""
        print("\n--- Testing team tasks timeline ---")
        
        response = self.app.get(f'/api/dashboard/manager/tasks-timeline/{self.test_manager_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check response structure (based on actual API response)
        self.assertIn('staff', data)
        self.assertIn('division_name', data)
        self.assertEqual(data['division_name'], self.test_division)
        
        # Check timeline data
        staff_data = data['staff']
        self.assertIsInstance(staff_data, list)
        self.assertGreater(len(staff_data), 0, "Should have staff data")
        
        # Check staff structure for timeline
        for staff in staff_data:
            self.assertIn('userid', staff)
            self.assertIn('name', staff)
            self.assertIn('role', staff)
            self.assertIn('task_count', staff)
            self.assertIn('tasks', staff)
            
            # Check task structure for timeline
            for task in staff['tasks']:
                self.assertIn('task_id', task)
                self.assertIn('task_name', task)
                self.assertIn('task_status', task)
                self.assertIn('start_date', task)
                self.assertIn('end_date', task)
        
        print(f"✅ Timeline data: {len(staff_data)} staff members")
    
    def test_manager_authorization(self):
        """Test that only managers can access team task endpoints"""
        print("\n--- Testing manager authorization ---")
        
        # Test with non-manager user (should fail)
        response = self.app.get(f'/api/dashboard/manager/tasks-by-staff/{self.test_non_manager_id}')
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Unauthorized', data['error'])
        
        # Test with manager user (should succeed)
        response = self.app.get(f'/api/dashboard/manager/tasks-by-staff/{self.test_manager_id}')
        self.assertEqual(response.status_code, 200)
        
        print("✅ Manager authorization working correctly")
    
    def test_nonexistent_manager(self):
        """Test behavior with nonexistent manager ID"""
        print("\n--- Testing nonexistent manager ID ---")
        
        nonexistent_manager_id = "nonexistent_manager_12345"
        
        response = self.app.get(f'/api/dashboard/manager/tasks-by-staff/{nonexistent_manager_id}')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('User not found', data['error'])
        
        print("✅ Nonexistent manager ID handled correctly")
    
    def test_manager_without_division(self):
        """Test behavior with manager who has no division"""
        print("\n--- Testing manager without division ---")
        
        # Create a manager without division
        manager_no_division_data = {
            'id': 'test_manager_no_division_123',
            'name': 'Test Manager No Division',
            'email': 'testmanager.nodivision@example.com',
            'role_name': 'Manager',
            'role_num': 3,  # Manager role
            'division_name': None  # No division
        }
        
        manager_ref = self.db.collection('Users').document('test_manager_no_division_123')
        manager_ref.set(manager_no_division_data)
        
        try:
            response = self.app.get(f'/api/dashboard/manager/tasks-by-staff/test_manager_no_division_123')
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIn('Division not found', data['error'])
            
            print("✅ Manager without division handled correctly")
            
        finally:
            # Clean up
            try:
                self.db.collection('Users').document('test_manager_no_division_123').delete()
            except Exception as e:
                print(f"Warning: Could not delete test manager: {e}")
    
    def test_empty_team(self):
        """Test behavior with manager who has no team members"""
        print("\n--- Testing manager with empty team ---")
        
        # Create a manager with a unique division (no other members)
        manager_empty_team_data = {
            'id': 'test_manager_empty_team_123',
            'name': 'Test Manager Empty Team',
            'email': 'testmanager.emptyteam@example.com',
            'role_name': 'Manager',
            'role_num': 3,  # Manager role
            'division_name': 'Empty Team Division'  # Unique division
        }
        
        manager_ref = self.db.collection('Users').document('test_manager_empty_team_123')
        manager_ref.set(manager_empty_team_data)
        
        try:
            response = self.app.get(f'/api/dashboard/manager/tasks-by-staff/test_manager_empty_team_123')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            # Should return only the manager (no other team members)
            staff_data = data['tasks_by_staff']
            self.assertEqual(len(staff_data), 1, "Should have only the manager")
            self.assertEqual(staff_data[0]['staff_id'], 'test_manager_empty_team_123')
            self.assertEqual(staff_data[0]['task_count'], 0, "Manager should have no tasks")
            self.assertEqual(data['division_name'], 'Empty Team Division')
            
            print("✅ Empty team handled correctly")
            
        finally:
            # Clean up
            try:
                self.db.collection('Users').document('test_manager_empty_team_123').delete()
            except Exception as e:
                print(f"Warning: Could not delete test manager: {e}")
    
    def test_task_assignment_validation(self):
        """Test that tasks are properly assigned to team members"""
        print("\n--- Testing task assignment validation ---")
        
        response = self.app.get(f'/api/dashboard/manager/tasks-by-staff/{self.test_manager_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        staff_data = data['tasks_by_staff']
        
        # Find staff 1 data
        staff_1_data = None
        for staff in staff_data:
            if staff['staff_id'] == self.test_staff_1_id:
                staff_1_data = staff
                break
        
        self.assertIsNotNone(staff_1_data, "Staff 1 should be in the team")
        
        # Staff 1 should have multiple tasks (including multi-assigned task)
        self.assertGreater(staff_1_data['task_count'], 1, "Staff 1 should have multiple tasks")
        
        # Check that multi-assigned task appears for both staff members
        multi_assigned_task_found = False
        for staff in staff_data:
            for task in staff['tasks']:
                if task['task_name'] == 'Multi-Assigned Task':
                    multi_assigned_task_found = True
                    break
        
        self.assertTrue(multi_assigned_task_found, "Multi-assigned task should appear in team data")
        
        print("✅ Task assignment validation passed")
    
    def test_response_format_consistency(self):
        """Test that all endpoints return consistent response formats"""
        print("\n--- Testing response format consistency ---")
        
        endpoints = [
            f'/api/dashboard/manager/tasks-by-staff/{self.test_manager_id}',
            f'/api/dashboard/manager/tasks-by-status/{self.test_manager_id}',
            f'/api/dashboard/manager/tasks-by-priority/{self.test_manager_id}',
            f'/api/dashboard/manager/total-tasks/{self.test_manager_id}',
            f'/api/dashboard/manager/pending-tasks-by-age/{self.test_manager_id}',
            f'/api/dashboard/manager/tasks-timeline/{self.test_manager_id}'
        ]
        
        for endpoint in endpoints:
            response = self.app.get(endpoint)
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            # All endpoints should have division_name
            self.assertIn('division_name', data)
            self.assertEqual(data['division_name'], self.test_division)
            
            # All endpoints should return valid JSON
            self.assertIsInstance(data, dict)
        
        print("✅ Response format consistency verified")


if __name__ == '__main__':
    print("=" * 80)
    print("SCRUM-8: VIEW TEAM'S TASKS - INTEGRATION TESTING")
    print("=" * 80)
    print("Testing real API endpoints with real database")
    print("=" * 80)
    
    # Run the tests
    unittest.main(verbosity=2)
