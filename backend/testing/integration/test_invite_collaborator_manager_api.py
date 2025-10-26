#!/usr/bin/env python3
"""
Integration Tests for SCRUM-25: Invite collaborator to a project [Manager]
Tests the API endpoint for managers to invite collaborators to projects.
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

class TestInviteCollaboratorManagerIntegration(unittest.TestCase):
    """C2 Integration tests for Invite Collaborator to Project [Manager] functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        print("=" * 80)
        print("INTEGRATION TESTING - INVITE COLLABORATOR TO PROJECT [MANAGER]")
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
        cls.test_manager_id = "test_manager_collab_123"
        cls.test_staff_1_id = "test_staff_collab_456"
        cls.test_staff_2_id = "test_staff_collab_789"
        cls.test_staff_3_id = "test_staff_collab_101"
        cls.test_external_user_id = "test_external_collab_202"
        
        # Test division name
        cls.test_division = "Test Collaboration Division"
        
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
        """Create test users and project for collaborator invitation testing"""
        print("Setting up test data...")
        
        # Create test users
        users_data = [
            {
                'id': cls.test_manager_id,
                'name': 'Test Manager Collaborator',
                'email': 'testmanager.collab@example.com',
                'role_name': 'Manager',
                'role_num': 2,  # Manager role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_staff_1_id,
                'name': 'Test Staff Collaborator 1',
                'email': 'teststaff1.collab@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_staff_2_id,
                'name': 'Test Staff Collaborator 2',
                'email': 'teststaff2.collab@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_staff_3_id,
                'name': 'Test Staff Collaborator 3',
                'email': 'teststaff3.collab@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_external_user_id,
                'name': 'Test External User',
                'email': 'testexternal.collab@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': 'External Division'  # Different division
            }
        ]
        
        for user_data in users_data:
            user_ref = cls.db.collection('Users').document(user_data['id'])
            user_ref.set(user_data)
        
        # Create test project
        current_date = datetime.now()
        project_data = {
            'proj_name': 'Test Collaboration Project',
            'proj_desc': 'Test project for collaborator invitation',
            'start_date': current_date + timedelta(days=1),
            'end_date': current_date + timedelta(days=30),
            'owner': cls.test_manager_id,
            'division_name': cls.test_division,
            'collaborators': [cls.test_manager_id, cls.test_staff_1_id],  # Initial collaborators
            'proj_status': 'Not Started',
            'is_deleted': False,
            'createdAt': current_date,
            'updatedAt': current_date
        }
        
        project_ref = cls.db.collection('Projects').document('test_project_collab_123')
        project_ref.set(project_data)
        cls.test_project_id = 'test_project_collab_123'
        
        print(f"Created {len(users_data)} test users and 1 test project")
    
    @classmethod
    def cleanup_test_data(cls):
        """Clean up test data"""
        print("Cleaning up test data...")
        
        # Delete test users
        user_ids = [cls.test_manager_id, cls.test_staff_1_id, cls.test_staff_2_id, cls.test_staff_3_id, cls.test_external_user_id]
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
    
    def test_invite_collaborator_manager_basic(self):
        """Test basic functionality of manager inviting collaborators to project"""
        print("\n--- Testing basic manager collaborator invitation ---")
        
        # Prepare update data with additional collaborators
        current_date = datetime.now()
        update_data = {
            'proj_name': 'Test Collaboration Project',
            'proj_desc': 'Test project for collaborator invitation',
            'start_date': (current_date + timedelta(days=1)).isoformat() + 'Z',
            'end_date': (current_date + timedelta(days=30)).isoformat() + 'Z',
            'owner': self.test_manager_id,
            'division_name': self.test_division,
            'collaborators': [
                self.test_manager_id,  # Owner
                self.test_staff_1_id,  # Existing collaborator
                self.test_staff_2_id,  # New collaborator
                self.test_staff_3_id   # Another new collaborator
            ]
        }
        
        response = self.app.put(f'/api/projects/{self.test_project_id}',
                               data=json.dumps(update_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Should have success message
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Project updated successfully')
        
        # Verify collaborators were added in database
        project_doc = self.db.collection('Projects').document(self.test_project_id).get()
        project_data = project_doc.to_dict()
        
        collaborators = project_data.get('collaborators', [])
        self.assertIn(self.test_staff_2_id, collaborators, "New collaborator should be added")
        self.assertIn(self.test_staff_3_id, collaborators, "Another new collaborator should be added")
        self.assertIn(self.test_manager_id, collaborators, "Owner should remain")
        self.assertIn(self.test_staff_1_id, collaborators, "Existing collaborator should remain")
        
        print(f"✅ Successfully added {len(collaborators)} collaborators to project")
    
    def test_invite_collaborator_validation(self):
        """Test validation requirements for collaborator invitation"""
        print("\n--- Testing collaborator invitation validation ---")
        
        current_date = datetime.now()
        
        # Test missing required fields
        invalid_data_sets = [
            # Missing proj_name
            {
                'proj_desc': 'Test project',
                'start_date': (current_date + timedelta(days=1)).isoformat() + 'Z',
                'end_date': (current_date + timedelta(days=30)).isoformat() + 'Z',
                'owner': self.test_manager_id,
                'collaborators': [self.test_manager_id]
            },
            # Missing collaborators
            {
                'proj_name': 'Test Project',
                'proj_desc': 'Test project',
                'start_date': (current_date + timedelta(days=1)).isoformat() + 'Z',
                'end_date': (current_date + timedelta(days=30)).isoformat() + 'Z',
                'owner': self.test_manager_id
            },
            # Empty collaborators
            {
                'proj_name': 'Test Project',
                'proj_desc': 'Test project',
                'start_date': (current_date + timedelta(days=1)).isoformat() + 'Z',
                'end_date': (current_date + timedelta(days=30)).isoformat() + 'Z',
                'owner': self.test_manager_id,
                'collaborators': []
            },
            # Invalid date format
            {
                'proj_name': 'Test Project',
                'proj_desc': 'Test project',
                'start_date': 'invalid-date',
                'end_date': (current_date + timedelta(days=30)).isoformat() + 'Z',
                'owner': self.test_manager_id,
                'collaborators': [self.test_manager_id]
            },
            # Start date in past
            {
                'proj_name': 'Test Project',
                'proj_desc': 'Test project',
                'start_date': (current_date - timedelta(days=1)).isoformat() + 'Z',
                'end_date': (current_date + timedelta(days=30)).isoformat() + 'Z',
                'owner': self.test_manager_id,
                'collaborators': [self.test_manager_id]
            },
            # End date before start date
            {
                'proj_name': 'Test Project',
                'proj_desc': 'Test project',
                'start_date': (current_date + timedelta(days=10)).isoformat() + 'Z',
                'end_date': (current_date + timedelta(days=5)).isoformat() + 'Z',
                'owner': self.test_manager_id,
                'collaborators': [self.test_manager_id]
            }
        ]
        
        for i, invalid_data in enumerate(invalid_data_sets):
            with self.subTest(test_case=i):
                response = self.app.put(f'/api/projects/{self.test_project_id}',
                                       data=json.dumps(invalid_data),
                                       content_type='application/json')
                
                self.assertEqual(response.status_code, 400)
                data = json.loads(response.data)
                self.assertIn('error', data)
                print(f"✅ Validation test {i+1}: {data['error']}")
    
    def test_invite_collaborator_owner_handling(self):
        """Test that owner is automatically added to collaborators list"""
        print("\n--- Testing owner handling in collaborators ---")
        
        current_date = datetime.now()
        
        # Update project with owner not in collaborators list
        update_data = {
            'proj_name': 'Test Collaboration Project',
            'proj_desc': 'Test project for collaborator invitation',
            'start_date': (current_date + timedelta(days=1)).isoformat() + 'Z',
            'end_date': (current_date + timedelta(days=30)).isoformat() + 'Z',
            'owner': self.test_manager_id,
            'division_name': self.test_division,
            'collaborators': [self.test_staff_1_id, self.test_staff_2_id]  # Owner not included
        }
        
        response = self.app.put(f'/api/projects/{self.test_project_id}',
                               data=json.dumps(update_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify owner was automatically added
        project_doc = self.db.collection('Projects').document(self.test_project_id).get()
        project_data = project_doc.to_dict()
        
        collaborators = project_data.get('collaborators', [])
        self.assertIn(self.test_manager_id, collaborators, "Owner should be automatically added to collaborators")
        self.assertIn(self.test_staff_1_id, collaborators, "Staff 1 should be in collaborators")
        self.assertIn(self.test_staff_2_id, collaborators, "Staff 2 should be in collaborators")
        
        print("✅ Owner automatically added to collaborators list")
    
    def test_invite_collaborator_duplicate_handling(self):
        """Test handling of duplicate collaborators"""
        print("\n--- Testing duplicate collaborator handling ---")
        
        current_date = datetime.now()
        
        # Update project with duplicate collaborators
        update_data = {
            'proj_name': 'Test Collaboration Project',
            'proj_desc': 'Test project for collaborator invitation',
            'start_date': (current_date + timedelta(days=1)).isoformat() + 'Z',
            'end_date': (current_date + timedelta(days=30)).isoformat() + 'Z',
            'owner': self.test_manager_id,
            'division_name': self.test_division,
            'collaborators': [
                self.test_manager_id,
                self.test_staff_1_id,
                self.test_staff_1_id,  # Duplicate
                self.test_staff_2_id,
                self.test_staff_2_id   # Another duplicate
            ]
        }
        
        response = self.app.put(f'/api/projects/{self.test_project_id}',
                               data=json.dumps(update_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify duplicates are preserved (API behavior)
        project_doc = self.db.collection('Projects').document(self.test_project_id).get()
        project_data = project_doc.to_dict()
        
        collaborators = project_data.get('collaborators', [])
        # API preserves duplicates as provided
        self.assertIn(self.test_manager_id, collaborators, "Owner should be in collaborators")
        self.assertIn(self.test_staff_1_id, collaborators, "Staff 1 should be in collaborators")
        self.assertIn(self.test_staff_2_id, collaborators, "Staff 2 should be in collaborators")
        
        # Count occurrences to verify duplicates are preserved
        staff_1_count = collaborators.count(self.test_staff_1_id)
        staff_2_count = collaborators.count(self.test_staff_2_id)
        
        self.assertEqual(staff_1_count, 2, "Staff 1 should appear twice (duplicate preserved)")
        self.assertEqual(staff_2_count, 2, "Staff 2 should appear twice (duplicate preserved)")
        
        print("✅ Duplicate collaborators preserved as provided")
    
    def test_invite_collaborator_nonexistent_project(self):
        """Test behavior with nonexistent project ID"""
        print("\n--- Testing nonexistent project ID ---")
        
        nonexistent_project_id = "nonexistent_project_12345"
        current_date = datetime.now()
        
        update_data = {
            'proj_name': 'Test Project',
            'proj_desc': 'Test project',
            'start_date': (current_date + timedelta(days=1)).isoformat() + 'Z',
            'end_date': (current_date + timedelta(days=30)).isoformat() + 'Z',
            'owner': self.test_manager_id,
            'collaborators': [self.test_manager_id]
        }
        
        response = self.app.put(f'/api/projects/{nonexistent_project_id}',
                               data=json.dumps(update_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Project not found', data['error'])
        
        print("✅ Nonexistent project ID handled correctly")
    
    def test_invite_collaborator_no_data(self):
        """Test behavior when no data is provided"""
        print("\n--- Testing no data provided ---")
        
        response = self.app.put(f'/api/projects/{self.test_project_id}',
                               data=json.dumps({}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('No data provided', data['error'])
        
        print("✅ No data provided handled correctly")
    
    def test_invite_collaborator_project_name_validation(self):
        """Test project name validation"""
        print("\n--- Testing project name validation ---")
        
        current_date = datetime.now()
        
        # Test short project name
        update_data = {
            'proj_name': 'AB',  # Too short
            'proj_desc': 'Test project',
            'start_date': (current_date + timedelta(days=1)).isoformat() + 'Z',
            'end_date': (current_date + timedelta(days=30)).isoformat() + 'Z',
            'owner': self.test_manager_id,
            'collaborators': [self.test_manager_id]
        }
        
        response = self.app.put(f'/api/projects/{self.test_project_id}',
                               data=json.dumps(update_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Project name must be at least 3 characters', data['error'])
        
        print("✅ Project name validation working correctly")
    
    def test_invite_collaborator_status_update(self):
        """Test updating project status along with collaborators"""
        print("\n--- Testing project status update with collaborators ---")
        
        current_date = datetime.now()
        
        update_data = {
            'proj_name': 'Test Collaboration Project',
            'proj_desc': 'Test project for collaborator invitation',
            'start_date': (current_date + timedelta(days=1)).isoformat() + 'Z',
            'end_date': (current_date + timedelta(days=30)).isoformat() + 'Z',
            'owner': self.test_manager_id,
            'division_name': self.test_division,
            'collaborators': [self.test_manager_id, self.test_staff_1_id, self.test_staff_2_id],
            'proj_status': 'In Progress'  # Update status
        }
        
        response = self.app.put(f'/api/projects/{self.test_project_id}',
                               data=json.dumps(update_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify status was updated
        project_doc = self.db.collection('Projects').document(self.test_project_id).get()
        project_data = project_doc.to_dict()
        
        self.assertEqual(project_data.get('proj_status'), 'In Progress')
        
        print("✅ Project status updated along with collaborators")
    
    def test_invite_collaborator_response_format(self):
        """Test that response format includes all necessary fields"""
        print("\n--- Testing response format ---")
        
        current_date = datetime.now()
        
        update_data = {
            'proj_name': 'Test Collaboration Project',
            'proj_desc': 'Test project for collaborator invitation',
            'start_date': (current_date + timedelta(days=1)).isoformat() + 'Z',
            'end_date': (current_date + timedelta(days=30)).isoformat() + 'Z',
            'owner': self.test_manager_id,
            'division_name': self.test_division,
            'collaborators': [self.test_manager_id, self.test_staff_1_id, self.test_staff_2_id]
        }
        
        response = self.app.put(f'/api/projects/{self.test_project_id}',
                               data=json.dumps(update_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check response structure
        required_fields = ['message', 'project']
        for field in required_fields:
            self.assertIn(field, data, f"Response should have {field} field")
        
        # Check project data structure
        project = data['project']
        project_fields = ['id', 'proj_name', 'proj_desc', 'start_date', 'end_date', 'owner', 'collaborators']
        for field in project_fields:
            self.assertIn(field, project, f"Project should have {field} field")
        
        # Verify collaborators in response
        self.assertIn(self.test_staff_2_id, project['collaborators'], "New collaborator should be in response")
        
        print("✅ Response format is correct")
    
    def test_invite_collaborator_edge_cases(self):
        """Test edge cases for collaborator invitation"""
        print("\n--- Testing collaborator invitation edge cases ---")
        
        current_date = datetime.now()
        
        # Test with maximum collaborators (if there's a limit)
        many_collaborators = [
            self.test_manager_id,
            self.test_staff_1_id,
            self.test_staff_2_id,
            self.test_staff_3_id,
            self.test_external_user_id
        ]
        
        update_data = {
            'proj_name': 'Test Collaboration Project',
            'proj_desc': 'Test project for collaborator invitation',
            'start_date': (current_date + timedelta(days=1)).isoformat() + 'Z',
            'end_date': (current_date + timedelta(days=30)).isoformat() + 'Z',
            'owner': self.test_manager_id,
            'division_name': self.test_division,
            'collaborators': many_collaborators
        }
        
        response = self.app.put(f'/api/projects/{self.test_project_id}',
                               data=json.dumps(update_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify all collaborators were added
        project_doc = self.db.collection('Projects').document(self.test_project_id).get()
        project_data = project_doc.to_dict()
        
        collaborators = project_data.get('collaborators', [])
        for collaborator in many_collaborators:
            self.assertIn(collaborator, collaborators, f"Collaborator {collaborator} should be added")
        
        print(f"✅ Successfully handled {len(many_collaborators)} collaborators")


if __name__ == '__main__':
    print("=" * 80)
    print("SCRUM-25: INVITE COLLABORATOR TO PROJECT [MANAGER] - INTEGRATION TESTING")
    print("=" * 80)
    print("Testing real API endpoints with real database")
    print("=" * 80)
    
    # Run the tests
    unittest.main(verbosity=2)
