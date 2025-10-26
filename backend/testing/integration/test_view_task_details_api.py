#!/usr/bin/env python3
"""
REAL Integration Tests - View My Task Details [Staff]
Tests staff's ability to view detailed task information via API with REAL database integration.
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


class TestViewTaskDetailsAPI(unittest.TestCase):
    """REAL Integration tests for viewing task details with real database"""
    
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
    
    def setup_test_project(self):
        """Create real test project in the database"""
        future_start = datetime.now() + timedelta(days=1)
        future_end = datetime.now() + timedelta(days=30)
        
        project_data = {
            'proj_name': f'Test Project {self.timestamp}',
            'proj_desc': 'Test project for task details viewing',
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
        """Create real test tasks in the database"""
        future_start = datetime.now() + timedelta(days=1)
        future_end = datetime.now() + timedelta(days=30)
        
        # Task 1: Assigned to staff1 (In Progress)
        task1_data = {
            'task_name': f'Task 1 - Staff1 {self.timestamp}',
            'task_desc': 'Task assigned to staff 1 for details viewing',
            'start_date': future_start,
            'end_date': future_end,
            'task_status': 'In Progress',
            'priority_level': 3,
            'proj_ID': self.test_project_id,
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff1_id],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
            'is_deleted': False,
            'attachments': [
                {
                    'name': 'test_document.pdf',
                    'downloadURL': 'https://example.com/test_document.pdf',
                    'size': 1024,
                    'type': 'application/pdf'
                }
            ],
            'subtasks': [
                {
                    'name': 'Subtask 1',
                    'status': 'Completed',
                    'description': 'First subtask'
                },
                {
                    'name': 'Subtask 2',
                    'status': 'In Progress',
                    'description': 'Second subtask'
                }
            ]
        }
        
        task1_ref = self.db.collection('Tasks').add(task1_data)
        self.test_task1_id = task1_ref[1].id
        self.test_task_ids.append(self.test_task1_id)
        
        # Task 2: Assigned to staff2 (Completed)
        task2_data = {
            'task_name': f'Task 2 - Staff2 {self.timestamp}',
            'task_desc': 'Completed task assigned to staff 2',
            'start_date': future_start,
            'end_date': future_end,
            'task_status': 'Completed',
            'priority_level': 2,
            'proj_ID': self.test_project_id,
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff2_id],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
            'is_deleted': False,
            'attachments': [],
            'subtasks': []
        }
        
        task2_ref = self.db.collection('Tasks').add(task2_data)
        self.test_task2_id = task2_ref[1].id
        self.test_task_ids.append(self.test_task2_id)
        
        # Task 3: Assigned to both staff1 and staff2
        task3_data = {
            'task_name': f'Task 3 - Both Staff {self.timestamp}',
            'task_desc': 'Task assigned to both staff members',
            'start_date': future_start,
            'end_date': future_end,
            'task_status': 'Under Review',
            'priority_level': 1,
            'proj_ID': self.test_project_id,
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff1_id, self.test_staff2_id],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
            'is_deleted': False,
            'attachments': [
                {
                    'name': 'shared_document.docx',
                    'downloadURL': 'https://example.com/shared_document.docx',
                    'size': 2048,
                    'type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                }
            ],
            'subtasks': [
                {
                    'name': 'Review subtask',
                    'status': 'In Progress',
                    'description': 'Review work'
                }
            ]
        }
        
        task3_ref = self.db.collection('Tasks').add(task3_data)
        self.test_task3_id = task3_ref[1].id
        self.test_task_ids.append(self.test_task3_id)
        
        # Task 4: Owned by staff1 (not assigned to them)
        task4_data = {
            'task_name': f'Task 4 - Owned by Staff1 {self.timestamp}',
            'task_desc': 'Task owned by staff 1',
            'start_date': future_start,
            'end_date': future_end,
            'task_status': 'Not Started',
            'priority_level': 4,
            'proj_ID': self.test_project_id,
            'owner': self.test_staff1_id,
            'assigned_to': [self.test_staff2_id],  # Assigned to staff2, owned by staff1
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
            'is_deleted': False,
            'attachments': [],
            'subtasks': []
        }
        
        task4_ref = self.db.collection('Tasks').add(task4_data)
        self.test_task4_id = task4_ref[1].id
        self.test_task_ids.append(self.test_task4_id)
        
        # Task 5: Deleted task (should not be accessible)
        task5_data = {
            'task_name': f'Task 5 - Deleted {self.timestamp}',
            'task_desc': 'Deleted task',
            'start_date': future_start,
            'end_date': future_end,
            'task_status': 'In Progress',
            'priority_level': 3,
            'proj_ID': self.test_project_id,
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff1_id],
            'createdAt': datetime.now(),
            'updatedAt': datetime.now(),
            'is_deleted': True  # This task is deleted
        }
        
        task5_ref = self.db.collection('Tasks').add(task5_data)
        self.test_task5_id = task5_ref[1].id
        self.test_task_ids.append(self.test_task5_id)
    
    def test_view_task_details_staff1_assigned_task(self):
        """Test staff1 viewing details of task assigned to them with REAL database"""
        response = self.client.get(f'/api/tasks/{self.test_task1_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Verify task data structure
        self.assertIn('id', response_data)
        self.assertIn('task_name', response_data)
        self.assertIn('task_desc', response_data)
        self.assertIn('task_status', response_data)
        self.assertIn('priority_level', response_data)
        self.assertIn('proj_ID', response_data)
        self.assertIn('owner', response_data)
        self.assertIn('assigned_to', response_data)
        self.assertIn('start_date', response_data)
        self.assertIn('end_date', response_data)
        self.assertIn('attachments', response_data)
        self.assertIn('subtasks', response_data)
        
        # Verify specific task data
        self.assertEqual(response_data['task_name'], f'Task 1 - Staff1 {self.timestamp}')
        self.assertEqual(response_data['task_status'], 'In Progress')
        self.assertEqual(response_data['priority_level'], 3)
        self.assertEqual(response_data['proj_ID'], self.test_project_id)
        self.assertEqual(response_data['owner'], self.test_manager_id)
        self.assertIn(self.test_staff1_id, response_data['assigned_to'])
        
        # Verify attachments
        self.assertIsInstance(response_data['attachments'], list)
        self.assertEqual(len(response_data['attachments']), 1)
        attachment = response_data['attachments'][0]
        self.assertEqual(attachment['name'], 'test_document.pdf')
        self.assertEqual(attachment['type'], 'application/pdf')
        
        # Verify subtasks
        self.assertIsInstance(response_data['subtasks'], list)
        self.assertEqual(len(response_data['subtasks']), 2)
        subtask_names = [subtask['name'] for subtask in response_data['subtasks']]
        self.assertIn('Subtask 1', subtask_names)
        self.assertIn('Subtask 2', subtask_names)
    
    def test_view_task_details_staff2_assigned_task(self):
        """Test staff2 viewing details of task assigned to them with REAL database"""
        response = self.client.get(f'/api/tasks/{self.test_task2_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Verify specific task data
        self.assertEqual(response_data['task_name'], f'Task 2 - Staff2 {self.timestamp}')
        self.assertEqual(response_data['task_status'], 'Completed')
        self.assertEqual(response_data['priority_level'], 2)
        self.assertIn(self.test_staff2_id, response_data['assigned_to'])
        
        # Verify no attachments
        self.assertEqual(len(response_data['attachments']), 0)
        
        # Verify no subtasks
        self.assertEqual(len(response_data['subtasks']), 0)
    
    def test_view_task_details_shared_task(self):
        """Test viewing details of task assigned to multiple staff with REAL database"""
        response = self.client.get(f'/api/tasks/{self.test_task3_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Verify specific task data
        self.assertEqual(response_data['task_name'], f'Task 3 - Both Staff {self.timestamp}')
        self.assertEqual(response_data['task_status'], 'Under Review')
        self.assertEqual(response_data['priority_level'], 1)
        
        # Verify multiple assignees
        self.assertIn(self.test_staff1_id, response_data['assigned_to'])
        self.assertIn(self.test_staff2_id, response_data['assigned_to'])
        self.assertEqual(len(response_data['assigned_to']), 2)
        
        # Verify attachments
        self.assertEqual(len(response_data['attachments']), 1)
        attachment = response_data['attachments'][0]
        self.assertEqual(attachment['name'], 'shared_document.docx')
        
        # Verify subtasks
        self.assertEqual(len(response_data['subtasks']), 1)
        subtask = response_data['subtasks'][0]
        self.assertEqual(subtask['name'], 'Review subtask')
        self.assertEqual(subtask['status'], 'In Progress')
    
    def test_view_task_details_owned_task(self):
        """Test viewing details of task owned by staff1 with REAL database"""
        response = self.client.get(f'/api/tasks/{self.test_task4_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Verify specific task data
        self.assertEqual(response_data['task_name'], f'Task 4 - Owned by Staff1 {self.timestamp}')
        self.assertEqual(response_data['task_status'], 'Not Started')
        self.assertEqual(response_data['priority_level'], 4)
        self.assertEqual(response_data['owner'], self.test_staff1_id)
        self.assertIn(self.test_staff2_id, response_data['assigned_to'])
    
    def test_view_task_details_nonexistent_task(self):
        """Test viewing details of nonexistent task with REAL database"""
        fake_task_id = 'nonexistent_task_id'
        
        response = self.client.get(f'/api/tasks/{fake_task_id}')
        
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['error'], 'Task not found')
    
    def test_view_task_details_deleted_task(self):
        """Test viewing details of deleted task with REAL database"""
        response = self.client.get(f'/api/tasks/{self.test_task5_id}')
        
        # The API should still return the task details even if it's deleted
        # (deletion is handled by filtering in list views, not individual task views)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Verify it's the deleted task
        self.assertEqual(response_data['task_name'], f'Task 5 - Deleted {self.timestamp}')
        self.assertTrue(response_data.get('is_deleted', False))
    
    def test_view_task_details_data_types(self):
        """Test that returned task data has correct data types with REAL database"""
        response = self.client.get(f'/api/tasks/{self.test_task1_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Verify data types
        self.assertIsInstance(response_data['id'], str)
        self.assertIsInstance(response_data['task_name'], str)
        self.assertIsInstance(response_data['task_desc'], str)
        self.assertIsInstance(response_data['task_status'], str)
        self.assertIsInstance(response_data['priority_level'], int)
        self.assertIsInstance(response_data['assigned_to'], list)
        self.assertIsInstance(response_data['attachments'], list)
        self.assertIsInstance(response_data['subtasks'], list)
        
        # Verify date formats (should be ISO strings)
        self.assertIsInstance(response_data['start_date'], str)
        self.assertIsInstance(response_data['end_date'], str)
        self.assertIsInstance(response_data['createdAt'], str)
        self.assertIsInstance(response_data['updatedAt'], str)
    
    def test_view_task_details_timestamp_conversion(self):
        """Test that timestamps are properly converted to ISO format with REAL database"""
        response = self.client.get(f'/api/tasks/{self.test_task1_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Verify timestamp formats
        start_date = response_data['start_date']
        end_date = response_data['end_date']
        created_at = response_data['createdAt']
        updated_at = response_data['updatedAt']
        
        # Should be ISO format strings
        self.assertRegex(start_date, r'\d{4}-\d{2}-\d{2}')
        self.assertRegex(end_date, r'\d{4}-\d{2}-\d{2}')
        self.assertRegex(created_at, r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
        self.assertRegex(updated_at, r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
    
    def test_view_task_details_attachment_structure(self):
        """Test that attachment data has proper structure with REAL database"""
        response = self.client.get(f'/api/tasks/{self.test_task1_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Verify attachment structure
        attachments = response_data['attachments']
        self.assertIsInstance(attachments, list)
        self.assertEqual(len(attachments), 1)
        
        attachment = attachments[0]
        self.assertIn('name', attachment)
        self.assertIn('downloadURL', attachment)
        self.assertIn('size', attachment)
        self.assertIn('type', attachment)
        
        self.assertEqual(attachment['name'], 'test_document.pdf')
        self.assertEqual(attachment['type'], 'application/pdf')
        self.assertEqual(attachment['size'], 1024)
    
    def test_view_task_details_subtask_structure(self):
        """Test that subtask data has proper structure with REAL database"""
        response = self.client.get(f'/api/tasks/{self.test_task1_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Verify subtask structure
        subtasks = response_data['subtasks']
        self.assertIsInstance(subtasks, list)
        self.assertEqual(len(subtasks), 2)
        
        # Check first subtask
        subtask1 = subtasks[0]
        self.assertIn('name', subtask1)
        self.assertIn('status', subtask1)
        self.assertIn('description', subtask1)
        
        self.assertEqual(subtask1['name'], 'Subtask 1')
        self.assertEqual(subtask1['status'], 'Completed')
        self.assertEqual(subtask1['description'], 'First subtask')
        
        # Check second subtask
        subtask2 = subtasks[1]
        self.assertEqual(subtask2['name'], 'Subtask 2')
        self.assertEqual(subtask2['status'], 'In Progress')
        self.assertEqual(subtask2['description'], 'Second subtask')
    
    def test_view_task_details_error_handling(self):
        """Test error handling for invalid task ID format with REAL database"""
        # Test with invalid task ID format
        invalid_task_id = 'invalid_task_id_with_special_chars!@#'
        
        response = self.client.get(f'/api/tasks/{invalid_task_id}')
        
        # Should return 404 for invalid task ID
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['error'], 'Task not found')
    
    def test_view_task_details_manager_access(self):
        """Test manager viewing task details with REAL database"""
        response = self.client.get(f'/api/tasks/{self.test_task1_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Manager should be able to view any task details
        self.assertEqual(response_data['task_name'], f'Task 1 - Staff1 {self.timestamp}')
        self.assertEqual(response_data['owner'], self.test_manager_id)
    
    def test_view_task_details_cross_user_access(self):
        """Test that staff can view task details even if not assigned to them with REAL database"""
        # Staff1 viewing task assigned to staff2
        response = self.client.get(f'/api/tasks/{self.test_task2_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Should be able to view task details
        self.assertEqual(response_data['task_name'], f'Task 2 - Staff2 {self.timestamp}')
        self.assertIn(self.test_staff2_id, response_data['assigned_to'])
    
    def test_view_task_details_comprehensive_data_validation(self):
        """Test comprehensive data validation for task details with REAL database"""
        response = self.client.get(f'/api/tasks/{self.test_task3_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Verify all required fields are present
        required_fields = [
            'id', 'task_name', 'task_desc', 'task_status', 'priority_level',
            'proj_ID', 'owner', 'assigned_to', 'start_date', 'end_date',
            'createdAt', 'updatedAt', 'attachments', 'subtasks'
        ]
        
        for field in required_fields:
            self.assertIn(field, response_data, f"Missing required field: {field}")
        
        # Verify field values are not None or empty strings
        self.assertIsNotNone(response_data['task_name'])
        self.assertIsNotNone(response_data['task_desc'])
        self.assertIsNotNone(response_data['task_status'])
        self.assertIsNotNone(response_data['priority_level'])
        self.assertIsNotNone(response_data['proj_ID'])
        self.assertIsNotNone(response_data['owner'])
        self.assertIsNotNone(response_data['assigned_to'])
        
        # Verify arrays are not None
        self.assertIsNotNone(response_data['attachments'])
        self.assertIsNotNone(response_data['subtasks'])


if __name__ == '__main__':
    print("=" * 80)
    print("REAL INTEGRATION TESTING - VIEW MY TASK DETAILS [STAFF]")
    print("=" * 80)
    print("Testing staff's ability to view detailed task information with REAL database integration")
    print("Tests Flask app + business logic + real database")
    print("=" * 80)
    
    # Run with verbose output
    unittest.main(verbosity=2)
