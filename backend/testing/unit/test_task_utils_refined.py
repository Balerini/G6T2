"""
Refined Unit Tests for Task Utility Functions
Tests actual utility functions imported from utils module.
Following the pure function pattern from the example code.
"""
import unittest
import sys
import os
from datetime import datetime, date

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import actual utility functions (not redefined ones!)
from utils.task_utils import (
    parse_date_value,
    validate_priority_level,
    validate_task_data,
    format_task_status,
    calculate_task_duration,
    is_task_overdue,
    validate_subtask_data
)


class TestTaskUtilsRefined(unittest.TestCase):
    """Refined unit tests for task utility functions"""
    
    def test_parse_date_value_none(self):
        """Test parsing None value"""
        result = parse_date_value(None)
        self.assertIsNone(result)
    
    def test_parse_date_value_datetime(self):
        """Test parsing datetime object"""
        dt = datetime(2024, 1, 15, 10, 30)
        result = parse_date_value(dt)
        self.assertEqual(result, date(2024, 1, 15))
    
    def test_parse_date_value_iso_string(self):
        """Test parsing ISO date string"""
        result = parse_date_value("2024-01-15")
        self.assertEqual(result, date(2024, 1, 15))
    
    def test_parse_date_value_invalid_string(self):
        """Test parsing invalid date string"""
        result = parse_date_value("invalid-date")
        self.assertIsNone(result)
    
    def test_validate_priority_level_valid(self):
        """Test valid priority levels"""
        self.assertTrue(validate_priority_level(1))
        self.assertTrue(validate_priority_level(5))
        self.assertTrue(validate_priority_level(10))
        self.assertTrue(validate_priority_level("5"))
    
    def test_validate_priority_level_invalid(self):
        """Test invalid priority levels"""
        self.assertFalse(validate_priority_level(0))
        self.assertFalse(validate_priority_level(11))
        self.assertFalse(validate_priority_level("invalid"))
        self.assertFalse(validate_priority_level(None))
    
    def test_validate_task_data_valid(self):
        """Test valid task data"""
        valid_data = {
            'task_name': 'Test Task',
            'start_date': '2024-01-15',
            'priority_level': 5
        }
        errors = validate_task_data(valid_data)
        self.assertEqual(len(errors), 0)
    
    def test_validate_task_data_missing_fields(self):
        """Test task data with missing required fields"""
        invalid_data = {
            'task_name': 'Test Task'
            # Missing start_date and priority_level
        }
        errors = validate_task_data(invalid_data)
        self.assertGreater(len(errors), 0)
        self.assertIn("Required field missing: start_date", errors)
        self.assertIn("Required field missing: priority_level", errors)
    
    def test_validate_task_data_invalid_priority(self):
        """Test task data with invalid priority"""
        invalid_data = {
            'task_name': 'Test Task',
            'start_date': '2024-01-15',
            'priority_level': 15  # Invalid priority
        }
        errors = validate_task_data(invalid_data)
        self.assertIn("Priority level must be between 1 and 10", errors)
    
    def test_format_task_status(self):
        """Test task status formatting"""
        self.assertEqual(format_task_status('ongoing'), 'Ongoing')
        self.assertEqual(format_task_status('COMPLETED'), 'Completed')
        self.assertEqual(format_task_status('unknown_status'), 'Unknown_Status')
        self.assertEqual(format_task_status(''), 'Unknown')
        self.assertEqual(format_task_status(None), 'Unknown')
    
    def test_calculate_task_duration(self):
        """Test task duration calculation"""
        duration = calculate_task_duration('2024-01-01', '2024-01-10')
        self.assertEqual(duration, 9)
        
        # Test with invalid dates
        duration = calculate_task_duration('invalid', '2024-01-10')
        self.assertEqual(duration, 0)
    
    def test_is_task_overdue(self):
        """Test overdue task detection"""
        # Test with past date
        past_date = '2023-01-01'
        self.assertTrue(is_task_overdue(past_date))
        
        # Test with future date
        future_date = '2030-01-01'
        self.assertFalse(is_task_overdue(future_date))
        
        # Test with None
        self.assertFalse(is_task_overdue(None))
    
    def test_validate_subtask_data(self):
        """Test subtask data validation"""
        valid_data = {
            'subtask_name': 'Test Subtask',
            'start_date': '2024-01-15'
        }
        errors = validate_subtask_data(valid_data)
        self.assertEqual(len(errors), 0)
        
        # Test with missing fields
        invalid_data = {'subtask_name': 'Test'}
        errors = validate_subtask_data(invalid_data)
        self.assertIn("Required field missing: start_date", errors)


if __name__ == '__main__':
    print("=" * 80)
    print("REFINED UNIT TESTING - TASK UTILITIES")
    print("=" * 80)
    print("Testing actual utility functions imported from utils module")
    print("Following pure function pattern - no side effects, no external dependencies")
    print("=" * 80)
    
    unittest.main(verbosity=2)
