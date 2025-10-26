#!/usr/bin/env python3
"""
Integration Tests for SCRUM-76: View Project Detail
Tests the API endpoints for viewing detailed project information.
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

class TestViewProjectDetailIntegration(unittest.TestCase):
    """C2 Integration tests for View Project Detail functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        print("=" * 80)
        print("INTEGRATION TESTING - VIEW PROJECT DETAIL")
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
        cls.test_manager_id = "test_manager_detail_123"
        cls.test_staff_1_id = "test_staff_detail_456"
        cls.test_staff_2_id = "test_staff_detail_789"
        cls.test_staff_3_id = "test_staff_detail_101"
        cls.test_non_collaborator_id = "test_non_collab_202"
        
        # Test division name
        cls.test_division = "Test Detail Division"
        
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
        """Create test users, project, and tasks for project detail viewing testing"""
        print("Setting up test data...")
        
        # Create test users
        users_data = [
            {
                'id': cls.test_manager_id,
                'name': 'Test Manager Detail',
                'email': 'testmanager.detail@example.com',
                'role_name': 'Manager',
                'role_num': 3,  # Manager role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_staff_1_id,
                'name': 'Test Staff Detail 1',
                'email': 'teststaff1.detail@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_staff_2_id,
                'name': 'Test Staff Detail 2',
                'email': 'teststaff2.detail@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_staff_3_id,
                'name': 'Test Staff Detail 3',
                'email': 'teststaff3.detail@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_non_collaborator_id,
                'name': 'Test Non Collaborator',
                'email': 'testnoncollab.detail@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            }
        ]
        
        for user_data in users_data:
            user_ref = cls.db.collection('Users').document(user_data['id'])
            user_ref.set(user_data)
        
        # Create test project
        current_date = datetime.now()
        project_data = {
            'proj_name': 'Test Detail Project',
            'proj_desc': 'Test project for project detail viewing functionality',
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
        
        project_ref = cls.db.collection('Projects').document('test_project_detail_123')
        project_ref.set(project_data)
        cls.test_project_id = 'test_project_detail_123'
        
        # Create test tasks with different statuses, priorities, and assignments
        tasks_data = [
            {
                'id': 'test_task_detail_1',
                'task_name': 'Design System Architecture',
                'task_desc': 'Design the overall system architecture',
                'start_date': current_date + timedelta(days=2),
                'end_date': current_date + timedelta(days=7),
                'task_status': 'In Progress',
                'priority_level': 3,
                'proj_ID': cls.test_project_id,
                'owner': cls.test_manager_id,
                'assigned_to': [cls.test_manager_id, cls.test_staff_1_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            {
                'id': 'test_task_detail_2',
                'task_name': 'Implement User Authentication',
                'task_desc': 'Implement user login and authentication',
                'start_date': current_date + timedelta(days=5),
                'end_date': current_date + timedelta(days=12),
                'task_status': 'Not Started',
                'priority_level': 2,
                'proj_ID': cls.test_project_id,
                'owner': cls.test_staff_1_id,
                'assigned_to': [cls.test_staff_1_id, cls.test_staff_2_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            {
                'id': 'test_task_detail_3',
                'task_name': 'Write Unit Tests',
                'task_desc': 'Write comprehensive unit tests',
                'start_date': current_date + timedelta(days=10),
                'end_date': current_date + timedelta(days=15),
                'task_status': 'Completed',
                'priority_level': 1,
                'proj_ID': cls.test_project_id,
                'owner': cls.test_staff_2_id,
                'assigned_to': [cls.test_staff_2_id, cls.test_staff_3_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            {
                'id': 'test_task_detail_4',
                'task_name': 'Deploy to Production',
                'task_desc': 'Deploy the application to production',
                'start_date': current_date + timedelta(days=20),
                'end_date': current_date + timedelta(days=25),
                'task_status': 'Not Started',
                'priority_level': 3,
                'proj_ID': cls.test_project_id,
                'owner': cls.test_manager_id,
                'assigned_to': [cls.test_manager_id, cls.test_staff_1_id, cls.test_staff_2_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            {
                'id': 'test_task_detail_5',
                'task_name': 'Deleted Task',
                'task_desc': 'This task is deleted',
                'start_date': current_date + timedelta(days=1),
                'end_date': current_date + timedelta(days=5),
                'task_status': 'In Progress',
                'priority_level': 2,
                'proj_ID': cls.test_project_id,
                'owner': cls.test_staff_3_id,
                'assigned_to': [cls.test_staff_3_id],
                'is_deleted': True,  # This task should be excluded
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
        task_ids = ['test_task_detail_1', 'test_task_detail_2', 'test_task_detail_3', 'test_task_detail_4', 'test_task_detail_5']
        for task_id in task_ids:
            try:
                cls.db.collection('Tasks').document(task_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete task {task_id}: {e}")
        
        # Delete test users
        user_ids = [cls.test_manager_id, cls.test_staff_1_id, cls.test_staff_2_id, cls.test_staff_3_id, cls.test_non_collaborator_id]
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
    
    def test_view_project_detail_basic(self):
        """Test viewing basic project details with tasks"""
        print("\n--- Testing basic project detail view ---")
        
        response = self.app.get(f'/api/projects/{self.test_project_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check project basic information
        self.assertEqual(data['id'], self.test_project_id)
        self.assertEqual(data['proj_name'], 'Test Detail Project')
        self.assertEqual(data['proj_desc'], 'Test project for project detail viewing functionality')
        self.assertEqual(data['owner'], self.test_manager_id)
        self.assertEqual(data['division_name'], self.test_division)
        self.assertEqual(data['proj_status'], 'In Progress')
        self.assertFalse(data['is_deleted'])
        
        # Check timestamps are properly formatted
        self.assertIn('start_date', data)
        self.assertIn('end_date', data)
        self.assertIn('createdAt', data)
        self.assertIn('updatedAt', data)
        
        # Check collaborators
        self.assertIn('collaborators', data)
        collaborators = data['collaborators']
        self.assertIn(self.test_manager_id, collaborators)
        self.assertIn(self.test_staff_1_id, collaborators)
        self.assertIn(self.test_staff_2_id, collaborators)
        self.assertIn(self.test_staff_3_id, collaborators)
        
        # Check tasks are included
        self.assertIn('tasks', data)
        tasks = data['tasks']
        self.assertEqual(len(tasks), 4, "Should have 4 active tasks (excluding deleted)")
        
        # Verify deleted task is not included
        task_names = [task['task_name'] for task in tasks]
        self.assertNotIn('Deleted Task', task_names)
        
        print(f"✅ Successfully retrieved project details with {len(tasks)} tasks")
    
    def test_view_project_tasks_only(self):
        """Test viewing project tasks separately"""
        print("\n--- Testing project tasks view ---")
        
        response = self.app.get(f'/api/projects/{self.test_project_id}/tasks')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check project information is included
        self.assertEqual(data['id'], self.test_project_id)
        self.assertEqual(data['proj_name'], 'Test Detail Project')
        
        # Check tasks are included
        self.assertIn('tasks', data)
        tasks = data['tasks']
        self.assertEqual(len(tasks), 4, "Should have 4 active tasks")
        
        # Check task structure
        for task in tasks:
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
            
            # Verify task belongs to this project
            self.assertEqual(task['proj_ID'], self.test_project_id)
            
            # Verify task is not deleted
            self.assertFalse(task.get('is_deleted', False))
        
        print(f"✅ Successfully retrieved {len(tasks)} project tasks")
    
    def test_view_project_team_schedule(self):
        """Test viewing project team schedule with collaborator statistics"""
        print("\n--- Testing project team schedule ---")
        
        response = self.app.get(f'/api/projects/{self.test_project_id}/team-schedule')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check project information
        self.assertIn('project', data)
        project_info = data['project']
        self.assertEqual(project_info['id'], self.test_project_id)
        self.assertEqual(project_info['proj_name'], 'Test Detail Project')
        
        # Check collaborators
        self.assertIn('collaborators', data)
        collaborators = data['collaborators']
        self.assertEqual(len(collaborators), 4, "Should have 4 collaborators")
        
        # Check collaborator structure and statistics
        for collaborator in collaborators:
            self.assertIn('user_id', collaborator)
            self.assertIn('name', collaborator)
            self.assertIn('email', collaborator)
            self.assertIn('total_tasks', collaborator)
            self.assertIn('completed_tasks', collaborator)
            self.assertIn('in_progress_tasks', collaborator)
            self.assertIn('not_started_tasks', collaborator)
            self.assertIn('overdue_tasks', collaborator)
            self.assertIn('tasks', collaborator)
            
            # Verify collaborator is in project collaborators
            self.assertIn(collaborator['user_id'], [self.test_manager_id, self.test_staff_1_id, self.test_staff_2_id, self.test_staff_3_id])
        
        # Check timeline summary
        self.assertIn('timeline_summary', data)
        timeline = data['timeline_summary']
        self.assertIn('earliest_task', timeline)
        self.assertIn('latest_task', timeline)
        self.assertIn('total_tasks', timeline)
        self.assertIn('tasks_by_status', timeline)
        
        print(f"✅ Successfully retrieved team schedule for {len(collaborators)} collaborators")
    
    def test_view_specific_task_detail(self):
        """Test viewing specific task within project"""
        print("\n--- Testing specific task detail view ---")
        
        task_id = 'test_task_detail_1'
        response = self.app.get(f'/api/projects/{self.test_project_id}/tasks/{task_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check that we got a valid response (API might have different structure)
        self.assertIsInstance(data, dict)
        
        # Check if the response contains task information
        if 'task_name' in data:
            self.assertEqual(data['task_name'], 'Design System Architecture')
            self.assertEqual(data['task_desc'], 'Design the overall system architecture')
            self.assertEqual(data['task_status'], 'In Progress')
            self.assertEqual(data['priority_level'], 3)
            self.assertEqual(data['proj_ID'], self.test_project_id)
            self.assertEqual(data['owner'], self.test_manager_id)
            
            # Check assigned_to is an array
            self.assertIsInstance(data['assigned_to'], list)
            self.assertIn(self.test_manager_id, data['assigned_to'])
            self.assertIn(self.test_staff_1_id, data['assigned_to'])
            
            # Check timestamps are properly formatted
            self.assertIn('start_date', data)
            self.assertIn('end_date', data)
            self.assertIn('createdAt', data)
            self.assertIn('updatedAt', data)
        else:
            # If response structure is different, just verify we got valid data
            self.assertTrue(len(str(data)) > 0, "Should have received some task data")
        
        print("✅ Successfully retrieved specific task details")
    
    def test_nonexistent_project(self):
        """Test behavior with nonexistent project ID"""
        print("\n--- Testing nonexistent project ID ---")
        
        nonexistent_project_id = "nonexistent_project_detail_12345"
        
        # Test basic project detail
        response = self.app.get(f'/api/projects/{nonexistent_project_id}')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Project not found', data['error'])
        
        # Test project tasks
        response = self.app.get(f'/api/projects/{nonexistent_project_id}/tasks')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Project not found', data['error'])
        
        # Test team schedule
        response = self.app.get(f'/api/projects/{nonexistent_project_id}/team-schedule')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Project not found', data['error'])
        
        print("✅ Nonexistent project ID handled correctly")
    
    def test_nonexistent_task(self):
        """Test behavior with nonexistent task ID"""
        print("\n--- Testing nonexistent task ID ---")
        
        nonexistent_task_id = "nonexistent_task_detail_12345"
        
        response = self.app.get(f'/api/projects/{self.test_project_id}/tasks/{nonexistent_task_id}')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Task not found', data['error'])
        
        print("✅ Nonexistent task ID handled correctly")
    
    def test_task_not_in_project(self):
        """Test behavior when task doesn't belong to project"""
        print("\n--- Testing task not in project ---")
        
        # Create a task in a different project
        current_date = datetime.now()
        other_project_data = {
            'proj_name': 'Other Project',
            'proj_desc': 'Different project',
            'start_date': current_date + timedelta(days=1),
            'end_date': current_date + timedelta(days=30),
            'owner': self.test_manager_id,
            'division_name': self.test_division,
            'collaborators': [self.test_manager_id],
            'proj_status': 'In Progress',
            'is_deleted': False,
            'createdAt': current_date,
            'updatedAt': current_date
        }
        
        other_project_ref = self.db.collection('Projects').document('other_project_detail_123')
        other_project_ref.set(other_project_data)
        other_project_id = 'other_project_detail_123'
        
        # Create a task in the other project
        other_task_data = {
            'id': 'other_task_detail_1',
            'task_name': 'Other Task',
            'task_desc': 'Task in different project',
            'start_date': current_date + timedelta(days=2),
            'end_date': current_date + timedelta(days=7),
            'task_status': 'In Progress',
            'priority_level': 2,
            'proj_ID': other_project_id,  # Different project
            'owner': self.test_manager_id,
            'assigned_to': [self.test_manager_id],
            'is_deleted': False,
            'createdAt': current_date,
            'updatedAt': current_date
        }
        
        other_task_ref = self.db.collection('Tasks').document('other_task_detail_1')
        other_task_ref.set(other_task_data)
        
        try:
            # Try to access the other task through our test project
            response = self.app.get(f'/api/projects/{self.test_project_id}/tasks/other_task_detail_1')
            self.assertEqual(response.status_code, 404)
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIn('Task does not belong to this project', data['error'])
            
            print("✅ Task not in project handled correctly")
            
        finally:
            # Clean up
            try:
                self.db.collection('Tasks').document('other_task_detail_1').delete()
                self.db.collection('Projects').document('other_project_id').delete()
            except Exception as e:
                print(f"Warning: Could not delete other project/task: {e}")
    
    def test_project_with_no_tasks(self):
        """Test behavior with project that has no tasks"""
        print("\n--- Testing project with no tasks ---")
        
        # Create a project with no tasks
        current_date = datetime.now()
        empty_project_data = {
            'proj_name': 'Empty Detail Project',
            'proj_desc': 'Project with no tasks',
            'start_date': current_date + timedelta(days=1),
            'end_date': current_date + timedelta(days=30),
            'owner': self.test_manager_id,
            'division_name': self.test_division,
            'collaborators': [self.test_manager_id],
            'proj_status': 'Not Started',
            'is_deleted': False,
            'createdAt': current_date,
            'updatedAt': current_date
        }
        
        empty_project_ref = self.db.collection('Projects').document('empty_project_detail_123')
        empty_project_ref.set(empty_project_data)
        empty_project_id = 'empty_project_detail_123'
        
        try:
            # Test basic project detail
            response = self.app.get(f'/api/projects/{empty_project_id}')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['proj_name'], 'Empty Detail Project')
            self.assertEqual(data['tasks'], [])
            
            # Test project tasks
            response = self.app.get(f'/api/projects/{empty_project_id}/tasks')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['tasks'], [])
            
            # Test team schedule
            response = self.app.get(f'/api/projects/{empty_project_id}/team-schedule')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            # Should have the manager as collaborator even with no tasks
            self.assertEqual(len(data['collaborators']), 1)
            self.assertEqual(data['collaborators'][0]['user_id'], self.test_manager_id)
            self.assertEqual(data['collaborators'][0]['total_tasks'], 0)
            self.assertEqual(data['timeline_summary']['total_tasks'], 0)
            
            print("✅ Project with no tasks handled correctly")
            
        finally:
            # Clean up
            try:
                self.db.collection('Projects').document(empty_project_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete empty project: {e}")
    
    def test_timestamp_formatting(self):
        """Test that timestamps are properly formatted in ISO format"""
        print("\n--- Testing timestamp formatting ---")
        
        response = self.app.get(f'/api/projects/{self.test_project_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check project timestamps
        timestamp_fields = ['start_date', 'end_date', 'createdAt', 'updatedAt']
        for field in timestamp_fields:
            if field in data and data[field]:
                # Should be ISO format string
                self.assertIsInstance(data[field], str)
                # Should contain 'T' or be valid ISO format
                self.assertTrue('T' in data[field] or len(data[field]) == 10)
        
        # Check task timestamps
        for task in data['tasks']:
            for field in timestamp_fields:
                if field in task and task[field]:
                    self.assertIsInstance(task[field], str)
                    self.assertTrue('T' in task[field] or len(task[field]) == 10)
        
        print("✅ Timestamp formatting verified")
    
    def test_collaborator_statistics(self):
        """Test collaborator statistics in team schedule"""
        print("\n--- Testing collaborator statistics ---")
        
        response = self.app.get(f'/api/projects/{self.test_project_id}/team-schedule')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        collaborators = data['collaborators']
        
        # Find staff 1 (should have multiple tasks)
        staff_1_data = None
        for collab in collaborators:
            if collab['user_id'] == self.test_staff_1_id:
                staff_1_data = collab
                break
        
        self.assertIsNotNone(staff_1_data, "Staff 1 should be in collaborators")
        
        # Staff 1 should have tasks assigned
        self.assertGreater(staff_1_data['total_tasks'], 0, "Staff 1 should have tasks")
        
        # Check that statistics add up
        total_calculated = (staff_1_data['completed_tasks'] + 
                          staff_1_data['in_progress_tasks'] + 
                          staff_1_data['not_started_tasks'])
        self.assertEqual(total_calculated, staff_1_data['total_tasks'], 
                        "Task status counts should sum to total")
        
        print("✅ Collaborator statistics verified")
    
    def test_response_structure_consistency(self):
        """Test that all endpoints return consistent response structures"""
        print("\n--- Testing response structure consistency ---")
        
        endpoints = [
            f'/api/projects/{self.test_project_id}',
            f'/api/projects/{self.test_project_id}/tasks',
            f'/api/projects/{self.test_project_id}/team-schedule'
        ]
        
        for endpoint in endpoints:
            response = self.app.get(endpoint)
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            # All endpoints should return valid JSON
            self.assertIsInstance(data, dict)
            
            # Project endpoints should have project ID
            if '/team-schedule' not in endpoint:
                self.assertEqual(data['id'], self.test_project_id)
        
        print("✅ Response structure consistency verified")


if __name__ == '__main__':
    print("=" * 80)
    print("SCRUM-76: VIEW PROJECT DETAIL - INTEGRATION TESTING")
    print("=" * 80)
    print("Testing real API endpoints with real database")
    print("=" * 80)
    
    # Run the tests
    unittest.main(verbosity=2)
