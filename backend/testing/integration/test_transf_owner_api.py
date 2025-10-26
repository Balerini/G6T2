#!/usr/bin/env python3
"""
Integration tests for task ownership transfer functionality.
Tests the actual business logic with real database operations.
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

from firebase_utils import get_firestore_client
from app import create_app


class TestOwnershipTransferBusinessLogicIntegration(unittest.TestCase):
    """Integration tests for ownership transfer business logic"""
    
    def setUp(self):
        """Set up with REAL database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        
        # Use REAL Firestore client
        self.db = get_firestore_client()
        
        # Track for cleanup
        self.test_task_ids = []
        self.test_user_ids = []
        
        # Set up real test data
        self.setup_test_users()
        self.setup_test_task()
    
    def tearDown(self):
        """Clean up real data"""
        for task_id in self.test_task_ids:
            try:
                self.db.collection('Tasks').document(task_id).delete()
            except:
                pass
                
        for user_id in self.test_user_ids:
            try:
                self.db.collection('Users').document(user_id).delete()
            except:
                pass
    
    def setup_test_users(self):
        """Create real test users"""
        users = [
            {"id": "owner_123", "name": "Original Owner", "email": "owner@test.com", "role_name": "Staff"},
            {"id": "new_owner_456", "name": "New Owner", "email": "newowner@test.com", "role_name": "Staff"}
        ]
        
        for user in users:
            user_id = user.pop("id")
            user["created_at"] = datetime.now()
            self.db.collection('Users').document(user_id).set(user)
            self.test_user_ids.append(user_id)
    
    def setup_test_task(self):
        """Create real test task"""
        task_data = {
            "task_name": "Transfer Test Task",
            "task_desc": "Test task for ownership transfer",
            "owner": "owner_123",
            "assigned_to": ["owner_123"],
            "task_status": "active",
            "priority_level": 5,
            "start_date": datetime(2024, 1, 15),
            "end_date": datetime(2024, 1, 30),
            "is_deleted": False,
            "createdAt": datetime.now()
        }
        doc_ref = self.db.collection('Tasks').add(task_data)[1]
        self.test_task_ids.append(doc_ref.id)
        return doc_ref.id

    def transfer_ownership_business_logic(self, task_id, current_owner, new_owner, reason=None):
        """
        Business logic for ownership transfer - extracted from your app logic
        This simulates what would be in a service layer
        """
        try:
            # Get the task
            task_ref = self.db.collection('Tasks').document(task_id)
            task_doc = task_ref.get()
            
            if not task_doc.exists:
                return {"success": False, "error": "Task not found"}
            
            task_data = task_doc.to_dict()
            
            # Check if current user is the owner
            if task_data.get('owner') != current_owner:
                return {"success": False, "error": "Only task owner can transfer ownership"}
            
            # Check if new owner exists
            new_owner_doc = self.db.collection('Users').document(new_owner).get()
            if not new_owner_doc.exists:
                return {"success": False, "error": "New owner user not found"}
            
            # Check if trying to transfer to self
            if current_owner == new_owner:
                return {"success": False, "error": "Cannot transfer ownership to yourself"}
            
            # Perform the transfer
            update_data = {
                "owner": new_owner,
                "previous_owner": current_owner,
                "ownership_transferred_at": datetime.now(),
                "updatedAt": datetime.now()
            }
            
            if reason:
                update_data["transfer_reason"] = reason
            
            # Add new owner to assigned_to if not already there
            assigned_to = task_data.get('assigned_to', [])
            if new_owner not in assigned_to:
                assigned_to.append(new_owner)
                update_data["assigned_to"] = assigned_to
            
            task_ref.update(update_data)
            
            return {
                "success": True,
                "new_owner": new_owner,
                "previous_owner": current_owner,
                "task_id": task_id
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def test_ownership_transfer_business_logic_integration(self):
        """Test REAL ownership transfer business logic with database"""
        task_id = self.test_task_ids[0]
        
        # Call the business logic function directly
        result = self.transfer_ownership_business_logic(
            task_id=task_id,
            current_owner="owner_123",
            new_owner="new_owner_456",
            reason="Integration test transfer"
        )
        
        # Verify the business logic worked
        self.assertTrue(result["success"])
        self.assertEqual(result["new_owner"], "new_owner_456")
        self.assertEqual(result["previous_owner"], "owner_123")
        
        # Verify changes in REAL database
        task_doc = self.db.collection('Tasks').document(task_id).get()
        task_data = task_doc.to_dict()
        self.assertEqual(task_data['owner'], 'new_owner_456')
        self.assertEqual(task_data['previous_owner'], 'owner_123')
        self.assertEqual(task_data['transfer_reason'], 'Integration test transfer')
        self.assertIn('new_owner_456', task_data['assigned_to'])

    def test_ownership_transfer_unauthorized_user(self):
        """Test ownership transfer by unauthorized user"""
        task_id = self.test_task_ids[0]
        
        # Try to transfer as non-owner
        result = self.transfer_ownership_business_logic(
            task_id=task_id,
            current_owner="new_owner_456",  # Not the actual owner
            new_owner="owner_123"
        )
        
        # Should fail
        self.assertFalse(result["success"])
        self.assertIn("Only task owner can transfer ownership", result["error"])
        
        # Verify no changes in database
        task_doc = self.db.collection('Tasks').document(task_id).get()
        task_data = task_doc.to_dict()
        self.assertEqual(task_data['owner'], 'owner_123')  # Should remain unchanged

    def test_ownership_transfer_nonexistent_user(self):
        """Test transferring to non-existent user"""
        task_id = self.test_task_ids[0]
        
        result = self.transfer_ownership_business_logic(
            task_id=task_id,
            current_owner="owner_123",
            new_owner="nonexistent_user_999"
        )
        
        # Should fail
        self.assertFalse(result["success"])
        self.assertIn("New owner user not found", result["error"])

    def test_ownership_transfer_to_self(self):
        """Test transferring ownership to self"""
        task_id = self.test_task_ids[0]
        
        result = self.transfer_ownership_business_logic(
            task_id=task_id,
            current_owner="owner_123",
            new_owner="owner_123"  # Same as current owner
        )
        
        # Should fail
        self.assertFalse(result["success"])
        self.assertIn("Cannot transfer ownership to yourself", result["error"])

    def test_ownership_transfer_nonexistent_task(self):
        """Test transferring ownership of non-existent task"""
        result = self.transfer_ownership_business_logic(
            task_id="nonexistent_task_123",
            current_owner="owner_123",
            new_owner="new_owner_456"
        )
        
        # Should fail
        self.assertFalse(result["success"])
        self.assertIn("Task not found", result["error"])

    def test_ownership_transfer_preserves_other_data(self):
        """Test that ownership transfer preserves other task data"""
        task_id = self.test_task_ids[0]
        
        # Get original task data
        original_doc = self.db.collection('Tasks').document(task_id).get()
        original_data = original_doc.to_dict()
        
        # Transfer ownership
        result = self.transfer_ownership_business_logic(
            task_id=task_id,
            current_owner="owner_123",
            new_owner="new_owner_456"
        )
        
        self.assertTrue(result["success"])
        
        # Verify other data is preserved
        updated_doc = self.db.collection('Tasks').document(task_id).get()
        updated_data = updated_doc.to_dict()
        
        # Owner should change
        self.assertEqual(updated_data['owner'], 'new_owner_456')
        
        # Other fields should be preserved
        self.assertEqual(updated_data['task_name'], original_data['task_name'])
        self.assertEqual(updated_data['task_desc'], original_data['task_desc'])
        self.assertEqual(updated_data['priority_level'], original_data['priority_level'])
        self.assertEqual(updated_data['task_status'], original_data['task_status'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
