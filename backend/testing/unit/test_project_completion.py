#!/usr/bin/env python3
"""
C1 Unit Tests - Project Completion Function
Tests individual project completion function in complete isolation.
Based on actual function in routes/project.py.
"""

import unittest
import sys
import os
from unittest.mock import MagicMock

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import individual function for unit testing
from project_utils import is_project_completed, is_project_completed_pure


class TestProjectCompletionUnit(unittest.TestCase):
    """C1 Unit tests for is_project_completed function from project.py"""
    
    def test_is_project_completed_no_tasks(self):
        """Test project completion with no tasks"""
        # Mock database with no tasks
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_db.collection.return_value = mock_tasks_ref
        mock_tasks_ref.where.return_value.stream.return_value = []
        
        result = is_project_completed("project123", mock_db)
        self.assertFalse(result, "Project with no tasks should not be completed")
    
    def test_is_project_completed_all_tasks_completed(self):
        """Test project completion with all tasks completed"""
        # Mock database with completed tasks
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_db.collection.return_value = mock_tasks_ref
        
        # Mock completed task
        mock_task = MagicMock()
        mock_task.to_dict.return_value = {
            'task_status': 'Completed',
            'is_deleted': False,
            'subtasks': []
        }
        mock_tasks_ref.where.return_value.stream.return_value = [mock_task]
        
        result = is_project_completed("project123", mock_db)
        self.assertTrue(result, "Project with all tasks completed should be completed")
    
    def test_is_project_completed_some_tasks_incomplete(self):
        """Test project completion with some tasks incomplete"""
        # Mock database with mixed task statuses
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_db.collection.return_value = mock_tasks_ref
        
        # Mock completed and incomplete tasks
        mock_completed_task = MagicMock()
        mock_completed_task.to_dict.return_value = {
            'task_status': 'Completed',
            'is_deleted': False,
            'subtasks': []
        }
        
        mock_incomplete_task = MagicMock()
        mock_incomplete_task.to_dict.return_value = {
            'task_status': 'In Progress',
            'is_deleted': False,
            'subtasks': []
        }
        
        mock_tasks_ref.where.return_value.stream.return_value = [mock_completed_task, mock_incomplete_task]
        
        result = is_project_completed("project123", mock_db)
        self.assertFalse(result, "Project with incomplete tasks should not be completed")
    
    def test_is_project_completed_deleted_tasks_ignored(self):
        """Test that deleted tasks are ignored in completion check"""
        # Mock database with deleted tasks
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_db.collection.return_value = mock_tasks_ref
        
        # Mock deleted task
        mock_deleted_task = MagicMock()
        mock_deleted_task.to_dict.return_value = {
            'task_status': 'In Progress',
            'is_deleted': True,
            'subtasks': []
        }
        mock_tasks_ref.where.return_value.stream.return_value = [mock_deleted_task]
        
        result = is_project_completed("project123", mock_db)
        self.assertTrue(result, "Project with only deleted tasks should be considered completed")
    
    def test_is_project_completed_with_subtasks(self):
        """Test project completion with subtasks"""
        # Mock database with task and subtasks
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_db.collection.return_value = mock_tasks_ref
        
        # Mock task with completed subtasks
        mock_task = MagicMock()
        mock_task.to_dict.return_value = {
            'task_status': 'Completed',
            'is_deleted': False,
            'subtasks': [
                {'status': 'Completed', 'is_deleted': False},
                {'status': 'Completed', 'is_deleted': False}
            ]
        }
        mock_tasks_ref.where.return_value.stream.return_value = [mock_task]
        
        result = is_project_completed("project123", mock_db)
        self.assertTrue(result, "Project with completed task and subtasks should be completed")
    
    def test_is_project_completed_with_incomplete_subtasks(self):
        """Test project completion with incomplete subtasks"""
        # Mock database with task and incomplete subtasks
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_db.collection.return_value = mock_tasks_ref
        
        # Mock task with incomplete subtasks
        mock_task = MagicMock()
        mock_task.to_dict.return_value = {
            'task_status': 'Completed',
            'is_deleted': False,
            'subtasks': [
                {'status': 'Completed', 'is_deleted': False},
                {'status': 'In Progress', 'is_deleted': False}
            ]
        }
        mock_tasks_ref.where.return_value.stream.return_value = [mock_task]
        
        result = is_project_completed("project123", mock_db)
        self.assertFalse(result, "Project with incomplete subtasks should not be completed")
    
    def test_is_project_completed_deleted_subtasks_ignored(self):
        """Test that deleted subtasks are ignored in completion check"""
        # Mock database with task and deleted subtasks
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_db.collection.return_value = mock_tasks_ref
        
        # Mock task with deleted subtasks
        mock_task = MagicMock()
        mock_task.to_dict.return_value = {
            'task_status': 'Completed',
            'is_deleted': False,
            'subtasks': [
                {'status': 'In Progress', 'is_deleted': True},
                {'status': 'In Progress', 'is_deleted': True}
            ]
        }
        mock_tasks_ref.where.return_value.stream.return_value = [mock_task]
        
        result = is_project_completed("project123", mock_db)
        self.assertTrue(result, "Project with only deleted subtasks should be considered completed")
    
    def test_is_project_completed_database_error(self):
        """Test project completion with database error"""
        # Mock database that raises exception
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_db.collection.return_value = mock_tasks_ref
        mock_tasks_ref.where.return_value.stream.side_effect = Exception("Database error")
        
        result = is_project_completed("project123", mock_db)
        self.assertFalse(result, "Project completion should return False on database error")
    
    def test_is_project_completed_edge_cases(self):
        """Test project completion with various edge cases"""
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_db.collection.return_value = mock_tasks_ref
        
        # Test with empty subtasks list
        mock_task = MagicMock()
        mock_task.to_dict.return_value = {
            'task_status': 'Completed',  # Task must be completed
            'is_deleted': False,
            'subtasks': []
        }
        mock_tasks_ref.where.return_value.stream.return_value = [mock_task]
        
        result = is_project_completed("project123", mock_db)
        self.assertTrue(result, "Project with completed task and empty subtasks should be considered completed")
        
        # Test with None subtasks - this should cause an exception and return False
        mock_task.to_dict.return_value = {
            'task_status': 'Completed',  # Task must be completed
            'is_deleted': False,
            'subtasks': None
        }
        
        result = is_project_completed("project123", mock_db)
        self.assertFalse(result, "Project with None subtasks should return False due to iteration error")
        
        # Test with missing subtasks key
        mock_task.to_dict.return_value = {
            'task_status': 'Completed',  # Task must be completed
            'is_deleted': False
        }
        
        result = is_project_completed("project123", mock_db)
        self.assertTrue(result, "Project with completed task and missing subtasks key should be considered completed")


