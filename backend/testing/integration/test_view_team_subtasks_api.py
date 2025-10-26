#!/usr/bin/env python3
"""
REAL Integration tests for View Team's Subtasks (SCRUM-41).
Tests the complete flow: API → Backend → Firebase Database
Manager viewing all team member subtasks
"""

import unittest
import sys
import os
import json
from datetime import datetime, timedelta
import time

# FIXED PATH SETUP
current_file = os.path.abspath(__file__)
integration_dir = os.path.dirname(current_file)
testing_dir = os.path.dirname(integration_dir)
backend_dir = os.path.dirname(testing_dir)

sys.path.insert(0, backend_dir)

# Set Firebase credentials
service_account_path = os.path.join(backend_dir, 'service-account.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path

from app import create_app
from firebase_utils import get_firestore_client


class TestViewTeamSubtasksIntegration(unittest.TestCase):
    """REAL Integration tests for viewing team subtasks (SCRUM-41)"""
    
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
        self.setup_test_subtasks()
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
        """Create REAL test users - manager and staff"""
        users = [
            {
                "id": "team_manager_123",
                "name": "Test Manager",
                "email": "manager@test.com",
                "role_name": "Manager",
                "role_num": 3,
                "division_name": "Engineering"
            },
            {
                "id": "team_staff_456",
                "name": "Staff Member 1",
                "email": "staff1@test.com",
                "role_name": "Staff",
                "role_num": 4,
                "division_name": "Engineering"
            },
            {
                "id": "team_staff_789",
                "name": "Staff Member 2",
                "email": "staff2@test.com",
                "role_name": "Staff",
                "role_num": 4,
                "division_name": "Engineering"
            },
            {
                "id": "other_staff_999",
                "name": "Other Department Staff",
                "email": "other@test.com",
                "role_name": "Staff",
                "role_num": 4,
                "division_name": "Marketing"  # Different division
            },
            {
                "id": "non_manager_111",
                "name": "Regular Staff",
                "email": "regular@test.com",
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
            "proj_name": "Team Test Project",
            "proj_desc": "Project for team subtasks testing",
            "start_date": future_start,
            "end_date": future_end,
            "owner": "team_manager_123",
            "collaborators": ["team_manager_123", "team_staff_456", "team_staff_789"],
            "division_name": "Engineering",
            "createdAt": datetime.now()
        }
        doc_ref = self.db.collection('Projects').add(project_data)[1]
        self.test_project_ids.append(doc_ref.id)
        self.test_project_id = doc_ref.id
        return doc_ref.id
    
    def setup_test_task(self):
        """Create REAL test task"""
        future_start = datetime.now() + timedelta(days=1)
        future_end = datetime.now() + timedelta(days=30)
        
        task_data = {
            "task_name": "Team Test Task",
            "task_desc": "Task for team subtasks testing",
            "owner": "team_manager_123",
            "assigned_to": ["team_staff_456", "team_staff_789"],
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
    
    def setup_test_subtasks(self):
        """Create REAL test subtasks for team members"""
        future_start = datetime.now() + timedelta(days=1)
        future_end_1 = datetime.now() + timedelta(days=5)
        future_end_2 = datetime.now() + timedelta(days=10)
        future_end_3 = datetime.now() + timedelta(days=15)
        
        subtasks = [
            {
                "name": "Staff 1 Subtask - High Priority",
                "description": "High priority task for staff 1",
                "start_date": future_start.strftime('%Y-%m-%d'),
                "end_date": future_end_1.strftime('%Y-%m-%d'),
                "status": "Ongoing",
                "priority": 8,
                "parent_task_id": self.test_task_id,
                "project_id": self.test_project_id,
                "assigned_to": ["team_staff_456"],
                "owner": "team_staff_456",
                "is_deleted": False,
                "createdAt": datetime.now()
            },
            {
                "name": "Staff 1 Subtask - Completed",
                "description": "Completed task for staff 1",
                "start_date": future_start.strftime('%Y-%m-%d'),
                "end_date": future_end_2.strftime('%Y-%m-%d'),
                "status": "Completed",
                "priority": 5,
                "parent_task_id": self.test_task_id,
                "project_id": self.test_project_id,
                "assigned_to": ["team_staff_456"],
                "owner": "team_staff_456",
                "is_deleted": False,
                "createdAt": datetime.now()
            },
            {
                "name": "Staff 2 Subtask - Medium Priority",
                "description": "Medium priority task for staff 2",
                "start_date": future_start.strftime('%Y-%m-%d'),
                "end_date": future_end_3.strftime('%Y-%m-%d'),
                "status": "Under Review",
                "priority": 6,
                "parent_task_id": self.test_task_id,
                "project_id": self.test_project_id,
                "assigned_to": ["team_staff_789"],
                "owner": "team_staff_789",
                "is_deleted": False,
                "createdAt": datetime.now()
            },
            {
                "name": "Staff 2 Subtask - Low Priority",
                "description": "Low priority task for staff 2",
                "start_date": future_start.strftime('%Y-%m-%d'),
                "end_date": future_end_1.strftime('%Y-%m-%d'),
                "status": "Unassigned",
                "priority": 3,
                "parent_task_id": self.test_task_id,
                "project_id": self.test_project_id,
                "assigned_to": ["team_staff_789"],
                "owner": "team_staff_789",
                "is_deleted": False,
                "createdAt": datetime.now()
            },
            {
                "name": "Deleted Subtask - Should Not Appear",
                "description": "This is deleted",
                "start_date": future_start.strftime('%Y-%m-%d'),
                "end_date": future_end_1.strftime('%Y-%m-%d'),
                "status": "Ongoing",
                "priority": 5,
                "parent_task_id": self.test_task_id,
                "project_id": self.test_project_id,
                "assigned_to": ["team_staff_456"],
                "owner": "team_staff_456",
                "is_deleted": True,  # Deleted
                "createdAt": datetime.now()
            }
        ]
        
        for subtask_data in subtasks:
            doc_ref = self.db.collection('subtasks').add(subtask_data)[1]
            self.test_subtask_ids.append(doc_ref.id)

    # ==================== AC TEST 1: Manager Can View Team Subtasks ====================
    def test_manager_view_team_subtasks_success(self):
        """
        AC: Manager can view all team member's subtasks
        AC: View subtask details (name, due date, status)
        AC: View which employee is in charge
        AC: Rendered within 3 seconds
        """
        start_time = time.time()
        
        response = self.client.get(f'/api/subtasks/team/team_manager_123')
        
        response_time = time.time() - start_time
        
        # Should succeed
        self.assertEqual(response.status_code, 200)
        
        # AC: Rendered within 3 seconds
        self.assertLess(response_time, 3.0,
                       f"Response took {response_time:.2f}s, should be < 3s")
        
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        
        # Should have 4 non-deleted subtasks
        self.assertEqual(len(response_data), 4)
        
        # AC: Can view subtask details
        for subtask in response_data:
            self.assertIn('id', subtask)
            self.assertIn('name', subtask)
            self.assertIn('end_date', subtask)  # Due date
            self.assertIn('status', subtask)
            self.assertIn('priority', subtask)
            self.assertIn('ownerName', subtask)  # Employee in charge
            self.assertIn('owner_id', subtask)
        
        # AC: Can view which employee is in charge
        owner_names = [s['ownerName'] for s in response_data]
        self.assertIn('Staff Member 1', owner_names)
        self.assertIn('Staff Member 2', owner_names)
        
        print(f"✅ Manager viewed {len(response_data)} team subtasks in {response_time:.2f}s")

    # ==================== AC TEST 2: Only View Own Team Subtasks ====================
    def test_manager_only_views_own_team_subtasks(self):
        """
        AC: Can only view subtasks of staff within manager's own team (same division)
        """
        response = self.client.get(f'/api/subtasks/team/team_manager_123')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Verify all subtasks are from Engineering division staff only
        for subtask in response_data:
            owner_id = subtask['owner_id']
            # Should be either team_staff_456 or team_staff_789 (Engineering division)
            self.assertIn(owner_id, ['team_staff_456', 'team_staff_789'])
            # Should NOT be other_staff_999 (Marketing division)
            self.assertNotEqual(owner_id, 'other_staff_999')
        
        print("✅ Manager only sees subtasks from own team (Engineering division)")

    # ==================== AC TEST 3: Non-Manager Cannot View Team Subtasks ====================
    def test_non_manager_cannot_view_team_subtasks(self):
        """
        AC: Only managers can view team subtasks (authorization check)
        """
        # Try with a regular staff member
        response = self.client.get(f'/api/subtasks/team/non_manager_111')
        
        # Should be forbidden
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('not authorized', response_data['error'].lower())
        
        print("✅ Non-manager correctly denied access to team subtasks")

    # ==================== AC TEST 4: Nonexistent Manager ====================
    def test_nonexistent_manager(self):
        """Test error handling for nonexistent manager"""
        response = self.client.get(f'/api/subtasks/team/nonexistent_manager_999')
        
        # Should return 404
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('not found', response_data['error'].lower())
        
        print("✅ Nonexistent manager returns 404")

    # ==================== AC TEST 5: Empty Team (No Subtasks) ====================
    def test_manager_with_no_team_subtasks(self):
        """
        AC: If no subtask exists for the team, appropriate response is returned
        """
        # Create a manager with no team members having subtasks
        empty_manager_data = {
            "name": "Empty Team Manager",
            "email": "empty@test.com",
            "role_name": "Manager",
            "role_num": 3,
            "division_name": "HR",  # Different division with no subtasks
            "created_at": datetime.now()
        }
        empty_manager_ref = self.db.collection('Users').document('empty_manager_999').set(empty_manager_data)
        self.test_user_ids.append('empty_manager_999')
        
        response = self.client.get(f'/api/subtasks/team/empty_manager_999')
        
        # Should succeed but return empty list
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        self.assertEqual(len(response_data), 0)
        
        print("✅ Manager with no team subtasks returns empty list")

    # ==================== AC TEST 6: Deleted Subtasks Not Shown ====================
    def test_deleted_subtasks_not_shown(self):
        """Verify that deleted subtasks are not included in team view"""
        response = self.client.get(f'/api/subtasks/team/team_manager_123')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Verify deleted subtask is not in results
        subtask_names = [s['name'] for s in response_data]
        self.assertNotIn('Deleted Subtask - Should Not Appear', subtask_names)
        
        # Should only have 4 non-deleted subtasks
        self.assertEqual(len(response_data), 4)
        
        print("✅ Deleted subtasks correctly excluded from team view")

    # ==================== AC TEST 7: Subtask Data Structure ====================
    def test_subtask_data_structure(self):
        """
        AC: Each subtask displays correct details
        Verify response contains all required fields
        """
        response = self.client.get(f'/api/subtasks/team/team_manager_123')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Check first subtask has all required fields
        if response_data:
            subtask = response_data[0]
            
            required_fields = [
                'id', 'name', 'ownerName', 'owner_id', 
                'end_date', 'status', 'priority', 
                'task_id', 'proj_ID'
            ]
            
            for field in required_fields:
                self.assertIn(field, subtask, f"Missing required field: {field}")
            
            # Verify data types
            self.assertIsInstance(subtask['name'], str)
            self.assertIsInstance(subtask['ownerName'], str)
            self.assertIsInstance(subtask['status'], str)
            self.assertIsInstance(subtask['priority'], (int, float))
        
        print("✅ Subtask data structure verified")

    # ==================== AC TEST 8: Multiple Staff Members ====================
    def test_subtasks_from_multiple_staff_members(self):
        """Verify subtasks from different team members are all shown"""
        response = self.client.get(f'/api/subtasks/team/team_manager_123')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Get unique owners
        unique_owners = set(s['owner_id'] for s in response_data)
        
        # Should have subtasks from both staff members
        self.assertIn('team_staff_456', unique_owners)
        self.assertIn('team_staff_789', unique_owners)
        self.assertGreaterEqual(len(unique_owners), 2)
        
        print(f"✅ Subtasks from {len(unique_owners)} different team members")

    # ==================== AC TEST 9: Performance with Many Subtasks ====================
    def test_performance_with_many_subtasks(self):
        """
        AC: Must render within 3 seconds even with many subtasks
        """
        # Create additional subtasks
        future_start = datetime.now() + timedelta(days=1)
        future_end = datetime.now() + timedelta(days=10)
        
        for i in range(20):
            subtask_data = {
                "name": f"Performance Test Subtask {i}",
                "description": f"Test subtask {i}",
                "start_date": future_start.strftime('%Y-%m-%d'),
                "end_date": future_end.strftime('%Y-%m-%d'),
                "status": "Ongoing",
                "priority": i % 10,
                "parent_task_id": self.test_task_id,
                "project_id": self.test_project_id,
                "assigned_to": ["team_staff_456"],
                "owner": "team_staff_456",
                "is_deleted": False,
                "createdAt": datetime.now()
            }
            doc_ref = self.db.collection('subtasks').add(subtask_data)[1]
            self.test_subtask_ids.append(doc_ref.id)
        
        start_time = time.time()
        response = self.client.get(f'/api/subtasks/team/team_manager_123')
        response_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 3.0,
                       f"Performance test took {response_time:.2f}s with many subtasks")
        
        response_data = json.loads(response.data)
        self.assertGreaterEqual(len(response_data), 24)  # 4 + 20 additional
        
        print(f"✅ Performance test passed: {len(response_data)} subtasks in {response_time:.2f}s")

    # ==================== AC TEST 10: Different Statuses Present ====================
    def test_different_statuses_present(self):
        """
        AC: Can filter by status (verify different statuses exist)
        """
        response = self.client.get(f'/api/subtasks/team/team_manager_123')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Get unique statuses
        unique_statuses = set(s['status'] for s in response_data)
        
        # Should have multiple different statuses
        self.assertGreaterEqual(len(unique_statuses), 2)
        
        # Verify specific statuses exist
        statuses_list = list(unique_statuses)
        print(f"✅ Found {len(unique_statuses)} different statuses: {statuses_list}")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("SCRUM-41 INTEGRATION TESTS: View Team's Subtasks")
    print("="*60)
    unittest.main(verbosity=2)