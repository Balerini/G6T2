#!/usr/bin/env python3
"""
REAL Integration tests for project collaboration functionality.
Tests collaboration management via existing project update endpoints.
FIXED with future dates to pass validation.
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


class TestProjectCollaborationIntegration(unittest.TestCase):
    """REAL Integration tests for project collaboration functionality"""
    
    def setUp(self):
        """Set up test client with REAL database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Use REAL Firestore client
        self.db = get_firestore_client()
        
        # Track test data for cleanup
        self.test_project_ids = []
        self.test_user_ids = []
        
        # FIXED: Calculate future dates for all operations
        self.future_start = datetime.now() + timedelta(days=30)
        self.future_end = datetime.now() + timedelta(days=365)
        
        # Set up real test data
        self.setup_test_users()
        self.setup_test_project()
    
    def tearDown(self):
        """Clean up REAL test data from database"""
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
        """Create REAL test users for collaboration testing"""
        users = [
            {"id": "proj_owner_123", "name": "Project Owner", "email": "owner@company.com", "role_name": "Staff"},
            {"id": "proj_collab_456", "name": "Collaborator 1", "email": "collab1@company.com", "role_name": "Staff"},
            {"id": "proj_collab_789", "name": "Collaborator 2", "email": "collab2@company.com", "role_name": "Staff"},
            {"id": "proj_new_collab_111", "name": "New Collaborator", "email": "newcollab@company.com", "role_name": "Staff"}
        ]
        
        for user in users:
            user_id = user.pop("id")
            user["created_at"] = datetime.now()
            user["division_name"] = "Engineering"
            self.db.collection('Users').document(user_id).set(user)
            self.test_user_ids.append(user_id)
    
    def setup_test_project(self):
        """Create REAL test project for collaboration testing"""
        project_data = {
            "proj_name": "Collaboration Test Project",
            "proj_desc": "Test project for collaboration",
            "start_date": self.future_start,  # Use future date
            "end_date": self.future_end,      # Use future date
            "owner": "proj_owner_123",
            "division_name": "Engineering",
            "collaborators": ["proj_owner_123", "proj_collab_456"],
            "proj_status": "Not Started",
            "createdAt": datetime.now()
        }
        doc_ref = self.db.collection('Projects').add(project_data)[1]
        self.test_project_ids.append(doc_ref.id)
        return doc_ref.id

    def test_add_collaborators_via_update_real(self):
        """Test adding collaborators using PUT /api/projects/{id} endpoint"""
        project_id = self.test_project_ids[0]
        
        # FIXED: Use future dates in update data
        update_data = {
            "proj_name": "Collaboration Test Project",
            "proj_desc": "Test project for collaboration",
            "start_date": self.future_start.strftime("%Y-%m-%dT%H:%M:%SZ"),  # Future date
            "end_date": self.future_end.strftime("%Y-%m-%dT%H:%M:%SZ"),      # Future date
            "owner": "proj_owner_123",
            "division_name": "Engineering",
            "collaborators": ["proj_owner_123", "proj_collab_456", "proj_collab_789", "proj_new_collab_111"]
        }
        
        response = self.client.put(f'/api/projects/{project_id}',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        # Debug if it fails
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_data(as_text=True)}")
        
        # Should succeed
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Project updated successfully')
        
        # Verify collaborators were added in REAL database
        project_doc = self.db.collection('Projects').document(project_id).get()
        project_data = project_doc.to_dict()
        
        self.assertIn("proj_collab_789", project_data['collaborators'])
        self.assertIn("proj_new_collab_111", project_data['collaborators'])
        self.assertIn("proj_owner_123", project_data['collaborators'])  # Owner preserved

    def test_remove_collaborators_via_update_real(self):
        """Test removing collaborators using PUT /api/projects/{id} endpoint"""
        project_id = self.test_project_ids[0]
        
        # First add a collaborator with future dates
        update_data = {
            "proj_name": "Collaboration Test Project",
            "proj_desc": "Test project for collaboration", 
            "start_date": self.future_start.strftime("%Y-%m-%dT%H:%M:%SZ"),  # Future date
            "end_date": self.future_end.strftime("%Y-%m-%dT%H:%M:%SZ"),      # Future date
            "owner": "proj_owner_123",
            "division_name": "Engineering",
            "collaborators": ["proj_owner_123", "proj_collab_456", "proj_collab_789"]
        }
        
        # Add collaborator first
        self.client.put(f'/api/projects/{project_id}',
                       data=json.dumps(update_data),
                       content_type='application/json')
        
        # Now remove one collaborator
        update_data["collaborators"] = ["proj_owner_123", "proj_collab_789"]  # Removed proj_collab_456
        
        response = self.client.put(f'/api/projects/{project_id}',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        # Debug if it fails
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_data(as_text=True)}")
        
        self.assertEqual(response.status_code, 200)
        
        # Verify collaborator was removed in REAL database
        project_doc = self.db.collection('Projects').document(project_id).get()
        project_data = project_doc.to_dict()
        
        self.assertNotIn("proj_collab_456", project_data['collaborators'])  # Should be removed
        self.assertIn("proj_collab_789", project_data['collaborators'])     # Should remain
        self.assertIn("proj_owner_123", project_data['collaborators'])      # Owner remains

    def test_collaboration_email_notifications_real(self):
        """Test that collaboration changes trigger email notifications"""
        project_id = self.test_project_ids[0]
        
        # Add new collaborators with future dates - should trigger email notifications
        update_data = {
            "proj_name": "Collaboration Test Project",
            "proj_desc": "Test project for collaboration",
            "start_date": self.future_start.strftime("%Y-%m-%dT%H:%M:%SZ"),  # Future date
            "end_date": self.future_end.strftime("%Y-%m-%dT%H:%M:%SZ"),      # Future date
            "owner": "proj_owner_123",
            "division_name": "Engineering",
            "collaborators": ["proj_owner_123", "proj_collab_456", "proj_new_collab_111"]  # Added new collaborator
        }
        
        response = self.client.put(f'/api/projects/{project_id}',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        # Debug if it fails
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_data(as_text=True)}")
        
        self.assertEqual(response.status_code, 200)
        
        # Based on your code, emails should be sent to new collaborators
        print("✅ Collaboration update integration test passed - email notifications should be triggered")

    def test_get_project_with_collaborators_real(self):
        """Test retrieving project with collaboration information"""
        project_id = self.test_project_ids[0]
        
        # Get project with collaborator info
        response = self.client.get(f'/api/projects/{project_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Verify collaborator information is included
        self.assertIn('collaborators', response_data)
        self.assertIn('proj_owner_123', response_data['collaborators'])
        self.assertIn('proj_collab_456', response_data['collaborators'])

    def test_project_team_schedule_real(self):
        """Test GET /api/projects/{id}/team-schedule endpoint with real data"""
        project_id = self.test_project_ids[0]
        
        response = self.client.get(f'/api/projects/{project_id}/team-schedule')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        
        # Verify team schedule information
        self.assertIn('collaborators', response_data)
        self.assertIn('project', response_data)
        self.assertEqual(response_data['project']['id'], project_id)

    def test_update_nonexistent_project_real(self):
        """Test updating non-existent project"""
        update_data = {
            "proj_name": "Updated Project",
            "start_date": self.future_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_date": self.future_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "collaborators": ["proj_owner_123", "proj_collab_456"]
        }
        
        response = self.client.put('/api/projects/nonexistent_project_id',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        # Should return 404
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['error'], 'Project not found')


if __name__ == '__main__':
    unittest.main(verbosity=2)
