#!/usr/bin/env python3
"""
REAL Integration tests for viewing deleted tasks functionality.
Include proper JSON payloads for delete operations.
"""

import unittest
import sys
import os
import json
from datetime import datetime, timedelta
import pytz

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Firebase credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/ean/Documents/SMU Y3/SPM/G6T2/backend/service-account.json'

from app import create_app
from firebase_utils import get_firestore_client


class TestViewDeletedTasksIntegration(unittest.TestCase):
    """REAL Integration tests for viewing deleted tasks functionality"""
    
    def setUp(self):
        """Set up test client with REAL database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Use REAL Firestore client
        self.db = get_firestore_client()
        
        # Track test data for cleanup
        self.test_task_ids = []
        self.test_project_ids = []
        self.test_user_ids = []
        
        # Set up real test data
        self.setup_test_users()
        self.setup_test_project()
        self.setup_test_tasks()
    
    def tearDown(self):
        """Clean up REAL test data from database"""
        for task_id in self.test_task_ids:
            try:
                self.db.collection('Tasks').document(task_id).delete()
            except:
                pass
        
        for project_id in self.test_project_ids:
            try:
                self.db.collection('Projects').document(project_id).delete()
            except:
                pass
        
        for user_id in self.test_user_ids:
            try:
                self.db.collection('Users').document(user_id).delete()
            except:
                pass
    
    def setup_test_users(self):
        """Create REAL test users"""
        users = [
            {"id": "view_task_owner_123", "name": "View Task Owner", "email": "owner@test.com", "role_name": "Staff"},
            {"id": "view_task_user_456", "name": "View Task User", "email": "user@test.com", "role_name": "Staff"},
            {"id": "view_unauthorized_789", "name": "Unauthorized User", "email": "unauthorized@test.com", "role_name": "Staff"}
        ]
        
        for user in users:
            user_id = user.pop("id")
            user["created_at"] = datetime.now()
            self.db.collection('Users').document(user_id).set(user)
            self.test_user_ids.append(user_id)
    
    def setup_test_project(self):
        """Create REAL test project"""
        future_start = datetime.now() + timedelta(days=30)
        future_end = datetime.now() + timedelta(days=365)
        
        project_data = {
            "proj_name": "View Deleted Tasks Test Project",
            "description": "Test project for viewing deleted tasks",
            "start_date": future_start,
            "end_date": future_end,
            "owner": "view_task_owner_123",
            "collaborators": ["view_task_owner_123", "view_task_user_456"],
            "created_at": datetime.now()
        }
        doc_ref = self.db.collection('Projects').add(project_data)[1]
        self.test_project_ids.append(doc_ref.id)
        return doc_ref.id
    
    def setup_test_tasks(self):
        """Create REAL test tasks for view testing"""
        future_start = datetime.now() + timedelta(days=30)
        future_end = datetime.now() + timedelta(days=365)
        
        tasks_data = [
            {
                "task_name": "User 123 Deleted Task",
                "task_desc": "Task deleted by user 123",
                "owner": "view_task_owner_123",
                "assigned_to": ["view_task_owner_123"],
                "task_status": "active",
                "priority_level": 5,
                "start_date": future_start,
                "end_date": future_end,
                "is_deleted": False,
                "createdAt": datetime.now() - timedelta(days=5)
            },
            {
                "task_name": "User 456 Deleted Task",
                "task_desc": "Task deleted by user 456",
                "owner": "view_task_user_456",
                "assigned_to": ["view_task_user_456"],
                "task_status": "active",
                "priority_level": 3,
                "start_date": future_start,
                "end_date": future_end,
                "is_deleted": False,
                "createdAt": datetime.now() - timedelta(days=3)
            },
            {
                "task_name": "Active Task (Should Not Appear)",
                "task_desc": "This should not appear in deleted list",
                "owner": "view_task_owner_123",
                "assigned_to": ["view_task_owner_123"],
                "task_status": "active",
                "priority_level": 4,
                "start_date": future_start,
                "end_date": future_end,
                "is_deleted": False,
                "createdAt": datetime.now() - timedelta(days=1)
            }
        ]
        
        for task_data in tasks_data:
            doc_ref = self.db.collection('Tasks').add(task_data)[1]
            self.test_task_ids.append(doc_ref.id)

    def test_view_deleted_tasks_complete_integration_real(self):
        """Test complete Delete → View integration workflow"""
        # Step 1: Delete some tasks (creates test data)
        task_id_1 = self.test_task_ids[0]
        task_id_2 = self.test_task_ids[1]
        
        # Delete first task with proper JSON payload
        delete_payload_123 = {"userId": "view_task_owner_123"}
        delete_response_1 = self.client.put(f'/api/tasks/{task_id_1}/delete',
                                          data=json.dumps(delete_payload_123),
                                          content_type='application/json')
        self.assertEqual(delete_response_1.status_code, 200)
        
        # Delete second task with proper JSON payload  
        delete_payload_456 = {"userId": "view_task_user_456"}
        delete_response_2 = self.client.put(f'/api/tasks/{task_id_2}/delete',
                                          data=json.dumps(delete_payload_456),
                                          content_type='application/json')
        self.assertEqual(delete_response_2.status_code, 200)
        
        # Step 2: View deleted tasks - tests API → Database → Filtering integration
        response = self.client.get('/api/tasks/deleted?userId=view_task_owner_123')
        
        # Should succeed
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Step 3: Verify integration - deleted items appear, active items don't
        deleted_names = [task['task_name'] for task in response_data]
        self.assertIn('User 123 Deleted Task', deleted_names)
        self.assertNotIn('Active Task (Should Not Appear)', deleted_names)

    def test_user_specific_deleted_tasks_integration_real(self):
        """Test user authorization → data filtering integration"""
        # Delete tasks by different users with proper payloads
        delete_payload_123 = {"userId": "view_task_owner_123"}
        self.client.put(f'/api/tasks/{self.test_task_ids[0]}/delete',
                       data=json.dumps(delete_payload_123),
                       content_type='application/json')  # Owned by user 123
        
        delete_payload_456 = {"userId": "view_task_user_456"}
        self.client.put(f'/api/tasks/{self.test_task_ids[1]}/delete',
                       data=json.dumps(delete_payload_456),
                       content_type='application/json')  # Owned by user 456
        
        # User 123 should only see their deleted tasks
        response_123 = self.client.get('/api/tasks/deleted?userId=view_task_owner_123')
        self.assertEqual(response_123.status_code, 200)
        data_123 = json.loads(response_123.data)
        names_123 = [t['task_name'] for t in data_123]
        
        # User 456 should only see their deleted tasks
        response_456 = self.client.get('/api/tasks/deleted?userId=view_task_user_456')
        self.assertEqual(response_456.status_code, 200)
        data_456 = json.loads(response_456.data)
        names_456 = [t['task_name'] for t in data_456]
        
        # Test authorization integration - users see only their own data
        self.assertIn('User 123 Deleted Task', names_123)
        self.assertNotIn('User 456 Deleted Task', names_123)
        
        self.assertIn('User 456 Deleted Task', names_456)
        self.assertNotIn('User 123 Deleted Task', names_456)

    def test_empty_deleted_list_integration_real(self):
        """Test API → Database integration when no deleted items exist"""
        # Don't delete any tasks
        response = self.client.get('/api/tasks/deleted?userId=view_task_owner_123')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Should return empty array
        self.assertEqual(len(response_data), 0)
        self.assertIsInstance(response_data, list)

    def test_delete_then_view_real_time_integration(self):
        """Test real-time integration - view updates immediately after delete"""
        # Initial state - no deleted tasks
        initial_response = self.client.get('/api/tasks/deleted?userId=view_task_owner_123')
        initial_data = json.loads(initial_response.data)
        initial_count = len(initial_data)
        
        # Delete a task with proper JSON payload
        task_id = self.test_task_ids[0]
        delete_payload = {"userId": "view_task_owner_123"}
        delete_response = self.client.put(f'/api/tasks/{task_id}/delete',
                                        data=json.dumps(delete_payload),
                                        content_type='application/json')
        self.assertEqual(delete_response.status_code, 200)
        
        # Immediately check view - should show the deleted item
        after_delete_response = self.client.get('/api/tasks/deleted?userId=view_task_owner_123')
        after_delete_data = json.loads(after_delete_response.data)
        
        # Integration test - count should increase by 1
        self.assertEqual(len(after_delete_data), initial_count + 1)
        
        # Verify the specific item appears
        deleted_names = [t['task_name'] for t in after_delete_data]
        self.assertIn('User 123 Deleted Task', deleted_names)

    def test_cross_component_consistency_integration(self):
        """Test data consistency across Delete API and View API"""
        task_id = self.test_task_ids[0]
        
        # Delete via API with proper JSON payload
        delete_payload = {"userId": "view_task_owner_123"}
        delete_response = self.client.put(f'/api/tasks/{task_id}/delete',
                                        data=json.dumps(delete_payload),
                                        content_type='application/json')
        delete_data = json.loads(delete_response.data)
        
        # View via API
        view_response = self.client.get('/api/tasks/deleted?userId=view_task_owner_123')
        view_data = json.loads(view_response.data)
        
        # Find the deleted task in view response
        deleted_task = None
        for task in view_data:
            if task['task_name'] == 'User 123 Deleted Task':
                deleted_task = task
                break
        
        # Test cross-component integration - data consistency
        self.assertIsNotNone(deleted_task)
        self.assertEqual(deleted_task['task_name'], 'User 123 Deleted Task')

    def test_database_query_filtering_integration(self):
        """Test API → Database query → Filtering logic integration"""
        # Create mixed state: some deleted, some active
        delete_payload = {"userId": "view_task_owner_123"}
        self.client.put(f'/api/tasks/{self.test_task_ids[0]}/delete',
                       data=json.dumps(delete_payload),
                       content_type='application/json')  # Delete first
        # Keep second and third active
        
        # Test filtering integration
        response = self.client.get('/api/tasks/deleted?userId=view_task_owner_123')
        response_data = json.loads(response.data)
        
        # Should not include active tasks
        task_names = [t['task_name'] for t in response_data]
        self.assertNotIn('Active Task (Should Not Appear)', task_names)
        
        # Should include the deleted task
        self.assertIn('User 123 Deleted Task', task_names)

    def test_missing_userid_parameter_error_handling_real(self):
        """Test error handling when userId parameter is missing"""
        response = self.client.get('/api/tasks/deleted')  # No userId parameter
        
        # Should return 400
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['error'], 'userId parameter is required')

    def test_view_deleted_tasks_with_assigned_users_integration(self):
        """Test viewing deleted tasks with different assignment scenarios"""
        task_id = self.test_task_ids[1]  # Multi-assigned task
        
        # Delete the task with proper JSON payload
        delete_payload = {"userId": "view_task_user_456"}
        delete_response = self.client.put(f'/api/tasks/{task_id}/delete',
                                        data=json.dumps(delete_payload),
                                        content_type='application/json')
        self.assertEqual(delete_response.status_code, 200)
        
        # View as owner
        owner_response = self.client.get('/api/tasks/deleted?userId=view_task_user_456')
        owner_data = json.loads(owner_response.data)
        owner_names = [t['task_name'] for t in owner_data]
        
        # Owner should see their deleted task
        self.assertIn('User 456 Deleted Task', owner_names)


if __name__ == '__main__':
    unittest.main(verbosity=2)
