#!/usr/bin/env python3
"""
REAL Integration Tests - Subtask Feature
Tests subtask API endpoints with REAL database integration.
Tests Flask app + business logic + real database integration.
"""

import unittest
import sys
import os
import json
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set Firebase credentials with relative path
service_account_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'service-account.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path

from app import create_app
from firebase_utils import get_firestore_client


class TestSubtaskAPI(unittest.TestCase):
    """REAL Integration tests for subtask CRUD operations with real database"""
    
    def setUp(self):
        """Set up test fixtures with REAL database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Use REAL Firestore client
        self.db = get_firestore_client()
        
        # Track test data for cleanup
        self.test_task_ids = []
        self.test_subtask_ids = []
        
        # Generate unique test data to avoid conflicts
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Set up real test data
        self.setup_test_task()
    
    def tearDown(self):
        """Clean up REAL test data from database"""
        # Clean up test subtasks
        for subtask_id in self.test_subtask_ids:
            try:
                self.db.collection('subtasks').document(subtask_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete test subtask {subtask_id}: {e}")
        
        # Clean up test tasks
        for task_id in self.test_task_ids:
            try:
                self.db.collection('Tasks').document(task_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete test task {task_id}: {e}")
        
        self.test_task_ids.clear()
        self.test_subtask_ids.clear()
    
    def setup_test_task(self):
        """Create a real test task in the database"""
        # Calculate future dates for validation
        future_start = datetime.now() + timedelta(days=1)
        future_end = datetime.now() + timedelta(days=30)
        
        task_data = {
            'task_name': f'Test Task {self.timestamp}',
            'task_status': 'In Progress',
            'priority_level': 3,
            'start_date': future_start.strftime('%Y-%m-%d'),
            'end_date': future_end.strftime('%Y-%m-%d'),
            'proj_ID': f'test_project_{self.timestamp}',
            'task_description': 'Test task for subtask testing',
            'created_by': f'test_user_{self.timestamp}',
            'created_at': datetime.now().isoformat(),
            'assigned_to': [f'test_user_{self.timestamp}']
        }
        
        # Create task in real database
        task_ref = self.db.collection('Tasks').add(task_data)
        self.test_task_id = task_ref[1].id
        self.test_task_ids.append(self.test_task_id)
        
        # Store task data for tests
        self.sample_task = task_data
        self.sample_task['id'] = self.test_task_id
    
    def test_create_subtask_success(self):
        """Test successful subtask creation via API with REAL database"""
        # Real subtask data matching the API schema
        subtask_data = {
            'name': f'Test Subtask {self.timestamp}',
            'status': 'Not Started',
            'priority': 2,
            'start_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'parent_task_id': self.test_task_id,
            'project_id': None,
            'assigned_to': [],
            'description': 'Test subtask description'
        }
        
        # Create subtask via API
        response = self.client.post('/api/subtasks',
                                   data=json.dumps(subtask_data),
                                   content_type='application/json')
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertIn('message', response_data)
        self.assertIn('subtaskId', response_data)
        self.assertEqual(response_data['message'], 'Subtask created successfully')
        
        # Track subtask for cleanup
        self.test_subtask_ids.append(response_data['subtaskId'])
        
        # Verify subtask exists in real database
        subtask_doc = self.db.collection('subtasks').document(response_data['subtaskId']).get()
        self.assertTrue(subtask_doc.exists)
        
        subtask_data_from_db = subtask_doc.to_dict()
        self.assertEqual(subtask_data_from_db['name'], subtask_data['name'])
        self.assertEqual(subtask_data_from_db['status'], subtask_data['status'])
        self.assertEqual(subtask_data_from_db['priority'], subtask_data['priority'])
        self.assertEqual(subtask_data_from_db['parent_task_id'], subtask_data['parent_task_id'])
    
    def test_create_subtask_missing_task(self):
        """Test subtask creation with non-existent task via API with REAL database"""
        subtask_data = {
            'name': f'Test Subtask {self.timestamp}',
            'status': 'Not Started',
            'priority_level': 2,
            'start_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'parent_task_id': 'non_existent_task_id',
            'project_id': None,
            'assigned_to': []
        }
        
        response = self.client.post('/api/subtasks',
                                   data=json.dumps(subtask_data),
                                   content_type='application/json')
        
        # Should return 404 for non-existent task
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('Parent task not found', response_data['error'])
    
    def test_create_subtask_missing_required_fields(self):
        """Test subtask creation with missing required fields via API with REAL database"""
        # Missing required fields
        incomplete_data = {
            'name': f'Test Subtask {self.timestamp}',
            'status': 'Not Started',
            # Missing start_date, end_date, parent_task_id
            'priority_level': 2
        }
        
        response = self.client.post('/api/subtasks',
                                   data=json.dumps(incomplete_data),
                                   content_type='application/json')
        
        # Should return validation error
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('required', response_data['error'])
    
    def test_create_subtask_invalid_dates(self):
        """Test subtask creation with invalid dates via API with REAL database"""
        # End date before start date
        invalid_data = {
            'name': f'Test Subtask {self.timestamp}',
            'status': 'Not Started',
            'priority_level': 2,
            'start_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),  # Later date
            'end_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),    # Earlier date
            'parent_task_id': self.test_task_id,
            'project_id': None,
            'assigned_to': []
        }
        
        response = self.client.post('/api/subtasks',
                                   data=json.dumps(invalid_data),
                                   content_type='application/json')
        
        # Should return validation error
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
    
    def test_get_subtask_by_id(self):
        """Test retrieving a specific subtask via API with REAL database"""
        # First create a subtask
        subtask_data = {
            'name': f'Test Subtask {self.timestamp}',
            'status': 'Not Started',
            'priority_level': 2,
            'start_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'parent_task_id': self.test_task_id,
            'project_id': None,
            'assigned_to': []
        }
        
        create_response = self.client.post('/api/subtasks',
                                         data=json.dumps(subtask_data),
                                         content_type='application/json')
        
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        subtask_id = create_data['subtask_id']
        self.test_subtask_ids.append(subtask_id)
        
        # Get the specific subtask
        response = self.client.get(f'/api/subtasks/{subtask_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])
        self.assertIn('subtask', response_data)
        
        subtask = response_data['subtask']
        self.assertEqual(subtask['name'], subtask_data['name'])
        self.assertEqual(subtask['status'], subtask_data['status'])
        self.assertEqual(subtask['priority_level'], subtask_data['priority_level'])
    
    def test_get_nonexistent_subtask(self):
        """Test retrieving a non-existent subtask via API with REAL database"""
        fake_subtask_id = 'non_existent_subtask_id'
        
        response = self.client.get(f'/api/subtasks/{fake_subtask_id}')
        
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
        self.assertIn('Subtask not found', response_data['error'])
    
    def test_update_subtask(self):
        """Test updating a subtask via API with REAL database"""
        # First create a subtask
        subtask_data = {
            'name': f'Test Subtask {self.timestamp}',
            'status': 'Not Started',
            'priority_level': 2,
            'start_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'parent_task_id': self.test_task_id,
            'project_id': None,
            'assigned_to': []
        }
        
        create_response = self.client.post('/api/subtasks',
                                         data=json.dumps(subtask_data),
                                         content_type='application/json')
        
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        subtask_id = create_data['subtask_id']
        self.test_subtask_ids.append(subtask_id)
        
        # Update the subtask
        update_data = {
            'name': f'Updated Subtask {self.timestamp}',
            'status': 'In Progress',
            'priority_level': 1,
            'start_date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=6)).strftime('%Y-%m-%d'),
            'description': 'Updated description'
        }
        
        response = self.client.put(f'/api/subtasks/{subtask_id}',
                                  data=json.dumps(update_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])
        
        # Verify subtask was updated in real database
        subtask_doc = self.db.collection('subtasks').document(subtask_id).get()
        self.assertTrue(subtask_doc.exists)
        
        subtask_data_from_db = subtask_doc.to_dict()
        self.assertEqual(subtask_data_from_db['name'], update_data['name'])
        self.assertEqual(subtask_data_from_db['status'], update_data['status'])
        self.assertEqual(subtask_data_from_db['priority_level'], update_data['priority_level'])
    
    def test_delete_subtask(self):
        """Test deleting a subtask via API with REAL database"""
        # First create a subtask
        subtask_data = {
            'name': f'Test Subtask {self.timestamp}',
            'status': 'Not Started',
            'priority_level': 2,
            'start_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'parent_task_id': self.test_task_id,
            'project_id': None,
            'assigned_to': []
        }
        
        create_response = self.client.post('/api/subtasks',
                                         data=json.dumps(subtask_data),
                                         content_type='application/json')
        
        self.assertEqual(create_response.status_code, 201)
        create_data = json.loads(create_response.data)
        subtask_id = create_data['subtask_id']
        
        # Verify subtask exists in database
        subtask_doc = self.db.collection('subtasks').document(subtask_id).get()
        self.assertTrue(subtask_doc.exists)
        
        # Delete the subtask
        response = self.client.delete(f'/api/subtasks/{subtask_id}')
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])
        
        # Verify subtask was deleted from real database
        subtask_doc = self.db.collection('subtasks').document(subtask_id).get()
        self.assertFalse(subtask_doc.exists)


if __name__ == '__main__':
    print("=" * 80)
    print("REAL INTEGRATION TESTING - SUBTASK FEATURE")
    print("=" * 80)
    print("Testing subtask API endpoints with REAL database integration")
    print("Tests Flask app + business logic + real database")
    print("=" * 80)
    
    # Run with verbose output
    unittest.main(verbosity=2)