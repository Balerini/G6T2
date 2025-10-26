#!/usr/bin/env python3
"""
REAL Integration Tests - Project Creation Feature
Tests project creation API endpoints with REAL database integration.
Tests Flask app + business logic + real database integration.
"""

import unittest
import json
from datetime import datetime, timedelta
from flask import Flask
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set Firebase credentials with relative path
service_account_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'service-account.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path

from routes.project import projects_bp
from firebase_utils import get_firestore_client


class TestCreateProject(unittest.TestCase):
    """REAL Integration tests for project creation with real database"""
    
    def setUp(self):
        """Set up test fixtures with REAL database"""
        # Create Flask app
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.register_blueprint(projects_bp)
        self.client = self.app.test_client()
        
        # Use REAL Firestore client
        self.db = get_firestore_client()
        
        # Track test data for cleanup
        self.test_project_ids = []
        self.test_user_ids = []
        
        # Generate unique test data to avoid conflicts
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Set up real test users
        self.setup_test_users()
    
    def tearDown(self):
        """Clean up REAL test data from database"""
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
        
        self.test_project_ids.clear()
        self.test_user_ids.clear()
    
    def setup_test_users(self):
        """Create real test users in the database"""
        # Create owner user
        owner_data = {
            'name': f'Test Owner {self.timestamp}',
            'email': f'owner.{self.timestamp}@company.com',
            'role_name': 'Manager',
            'role_num': 3,
            'division_name': 'IT Department',
            'created_at': datetime.now().isoformat()
        }
        
        owner_ref = self.db.collection('Users').add(owner_data)
        self.test_owner_id = owner_ref[1].id
        self.test_user_ids.append(self.test_owner_id)
        
        # Create collaborator user
        collaborator_data = {
            'name': f'Test Collaborator {self.timestamp}',
            'email': f'collaborator.{self.timestamp}@company.com',
            'role_name': 'Staff',
            'role_num': 4,
            'division_name': 'IT Department',
            'created_at': datetime.now().isoformat()
        }
        
        collaborator_ref = self.db.collection('Users').add(collaborator_data)
        self.test_collaborator_id = collaborator_ref[1].id
        self.test_user_ids.append(self.test_collaborator_id)
    
    def test_create_project_success(self):
        """Test successful project creation with REAL database"""
        # Real project data with future dates
        future_start = datetime.now() + timedelta(days=1)
        future_end = datetime.now() + timedelta(days=30)
        
        project_data = {
            'proj_name': f'Test Project {self.timestamp}',
            'proj_desc': 'Test project description for integration testing',
            'start_date': future_start.strftime('%Y-%m-%d'),
            'end_date': future_end.strftime('%Y-%m-%d'),
            'owner': self.test_owner_id,
            'division_name': 'IT Department',
            'collaborators': [self.test_owner_id, self.test_collaborator_id]
        }
        
        # Mock headers for authentication
        headers = {
            'X-User-Id': self.test_owner_id,
            'X-User-Role': 'manager',
            'X-User-Name': f'Test Owner {self.timestamp}'
        }
        
        response = self.client.post('/api/projects',
                                   json=project_data,
                                   headers=headers)
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertIn('message', response_data)
        self.assertIn('project', response_data)
        
        # Track project for cleanup
        if 'project' in response_data and 'id' in response_data['project']:
            self.test_project_ids.append(response_data['project']['id'])
        
        # Verify project exists in real database
        if 'project' in response_data and 'id' in response_data['project']:
            project_doc = self.db.collection('Projects').document(response_data['project']['id']).get()
            self.assertTrue(project_doc.exists)
            
            project_data_from_db = project_doc.to_dict()
            self.assertEqual(project_data_from_db['proj_name'], project_data['proj_name'])
            self.assertEqual(project_data_from_db['proj_desc'], project_data['proj_desc'])
            self.assertEqual(project_data_from_db['owner'], project_data['owner'])
            self.assertEqual(project_data_from_db['division_name'], project_data['division_name'])
    
    def test_create_project_missing_required_fields(self):
        """Test project creation with missing required fields with REAL database"""
        # Missing proj_name
        incomplete_data = {
            'proj_desc': 'Test description',
            'start_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'owner': self.test_owner_id,
            'division_name': 'IT Department'
        }
        
        headers = {
            'X-User-Id': self.test_owner_id,
            'X-User-Role': 'manager',
            'X-User-Name': f'Test Owner {self.timestamp}'
        }
        
        response = self.client.post('/api/projects',
                                   json=incomplete_data,
                                   headers=headers)
        
        # Should return validation error
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('required', response_data['error'].lower())
    
    def test_create_project_invalid_dates(self):
        """Test project creation with invalid dates with REAL database"""
        # End date before start date
        invalid_data = {
            'proj_name': f'Test Project {self.timestamp}',
            'proj_desc': 'Test description',
            'start_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),  # Later date
            'end_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),    # Earlier date
            'owner': self.test_owner_id,
            'division_name': 'IT Department'
        }
        
        headers = {
            'X-User-Id': self.test_owner_id,
            'X-User-Role': 'manager',
            'X-User-Name': f'Test Owner {self.timestamp}'
        }
        
        response = self.client.post('/api/projects',
                                   json=invalid_data,
                                   headers=headers)
        
        # Should return validation error
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    def test_create_project_past_start_date(self):
        """Test project creation with past start date with REAL database"""
        # Start date in the past
        past_data = {
            'proj_name': f'Test Project {self.timestamp}',
            'proj_desc': 'Test description',
            'start_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),  # Past date
            'end_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'owner': self.test_owner_id,
            'division_name': 'IT Department'
        }
        
        headers = {
            'X-User-Id': self.test_owner_id,
            'X-User-Role': 'manager',
            'X-User-Name': f'Test Owner {self.timestamp}'
        }
        
        response = self.client.post('/api/projects',
                                   json=past_data,
                                   headers=headers)
        
        # Should return validation error
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    def test_create_project_invalid_owner(self):
        """Test project creation with invalid owner with REAL database"""
        project_data = {
            'proj_name': f'Test Project {self.timestamp}',
            'proj_desc': 'Test description',
            'start_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'owner': 'non_existent_user_id',  # Invalid owner
            'division_name': 'IT Department'
        }
        
        headers = {
            'X-User-Id': self.test_owner_id,
            'X-User-Role': 'manager',
            'X-User-Name': f'Test Owner {self.timestamp}'
        }
        
        response = self.client.post('/api/projects',
                                   json=project_data,
                                   headers=headers)
        
        # Should return validation error
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    def test_create_project_unauthorized_user(self):
        """Test project creation with unauthorized user with REAL database"""
        project_data = {
            'proj_name': f'Test Project {self.timestamp}',
            'proj_desc': 'Test description',
            'start_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'owner': self.test_owner_id,
            'division_name': 'IT Department'
        }
        
        # Unauthorized headers (staff trying to create project)
        headers = {
            'X-User-Id': self.test_collaborator_id,
            'X-User-Role': 'staff',
            'X-User-Name': f'Test Collaborator {self.timestamp}'
        }
        
        response = self.client.post('/api/projects',
                                   json=project_data,
                                   headers=headers)
        
        # Should return authorization error
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    def test_create_project_missing_headers(self):
        """Test project creation with missing authentication headers with REAL database"""
        project_data = {
            'proj_name': f'Test Project {self.timestamp}',
            'proj_desc': 'Test description',
            'start_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'owner': self.test_owner_id,
            'division_name': 'IT Department'
        }
        
        # No headers
        response = self.client.post('/api/projects',
                                   json=project_data)
        
        # Should return authentication error
        self.assertEqual(response.status_code, 401)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    def test_create_project_duplicate_name(self):
        """Test project creation with duplicate name with REAL database"""
        # First create a project
        project_data = {
            'proj_name': f'Duplicate Test Project {self.timestamp}',
            'proj_desc': 'Test description',
            'start_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'owner': self.test_owner_id,
            'division_name': 'IT Department'
        }
        
        headers = {
            'X-User-Id': self.test_owner_id,
            'X-User-Role': 'manager',
            'X-User-Name': f'Test Owner {self.timestamp}'
        }
        
        response1 = self.client.post('/api/projects',
                                    json=project_data,
                                    headers=headers)
        
        self.assertEqual(response1.status_code, 201)
        response1_data = json.loads(response1.data)
        if 'project' in response1_data and 'id' in response1_data['project']:
            self.test_project_ids.append(response1_data['project']['id'])
        
        # Try to create another project with the same name
        duplicate_data = project_data.copy()
        duplicate_data['proj_desc'] = 'Different description'
        
        response2 = self.client.post('/api/projects',
                                    json=duplicate_data,
                                    headers=headers)
        
        # Should return validation error for duplicate name
        self.assertEqual(response2.status_code, 400)
        response2_data = json.loads(response2.data)
        self.assertIn('error', response2_data)


if __name__ == '__main__':
    print("=" * 80)
    print("REAL INTEGRATION TESTING - PROJECT CREATION FEATURE")
    print("=" * 80)
    print("Testing project creation API endpoints with REAL database integration")
    print("Tests Flask app + business logic + real database")
    print("=" * 80)
    
    # Run with verbose output
    unittest.main(verbosity=2)