class TestProjectCompletionPureUnit(unittest.TestCase):
    """C1 Unit tests for is_project_completed_pure function - pure function testing"""
    
    def test_is_project_completed_pure_no_tasks(self):
        """Test pure function with no tasks"""
        result = is_project_completed_pure([])
        self.assertFalse(result, "Project with no tasks should not be considered completed")
    
    def test_is_project_completed_pure_all_completed(self):
        """Test pure function with all tasks and subtasks completed"""
        tasks_data = [
            {
                'task_status': 'Completed',
                'is_deleted': False,
                'subtasks': [
                    {'status': 'Completed', 'is_deleted': False},
                    {'status': 'Completed', 'is_deleted': False}
                ]
            },
            {
                'task_status': 'Completed',
                'is_deleted': False,
                'subtasks': []
            }
        ]
        
        result = is_project_completed_pure(tasks_data)
        self.assertTrue(result, "Project with all tasks and subtasks completed should be completed")
    
    def test_is_project_completed_pure_some_incomplete_task(self):
        """Test pure function with some tasks not completed"""
        tasks_data = [
            {
                'task_status': 'Completed',
                'is_deleted': False,
                'subtasks': []
            },
            {
                'task_status': 'In Progress',
                'is_deleted': False,
                'subtasks': []
            }
        ]
        
        result = is_project_completed_pure(tasks_data)
        self.assertFalse(result, "Project with incomplete tasks should not be completed")
    
    def test_is_project_completed_pure_deleted_tasks_ignored(self):
        """Test pure function with deleted tasks ignored"""
        tasks_data = [
            {
                'task_status': 'In Progress',
                'is_deleted': True,
                'subtasks': []
            }
        ]
        
        result = is_project_completed_pure(tasks_data)
        self.assertTrue(result, "Project with only deleted tasks should be considered completed")
    
    def test_is_project_completed_pure_with_incomplete_subtasks(self):
        """Test pure function with incomplete subtasks"""
        tasks_data = [
            {
                'task_status': 'Completed',
                'is_deleted': False,
                'subtasks': [
                    {'status': 'Completed', 'is_deleted': False},
                    {'status': 'In Progress', 'is_deleted': False}
                ]
            }
        ]
        
        result = is_project_completed_pure(tasks_data)
        self.assertFalse(result, "Project with incomplete subtasks should not be completed")
    
    def test_is_project_completed_pure_deleted_subtasks_ignored(self):
        """Test pure function with deleted subtasks ignored"""
        tasks_data = [
            {
                'task_status': 'Completed',
                'is_deleted': False,
                'subtasks': [
                    {'status': 'Completed', 'is_deleted': False},
                    {'status': 'In Progress', 'is_deleted': True}  # Deleted subtask
                ]
            }
        ]
        
        result = is_project_completed_pure(tasks_data)
        self.assertTrue(result, "Project with deleted subtasks should be considered completed if other subtasks are complete")
    
    def test_is_project_completed_pure_edge_cases(self):
        """Test pure function with edge cases"""
        # Test with empty subtasks list
        tasks_data = [
            {
                'task_status': 'Completed',
                'is_deleted': False,
                'subtasks': []
            }
        ]
        
        result = is_project_completed_pure(tasks_data)
        self.assertTrue(result, "Project with completed task and empty subtasks should be considered completed")
        
        # Test with None subtasks
        tasks_data = [
            {
                'task_status': 'Completed',
                'is_deleted': False,
                'subtasks': None
            }
        ]
        
        result = is_project_completed_pure(tasks_data)
        self.assertTrue(result, "Project with completed task and None subtasks should be considered completed")
        
        # Test with missing subtasks key
        tasks_data = [
            {
                'task_status': 'Completed',
                'is_deleted': False
            }
        ]
        
        result = is_project_completed_pure(tasks_data)
        self.assertTrue(result, "Project with completed task and missing subtasks key should be considered completed")


if __name__ == '__main__':
    print("=" * 80)
    print("C1 UNIT TESTING - PROJECT COMPLETION FUNCTION")
    print("=" * 80)
    print("Testing individual project completion function in complete isolation")
    print("No external dependencies, no Flask app, no database")
    print("=" * 80)

    # Run with verbose output
    unittest.main(verbosity=2)
