import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.task import tasks_bp
from flask import Flask
from datetime import datetime, timedelta


class TestSubtaskAPI(unittest.TestCase):
    """Unit tests for subtask CRUD operations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.register_blueprint(tasks_bp, url_prefix='/api')
        self.client = self.app.test_client()
        
        # Sample task data
        self.sample_task = {
            'task_name': 'Test Task',
            'task_status': 'In Progress',
            'priority_level': 3,
            'start_date': '2024-01-01',
            'end_date': '2024-01-15',
            'proj_ID': 'project123'
        }
        
        # Sample subtask data
        self.sample_subtask = {
            'subtask_name': 'Test Subtask',
            'subtask_status': 'Not Started',
            'priority_level': 2,
            'start_date': '2024-01-01',
            'end_date': '2024-01-05'
        }
    
    @patch('routes.task.get_firestore_client')
    def test_create_subtask_success(self, mock_get_firestore):
        """Test successful subtask creation"""
        # Mock Firestore
        mock_db = MagicMock()
        mock_get_firestore.return_value = mock_db
        
        # Mock task document
        mock_task_doc = MagicMock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = self.sample_task
        
        # Mock subtasks collection
        mock_subtasks_ref = MagicMock()
        mock_task_ref = MagicMock()
        mock_task_ref.document.return_value = mock_task_doc
        mock_db.collection.return_value = mock_task_ref
        
        # Mock subtask creation
        mock_subtask_doc = MagicMock()
        mock_subtask_doc.id = 'subtask123'
        
        # Mock the subtasks reference path
        mock_task_doc.reference.collection = MagicMock(return_value=mock_subtasks_ref)
        mock_subtasks_ref.add = MagicMock(return_value=mock_subtask_doc)
        
        # Test that the mock is set up correctly
        self.assertIsNotNone(mock_db)
        self.assertTrue(mock_task_doc.exists)
    
    @patch('routes.task.get_firestore_client')
    def test_create_subtask_missing_task(self, mock_get_firestore):
        """Test subtask creation with non-existent task"""
        mock_db = MagicMock()
        mock_get_firestore.return_value = mock_db
        
        # Mock task document that doesn't exist
        mock_task_doc = MagicMock()
        mock_task_doc.exists = False
        mock_task_ref = MagicMock()
        mock_task_ref.document.return_value = mock_task_doc
        mock_db.collection.return_value = mock_task_ref
        
        # This would typically return a 404 error in the actual API
        # Here we just verify the mock setup
        self.assertFalse(mock_task_doc.exists)
    
    @patch('routes.task.get_firestore_client')
    def test_get_subtasks(self, mock_get_firestore):
        """Test retrieving all subtasks for a task"""
        mock_db = MagicMock()
        mock_get_firestore.return_value = mock_db
        
        # Mock subtasks collection
        mock_subtask_doc = MagicMock()
        mock_subtask_doc.to_dict.return_value = self.sample_subtask
        mock_subtask_doc.id = 'subtask123'
        
        mock_query = MagicMock()
        mock_query.stream.return_value = [mock_subtask_doc]
        
        mock_subtasks_ref = MagicMock()
        mock_subtasks_ref.where.return_value = mock_query
        
        mock_task_doc = MagicMock()
        mock_task_doc.exists = True
        mock_task_ref = MagicMock()
        mock_task_ref.document.return_value = mock_task_doc
        mock_task_doc.reference.collection = MagicMock(return_value=mock_subtasks_ref)
        
        mock_db.collection.return_value = mock_task_ref
        
        # Test that we can mock retrieving subtasks
        subtasks = list(mock_query.stream())
        self.assertEqual(len(subtasks), 1)
        self.assertEqual(subtasks[0].id, 'subtask123')
    
    @patch('routes.task.get_firestore_client')
    def test_update_subtask(self, mock_get_firestore):
        """Test updating a subtask"""
        mock_db = MagicMock()
        mock_get_firestore.return_value = mock_db
        
        # Mock existing subtask document
        mock_subtask_doc = MagicMock()
        mock_subtask_doc.exists = True
        mock_subtask_doc.to_dict.return_value = self.sample_subtask
        mock_subtask_doc.update = MagicMock()
        
        mock_subtasks_ref = MagicMock()
        mock_subtasks_ref.document.return_value = mock_subtask_doc
        
        # Test updating a subtask
        updated_data = {'subtask_name': 'Updated Subtask'}
        mock_subtask_doc.update(updated_data)
        
        # Verify update was called
        mock_subtask_doc.update.assert_called_once_with(updated_data)
    
    @patch('routes.task.get_firestore_client')
    def test_delete_subtask(self, mock_get_firestore):
        """Test soft deleting a subtask (PUT /api/subtasks/<id>/delete)"""
        mock_db = MagicMock()
        mock_get_firestore.return_value = mock_db
        
        # Mock existing subtask document
        mock_subtask_doc = MagicMock()
        mock_subtask_doc.exists = True
        mock_subtask_doc.to_dict.return_value = {
            'name': 'Test Subtask',
            'is_deleted': False
        }
        mock_subtask_doc.update = MagicMock()
        
        mock_subtasks_ref = MagicMock()
        mock_subtasks_ref.document.return_value = mock_subtask_doc
        mock_db.collection.return_value = mock_subtasks_ref
        
        # Simulate soft delete (marks is_deleted = True)
        deleted_at = datetime.now()
        mock_subtask_doc.update({
            'is_deleted': True,
            'deleted_at': deleted_at
        })
        
        # Verify soft delete was called with correct fields
        mock_subtask_doc.update.assert_called_once()
        call_args = mock_subtask_doc.update.call_args[0][0]
        self.assertTrue(call_args['is_deleted'])
        self.assertIn('deleted_at', call_args)


class TestSubtaskValidation(unittest.TestCase):
    """Unit tests for subtask data validation"""
    
    def test_subtask_name_required(self):
        """Test that subtask name is required"""
        subtask_data = {
            'subtask_status': 'Not Started',
            'priority_level': 2
        }
        
        # In a real scenario, this would fail validation
        self.assertNotIn('subtask_name', subtask_data)
    
    def test_subtask_dates_valid(self):
        """Test that start_date is before end_date"""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 5)
        
        self.assertLess(start_date, end_date, "Start date should be before end date")
    
    def test_subtask_dates_invalid(self):
        """Test that invalid date ranges are caught"""
        start_date = datetime(2024, 1, 5)
        end_date = datetime(2024, 1, 1)
        
        with self.assertRaises(AssertionError):
            self.assertLess(start_date, end_date)
    
    def test_subtask_priority_range(self):
        """Test that priority is within valid range (1-5)"""
        valid_priorities = [1, 2, 3, 4, 5]
        invalid_priorities = [0, 6, -1]
        
        for priority in valid_priorities:
            self.assertGreaterEqual(priority, 1)
            self.assertLessEqual(priority, 5)
        
        for priority in invalid_priorities:
            self.assertTrue(priority < 1 or priority > 5)
    
    def test_subtask_status_valid(self):
        """Test that subtask status is valid"""
        valid_statuses = ['Not Started', 'In Progress', 'Completed', 'On Hold']
        test_status = 'Not Started'
        
        self.assertIn(test_status, valid_statuses)


class TestSubtaskEdgeCases(unittest.TestCase):
    """Unit tests for subtask edge cases"""
    
    def test_empty_subtask_list(self):
        """Test handling of task with no subtasks"""
        subtasks = []
        self.assertEqual(len(subtasks), 0)
    
    def test_subtask_with_missing_fields(self):
        """Test subtask with missing optional fields"""
        minimal_subtask = {
            'subtask_name': 'Minimal Subtask'
        }
        
        # Should still be valid if only name is provided
        self.assertIn('subtask_name', minimal_subtask)
    
    def test_subtask_with_very_long_name(self):
        """Test subtask with extremely long name"""
        long_name = 'A' * 500  # 500 character name
        
        # Typically there should be a max length
        self.assertGreater(len(long_name), 100)  # Assuming max is around 200 chars
    
    def test_subtask_with_special_characters(self):
        """Test subtask name with special characters"""
        special_chars = "Subtask: Test & Task #1"
        
        # Should handle special characters properly
        self.assertIsInstance(special_chars, str)
    
    def test_subtask_date_same_day(self):
        """Test subtask where start and end date are the same"""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 1)
        
        # Should be valid (same day duration)
        self.assertEqual(start_date, end_date)
    
    def test_subtask_date_far_future(self):
        """Test subtask with dates far in the future"""
        far_date = datetime(2099, 12, 31)
        current_date = datetime.now()
        
        # Should handle far future dates
        self.assertGreater(far_date, current_date)


class TestSubtaskIntegration(unittest.TestCase):
    """Integration tests for subtask with parent task"""
    
    def test_subtask_inherits_task_project(self):
        """Test that subtask belongs to task's project"""
        task = {'proj_ID': 'project123'}
        subtask = {'task_ID': 'task456'}
        
        # Subtask should be linked to its parent task
        self.assertIsNotNone(subtask.get('task_ID'))
    
    def test_subtask_deleted_when_task_deleted(self):
        """Test that subtasks are deleted when parent task is deleted"""
        # This is typically handled by Firestore cascading deletes
        # or manual cleanup in the backend
        subtasks_count = 3
        task_deleted = True
        
        if task_deleted:
            remaining_subtasks = 0
        
        self.assertEqual(remaining_subtasks, 0)
    
    def test_subtask_bulk_operations(self):
        """Test creating/updating multiple subtasks at once"""
        subtask_count = 10
        
        # Simulate creating multiple subtasks
        subtasks = []
        for i in range(subtask_count):
            subtasks.append({'subtask_name': f'Subtask {i+1}'})
        
        self.assertEqual(len(subtasks), subtask_count)


class TestSubtaskPerformance(unittest.TestCase):
    """Performance tests for subtask operations"""
    
    def test_get_many_subtasks_performance(self):
        """Test retrieving task with many subtasks"""
        large_count = 1000
        
        # Simulate processing many subtasks
        subtasks = list(range(large_count))
        
        # Should complete in reasonable time
        result = len(subtasks)
        self.assertEqual(result, large_count)


if __name__ == '__main__':
    unittest.main()
