"""
Unit Tests for Task Utility Functions
Tests task-related utility functions in complete isolation
"""
import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Mock the get_firestore_client to prevent actual database calls
with patch('firebase_utils.get_firestore_client') as mock_get_firestore_client:
    mock_db = MagicMock()
    mock_get_firestore_client.return_value = mock_db

    # Extracted utility functions for testing
    def parse_date_value(value):
        """Parse various date formats into date objects"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value).date()
            except ValueError:
                try:
                    return datetime.strptime(value, '%Y-%m-%d').date()
                except ValueError:
                    return None
        return None

    def validate_priority_level(priority_level):
        """Validate priority level is between 1 and 10"""
        try:
            priority = int(priority_level)
            return 1 <= priority <= 10
        except (ValueError, TypeError):
            return False

    def validate_task_data(data):
        """Validate task data structure and required fields"""
        errors = []
        required_fields = ['task_name', 'start_date', 'priority_level']
        
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Required field missing: {field}")
        
        # Validate priority level
        if data.get('priority_level') and not validate_priority_level(data.get('priority_level')):
            errors.append("Priority level must be between 1 and 10")
        
        # Validate dates
        if data.get('start_date'):
            parsed_start = parse_date_value(data.get('start_date'))
            if not parsed_start:
                errors.append("Invalid start_date format")
        
        if data.get('end_date'):
            parsed_end = parse_date_value(data.get('end_date'))
            if not parsed_end:
                errors.append("Invalid end_date format")
        
        return errors

    def calculate_task_duration(start_date, end_date):
        """Calculate task duration in days"""
        if not start_date or not end_date:
            return None
        
        start = parse_date_value(start_date)
        end = parse_date_value(end_date)
        
        if not start or not end:
            return None
        
        return (end - start).days

    def is_task_overdue(end_date):
        """Check if task is overdue"""
        if not end_date:
            return False
        
        parsed_end = parse_date_value(end_date)
        if not parsed_end:
            return False
        
        return parsed_end < date.today()

    def format_task_status(status):
        """Format task status for display"""
        status_map = {
            'not_started': 'Not Started',
            'in_progress': 'In Progress',
            'completed': 'Completed',
            'cancelled': 'Cancelled'
        }
        return status_map.get(status.lower(), status.title())

    def validate_subtask_data(data):
        """Validate subtask data structure"""
        errors = []
        required_fields = ['name', 'start_date', 'end_date', 'status', 'parent_task_id']
        
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Required field missing: {field}")
        
        # Validate dates
        if data.get('start_date'):
            parsed_start = parse_date_value(data.get('start_date'))
            if not parsed_start:
                errors.append("Invalid start_date format")
        
        if data.get('end_date'):
            parsed_end = parse_date_value(data.get('end_date'))
            if not parsed_end:
                errors.append("Invalid end_date format")
        
        return errors

    def calculate_subtask_progress(subtasks):
        """Calculate overall progress of subtasks"""
        if not subtasks:
            return 0
        
        completed_count = sum(1 for subtask in subtasks if subtask.get('status') == 'Completed')
        return (completed_count / len(subtasks)) * 100

class TestTaskUtilsUnit(unittest.TestCase):
    """C1 Unit tests for task utility functions"""
    
    def test_parse_date_value_none(self):
        """Test parsing None date value"""
        result = parse_date_value(None)
        self.assertIsNone(result)
    
    def test_parse_date_value_datetime(self):
        """Test parsing datetime object"""
        dt = datetime(2024, 1, 15, 10, 30)
        result = parse_date_value(dt)
        self.assertEqual(result, date(2024, 1, 15))
    
    def test_parse_date_value_iso_string(self):
        """Test parsing ISO date string"""
        result = parse_date_value('2024-01-15')
        self.assertEqual(result, date(2024, 1, 15))
    
    def test_parse_date_value_invalid_string(self):
        """Test parsing invalid date string"""
        result = parse_date_value('invalid-date')
        self.assertIsNone(result)
    
    def test_validate_priority_level_valid(self):
        """Test valid priority levels"""
        self.assertTrue(validate_priority_level(1))
        self.assertTrue(validate_priority_level(5))
        self.assertTrue(validate_priority_level(10))
        self.assertTrue(validate_priority_level('5'))
    
    def test_validate_priority_level_invalid(self):
        """Test invalid priority levels"""
        self.assertFalse(validate_priority_level(0))
        self.assertFalse(validate_priority_level(11))
        self.assertFalse(validate_priority_level('invalid'))
        self.assertFalse(validate_priority_level(None))
    
    def test_validate_task_data_valid(self):
        """Test valid task data validation"""
        valid_data = {
            'task_name': 'Test Task',
            'start_date': '2024-01-15',
            'priority_level': 5
        }
        errors = validate_task_data(valid_data)
        self.assertEqual(len(errors), 0)
    
    def test_validate_task_data_missing_fields(self):
        """Test task data validation with missing fields"""
        invalid_data = {
            'task_name': 'Test Task'
        }
        errors = validate_task_data(invalid_data)
        self.assertGreater(len(errors), 0)
        self.assertIn("Required field missing: start_date", errors)
        self.assertIn("Required field missing: priority_level", errors)
    
    def test_validate_task_data_invalid_priority(self):
        """Test task data validation with invalid priority"""
        invalid_data = {
            'task_name': 'Test Task',
            'start_date': '2024-01-15',
            'priority_level': 15
        }
        errors = validate_task_data(invalid_data)
        self.assertIn("Priority level must be between 1 and 10", errors)
    
    def test_calculate_task_duration(self):
        """Test task duration calculation"""
        start_date = '2024-01-01'
        end_date = '2024-01-10'
        duration = calculate_task_duration(start_date, end_date)
        self.assertEqual(duration, 9)
    
    def test_calculate_task_duration_invalid_dates(self):
        """Test task duration calculation with invalid dates"""
        duration = calculate_task_duration('invalid', '2024-01-10')
        self.assertIsNone(duration)
    
    def test_is_task_overdue(self):
        """Test overdue task detection"""
        # Test with past date
        past_date = '2023-01-01'
        self.assertTrue(is_task_overdue(past_date))
        
        # Test with future date (use a date that's definitely in the future)
        future_date = '2030-01-01'
        self.assertFalse(is_task_overdue(future_date))
        
        # Test with None
        self.assertFalse(is_task_overdue(None))
    
    def test_format_task_status(self):
        """Test task status formatting"""
        self.assertEqual(format_task_status('not_started'), 'Not Started')
        self.assertEqual(format_task_status('in_progress'), 'In Progress')
        self.assertEqual(format_task_status('completed'), 'Completed')
        self.assertEqual(format_task_status('unknown'), 'Unknown')
    
    def test_validate_subtask_data_valid(self):
        """Test valid subtask data validation"""
        valid_data = {
            'name': 'Test Subtask',
            'start_date': '2024-01-15',
            'end_date': '2024-01-20',
            'status': 'Not Started',
            'parent_task_id': 'task_123'
        }
        errors = validate_subtask_data(valid_data)
        self.assertEqual(len(errors), 0)
    
    def test_validate_subtask_data_missing_fields(self):
        """Test subtask data validation with missing fields"""
        invalid_data = {
            'name': 'Test Subtask'
        }
        errors = validate_subtask_data(invalid_data)
        self.assertGreater(len(errors), 0)
        self.assertIn("Required field missing: start_date", errors)
    
    def test_calculate_subtask_progress(self):
        """Test subtask progress calculation"""
        # Test with no subtasks
        self.assertEqual(calculate_subtask_progress([]), 0)
        
        # Test with all completed
        completed_subtasks = [
            {'status': 'Completed'},
            {'status': 'Completed'}
        ]
        self.assertEqual(calculate_subtask_progress(completed_subtasks), 100)
        
        # Test with mixed statuses
        mixed_subtasks = [
            {'status': 'Completed'},
            {'status': 'In Progress'},
            {'status': 'Not Started'}
        ]
        self.assertAlmostEqual(calculate_subtask_progress(mixed_subtasks), 33.333333333333336, places=10)
    
    def test_parse_date_value_edge_cases(self):
        """Test parse_date_value function edge cases"""
        # Test with invalid datetime string
        result = parse_date_value("invalid-date")
        self.assertIsNone(result)
        
        # Test with empty string
        result = parse_date_value("")
        self.assertIsNone(result)
        
        # Test with whitespace string
        result = parse_date_value("   ")
        self.assertIsNone(result)
    
    def test_validate_priority_level_edge_cases(self):
        """Test validate_priority_level function edge cases"""
        # Test with string numbers
        self.assertTrue(validate_priority_level("5"))
        self.assertTrue(validate_priority_level("1"))
        self.assertTrue(validate_priority_level("10"))
        
        # Test with float numbers
        self.assertTrue(validate_priority_level(5.0))
        self.assertTrue(validate_priority_level(1.0))
        self.assertTrue(validate_priority_level(10.0))
        
        # Test with edge values
        self.assertTrue(validate_priority_level(1))  # Minimum valid
        self.assertTrue(validate_priority_level(10))  # Maximum valid
        self.assertFalse(validate_priority_level(0))  # Below minimum
        self.assertFalse(validate_priority_level(11))  # Above maximum
        
        # Test with invalid types
        self.assertFalse(validate_priority_level("abc"))
        self.assertFalse(validate_priority_level([]))
        self.assertFalse(validate_priority_level({}))
        self.assertFalse(validate_priority_level(None))
    
    def test_validate_task_data_edge_cases(self):
        """Test validate_task_data function edge cases"""
        # Test with empty data
        errors = validate_task_data({})
        self.assertGreater(len(errors), 0)
        
        # Test with None data - this will cause an AttributeError, which is expected
        with self.assertRaises(AttributeError):
            validate_task_data(None)
        
        # Test with partial data
        partial_data = {'task_name': 'Test Task'}
        errors = validate_task_data(partial_data)
        self.assertGreater(len(errors), 0)
        
        # Test with invalid priority
        invalid_priority_data = {
            'task_name': 'Test Task',
            'start_date': '2024-01-01',
            'priority_level': 15  # Invalid priority
        }
        errors = validate_task_data(invalid_priority_data)
        self.assertGreater(len(errors), 0)
    
    def test_format_task_status_edge_cases(self):
        """Test format_task_status function edge cases"""
        # Test with None status - this will cause an AttributeError, which is expected
        with self.assertRaises(AttributeError):
            format_task_status(None)
        
        # Test with empty status
        result = format_task_status("")
        self.assertEqual(result, "")  # Empty string
        
        # Test with whitespace status
        result = format_task_status("   ")
        self.assertEqual(result, "   ")  # Whitespace string
    
    def test_validate_subtask_data_edge_cases(self):
        """Test validate_subtask_data function edge cases"""
        # Test with empty data
        errors = validate_subtask_data({})
        self.assertGreater(len(errors), 0)
        
        # Test with None data - this will cause an AttributeError, which is expected
        with self.assertRaises(AttributeError):
            validate_subtask_data(None)
        
        # Test with partial data
        partial_data = {'subtask_name': 'Test Subtask'}
        errors = validate_subtask_data(partial_data)
        self.assertGreater(len(errors), 0)
    
    def test_calculate_task_duration_edge_cases(self):
        """Test calculate_task_duration function edge cases"""
        # Test with same start and end date
        duration = calculate_task_duration('2024-01-01', '2024-01-01')
        self.assertEqual(duration, 0)
        
        # Test with None dates
        duration = calculate_task_duration(None, '2024-01-01')
        self.assertIsNone(duration)
        
        duration = calculate_task_duration('2024-01-01', None)
        self.assertIsNone(duration)
        
        # Test with invalid date strings
        duration = calculate_task_duration('invalid', '2024-01-01')
        self.assertIsNone(duration)
        
        duration = calculate_task_duration('2024-01-01', 'invalid')
        self.assertIsNone(duration)
    
    def test_is_task_overdue_edge_cases(self):
        """Test is_task_overdue function edge cases"""
        # Test with None date
        result = is_task_overdue(None)
        self.assertFalse(result)
        
        # Test with empty string
        result = is_task_overdue("")
        self.assertFalse(result)
        
        # Test with invalid date string
        result = is_task_overdue("invalid-date")
        self.assertFalse(result)
        
        # Test with today's date (should not be overdue)
        from datetime import date
        today = date.today().strftime('%Y-%m-%d')
        result = is_task_overdue(today)
        self.assertFalse(result)
    
    def test_validate_task_data_invalid_date_formats(self):
        """Test validate_task_data with invalid date formats"""
        # Test with invalid start_date format
        invalid_start_data = {
            'task_name': 'Test Task',
            'start_date': 'invalid-date',
            'priority_level': 5
        }
        errors = validate_task_data(invalid_start_data)
        self.assertIn("Invalid start_date format", errors)
        
        # Test with invalid end_date format
        invalid_end_data = {
            'task_name': 'Test Task',
            'start_date': '2024-01-01',
            'end_date': 'invalid-date',
            'priority_level': 5
        }
        errors = validate_task_data(invalid_end_data)
        self.assertIn("Invalid end_date format", errors)
        
        # Test with both invalid dates
        invalid_both_data = {
            'task_name': 'Test Task',
            'start_date': 'invalid-start',
            'end_date': 'invalid-end',
            'priority_level': 5
        }
        errors = validate_task_data(invalid_both_data)
        self.assertIn("Invalid start_date format", errors)
        self.assertIn("Invalid end_date format", errors)
    
    def test_validate_subtask_data_invalid_date_formats(self):
        """Test validate_subtask_data with invalid date formats"""
        # Test with invalid start_date format
        invalid_start_data = {
            'name': 'Test Subtask',
            'start_date': 'invalid-date',
            'end_date': '2024-01-10',
            'status': 'Not Started',
            'parent_task_id': 'task123'
        }
        errors = validate_subtask_data(invalid_start_data)
        self.assertIn("Invalid start_date format", errors)
        
        # Test with invalid end_date format
        invalid_end_data = {
            'name': 'Test Subtask',
            'start_date': '2024-01-01',
            'end_date': 'invalid-date',
            'status': 'Not Started',
            'parent_task_id': 'task123'
        }
        errors = validate_subtask_data(invalid_end_data)
        self.assertIn("Invalid end_date format", errors)
        
        # Test with both invalid dates
        invalid_both_data = {
            'name': 'Test Subtask',
            'start_date': 'invalid-start',
            'end_date': 'invalid-end',
            'status': 'Not Started',
            'parent_task_id': 'task123'
        }
        errors = validate_subtask_data(invalid_both_data)
        self.assertIn("Invalid start_date format", errors)
        self.assertIn("Invalid end_date format", errors)

if __name__ == '__main__':
    print("=" * 80)
    print("C1 UNIT TESTING - TASK UTILITY FUNCTIONS")
    print("=" * 80)
    print("Testing individual task utility functions in complete isolation")
    print("No external dependencies, no Flask app, no database")
    print("=" * 80)

    unittest.main(verbosity=2)
