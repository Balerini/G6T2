#!/usr/bin/env python3
"""
REAL Integration tests for task deletion functionality.
Tests your actual delete endpoints with real database operations.
"""

import unittest
import sys
import os
import json
from datetime import datetime
import pytz

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Firebase credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/ean/Documents/SMU Y3/SPM/G6T2/backend/service-account.json'

from app import create_app
from firebase_utils import get_firestore_client


class TestDeleteTaskIntegration(unittest.TestCase):
    """REAL Integration tests for task deletion functionality"""
    
    def setUp(self):
        """Set up test client with REAL database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Use REAL Firestore client
        self.db = get_firestore_client()
        
        # Track test data for cleanup
        self.test_task_ids = []
        self.test_user_ids = []
        
        # Set up real test data
        self.setup_test_users()
        self.setup_test_tasks()
    
    def tearDown(self):
        """Clean up REAL test data from database"""
        # Clean up any remaining tasks (both regular and soft-deleted)
        for task_id in self.test_task_ids:
            try:
                self.db.collection('Tasks').document(task_id).delete()
            except:
                pass
        
        # Clean up test users
        for user_id in self.test_user_ids:
            try:
                self.db.collection('Users').document(user_id).delete()
            except:
                pass
    
    def setup_test_users(self):
        """Create REAL test users"""
        users = [
            {"id": "delete_owner_123", "name": "Delete Owner", "email": "owner@test.com", "role_name": "Staff"},
            {"id": "delete_user_456", "name": "Delete User", "email": "user@test.com", "role_name": "Staff"},
        ]
        
        for user in users:
            user_id = user.pop("id")
            user["created_at"] = datetime.now()
            self.db.collection('Users').document(user_id).set(user)
            self.test_user_ids.append(user_id)
    
    def setup_test_tasks(self):
        """Create REAL test tasks for deletion testing"""
        tasks_data = [
            {
                "task_name": "Task for Hard Delete",
                "task_desc": "This task will be permanently deleted",
                "owner": "delete_owner_123",
                "assigned_to": ["delete_owner_123"],
                "task_status": "active",
                "priority_level": 5,
                "is_deleted": False,
                "createdAt": datetime.now()
            },
            {
                "task_name": "Task for Soft Delete",
                "task_desc": "This task will be soft deleted",
                "owner": "delete_owner_123",
                "assigned_to": ["delete_owner_123"],
                "task_status": "active", 
                "priority_level": 3,
                "is_deleted": False,
                "createdAt": datetime.now()
            }
        ]
        
        for task_data in tasks_data:
            doc_ref = self.db.collection('Tasks').add(task_data)[1]
            self.test_task_ids.append(doc_ref.id)

    def test_hard_delete_task_real(self):
        """Test REAL hard delete using DELETE /api/tasks/{id} endpoint"""
        task_id = self.test_task_ids[0]
        
        # Verify task exists first
        task_doc = self.db.collection('Tasks').document(task_id).get()
        self.assertTrue(task_doc.exists)
        
        # Hard delete via your actual endpoint
        response = self.client.delete(f'/api/tasks/{task_id}')
        
        # Should succeed
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Task deleted successfully')
        
        # Verify task is completely gone from REAL database
        task_doc_after = self.db.collection('Tasks').document(task_id).get()
        self.assertFalse(task_doc_after.exists)

    def test_permanent_delete_task_real(self):
        """Test REAL permanent delete using DELETE /api/tasks/{id}/permanent endpoint"""
        task_id = self.test_task_ids[1]
        
        # First soft delete the task (set is_deleted=True)
        self.db.collection('Tasks').document(task_id).update({
            "is_deleted": True,
            "deleted_at": datetime.now()
        })
        
        # Now permanently delete via your actual endpoint
        response = self.client.delete(f'/api/tasks/{task_id}/permanent')
        
        # Should succeed
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Task permanently deleted')
        
        # Verify task is completely gone from REAL database
        task_doc_after = self.db.collection('Tasks').document(task_id).get()
        self.assertFalse(task_doc_after.exists)

    def test_soft_delete_task_real(self):
        """Test soft delete by manually setting is_deleted=True (simulating soft delete logic)"""
        task_id = self.test_task_ids[0]
        
        # Soft delete the task (this simulates your soft delete business logic)
        self.db.collection('Tasks').document(task_id).update({
            "is_deleted": True,
            "deleted_at": datetime.now()
        })
        
        # Verify task still exists but is marked as deleted
        task_doc = self.db.collection('Tasks').document(task_id).get()
        self.assertTrue(task_doc.exists)
        task_data = task_doc.to_dict()
        self.assertTrue(task_data['is_deleted'])
        self.assertIn('deleted_at', task_data)

    def test_get_deleted_tasks_real(self):
        """Test GET /api/tasks/deleted endpoint with real data"""
        task_id = self.test_task_ids[1]
        
        # First soft delete a task
        self.db.collection('Tasks').document(task_id).update({
            "is_deleted": True,
            "deleted_at": datetime.now()
        })
        
        # Get deleted tasks via your actual endpoint
        response = self.client.get('/api/tasks/deleted?userId=delete_owner_123')
        
        # Should succeed
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Should contain our deleted task
        deleted_task_names = [task['task_name'] for task in response_data]
        self.assertIn('Task for Soft Delete', deleted_task_names)
        
        # Verify the task is marked as deleted
        for task in response_data:
            if task['task_name'] == 'Task for Soft Delete':
                self.assertTrue(task.get('is_deleted', False))

    def test_restore_task_real(self):
        """Test PUT /api/tasks/{id}/restore endpoint with real data"""
        task_id = self.test_task_ids[0]
        
        # First soft delete a task
        self.db.collection('Tasks').document(task_id).update({
            "is_deleted": True,
            "deleted_at": datetime.now()
        })
        
        # Restore the task via your actual endpoint
        response = self.client.put(f'/api/tasks/{task_id}/restore')
        
        # Should succeed
        self.assertEqual(response.status_code, 200)
        
        # Verify task is restored in REAL database
        task_doc = self.db.collection('Tasks').document(task_id).get()
        self.assertTrue(task_doc.exists)
        task_data = task_doc.to_dict()
        self.assertFalse(task_data.get('is_deleted', True))  # Should be False or not present

    def test_delete_nonexistent_task_real(self):
        """Test deleting non-existent task"""
        response = self.client.delete('/api/tasks/nonexistent_task_id')
        
        # Should return 404
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['error'], 'Task not found')

    def test_delete_task_permission_real(self):
        """Test that delete operations work with proper user context"""
        task_id = self.test_task_ids[0]
        
        # Delete task with proper headers (simulating authenticated user)
        response = self.client.delete(f'/api/tasks/{task_id}',
                                    headers={'X-User-Id': 'delete_owner_123'})
        
        # Should succeed
        self.assertEqual(response.status_code, 200)
        
        # Verify task is gone
        task_doc = self.db.collection('Tasks').document(task_id).get()
        self.assertFalse(task_doc.exists)

    def test_restore_nonexistent_task_real(self):
        """Test restoring non-existent task"""
        response = self.client.put('/api/tasks/nonexistent_task_id/restore')
        
        # Should return 404 or appropriate error
        self.assertIn(response.status_code, [404, 400])

    def test_permanent_delete_nonexistent_task_real(self):
        """Test permanent delete of non-existent task"""
        response = self.client.delete('/api/tasks/nonexistent_task_id/permanent')
        
        # Should return appropriate error
        self.assertIn(response.status_code, [404, 500])


if __name__ == '__main__':
    unittest.main(verbosity=2)
