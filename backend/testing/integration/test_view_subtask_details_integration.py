#!/usr/bin/env python3
"""
REAL Integration tests for View Subtask Details (SCRUM-40).
Tests the complete flow: API → Backend → Firebase Database
Staff viewing subtask details
"""

import unittest
import sys
import os
import json
from datetime import datetime, timedelta

# FIXED PATH SETUP
current_file = os.path.abspath(__file__)
print(f"Test file location: {current_file}")

integration_dir = os.path.dirname(current_file)
testing_dir = os.path.dirname(integration_dir)
backend_dir = os.path.dirname(testing_dir)

print(f"Backend directory: {backend_dir}")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

service_account_path = os.path.join(backend_dir, 'service-account.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path

from app import create_app
from firebase_utils import get_firestore_client


class TestViewSubtaskDetailsIntegration(unittest.TestCase):
    """REAL Integration tests for viewing subtask details (SCRUM-40)"""
    
    def setUp(self):
        """Set up test client with REAL database"""
        print("\n" + "="*60)
        print("Setting up test...")
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        self.db = get_firestore_client()
        
        self.test_subtask_ids = []
        self.test_task_ids = []
        self.test_project_ids = []
        self.test_user_ids = []
        
        self.setup_test_users()
        self.setup_test_project()
        self.setup_test_task()
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
        """Create REAL test users"""
        users = [
            {
                "id": "staff_viewer_123",
                "name": "Staff Viewer",
                "email": "staffviewer@test.com",
                "role_name": "Staff",
                "role_num": 4,
                "division_name": "Engineering"
            },
            {
                "id": "staff_collab_456",
                "name": "Staff Collaborator",
                "email": "staffcollab@test.com",
                "role_name": "Staff",
                "role_num": 4,
                "division_name": "Engineering"
            },
            {
                "id": "manager_owner_789",
                "name": "Manager Owner",
                "email": "manager@test.com",
                "role_name": "Manager",
                "role_num": 3,
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
            "proj_name": "View Details Test Project",
            "proj_desc": "Project for testing subtask viewing",
            "start_date": future_start,
            "end_date": future_end,
            "owner": "manager_owner_789",
            "collaborators": ["manager_owner_789", "staff_viewer_123", "staff_collab_456"],
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
            "task_desc": "Parent task for view testing",
            "owner": "manager_owner_789",
            "assigned_to": ["manager_owner_789", "staff_viewer_123", "staff_collab_456"],
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
    
    def create_subtask(self, name="Test Subtask", description="Test description",
                       has_attachments=False, status="Unassigned"):
        """Helper: Create a test subtask"""
        future_start = datetime.now() + timedelta(days=2)
        future_end = datetime.now() + timedelta(days=10)
        
        attachments = []
        if has_attachments:
            attachments = [
                {"name": "design.pdf", "url": "https://example.com/design.pdf"},
                {"name": "specs.docx", "url": "https://example.com/specs.docx"}
            ]
        
        subtask_data = {
            "name": name,
            "description": description,
            "start_date": future_start.strftime('%Y-%m-%d'),
            "end_date": future_end.strftime('%Y-%m-%d'),
            "status": status,
            "priority": 5,
            "parent_task_id": self.test_task_id,
            "project_id": self.test_project_id,
            "assigned_to": ["manager_owner_789", "staff_viewer_123", "staff_collab_456"],
            "owner": "manager_owner_789",
            "attachments": attachments,
            "status_history": [],
            "is_deleted": False,
            "createdAt": datetime.now()
        }
        doc_ref = self.db.collection('subtasks').add(subtask_data)[1]
        self.test_subtask_ids.append(doc_ref.id)
        return doc_ref.id

    # ==================== AC TEST 1: View Complete Subtask Details ====================
    def test_view_complete_subtask_details_integration(self):
        """
        AC: Staff can view all subtask details
        AC: Displays name, description, collaborators, dates, attachments, status
        """
        # Create subtask with all details
        subtask_id = self.create_subtask(
            name="Complete Test Subtask",
            description="This subtask has all details filled in",
            has_attachments=True,
            status="Ongoing"
        )
        
        # Staff views subtask
        response = self.client.get(
            f'/api/subtasks/{subtask_id}',
            headers={
                'X-User-Id': 'staff_viewer_123',
                'X-User-Role': '4'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify all required fields are present
        self.assertIn('id', data)
        self.assertIn('name', data)
        self.assertIn('description', data)
        self.assertIn('collaborators', data)
        self.assertIn('start_date', data)
        self.assertIn('end_date', data)
        self.assertIn('attachments', data)
        self.assertIn('status', data)
        
        # Verify values
        self.assertEqual(data['name'], "Complete Test Subtask")
        self.assertEqual(data['description'], "This subtask has all details filled in")
        self.assertEqual(data['status'], "Ongoing")
        self.assertEqual(len(data['attachments']), 2)
        self.assertEqual(len(data['collaborators']), 3)
        
        print("✅ All subtask details displayed correctly")

    # ==================== AC TEST 2: Subtask Name Displayed ====================
    def test_subtask_name_displayed_integration(self):
        """
        AC: Subtask details page displays subtask name
        """
        subtask_id = self.create_subtask(name="Important Task - Phase 1")
        
        response = self.client.get(f'/api/subtasks/{subtask_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['name'], "Important Task - Phase 1")
        self.assertIsNotNone(data['name'])
        self.assertNotEqual(data['name'], '')
        
        print("✅ Subtask name displayed correctly")

    # ==================== AC TEST 3: Description Displayed ====================
    def test_description_displayed_integration(self):
        """
        AC: Subtask details page displays description
        """
        subtask_id = self.create_subtask(
            description="Complete the frontend implementation for the user dashboard"
        )
        
        response = self.client.get(f'/api/subtasks/{subtask_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(data['description'], 
                        "Complete the frontend implementation for the user dashboard")
        
        print("✅ Description displayed correctly")

    # ==================== AC TEST 4: Missing Description Handled ====================
    def test_missing_description_indicated_integration(self):
        """
        AC: Clear indication if description is missing
        """
        subtask_id = self.create_subtask(description="")
        
        response = self.client.get(f'/api/subtasks/{subtask_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Backend returns empty string for missing description
        # Frontend should display "No description provided"
        self.assertEqual(data['description'], '')
        
        print("✅ Missing description returned as empty string")

    # ==================== AC TEST 5: Collaborators Displayed ====================
    def test_collaborators_displayed_integration(self):
        """
        AC: Displays collaborators with user details
        """
        subtask_id = self.create_subtask()
        
        response = self.client.get(f'/api/subtasks/{subtask_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify collaborators array exists and has details
        self.assertIn('collaborators', data)
        self.assertGreater(len(data['collaborators']), 0)
        
        # Verify collaborator objects have user info
        for collab in data['collaborators']:
            self.assertIn('id', collab)
            self.assertIn('name', collab)
            self.assertIn('email', collab)
            self.assertIn('role_name', collab)
        
        # Verify specific collaborators
        collab_names = [c['name'] for c in data['collaborators']]
        self.assertIn('Manager Owner', collab_names)
        self.assertIn('Staff Viewer', collab_names)
        
        print("✅ Collaborators displayed with details")

    # ==================== AC TEST 6: Start Date Displayed ====================
    def test_start_date_displayed_integration(self):
        """
        AC: Displays start date
        """
        subtask_id = self.create_subtask()
        
        response = self.client.get(f'/api/subtasks/{subtask_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('start_date', data)
        self.assertIsNotNone(data['start_date'])
        
        print("✅ Start date displayed correctly")

    # ==================== AC TEST 7: End Date Displayed ====================
    def test_end_date_displayed_integration(self):
        """
        AC: Displays end date
        """
        subtask_id = self.create_subtask()
        
        response = self.client.get(f'/api/subtasks/{subtask_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('end_date', data)
        self.assertIsNotNone(data['end_date'])
        
        print("✅ End date displayed correctly")

    # ==================== AC TEST 8: Status Displayed ====================
    def test_status_displayed_integration(self):
        """
        AC: Displays status (Unassigned, Ongoing, Under Review, Completed)
        """
        # Test different statuses
        statuses = ["Unassigned", "Ongoing", "Under Review", "Completed"]
        
        for status in statuses:
            subtask_id = self.create_subtask(
                name=f"Subtask with {status}",
                status=status
            )
            
            response = self.client.get(f'/api/subtasks/{subtask_id}')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            self.assertEqual(data['status'], status)
        
        print("✅ All status types displayed correctly")

    # ==================== AC TEST 9: Attachments Displayed ====================
    def test_attachments_displayed_integration(self):
        """
        AC: Displays attachments
        """
        subtask_id = self.create_subtask(has_attachments=True)
        
        response = self.client.get(f'/api/subtasks/{subtask_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('attachments', data)
        self.assertEqual(len(data['attachments']), 2)
        
        # Verify attachment structure
        attachment = data['attachments'][0]
        self.assertIn('name', attachment)
        self.assertIn('url', attachment)
        
        print("✅ Attachments displayed correctly")

    # ==================== AC TEST 10: No Attachments Handled ====================
    def test_no_attachments_handled_integration(self):
        """
        AC: Clear indication if no attachments
        """
        subtask_id = self.create_subtask(has_attachments=False)
        
        response = self.client.get(f'/api/subtasks/{subtask_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('attachments', data)
        self.assertEqual(len(data['attachments']), 0)
        
        print("✅ No attachments returned as empty array")

    # ==================== AC TEST 11: Nonexistent Subtask ====================
    def test_nonexistent_subtask_returns_404_integration(self):
        """
        Test that viewing nonexistent subtask returns 404
        """
        fake_subtask_id = "nonexistent_subtask_999"
        
        response = self.client.get(f'/api/subtasks/{fake_subtask_id}')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        
        print("✅ Nonexistent subtask returns 404")

    # ==================== AC TEST 12: Deleted Subtask Returns 404 ====================
    def test_deleted_subtask_returns_404_integration(self):
        """
        Test that viewing deleted subtask returns 404
        """
        subtask_id = self.create_subtask()
        
        # Mark as deleted
        self.db.collection('subtasks').document(subtask_id).update({
            'is_deleted': True
        })
        
        response = self.client.get(f'/api/subtasks/{subtask_id}')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        
        print("✅ Deleted subtask returns 404")

    # ==================== AC TEST 13: Parent Task Info Available ====================
    def test_parent_task_info_available_integration(self):
        """
        AC: Navigation option to return to parent task
        (Backend provides parent_task_id for navigation)
        """
        subtask_id = self.create_subtask()
        
        response = self.client.get(f'/api/subtasks/{subtask_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('parent_task_id', data)
        self.assertEqual(data['parent_task_id'], self.test_task_id)
        
        print("✅ Parent task ID available for navigation")

    # ==================== AC TEST 14: Owner Info Displayed ====================
    def test_owner_info_displayed_integration(self):
        """
        Test that owner information is included
        """
        subtask_id = self.create_subtask()
        
        response = self.client.get(f'/api/subtasks/{subtask_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('owner', data)
        self.assertIn('owner_info', data)
        
        if data['owner_info']:
            self.assertIn('name', data['owner_info'])
            self.assertEqual(data['owner_info']['name'], 'Manager Owner')
        
        print("✅ Owner info displayed correctly")

    # ==================== AC TEST 15: All Required Fields Present ====================
    def test_all_required_fields_present_integration(self):
        """
        Comprehensive check that ALL required fields are present
        """
        subtask_id = self.create_subtask(has_attachments=True)
        
        response = self.client.get(f'/api/subtasks/{subtask_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        required_fields = [
            'id', 'name', 'description', 'start_date', 'end_date',
            'status', 'priority', 'parent_task_id', 'project_id',
            'owner', 'assigned_to', 'collaborators', 'attachments',
            'status_history'
        ]
        
        for field in required_fields:
            self.assertIn(field, data, f"Missing required field: {field}")
        
        print("✅ All required fields present in response")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("SCRUM-40 INTEGRATION TESTS: View Subtask Details")
    print("="*60)
    unittest.main(verbosity=2)