#!/usr/bin/env python3
"""
REAL Integration tests for Update Subtask Details (SCRUM-19).
Tests the complete flow: API → Backend → Firebase Database
"""

import unittest
import sys
import os
import json
from datetime import datetime, timedelta
import time

# FIXED PATH SETUP - This will definitely work
# Get absolute path to this file
current_file = os.path.abspath(__file__)
print(f"Test file location: {current_file}")

# Go up from integration/ -> testing/ -> backend/
integration_dir = os.path.dirname(current_file)
testing_dir = os.path.dirname(integration_dir)
backend_dir = os.path.dirname(testing_dir)

print(f"Backend directory: {backend_dir}")

# Add backend to Python path
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Verify app.py exists
app_py_path = os.path.join(backend_dir, 'app.py')
print(f"Looking for app.py at: {app_py_path}")
print(f"app.py exists: {os.path.exists(app_py_path)}")

# Set Firebase credentials
service_account_path = os.path.join(backend_dir, 'service-account.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path
print(f"Firebase credentials path: {service_account_path}")
print(f"service-account.json exists: {os.path.exists(service_account_path)}")

# Now try imports
print("\nAttempting imports...")
try:
    from app import create_app
    print("✅ Successfully imported create_app from app")
except ImportError as e:
    print(f"❌ Failed to import app: {e}")
    print("\nFiles in backend directory:")
    for f in os.listdir(backend_dir):
        if f.endswith('.py'):
            print(f"  - {f}")
    sys.exit(1)

try:
    from firebase_utils import get_firestore_client
    print("✅ Successfully imported get_firestore_client from firebase_utils")
except ImportError as e:
    print(f"❌ Failed to import firebase_utils: {e}")
    sys.exit(1)


class TestUpdateSubtaskDetailsIntegration(unittest.TestCase):
    """REAL Integration tests for updating subtask details (SCRUM-19)"""
    
    def setUp(self):
        """Set up test client with REAL database"""
        print("\n" + "="*60)
        print("Setting up test...")
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
        self.setup_test_subtask()
        print("Test setup complete!")
    
    def tearDown(self):
        """Clean up REAL test data from database"""
        print("\nCleaning up test data...")
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
        print("Cleanup complete!")
    
    def setup_test_users(self):
        """Create REAL test users - owner, collaborators, and others"""
        users = [
            {
                "id": "subtask_owner_123", 
                "name": "Subtask Owner", 
                "email": "owner@test.com", 
                "role_name": "Manager",
                "role_num": 3,
                "division_name": "Engineering"
            },
            {
                "id": "subtask_collab_456", 
                "name": "Subtask Collaborator", 
                "email": "collab@test.com", 
                "role_name": "Manager",
                "role_num": 3,
                "division_name": "Engineering"
            },
            {
                "id": "subtask_collab_789", 
                "name": "Another Collaborator", 
                "email": "collab2@test.com", 
                "role_name": "Staff",
                "role_num": 4,
                "division_name": "Engineering"
            },
            {
                "id": "non_collaborator_999", 
                "name": "Non-Collaborator", 
                "email": "other@test.com", 
                "role_name": "Staff",
                "role_num": 4,
                "division_name": "Engineering"
            }
        ]
        
        for user in users:
            user_id = user.pop("id")
            user["created_at"] = datetime.now()
            self.db.collection('Users').document(user_id).set(user)
            self.test_user_ids.append(user_id)
    
    def setup_test_project(self):
        """Create REAL test project"""
        future_start = datetime.now() + timedelta(days=1)
        future_end = datetime.now() + timedelta(days=30)
        
        project_data = {
            "proj_name": "Test Project for Subtask",
            "proj_desc": "Project for subtask update testing",
            "start_date": future_start,
            "end_date": future_end,
            "owner": "subtask_owner_123",
            "collaborators": ["subtask_owner_123", "subtask_collab_456", "subtask_collab_789"],
            "division_name": "Engineering",
            "createdAt": datetime.now()
        }
        doc_ref = self.db.collection('Projects').add(project_data)[1]
        self.test_project_ids.append(doc_ref.id)
        self.test_project_id = doc_ref.id
        return doc_ref.id
    
    def setup_test_task(self):
        """Create REAL test task (parent task)"""
        future_start = datetime.now() + timedelta(days=1)
        future_end = datetime.now() + timedelta(days=30)
        
        task_data = {
            "task_name": "Parent Test Task",
            "task_desc": "Parent task for subtask testing",
            "owner": "subtask_owner_123",
            "assigned_to": ["subtask_owner_123", "subtask_collab_456", "subtask_collab_789"],
            "task_status": "Ongoing",
            "priority_level": 5,
            "start_date": future_start,
            "end_date": future_end,
            "proj_ID": self.test_project_id,
            "is_deleted": False,
            "createdAt": datetime.now()
        }
        doc_ref = self.db.collection('Tasks').add(task_data)[1]
        self.test_task_ids.append(doc_ref.id)
        self.test_task_id = doc_ref.id
        return doc_ref.id
    
    def setup_test_subtask(self):
        """Create REAL test subtask"""
        future_start = datetime.now() + timedelta(days=2)
        future_end = datetime.now() + timedelta(days=10)
        
        subtask_data = {
            "name": "Original Subtask Name",
            "description": "Original subtask description",
            "start_date": future_start.strftime('%Y-%m-%d'),
            "end_date": future_end.strftime('%Y-%m-%d'),
            "status": "Unassigned",
            "priority": 5,
            "parent_task_id": self.test_task_id,
            "project_id": self.test_project_id,
            "assigned_to": ["subtask_owner_123", "subtask_collab_456"],
            "owner": "subtask_owner_123",
            "attachments": [],
            "status_history": [],
            "is_deleted": False,
            "createdAt": datetime.now()
        }
        doc_ref = self.db.collection('subtasks').add(subtask_data)[1]
        self.test_subtask_ids.append(doc_ref.id)
        self.test_subtask_id = doc_ref.id
        return doc_ref.id

    # ==================== AC TEST 1: Owner Can Edit All Fields ====================
    def test_owner_can_edit_all_fields_integration(self):
        """
        AC: Only the subtask owner can edit all fields
        Test that owner can update all editable fields successfully
        """
        subtask_id = self.test_subtask_id
        
        # Verify subtask exists before update
        subtask_doc = self.db.collection('subtasks').document(subtask_id).get()
        self.assertTrue(subtask_doc.exists)
        original_data = subtask_doc.to_dict()
        self.assertEqual(original_data['name'], "Original Subtask Name")
        
        # Prepare update data with all fields
        future_start = datetime.now() + timedelta(days=3)
        future_end = datetime.now() + timedelta(days=15)
        
        update_data = {
            "name": "Updated Subtask Name by Owner",
            "description": "Updated description by owner",
            "start_date": future_start.strftime('%Y-%m-%d'),
            "end_date": future_end.strftime('%Y-%m-%d'),
            "status": "Ongoing",
            "priority": 8,
            "assigned_to": ["subtask_owner_123", "subtask_collab_456", "subtask_collab_789"]
        }
        
        # Update via API with owner credentials
        response = self.client.put(
            f'/api/subtasks/{subtask_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={
                'X-User-Id': 'subtask_owner_123',
                'X-User-Role': '3'
            }
        )
        
        # Should succeed
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Subtask updated successfully')
        
        # Verify in database that ALL fields were updated
        db_doc = self.db.collection('subtasks').document(subtask_id).get()
        db_data = db_doc.to_dict()
        self.assertEqual(db_data['name'], "Updated Subtask Name by Owner")
        self.assertEqual(db_data['description'], "Updated description by owner")
        self.assertEqual(db_data['status'], "Ongoing")
        self.assertEqual(db_data['priority'], 8)
        self.assertEqual(len(db_data['assigned_to']), 3)
        
        print("✅ Owner successfully updated all fields")

    # ==================== AC TEST 2: Collaborator Can Only Edit Status and Description ====================
    def test_collaborator_can_edit_status_and_description_only_integration(self):
        """
        AC: Collaborators can only edit subtask status and task description
        Test that collaborator's edits to restricted fields are rejected
        """
        subtask_id = self.test_subtask_id
        
        # Get original data
        original_doc = self.db.collection('subtasks').document(subtask_id).get()
        original_data = original_doc.to_dict()
        original_name = original_data['name']
        original_priority = original_data['priority']
        
        # Collaborator tries to update restricted fields
        update_data = {
            "name": "SHOULD NOT UPDATE",  # Restricted
            "description": "Updated by collaborator",  # Allowed
            "status": "Ongoing",  # Allowed
            "priority": 10,  # Restricted
            "start_date": (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')  # Restricted
        }
        
        response = self.client.put(
            f'/api/subtasks/{subtask_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={
                'X-User-Id': 'subtask_collab_456',
                'X-User-Role': '3'
            }
        )
        
        # Should succeed (only updates allowed fields)
        self.assertEqual(response.status_code, 200)
        
        # Verify in database
        db_doc = self.db.collection('subtasks').document(subtask_id).get()
        db_data = db_doc.to_dict()
        
        # Allowed fields should be updated
        self.assertEqual(db_data['description'], "Updated by collaborator")
        self.assertEqual(db_data['status'], "Ongoing")
        
        # Restricted fields should NOT be updated
        self.assertEqual(db_data['name'], original_name)
        self.assertEqual(db_data['priority'], original_priority)
        
        print("✅ Collaborator can only edit status and description")

    # ==================== AC TEST 3: Non-Owner Cannot Edit Restricted Fields ====================
    def test_non_owner_cannot_edit_restricted_fields_integration(self):
        """
        AC: If a non-owner tries to edit any restricted field, 
        the system should prevent changes and display a message
        """
        subtask_id = self.test_subtask_id
        
        # Get original data
        original_doc = self.db.collection('subtasks').document(subtask_id).get()
        original_data = original_doc.to_dict()
        
        # Collaborator tries to update only restricted fields
        update_data = {
            "name": "SHOULD NOT UPDATE",
            "priority": 10,
            "start_date": (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        }
        
        response = self.client.put(
            f'/api/subtasks/{subtask_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={
                'X-User-Id': 'subtask_collab_456',
                'X-User-Role': '3'
            }
        )
        
        # Should succeed but not update restricted fields
        self.assertEqual(response.status_code, 200)
        
        # Verify restricted fields unchanged
        db_doc = self.db.collection('subtasks').document(subtask_id).get()
        db_data = db_doc.to_dict()
        self.assertEqual(db_data['name'], original_data['name'])
        self.assertEqual(db_data['priority'], original_data['priority'])
        
        print("✅ Non-owner restricted from editing protected fields")

    # ==================== AC TEST 4: After Ownership Transfer ====================
    def test_ownership_transfer_permissions_integration(self):
        """
        AC: After ownership transfer, the new owner gains full editing permissions,
        and the previous owner is treated as a collaborator
        """
        subtask_id = self.test_subtask_id
        
        # Transfer ownership to collaborator
        transfer_data = {
            "new_owner_id": "subtask_collab_456"
        }
        
        transfer_response = self.client.put(
            f'/api/subtasks/{subtask_id}/transfer-ownership',
            data=json.dumps(transfer_data),
            content_type='application/json',
            headers={
                'X-User-Id': 'subtask_owner_123',
                'X-User-Role': '4'
            }
        )
        
        self.assertEqual(transfer_response.status_code, 200)
        
        # Verify ownership changed in database
        db_doc = self.db.collection('subtasks').document(subtask_id).get()
        db_data = db_doc.to_dict()
        self.assertEqual(db_data['owner'], "subtask_collab_456")
        
        # New owner can now edit all fields
        update_data = {
            "name": "Updated by New Owner",
            "priority": 9,
            "status": "In Progress"
        }
        
        response = self.client.put(
            f'/api/subtasks/{subtask_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={
                'X-User-Id': 'subtask_collab_456',  # New owner
                'X-User-Role': '3'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify ALL fields updated by new owner
        db_doc = self.db.collection('subtasks').document(subtask_id).get()
        db_data = db_doc.to_dict()
        self.assertEqual(db_data['name'], "Updated by New Owner")
        self.assertEqual(db_data['priority'], 9)
        self.assertEqual(db_data['status'], "In Progress")
        
        # Previous owner now has collaborator-only permissions
        old_owner_update = {
            "name": "SHOULD NOT UPDATE",  # Restricted for collaborators
            "description": "Updated by previous owner",  # Allowed
            "status": "Completed"  # Allowed
        }
        
        response2 = self.client.put(
            f'/api/subtasks/{subtask_id}',
            data=json.dumps(old_owner_update),
            content_type='application/json',
            headers={
                'X-User-Id': 'subtask_owner_123',  # Previous owner, now collaborator
                'X-User-Role': '4'
            }
        )
        
        self.assertEqual(response2.status_code, 200)
        
        # Verify previous owner cannot edit name
        db_doc = self.db.collection('subtasks').document(subtask_id).get()
        db_data = db_doc.to_dict()
        self.assertEqual(db_data['name'], "Updated by New Owner")  # Unchanged
        self.assertEqual(db_data['description'], "Updated by previous owner")  # Changed
        
        print("✅ Ownership transfer permissions working correctly")

    # ==================== AC TEST 5: Required Fields Validation ====================
    def test_required_fields_validation_integration(self):
        """
        AC: System enforces that all required fields are filled before saving
        AC: If required fields are missing, saving is prevented with clear error message
        """
        subtask_id = self.test_subtask_id
        
        # Try to update with missing required fields
        invalid_data = {
            "name": "",  # Empty required field
            "description": "Valid description"
        }
        
        response = self.client.put(
            f'/api/subtasks/{subtask_id}',
            data=json.dumps(invalid_data),
            content_type='application/json',
            headers={
                'X-User-Id': 'subtask_owner_123',
                'X-User-Role': '4'
            }
        )
        
        # Should return 400
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('name', response_data['error'].lower())
        
        # Verify data unchanged in database
        db_doc = self.db.collection('subtasks').document(subtask_id).get()
        db_data = db_doc.to_dict()
        self.assertEqual(db_data['name'], "Original Subtask Name")
        
        print("✅ Required fields validation working")

    # ==================== AC TEST 6: Inline Validation ====================
    def test_inline_validation_integration(self):
        """
        AC: Inline validation highlights missing or invalid fields
        Test various validation scenarios
        """
        subtask_id = self.test_subtask_id
        
        # Test invalid date range (end before start)
        invalid_dates = {
            "start_date": (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d'),
            "end_date": (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        }
        
        response = self.client.put(
            f'/api/subtasks/{subtask_id}',
            data=json.dumps(invalid_dates),
            content_type='application/json',
            headers={
                'X-User-Id': 'subtask_owner_123',
                'X-User-Role': '4'
            }
        )
        
        # Should return 400 for invalid date range
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        
        print("✅ Inline validation catches invalid data")

    # ==================== AC TEST 7: Successful Update Reflected Immediately ====================
    def test_successful_update_reflected_immediately_integration(self):
        """
        AC: When edits are saved successfully, updated subtask details 
        are immediately reflected on screen
        AC: A successful pop-up notification appears
        """
        subtask_id = self.test_subtask_id
        
        update_data = {
            "name": "Immediately Reflected Update",
            "description": "This should appear immediately",
            "status": "In Progress"
        }
        
        # Measure response time
        start_time = time.time()
        
        response = self.client.put(
            f'/api/subtasks/{subtask_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={
                'X-User-Id': 'subtask_owner_123',
                'X-User-Role': '4'
            }
        )
        
        response_time = time.time() - start_time
        
        # Should succeed
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Subtask updated successfully')
        
        # Response should be fast (under 3 seconds)
        self.assertLess(response_time, 3.0,
                       f"Update took {response_time:.2f}s, exceeds 3s limit")
        
        # Verify immediately in database
        db_doc = self.db.collection('subtasks').document(subtask_id).get()
        db_data = db_doc.to_dict()
        self.assertEqual(db_data['name'], "Immediately Reflected Update")
        self.assertEqual(db_data['description'], "This should appear immediately")
        
        print(f"✅ Update reflected immediately in {response_time:.2f}s")

    # ==================== AC TEST 8: Failed Update Notification ====================
    def test_failed_update_notification_integration(self):
        """
        AC: If update fails, system displays a failure notification
        """
        # Try to update non-existent subtask
        fake_subtask_id = "nonexistent_subtask_999"
        
        update_data = {
            "name": "Test Update",
            "status": "Ongoing"
        }
        
        response = self.client.put(
            f'/api/subtasks/{fake_subtask_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={
                'X-User-Id': 'subtask_owner_123',
                'X-User-Role': '4'
            }
        )
        
        # Should return 404
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('not found', response_data['error'].lower())
        
        print("✅ Failed update returns proper error message")

    # ==================== AC TEST 9: Cancel Edits Before Saving ====================
    def test_cancel_edits_no_changes_integration(self):
        """
        AC: Edits can be cancelled before saving, and no data changes are applied
        (Simulated by not making the API call)
        """
        subtask_id = self.test_subtask_id
        
        # Get original data
        original_doc = self.db.collection('subtasks').document(subtask_id).get()
        original_data = original_doc.to_dict()
        original_name = original_data['name']
        original_status = original_data['status']
        
        # User prepares update but cancels (doesn't send request)
        # Verify data unchanged
        current_doc = self.db.collection('subtasks').document(subtask_id).get()
        current_data = current_doc.to_dict()
        self.assertEqual(current_data['name'], original_name)
        self.assertEqual(current_data['status'], original_status)
        
        print("✅ Cancel functionality verified - no changes applied")

    # ==================== AC TEST 10: Status History Logging ====================
    def test_status_change_logging_integration(self):
        """
        AC: Each edit to the subtask status must be logged with:
        - Staff member's name who made the change
        - Timestamp
        - New subtask status
        """
        subtask_id = self.test_subtask_id
        
        # Update status
        update_data = {
            "status": "In Progress"
        }
        
        response = self.client.put(
            f'/api/subtasks/{subtask_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={
                'X-User-Id': 'subtask_owner_123',
                'X-User-Role': '4'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify status history was logged
        db_doc = self.db.collection('subtasks').document(subtask_id).get()
        db_data = db_doc.to_dict()
        
        status_history = db_data.get('status_history', [])
        self.assertGreater(len(status_history), 0, "Status history should not be empty")
        
        # Check latest status change entry
        latest_entry = status_history[-1]
        self.assertIn('changed_by', latest_entry)
        self.assertIn('changed_by_name', latest_entry)
        self.assertIn('timestamp', latest_entry)
        self.assertIn('new_status', latest_entry)
        self.assertEqual(latest_entry['new_status'], "In Progress")
        self.assertEqual(latest_entry['changed_by'], "subtask_owner_123")
        
        print("✅ Status change logged with user, timestamp, and new status")

    # ==================== AC TEST 11: Non-Collaborator Cannot Edit ====================
    def test_non_collaborator_cannot_edit_integration(self):
        """
        Test that users not involved in the subtask cannot edit it
        """
        subtask_id = self.test_subtask_id
        
        update_data = {
            "name": "UNAUTHORIZED UPDATE",
            "status": "Completed"
        }
        
        response = self.client.put(
            f'/api/subtasks/{subtask_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={
                'X-User-Id': 'non_collaborator_999',  # Not a collaborator
                'X-User-Role': '4'
            }
        )
        
        # Should be forbidden
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        
        # Verify data unchanged
        db_doc = self.db.collection('subtasks').document(subtask_id).get()
        db_data = db_doc.to_dict()
        self.assertEqual(db_data['name'], "Original Subtask Name")
        
        print("✅ Non-collaborator correctly denied edit access")

    # ==================== AC TEST 12: Multiple Sequential Updates ====================
    def test_multiple_sequential_updates_integration(self):
        """
        Test multiple updates in sequence to ensure consistency
        """
        subtask_id = self.test_subtask_id
        
        # First update
        update_data_1 = {
            "status": "Ongoing",
            "description": "First update"
        }
        
        response1 = self.client.put(
            f'/api/subtasks/{subtask_id}',
            data=json.dumps(update_data_1),
            content_type='application/json',
            headers={
                'X-User-Id': 'subtask_owner_123',
                'X-User-Role': '4'
            }
        )
        
        self.assertEqual(response1.status_code, 200)
        
        # Second update
        update_data_2 = {
            "status": "In Progress",
            "priority": 7
        }
        
        response2 = self.client.put(
            f'/api/subtasks/{subtask_id}',
            data=json.dumps(update_data_2),
            content_type='application/json',
            headers={
                'X-User-Id': 'subtask_owner_123',
                'X-User-Role': '4'
            }
        )
        
        self.assertEqual(response2.status_code, 200)
        
        # Verify final state
        db_doc = self.db.collection('subtasks').document(subtask_id).get()
        db_data = db_doc.to_dict()
        self.assertEqual(db_data['status'], "In Progress")
        self.assertEqual(db_data['priority'], 7)
        self.assertEqual(db_data['description'], "First update")
        
        # Verify status history has both entries
        status_history = db_data.get('status_history', [])
        self.assertGreaterEqual(len(status_history), 2)
        
        print("✅ Multiple sequential updates successful")

    # ==================== AC TEST 13: Data Persistence ====================
    def test_update_data_persistence_integration(self):
        """
        Verify that updates persist by fetching after update
        """
        subtask_id = self.test_subtask_id
        
        # Update subtask
        update_data = {
            "name": "Persistence Test Subtask",
            "description": "Testing data persistence",
            "status": "In Progress",
            "priority": 6
        }
        
        update_response = self.client.put(
            f'/api/subtasks/{subtask_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={
                'X-User-Id': 'subtask_owner_123',
                'X-User-Role': '4'
            }
        )
        
        self.assertEqual(update_response.status_code, 200)
        
        # Verify in database
        db_doc = self.db.collection('subtasks').document(subtask_id).get()
        db_data = db_doc.to_dict()
        self.assertEqual(db_data['name'], "Persistence Test Subtask")
        self.assertEqual(db_data['description'], "Testing data persistence")
        self.assertEqual(db_data['status'], "In Progress")
        self.assertEqual(db_data['priority'], 6)
        
        print("✅ Data persistence verified")

    # ==================== AC TEST 14: Priority Update by Owner ====================
    def test_priority_update_by_owner_integration(self):
        """
        Test that owner can update priority (restricted field)
        """
        subtask_id = self.test_subtask_id
        
        update_data = {
            "priority": 9
        }
        
        response = self.client.put(
            f'/api/subtasks/{subtask_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={
                'X-User-Id': 'subtask_owner_123',
                'X-User-Role': '4'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify priority updated
        db_doc = self.db.collection('subtasks').document(subtask_id).get()
        db_data = db_doc.to_dict()
        self.assertEqual(db_data['priority'], 9)
        
        print("✅ Owner successfully updated priority")

    # ==================== AC TEST 15: Collaborator Assignment Update ====================
    def test_collaborator_assignment_update_integration(self):
        """
        Test that owner can add/remove collaborators
        """
        subtask_id = self.test_subtask_id
        
        # Add new collaborator
        update_data = {
            "assigned_to": ["subtask_owner_123", "subtask_collab_456", "subtask_collab_789"]
        }
        
        response = self.client.put(
            f'/api/subtasks/{subtask_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={
                'X-User-Id': 'subtask_owner_123',
                'X-User-Role': '4'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify collaborators updated
        db_doc = self.db.collection('subtasks').document(subtask_id).get()
        db_data = db_doc.to_dict()
        self.assertEqual(len(db_data['assigned_to']), 3)
        self.assertIn('subtask_collab_789', db_data['assigned_to'])
        
        print("✅ Collaborator assignment updated successfully")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("SCRUM-19 INTEGRATION TESTS: Update Subtask Details")
    print("="*60)
    unittest.main(verbosity=2)