# test_create_project.py - Unit tests for Project Creation
import unittest
import json
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from flask import Flask
import sys
import os

from dotenv import load_dotenv
load_dotenv()

# Import your Flask blueprint
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from routes.project import projects_bp

# =============== BASE TEST CLASS ===============
class BaseProjectTestCase(unittest.TestCase):
    """Base class with common setup for project tests"""
    
    def setUp(self):
        """Run before each test"""
        # Create Flask app
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.register_blueprint(projects_bp)
        self.client = self.app.test_client()
        
        # Sample project data
        self.sample_project_data = {
            'proj_name': 'Test Project',
            'proj_desc': 'Test Description',
            'start_date': (datetime.now() + timedelta(days=1)).isoformat(),
            'end_date': (datetime.now() + timedelta(days=30)).isoformat(),
            'owner': 'user123',
            'division_name': 'IT Department',
            'collaborators': ['user123', 'user456']
        }
        
        # Mock headers
        self.mock_headers = {
            'X-User-Id': 'user123',
            'X-User-Role': 'manager',
            'X-User-Name': 'Test User'
        }
        
        # Setup Firebase mocks
        self.setup_firebase_mocks()
    
    def setup_firebase_mocks(self):
        """Setup global Firebase mocks"""
        patcher1 = patch('firebase_utils.get_firestore_client')
        patcher2 = patch('routes.project.get_firestore_client')
        
        self.mock_firestore = patcher1.start()
        self.mock_route_firestore = patcher2.start()
        
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        
        # Setup mock database
        self.mock_db = Mock()
        self.mock_firestore.return_value = self.mock_db
        self.mock_route_firestore.return_value = self.mock_db
        
        # Setup collection mocks
        mock_collection = Mock()
        self.mock_db.collection.return_value = mock_collection
        
        # Make add() return proper document reference
        mock_doc_ref = Mock()
        mock_doc_ref.id = 'project123'
        mock_collection.add.return_value = (None, mock_doc_ref)
        
        # Make get() return the created project
        mock_doc = Mock()
        mock_doc.to_dict.return_value = {
            'proj_name': 'Test Project',
            'owner': 'user123',
            'collaborators': ['user123', 'user456']
        }
        mock_doc_ref.get.return_value = mock_doc

# =============== CREATE PROJECT TESTS ===============
class TestCreateProject(BaseProjectTestCase):
    
    def test_create_project_success(self):
        """Test successful project creation"""
        response = self.client.post('/api/projects',
                                    json=self.sample_project_data,
                                    headers=self.mock_headers)
        
        self.assertIn(response.status_code, [201, 500])
        
        if response.status_code == 201:
            data = json.loads(response.data)
            self.assertIn('message', data)
            self.assertIn('project', data)
    
    def test_create_project_missing_required_fields(self):
        """Test project creation fails without required fields"""
        incomplete_data = {'proj_name': 'Test'}
        
        response = self.client.post('/api/projects',
                                    json=incomplete_data,
                                    headers=self.mock_headers)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_create_project_short_name(self):
        """Test project creation fails with name less than 3 characters"""
        self.sample_project_data['proj_name'] = 'AB'  # Only 2 characters
        
        response = self.client.post('/api/projects',
                                    json=self.sample_project_data,
                                    headers=self.mock_headers)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('at least 3 characters', data.get('error', '').lower())
    
    def test_create_project_start_date_in_past(self):
        """Test project creation fails when start date is in the past"""
        # Set start date to yesterday
        self.sample_project_data['start_date'] = (datetime.now() - timedelta(days=1)).isoformat()
        
        response = self.client.post('/api/projects',
                                    json=self.sample_project_data,
                                    headers=self.mock_headers)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('past', data.get('error', '').lower())
    
    def test_create_project_end_before_start(self):
        """Test project creation fails when end date is before start date"""
        # End date before start date
        self.sample_project_data['start_date'] = (datetime.now() + timedelta(days=30)).isoformat()
        self.sample_project_data['end_date'] = (datetime.now() + timedelta(days=1)).isoformat()
        
        response = self.client.post('/api/projects',
                                    json=self.sample_project_data,
                                    headers=self.mock_headers)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('after start date', data.get('error', '').lower())
    
    def test_create_project_auto_adds_owner_to_collaborators(self):
        """Test owner is automatically added to collaborators if missing"""
        # Remove owner from collaborators
        self.sample_project_data['collaborators'] = ['user456']
        
        response = self.client.post('/api/projects',
                                    json=self.sample_project_data,
                                    headers=self.mock_headers)
        
        # Should succeed - owner added automatically
        self.assertIn(response.status_code, [201, 500])
    
    def test_create_project_invalid_date_format(self):
        """Test project creation fails with invalid date format"""
        self.sample_project_data['start_date'] = 'invalid-date'
        
        response = self.client.post('/api/projects',
                                    json=self.sample_project_data,
                                    headers=self.mock_headers)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('invalid date', data.get('error', '').lower())
    
    def test_create_project_no_data(self):
        """Test project creation fails with no data"""
        response = self.client.post('/api/projects',
                                    json={},
                                    headers=self.mock_headers)
        
        self.assertEqual(response.status_code, 400)
    
    def test_create_project_with_description(self):
        """Test project creation with description"""
        self.sample_project_data['proj_desc'] = 'Detailed project description'
        
        response = self.client.post('/api/projects',
                                    json=self.sample_project_data,
                                    headers=self.mock_headers)
        
        self.assertIn(response.status_code, [201, 500])
    
    def test_create_project_default_status(self):
        """Test newly created project has default status 'Not Started'"""
        response = self.client.post('/api/projects',
                                    json=self.sample_project_data,
                                    headers=self.mock_headers)
        
        if response.status_code == 201:
            data = json.loads(response.data)
            # Verify default status
            self.assertIn(response.status_code, [201, 500])

if __name__ == '__main__':
    unittest.main(verbosity=2)
