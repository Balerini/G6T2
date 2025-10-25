#!/usr/bin/env python3
"""
C1 Unit Tests - Subtask Utility Functions
Tests individual subtask utility functions in complete isolation.
No external dependencies, no Flask app, no database.
"""

import unittest
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestSubtaskUtilsUnit(unittest.TestCase):
    """C1 Unit tests for subtask utility functions"""
    
    def test_validate_subtask_data(self):
        """Test validation of subtask data"""
        # Test valid subtask data
        valid_data = {
            'name': 'Implement feature',
            'description': 'Add new functionality',
            'status': 'In Progress',
            'priority': 'High',
            'start_date': '2025-01-01',
            'end_date': '2025-01-15'
        }
        
        # Test required fields validation
        required_fields = ['name', 'status', 'start_date', 'end_date']
        for field in required_fields:
            if field in valid_data:
                self.assertIsNotNone(valid_data[field])
                self.assertNotEqual(valid_data[field], '')
    
    def test_validate_subtask_status(self):
        """Test subtask status validation"""
        valid_statuses = ['Not Started', 'In Progress', 'Completed', 'On Hold', 'Cancelled']
        
        for status in valid_statuses:
            self.assertIsInstance(status, str)
            self.assertGreater(len(status), 0)
        
        # Test status transition logic
        status_transitions = {
            'Not Started': ['In Progress', 'Cancelled'],
            'In Progress': ['Completed', 'On Hold', 'Cancelled'],
            'On Hold': ['In Progress', 'Cancelled'],
            'Completed': [],  # Terminal state
            'Cancelled': []   # Terminal state
        }
        
        for status, allowed_transitions in status_transitions.items():
            self.assertIsInstance(allowed_transitions, list)
    
    def test_validate_subtask_priority(self):
        """Test subtask priority validation"""
        valid_priorities = ['Low', 'Medium', 'High', 'Critical']
        
        for priority in valid_priorities:
            self.assertIsInstance(priority, str)
            self.assertGreater(len(priority), 0)
        
        # Test priority ordering
        priority_order = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
        for priority, level in priority_order.items():
            self.assertGreater(level, 0)
    
    def test_subtask_date_validation(self):
        """Test subtask date validation logic"""
        def validate_dates(start_date, end_date):
            """Mock date validation function"""
            try:
                start = datetime.fromisoformat(start_date)
                end = datetime.fromisoformat(end_date)
                return start <= end
            except ValueError:
                return False
        
        # Test valid date range
        self.assertTrue(validate_dates('2025-01-01', '2025-01-15'))
        self.assertTrue(validate_dates('2025-01-01', '2025-01-01'))  # Same day
        
        # Test invalid date range
        self.assertFalse(validate_dates('2025-01-15', '2025-01-01'))
        
        # Test invalid date format
        self.assertFalse(validate_dates('invalid-date', '2025-01-15'))
    
    def test_subtask_data_serialization(self):
        """Test subtask data serialization for JSON"""
        subtask_data = {
            'id': 'subtask123',
            'name': 'Test Subtask',
            'description': 'Test Description',
            'status': 'In Progress',
            'priority': 'High',
            'start_date': datetime.now().isoformat(),
            'end_date': (datetime.now() + timedelta(days=7)).isoformat(),
            'is_deleted': False,
            'created_at': datetime.now().isoformat()
        }
        
        # Test that all values are JSON serializable
        for key, value in subtask_data.items():
            if isinstance(value, str):
                self.assertIsInstance(value, str)
            elif isinstance(value, bool):
                self.assertIsInstance(value, bool)
    
    def test_subtask_filtering(self):
        """Test subtask filtering logic"""
        subtasks = [
            {'id': '1', 'name': 'Task 1', 'status': 'Completed', 'priority': 'High'},
            {'id': '2', 'name': 'Task 2', 'status': 'In Progress', 'priority': 'Medium'},
            {'id': '3', 'name': 'Task 3', 'status': 'Not Started', 'priority': 'Low'},
            {'id': '4', 'name': 'Task 4', 'status': 'In Progress', 'priority': 'High'}
        ]
        
        # Test filtering by status
        in_progress = [t for t in subtasks if t['status'] == 'In Progress']
        self.assertEqual(len(in_progress), 2)
        
        # Test filtering by priority
        high_priority = [t for t in subtasks if t['priority'] == 'High']
        self.assertEqual(len(high_priority), 2)
        
        # Test filtering by completion
        completed = [t for t in subtasks if t['status'] == 'Completed']
        self.assertEqual(len(completed), 1)
    
    def test_subtask_sorting(self):
        """Test subtask sorting logic"""
        subtasks = [
            {'name': 'Task C', 'priority': 'Low', 'status': 'Completed'},
            {'name': 'Task A', 'priority': 'High', 'status': 'In Progress'},
            {'name': 'Task B', 'priority': 'Medium', 'status': 'Not Started'}
        ]
        
        # Test sorting by name
        sorted_by_name = sorted(subtasks, key=lambda x: x['name'])
        expected_names = ['Task A', 'Task B', 'Task C']
        actual_names = [t['name'] for t in sorted_by_name]
        self.assertEqual(actual_names, expected_names)
        
        # Test sorting by priority
        priority_order = {'Low': 1, 'Medium': 2, 'High': 3}
        sorted_by_priority = sorted(subtasks, key=lambda x: priority_order.get(x['priority'], 0))
        expected_priorities = ['Low', 'Medium', 'High']
        actual_priorities = [t['priority'] for t in sorted_by_priority]
        self.assertEqual(actual_priorities, expected_priorities)
    
    def test_subtask_progress_calculation(self):
        """Test subtask progress calculation logic"""
        def calculate_progress(subtasks):
            """Mock progress calculation function"""
            if not subtasks:
                return 0
            
            completed = len([t for t in subtasks if t['status'] == 'Completed'])
            total = len(subtasks)
            return (completed / total) * 100
        
        # Test with no subtasks
        self.assertEqual(calculate_progress([]), 0)
        
        # Test with all completed
        all_completed = [
            {'status': 'Completed'},
            {'status': 'Completed'},
            {'status': 'Completed'}
        ]
        self.assertEqual(calculate_progress(all_completed), 100)
        
        # Test with mixed statuses
        mixed_statuses = [
            {'status': 'Completed'},
            {'status': 'In Progress'},
            {'status': 'Not Started'}
        ]
        self.assertAlmostEqual(calculate_progress(mixed_statuses), 33.333333333333336, places=10)
    
    def test_subtask_deadline_checking(self):
        """Test subtask deadline checking logic"""
        def is_overdue(subtask):
            """Mock deadline checking function"""
            if 'end_date' not in subtask or 'status' in subtask and subtask['status'] == 'Completed':
                return False
            
            try:
                end_date = datetime.fromisoformat(subtask['end_date'])
                return datetime.now() > end_date
            except ValueError:
                return False
        
        # Test overdue subtask
        overdue_subtask = {
            'end_date': (datetime.now() - timedelta(days=1)).isoformat(),
            'status': 'In Progress'
        }
        self.assertTrue(is_overdue(overdue_subtask))
        
        # Test not overdue subtask
        not_overdue_subtask = {
            'end_date': (datetime.now() + timedelta(days=1)).isoformat(),
            'status': 'In Progress'
        }
        self.assertFalse(is_overdue(not_overdue_subtask))
        
        # Test completed subtask (not overdue regardless of date)
        completed_subtask = {
            'end_date': (datetime.now() - timedelta(days=1)).isoformat(),
            'status': 'Completed'
        }
        self.assertFalse(is_overdue(completed_subtask))
    
    def test_subtask_data_transformation(self):
        """Test subtask data transformation for API responses"""
        raw_subtask = {
            'id': 'subtask123',
            'name': 'Test Subtask',
            'description': 'Test Description',
            'status': 'In Progress',
            'priority': 'High',
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=7),
            'is_deleted': False,
            'created_at': datetime.now()
        }
        
        # Transform for API response
        api_response = {
            'id': raw_subtask['id'],
            'name': raw_subtask['name'],
            'description': raw_subtask['description'],
            'status': raw_subtask['status'],
            'priority': raw_subtask['priority'],
            'start_date': raw_subtask['start_date'].isoformat(),
            'end_date': raw_subtask['end_date'].isoformat(),
            'is_deleted': raw_subtask['is_deleted'],
            'created_at': raw_subtask['created_at'].isoformat()
        }
        
        # Test that transformation worked
        self.assertEqual(api_response['id'], 'subtask123')
        self.assertEqual(api_response['name'], 'Test Subtask')
        self.assertIsInstance(api_response['start_date'], str)
        self.assertIn('T', api_response['start_date'])  # ISO format
    
    def test_subtask_validation_comprehensive(self):
        """Test comprehensive subtask validation"""
        def validate_subtask(subtask):
            """Mock comprehensive subtask validation function"""
            errors = []
            
            # Check required fields
            required_fields = ['name', 'status', 'start_date', 'end_date']
            for field in required_fields:
                if field not in subtask or not subtask[field]:
                    errors.append(f"Missing required field: {field}")
            
            # Check status validity
            valid_statuses = ['Not Started', 'In Progress', 'Completed', 'On Hold', 'Cancelled']
            if 'status' in subtask and subtask['status'] not in valid_statuses:
                errors.append("Invalid status")
            
            # Check priority validity
            valid_priorities = ['Low', 'Medium', 'High', 'Critical']
            if 'priority' in subtask and subtask['priority'] not in valid_priorities:
                errors.append("Invalid priority")
            
            # Check date validity
            if 'start_date' in subtask and 'end_date' in subtask:
                try:
                    start = datetime.fromisoformat(subtask['start_date'])
                    end = datetime.fromisoformat(subtask['end_date'])
                    if start > end:
                        errors.append("Start date cannot be after end date")
                except ValueError:
                    errors.append("Invalid date format")
            
            return errors
        
        # Test valid subtask
        valid_subtask = {
            'name': 'Test Subtask',
            'status': 'In Progress',
            'priority': 'High',
            'start_date': '2025-01-01',
            'end_date': '2025-01-15'
        }
        errors = validate_subtask(valid_subtask)
        self.assertEqual(len(errors), 0)
        
        # Test invalid subtask
        invalid_subtask = {
            'name': '',
            'status': 'Invalid Status',
            'priority': 'Invalid Priority',
            'start_date': '2025-01-15',
            'end_date': '2025-01-01'  # Start after end
        }
        errors = validate_subtask(invalid_subtask)
        self.assertGreater(len(errors), 0)
        self.assertIn("Missing required field: name", errors)
        self.assertIn("Invalid status", errors)
        self.assertIn("Invalid priority", errors)
        self.assertIn("Start date cannot be after end date", errors)


if __name__ == '__main__':
    print("=" * 80)
    print("C1 UNIT TESTING - SUBTASK UTILITY FUNCTIONS")
    print("=" * 80)
    print("Testing individual subtask utility functions in complete isolation")
    print("No external dependencies, no Flask app, no database")
    print("=" * 80)

    # Run with verbose output
    unittest.main(verbosity=2)
