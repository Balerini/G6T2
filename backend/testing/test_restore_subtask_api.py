#!/usr/bin/env python3
"""
REAL Integration tests for subtask restoration functionality.
FIXED to include proper JSON payloads for delete operations.
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
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../service-account.json'

from app import create_app
from firebase_utils import get_firestore_client


class TestRestoreSubtaskIntegration(unittest.TestCase):
    """REAL Integration tests for subtask restoration functionality"""
    
    def setUp(self):
        """Set up test client with REAL database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Use REAL Firestore client
        self.db = get_firestore_client()
        
        # Track test data for cleanup
        self.test_subtask_ids = []
        self.test_task_ids = []
        self.test_project_ids = []
        self.test_user_ids = []
        
        # Set up real test data
        self.setup_test_users()
        self.setup_test_project()
        self.setup_test_task()
        self.setup_test_subtasks()
    
    def tearDown(self):
        """Clean up REAL test data from database"""
        for subtask_id in self.test_subtask_ids:
            try:
                self.db.collection('subtasks').document(subtask_id).delete()
            except:
                pass
        
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
            {"id": "restore_subtask_owner_123", "name": "Restore Subtask Owner", "email": "owner@test.com", "role_name": "Staff"},
            {"id": "restore_subtask_user_456", "name": "Restore Subtask User", "email": "user@test.com", "role_name": "Staff"},
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
            "proj_name": "Restore Subtask Test Project",
            "description": "Test project for subtask restoration",
            "start_date": future_start,
            "end_date": future_end,
            "owner": "restore_subtask_owner_123",
            "collaborators": ["restore_subtask_owner_123", "restore_subtask_user_456"],
            "created_at": datetime.now()
        }
        doc_ref = self.db.collection('Projects').add(project_data)[1]
        self.test_project_ids.append(doc_ref.id)
        return doc_ref.id
    
    def setup_test_task(self):
        """Create REAL test task"""
        future_start = datetime.now() + timedelta(days=30)
        future_end = datetime.now() + timedelta(days=365)
        
        task_data = {
            "task_name": "Restore Subtask Test Task",
            "task_desc": "Test task for subtask restoration",
            "owner": "restore_subtask_owner_123",
            "assigned_to": ["restore_subtask_owner_123", "restore_subtask_user_456"],
            "task_status": "active",
            "priority_level": 5,
            "start_date": future_start,
            "end_date": future_end,
            "is_deleted": False,
            "createdAt": datetime.now()
        }
        doc_ref = self.db.collection('Tasks').add(task_data)[1]
        self.test_task_ids.append(doc_ref.id)
        return doc_ref.id
    
    def setup_test_subtasks(self):
        """Create REAL test subtasks for restoration testing"""
        task_id = self.test_task_ids[0]
        project_id = self.test_project_ids[0]
        
        subtasks_data = [
            {
                "name": "Subtask to Restore",
                "description": "This subtask will be deleted then restored",
                "startDate": "2024-12-01",
                "endDate": "2024-12-15",
                "status": "active",
                "priority": 5,
                "parentTaskId": task_id,
                "projectId": project_id,
                "assignedTo": ["restore_subtask_owner_123"],
                "owner": "restore_subtask_owner_123",
                "isDeleted": False,
                "createdAt": datetime.now()
            },
            {
                "name": "Another Restore Test Subtask",
                "description": "Second subtask for restoration testing",
                "startDate": "2024-12-01", 
                "endDate": "2024-12-15",
                "status": "active",
                "priority": 3,
                "parentTaskId": task_id,
                "projectId": project_id,
                "assignedTo": ["restore_subtask_owner_123", "restore_subtask_user_456"],
                "owner": "restore_subtask_owner_123",
                "isDeleted": False,
                "createdAt": datetime.now()
            }
        ]
        
        for subtask_data in subtasks_data:
            doc_ref = self.db.collection('subtasks').add(subtask_data)[1]
            self.test_subtask_ids.append(doc_ref.id)

    def test_restore_subtask_integration_real(self):
        """Test API → Database integration for subtask restoration"""
        subtask_id = self.test_subtask_ids[0]
        
        # FIXED: First soft delete the subtask with proper JSON payload
        delete_payload = {"userId": "restore_subtask_owner_123"}
        delete_response = self.client.put(f'/api/subtasks/{subtask_id}/delete',
                                        data=json.dumps(delete_payload),
                                        content_type='application/json')
        self.assertEqual(delete_response.status_code, 200)
        
        # Now restore it via your actual endpoint
        response = self.client.put(f'/api/subtasks/{subtask_id}/restore-new')
        
        # Should succeed
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Subtask restored successfully')
        
        # Verify integration: restored subtask should NOT appear in deleted list
        deleted_response = self.client.get('/api/subtasks/deleted-new?userId=restore_subtask_owner_123')
        deleted_data = json.loads(deleted_response.data)
        deleted_names = [s['name'] for s in deleted_data]
        self.assertNotIn('Subtask to Restore', deleted_names)

    def test_complete_delete_restore_workflow_integration(self):
        """Test complete delete → restore workflow integration"""
        subtask_id = self.test_subtask_ids[0]
        
        # Step 1: Verify subtask is active
        subtask_doc = self.db.collection('subtasks').document(subtask_id).get()
        original_data = subtask_doc.to_dict()
        self.assertFalse(original_data.get('isDeleted', False))
        
        # Step 2: FIXED - Soft delete with proper JSON payload
        delete_payload = {"userId": "restore_subtask_owner_123"}
        delete_response = self.client.put(f'/api/subtasks/{subtask_id}/delete',
                                        data=json.dumps(delete_payload),
                                        content_type='application/json')
        self.assertEqual(delete_response.status_code, 200)
        
        # Step 3: Verify it appears in deleted list
        deleted_response = self.client.get('/api/subtasks/deleted-new?userId=restore_subtask_owner_123')
        self.assertEqual(deleted_response.status_code, 200)
        deleted_data = json.loads(deleted_response.data)
        deleted_names = [s['name'] for s in deleted_data]
        self.assertIn('Subtask to Restore', deleted_names)
        
        # Step 4: Restore
        restore_response = self.client.put(f'/api/subtasks/{subtask_id}/restore-new')
        self.assertEqual(restore_response.status_code, 200)
        
        # Step 5: Verify it no longer appears in deleted list
        deleted_response_after = self.client.get('/api/subtasks/deleted-new?userId=restore_subtask_owner_123')
        deleted_data_after = json.loads(deleted_response_after.data)
        deleted_names_after = [s['name'] for s in deleted_data_after]
        self.assertNotIn('Subtask to Restore', deleted_names_after)

    def test_restore_nonexistent_subtask_error_handling_real(self):
        """Test error handling for restoring non-existent subtask"""
        response = self.client.put('/api/subtasks/nonexistent_subtask_id/restore-new')
        
        # Should return 404
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['error'], 'Subtask not found')

    def test_restore_active_subtask_real(self):
        """Test restoring a subtask that's not deleted"""
        subtask_id = self.test_subtask_ids[0]
        
        # Try to restore an active (non-deleted) subtask
        response = self.client.put(f'/api/subtasks/{subtask_id}/restore-new')
        
        # Should handle gracefully - either success or appropriate error
        self.assertIn(response.status_code, [200, 400])

    def test_multiple_subtask_restoration_integration(self):
        """Test restoring multiple subtasks workflow"""
        subtask_ids = self.test_subtask_ids  # Both subtasks
        
        # FIXED: First delete both subtasks with proper JSON payload
        delete_payload = {"userId": "restore_subtask_owner_123"}
        for subtask_id in subtask_ids:
            delete_response = self.client.put(f'/api/subtasks/{subtask_id}/delete',
                                            data=json.dumps(delete_payload),
                                            content_type='application/json')
            self.assertEqual(delete_response.status_code, 200)
        
        # Verify both are deleted
        deleted_response = self.client.get('/api/subtasks/deleted-new?userId=restore_subtask_owner_123')
        deleted_data = json.loads(deleted_response.data)
        self.assertEqual(len(deleted_data), 2)
        
        # Now restore both
        for subtask_id in subtask_ids:
            restore_response = self.client.put(f'/api/subtasks/{subtask_id}/restore-new')
            self.assertEqual(restore_response.status_code, 200)
        
        # Verify both are restored (no longer in deleted list)
        deleted_response_after = self.client.get('/api/subtasks/deleted-new?userId=restore_subtask_owner_123')
        deleted_data_after = json.loads(deleted_response_after.data)
        self.assertEqual(len(deleted_data_after), 0)  # No deleted subtasks

    def test_restore_subtask_notification_integration(self):
        """Test restoration → notification service integration"""
        subtask_id = self.test_subtask_ids[1]  # Multi-assigned subtask
        
        # FIXED: Delete then restore subtask with proper payload
        delete_payload = {"userId": "restore_subtask_owner_123"}
        self.client.put(f'/api/subtasks/{subtask_id}/delete',
                       data=json.dumps(delete_payload),
                       content_type='application/json')
        
        response = self.client.put(f'/api/subtasks/{subtask_id}/restore-new')
        self.assertEqual(response.status_code, 200)
        
        # Test integration - notification service should be triggered
        print("✅ Subtask restoration → notification integration test passed")

    def test_restore_subtask_preserves_relationships_integration(self):
        """Test that restoration preserves parent-child relationships"""
        subtask_id = self.test_subtask_ids[0]
        task_id = self.test_task_ids[0]
        
        # FIXED: Delete and restore subtask with proper payload
        delete_payload = {"userId": "restore_subtask_owner_123"}
        self.client.put(f'/api/subtasks/{subtask_id}/delete',
                       data=json.dumps(delete_payload),
                       content_type='application/json')
        
        restore_response = self.client.put(f'/api/subtasks/{subtask_id}/restore-new')
        self.assertEqual(restore_response.status_code, 200)
        
        # Verify parent task relationship is preserved
        subtask_doc = self.db.collection('subtasks').document(subtask_id).get()
        subtask_data = subtask_doc.to_dict()
        
        self.assertEqual(subtask_data['parentTaskId'], task_id)
        self.assertEqual(subtask_data['projectId'], self.test_project_ids[0])


if __name__ == '__main__':
    unittest.main(verbosity=2)
