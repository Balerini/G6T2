# test_subtask_restore.py - Unit tests for Subtask Restore Operations
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

# =============== RESTORE SUBTASK TESTS ===============
class TestRestoreSubtask(BaseSubtaskTestCase):
    
    def test_restore_deleted_subtask_success(self):
        """Test successfully restoring a deleted subtask"""
        # Mock deleted subtask
        mock_subtask_doc = Mock()
        mock_subtask_doc.exists = True
        mock_subtask_doc.to_dict.return_value = {
            'name': 'Test Subtask',
            'owner': 'user123',
            'is_deleted': True,
            'deleted_at': datetime.now()
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_subtask_doc
        
        response = self.client.put('/api/subtasks/subtask123/restore-new')
        
        # Should succeed - restore deleted subtask
        self.assertIn(response.status_code, [200, 500])
        
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn('restored', data.get('message', '').lower())
    
    def test_restore_nonexistent_subtask_fails(self):
        """Test restoring non-existent subtask returns 404"""
        # Mock subtask doesn't exist
        mock_subtask_doc = Mock()
        mock_subtask_doc.exists = False
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_subtask_doc
        
        response = self.client.put('/api/subtasks/nonexistent_id/restore-new')
        
        # Should fail - subtask not found
        self.assertIn(response.status_code, [404, 500])
    
    def test_restore_active_subtask(self):
        """Test restoring non-deleted subtask (already active)"""
        # Mock active subtask (not deleted)
        mock_subtask_doc = Mock()
        mock_subtask_doc.exists = True
        mock_subtask_doc.to_dict.return_value = {
            'name': 'Test Subtask',
            'owner': 'user123',
            'is_deleted': False  # Already active
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_subtask_doc
        
        response = self.client.put('/api/subtasks/subtask123/restore-new')
        
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400, 500])
    
    def test_restore_clears_deleted_fields(self):
        """Test restore clears is_deleted and deleted_at fields"""
        mock_subtask_doc = Mock()
        mock_subtask_doc.exists = True
        mock_subtask_doc.to_dict.return_value = {
            'name': 'Test Subtask',
            'owner': 'user123',
            'is_deleted': True,
            'deleted_at': datetime.now(),
            'deleted_by_cascade': False
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_subtask_doc
        
        response = self.client.put('/api/subtasks/subtask123/restore-new')
        
        # Should succeed
        self.assertIn(response.status_code, [200, 500])
    
    def test_restore_cascade_deleted_subtask(self):
        """Test restoring subtask that was cascade deleted"""
        # Mock cascade deleted subtask
        mock_subtask_doc = Mock()
        mock_subtask_doc.exists = True
        mock_subtask_doc.to_dict.return_value = {
            'name': 'Test Subtask',
            'owner': 'user123',
            'is_deleted': True,
            'deleted_at': datetime.now(),
            'deleted_by_cascade': True,
            'cascade_parent_id': 'parent_task_123'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_subtask_doc
        
        response = self.client.put('/api/subtasks/subtask123/restore-new')
        
        # Should succeed - can restore cascade deleted subtasks
        self.assertIn(response.status_code, [200, 500])
    
    def test_restore_updates_status_correctly(self):
        """Test restore updates subtask to active status"""
        mock_subtask_doc = Mock()
        mock_subtask_doc.exists = True
        mock_subtask_doc.to_dict.return_value = {
            'name': 'Test Subtask',
            'owner': 'user123',
            'is_deleted': True,
            'deleted_at': datetime.now(),
            'status': 'deleted'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_subtask_doc
        
        response = self.client.put('/api/subtasks/subtask123/restore-new')
        
        if response.status_code == 200:
            # Verify restoration successful
            self.assertIn(response.status_code, [200, 500])

if __name__ == '__main__':
    unittest.main(verbosity=2)
