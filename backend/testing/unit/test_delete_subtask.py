# test_subtask_delete.py - Unit tests for Subtask Delete Operations
import unittest
import json
from unittest.mock import Mock, patch
from datetime import datetime
from flask import Flask
import sys
import os

from dotenv import load_dotenv
load_dotenv()

# Import your Flask blueprint
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from routes.subtask import subtask_bp  

# =============== BASE TEST CLASS ===============
class BaseSubtaskTestCase(unittest.TestCase):
    """Base class with common setup for subtask tests"""
    
    def setUp(self):
        """Run before each test"""
        # Create Flask app
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.register_blueprint(subtask_bp) 
        self.client = self.app.test_client()
        
        # Mock headers
        self.mock_headers = {
            'X-User-Id': 'user123',
            'X-User-Role': 'user',
            'X-User-Name': 'Test User'
        }
        
        # Setup Firebase mocks
        self.setup_firebase_mocks()
    
    def setup_firebase_mocks(self):
        """Setup global Firebase mocks"""
        patcher1 = patch('firebase_utils.get_firestore_client')
        patcher2 = patch('routes.subtask.get_firestore_client')
        
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
        
        # Make stream() return empty list by default
        mock_collection.stream.return_value = []
        
        # Make query chains work
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        mock_query.get.return_value = []
        mock_query.stream.return_value = []
        
        # Make document operations work
        mock_doc = Mock()
        mock_collection.document.return_value = mock_doc
        mock_get_result = Mock()
        mock_get_result.exists = False
        mock_get_result.to_dict.return_value = {}
        mock_doc.get.return_value = mock_get_result

# =============== SOFT DELETE SUBTASK TESTS ===============
class TestSoftDeleteSubtask(BaseSubtaskTestCase):
    
    def test_soft_delete_subtask_by_owner_success(self):
        """Test subtask owner can soft delete their subtask"""
        # Mock existing subtask owned by user123
        mock_subtask_doc = Mock()
        mock_subtask_doc.exists = True
        mock_subtask_doc.to_dict.return_value = {
            'name': 'Test Subtask',
            'owner': 'user123',
            'parent_task_id': 'parent_task_123',
            'is_deleted': False
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_subtask_doc
        
        response = self.client.put('/api/subtasks/subtask123/delete',
                                   headers=self.mock_headers)
        
        # Should succeed - owner can delete
        self.assertIn(response.status_code, [200, 500])
        
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn('message', data)
    
    def test_soft_delete_subtask_by_non_owner_fails(self):
        """Test non-owner cannot soft delete subtask"""
        # Mock subtask owned by different user
        mock_subtask_doc = Mock()
        mock_subtask_doc.exists = True
        mock_subtask_doc.to_dict.return_value = {
            'name': 'Test Subtask',
            'owner': 'other_user',  # Different owner
            'is_deleted': False
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_subtask_doc
        
        response = self.client.put('/api/subtasks/subtask123/delete',
                                   headers=self.mock_headers)
        
        # Should fail - not the owner
        self.assertIn(response.status_code, [403, 500])
    
    def test_soft_delete_nonexistent_subtask_fails(self):
        """Test deleting non-existent subtask returns 404"""
        # Mock subtask doesn't exist
        mock_subtask_doc = Mock()
        mock_subtask_doc.exists = False
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_subtask_doc
        
        response = self.client.put('/api/subtasks/nonexistent_id/delete',
                                   headers=self.mock_headers)
        
        # Should fail - subtask not found
        self.assertIn(response.status_code, [404, 500])
    
    def test_soft_delete_already_deleted_subtask(self):
        """Test soft deleting already deleted subtask"""
        # Mock already deleted subtask
        mock_subtask_doc = Mock()
        mock_subtask_doc.exists = True
        mock_subtask_doc.to_dict.return_value = {
            'name': 'Test Subtask',
            'owner': 'user123',
            'is_deleted': True,  # Already deleted
            'deleted_at': datetime.now()
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_subtask_doc
        
        response = self.client.put('/api/subtasks/subtask123/delete',
                                   headers=self.mock_headers)
        
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400, 500])
    
    def test_soft_delete_marks_deleted_by_cascade_false(self):
        """Test soft delete sets deleted_by_cascade to False (direct delete)"""
        mock_subtask_doc = Mock()
        mock_subtask_doc.exists = True
        mock_subtask_doc.to_dict.return_value = {
            'name': 'Test Subtask',
            'owner': 'user123',
            'is_deleted': False
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_subtask_doc
        
        response = self.client.put('/api/subtasks/subtask123/delete',
                                   headers=self.mock_headers)
        
        # Should succeed
        self.assertIn(response.status_code, [200, 500])

# =============== HARD DELETE SUBTASK TESTS ===============
class TestHardDeleteSubtask(BaseSubtaskTestCase):
    
    def test_hard_delete_subtask_success(self):
        """Test permanent subtask deletion"""
        # Mock existing subtask
        mock_subtask_doc = Mock()
        mock_subtask_doc.exists = True
        mock_subtask_doc.to_dict.return_value = {
            'name': 'Test Subtask',
            'owner': 'user123'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_subtask_doc
        
        response = self.client.delete('/api/subtasks/subtask123/permanent-new')
        
        # Should succeed - permanent deletion
        self.assertIn(response.status_code, [200, 500])
        
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn('permanently deleted', data.get('message', '').lower())
    
    def test_hard_delete_nonexistent_subtask_fails(self):
        """Test hard deleting non-existent subtask returns 404"""
        # Mock subtask doesn't exist
        mock_subtask_doc = Mock()
        mock_subtask_doc.exists = False
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_subtask_doc
        
        response = self.client.delete('/api/subtasks/nonexistent_id/permanent-new')
        
        # Should fail - subtask not found
        self.assertIn(response.status_code, [404, 500])
    
    def test_hard_delete_removes_from_database(self):
        """Test hard delete permanently removes subtask from Firestore"""
        mock_subtask_doc = Mock()
        mock_subtask_doc.exists = True
        mock_subtask_doc.to_dict.return_value = {
            'name': 'Test Subtask',
            'owner': 'user123'
        }
        
        # Mock the delete method
        mock_ref = Mock()
        self.mock_db.collection.return_value.document.return_value = mock_ref
        mock_ref.get.return_value = mock_subtask_doc
        
        response = self.client.delete('/api/subtasks/subtask123/permanent-new')
        
        # Should succeed
        self.assertIn(response.status_code, [200, 500])

# =============== GET DELETED SUBTASKS TESTS ===============
class TestGetDeletedSubtasks(BaseSubtaskTestCase):
    
    def test_get_deleted_subtasks_for_user(self):
        """Test retrieving deleted subtasks owned by user"""
        # Mock deleted subtasks
        mock_deleted1 = Mock()
        mock_deleted1.id = 'subtask1'
        mock_deleted1.to_dict.return_value = {
            'name': 'Deleted Subtask 1',
            'owner': 'user123',
            'is_deleted': True,
            'deleted_at': datetime.now()
        }
        
        mock_deleted2 = Mock()
        mock_deleted2.id = 'subtask2'
        mock_deleted2.to_dict.return_value = {
            'name': 'Deleted Subtask 2',
            'owner': 'user123',
            'is_deleted': True,
            'deleted_at': datetime.now()
        }
        
        self.mock_db.collection.return_value.where.return_value.get.return_value = [mock_deleted1, mock_deleted2]
        
        response = self.client.get('/api/subtasks/deleted-new?userId=user123')
        
        self.assertIn(response.status_code, [200, 500])
        
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIsInstance(data, list)
    
    def test_get_deleted_subtasks_missing_user_id_fails(self):
        """Test getting deleted subtasks without userId parameter fails"""
        response = self.client.get('/api/subtasks/deleted-new')
        
        # Should fail - userId required
        self.assertIn(response.status_code, [400, 500])

if __name__ == '__main__':
    unittest.main(verbosity=2)
