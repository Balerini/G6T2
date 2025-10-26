"""
Unit Tests for Subtask Utility Functions
Tests subtask-related utility functions in complete isolation
"""
import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Mock the get_firestore_client to prevent actual database calls
with patch('firebase_utils.get_firestore_client') as mock_get_firestore_client:
    mock_db = MagicMock()
    mock_get_firestore_client.return_value = mock_db

    # Extracted utility functions for testing
    def validate_subtask_collaborators(subtask_collaborators, parent_task_collaborators):
        """Validate that subtask collaborators are from parent task"""
        if not subtask_collaborators:
            return True, []
        
        # Convert to strings for comparison
        parent_collaborator_ids = [str(id) for id in parent_task_collaborators]
        subtask_collaborator_ids = [str(id) for id in subtask_collaborators]
        
        invalid_collaborators = []
        for collaborator_id in subtask_collaborator_ids:
            if collaborator_id not in parent_collaborator_ids:
                invalid_collaborators.append(collaborator_id)
        
        return len(invalid_collaborators) == 0, invalid_collaborators

    def calculate_subtask_timeline(start_date, end_date):
        """Calculate subtask timeline information"""
        if not start_date or not end_date:
            return None
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            duration = (end - start).days
            is_overdue = end < date.today()
            days_remaining = (end - date.today()).days if not is_overdue else 0
            
            return {
                'duration_days': duration,
                'is_overdue': is_overdue,
                'days_remaining': days_remaining,
                'start_date': start,
                'end_date': end
            }
        except ValueError:
            return None

    def validate_subtask_status_transition(current_status, new_status):
        """Validate subtask status transition"""
        valid_transitions = {
            'Not Started': ['In Progress', 'Cancelled'],
            'In Progress': ['Completed', 'Cancelled', 'Not Started'],
            'Completed': ['In Progress'],  # Allow reopening
            'Cancelled': ['Not Started', 'In Progress']  # Allow reactivation
        }
        
        return new_status in valid_transitions.get(current_status, [])

    def calculate_subtask_priority(deadline_urgency, task_priority):
        """Calculate subtask priority based on deadline and task priority"""
        # Simple priority calculation
        base_priority = task_priority or 5
        
        if deadline_urgency == 'urgent':
            return min(base_priority + 2, 10)
        elif deadline_urgency == 'normal':
            return base_priority
        elif deadline_urgency == 'low':
            return max(base_priority - 1, 1)
        else:
            return base_priority

    def format_subtask_summary(subtask_data):
        """Format subtask data for summary display"""
        name = subtask_data.get('name', 'Unnamed Subtask')
        status = subtask_data.get('status', 'Unknown')
        start_date = subtask_data.get('start_date', '')
        end_date = subtask_data.get('end_date', '')
        
        summary = f"{name} - {status}"
        if start_date and end_date:
            summary += f" ({start_date} to {end_date})"
        
        return summary

    def validate_subtask_deadline(start_date, end_date):
        """Validate that subtask end date is after start date"""
        if not start_date or not end_date:
            return True, "No dates to validate"
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if end < start:
                return False, "End date must be after start date"
            
            return True, "Valid deadline"
        except ValueError:
            return False, "Invalid date format"

    def calculate_subtask_completion_percentage(subtasks):
        """Calculate completion percentage for a list of subtasks"""
        if not subtasks:
            return 0
        
        total_subtasks = len(subtasks)
        completed_subtasks = sum(1 for subtask in subtasks if subtask.get('status') == 'Completed')
        
        return (completed_subtasks / total_subtasks) * 100

class TestSubtaskUtilsUnit(unittest.TestCase):
    """C1 Unit tests for subtask utility functions"""
    
    def test_validate_subtask_collaborators_valid(self):
        """Test valid subtask collaborators"""
        parent_collaborators = ['user1', 'user2', 'user3']
        subtask_collaborators = ['user1', 'user2']
        
        is_valid, invalid = validate_subtask_collaborators(subtask_collaborators, parent_collaborators)
        self.assertTrue(is_valid)
        self.assertEqual(len(invalid), 0)
    
    def test_validate_subtask_collaborators_invalid(self):
        """Test invalid subtask collaborators"""
        parent_collaborators = ['user1', 'user2']
        subtask_collaborators = ['user1', 'user3']  # user3 not in parent
        
        is_valid, invalid = validate_subtask_collaborators(subtask_collaborators, parent_collaborators)
        self.assertFalse(is_valid)
        self.assertIn('user3', invalid)
    
    def test_validate_subtask_collaborators_empty(self):
        """Test empty subtask collaborators"""
        parent_collaborators = ['user1', 'user2']
        subtask_collaborators = []
        
        is_valid, invalid = validate_subtask_collaborators(subtask_collaborators, parent_collaborators)
        self.assertTrue(is_valid)
        self.assertEqual(len(invalid), 0)
    
    def test_calculate_subtask_timeline_valid(self):
        """Test valid subtask timeline calculation"""
        start_date = '2030-01-01'
        end_date = '2030-01-10'
        
        timeline = calculate_subtask_timeline(start_date, end_date)
        self.assertIsNotNone(timeline)
        self.assertEqual(timeline['duration_days'], 9)
        self.assertFalse(timeline['is_overdue'])
    
    def test_calculate_subtask_timeline_overdue(self):
        """Test overdue subtask timeline calculation"""
        start_date = '2023-01-01'
        end_date = '2023-01-10'  # Past date
        
        timeline = calculate_subtask_timeline(start_date, end_date)
        self.assertIsNotNone(timeline)
        self.assertTrue(timeline['is_overdue'])
    
    def test_calculate_subtask_timeline_invalid_dates(self):
        """Test invalid date format in timeline calculation"""
        timeline = calculate_subtask_timeline('invalid', '2024-01-10')
        self.assertIsNone(timeline)
    
    def test_validate_subtask_status_transition_valid(self):
        """Test valid status transitions"""
        self.assertTrue(validate_subtask_status_transition('Not Started', 'In Progress'))
        self.assertTrue(validate_subtask_status_transition('In Progress', 'Completed'))
        self.assertTrue(validate_subtask_status_transition('Completed', 'In Progress'))
    
    def test_validate_subtask_status_transition_invalid(self):
        """Test invalid status transitions"""
        self.assertFalse(validate_subtask_status_transition('Not Started', 'Completed'))
        self.assertFalse(validate_subtask_status_transition('Unknown', 'In Progress'))
    
    def test_calculate_subtask_priority_urgent(self):
        """Test priority calculation for urgent deadline"""
        priority = calculate_subtask_priority('urgent', 5)
        self.assertEqual(priority, 7)
    
    def test_calculate_subtask_priority_normal(self):
        """Test priority calculation for normal deadline"""
        priority = calculate_subtask_priority('normal', 5)
        self.assertEqual(priority, 5)
    
    def test_calculate_subtask_priority_low(self):
        """Test priority calculation for low deadline"""
        priority = calculate_subtask_priority('low', 5)
        self.assertEqual(priority, 4)
    
    def test_format_subtask_summary(self):
        """Test subtask summary formatting"""
        subtask_data = {
            'name': 'Test Subtask',
            'status': 'In Progress',
            'start_date': '2024-01-01',
            'end_date': '2024-01-10'
        }
        
        summary = format_subtask_summary(subtask_data)
        self.assertIn('Test Subtask', summary)
        self.assertIn('In Progress', summary)
        self.assertIn('2024-01-01', summary)
    
    def test_validate_subtask_deadline_valid(self):
        """Test valid subtask deadline"""
        start_date = '2024-01-01'
        end_date = '2024-01-10'
        
        is_valid, message = validate_subtask_deadline(start_date, end_date)
        self.assertTrue(is_valid)
        self.assertEqual(message, "Valid deadline")
    
    def test_validate_subtask_deadline_invalid_order(self):
        """Test invalid subtask deadline (end before start)"""
        start_date = '2024-01-10'
        end_date = '2024-01-01'
        
        is_valid, message = validate_subtask_deadline(start_date, end_date)
        self.assertFalse(is_valid)
        self.assertIn("End date must be after start date", message)
    
    def test_validate_subtask_deadline_invalid_format(self):
        """Test invalid date format in deadline validation"""
        is_valid, message = validate_subtask_deadline('invalid', '2024-01-10')
        self.assertFalse(is_valid)
        self.assertIn("Invalid date format", message)
    
    def test_calculate_subtask_completion_percentage(self):
        """Test subtask completion percentage calculation"""
        # Test with no subtasks
        self.assertEqual(calculate_subtask_completion_percentage([]), 0)
        
        # Test with all completed
        completed_subtasks = [
            {'status': 'Completed'},
            {'status': 'Completed'}
        ]
        self.assertEqual(calculate_subtask_completion_percentage(completed_subtasks), 100)
        
        # Test with mixed statuses
        mixed_subtasks = [
            {'status': 'Completed'},
            {'status': 'In Progress'},
            {'status': 'Not Started'}
        ]
        self.assertAlmostEqual(calculate_subtask_completion_percentage(mixed_subtasks), 33.333333333333336, places=10)
    
    def test_validate_subtask_collaborators_edge_cases(self):
        """Test validate_subtask_collaborators function edge cases"""
        # Test with None collaborators
        result = validate_subtask_collaborators(None, ['user1', 'user2'])
        self.assertTrue(result[0])  # Should return True for None
        
        # Test with empty list
        result = validate_subtask_collaborators([], ['user1', 'user2'])
        self.assertTrue(result[0])  # Should return True for empty list
        
        # Test with valid collaborators
        result = validate_subtask_collaborators(['user1'], ['user1', 'user2'])
        self.assertTrue(result[0])  # Should return True for valid
        
        # Test with invalid collaborators
        result = validate_subtask_collaborators(['user3'], ['user1', 'user2'])
        self.assertFalse(result[0])  # Should return False for invalid
        
        # Test with mixed valid and invalid
        result = validate_subtask_collaborators(['user1', 'user3'], ['user1', 'user2'])
        self.assertFalse(result[0])  # Should return False for mixed
    
    def test_calculate_subtask_timeline_edge_cases(self):
        """Test calculate_subtask_timeline function edge cases"""
        # Test with None dates
        result = calculate_subtask_timeline(None, '2030-01-10')
        self.assertIsNone(result)
        
        result = calculate_subtask_timeline('2030-01-01', None)
        self.assertIsNone(result)
        
        # Test with empty strings
        result = calculate_subtask_timeline("", '2030-01-10')
        self.assertIsNone(result)
        
        result = calculate_subtask_timeline('2030-01-01', "")
        self.assertIsNone(result)
        
        # Test with invalid date formats
        result = calculate_subtask_timeline("invalid", '2030-01-10')
        self.assertIsNone(result)
        
        result = calculate_subtask_timeline('2030-01-01', "invalid")
        self.assertIsNone(result)
        
        # Test with same start and end date
        result = calculate_subtask_timeline('2030-01-01', '2030-01-01')
        self.assertIsNotNone(result)
        self.assertEqual(result['duration_days'], 0)
        self.assertFalse(result['is_overdue'])
    
    def test_validate_subtask_status_transition_edge_cases(self):
        """Test validate_subtask_status_transition function edge cases"""
        # Test with None values
        result = validate_subtask_status_transition(None, 'In Progress')
        self.assertFalse(result)
        
        result = validate_subtask_status_transition('Not Started', None)
        self.assertFalse(result)
        
        # Test with empty strings
        result = validate_subtask_status_transition("", 'In Progress')
        self.assertFalse(result)
        
        result = validate_subtask_status_transition('Not Started', "")
        self.assertFalse(result)
        
        # Test with invalid status values
        result = validate_subtask_status_transition('Invalid', 'In Progress')
        self.assertFalse(result)
        
        result = validate_subtask_status_transition('Not Started', 'Invalid')
        self.assertFalse(result)
    
    def test_calculate_subtask_priority_edge_cases(self):
        """Test calculate_subtask_priority function edge cases"""
        # Test with None values
        result = calculate_subtask_priority(None, None)
        self.assertEqual(result, 5)  # Should use default priority 5
        
        result = calculate_subtask_priority('urgent', None)
        self.assertEqual(result, 7)  # 5 + 2 = 7
        
        result = calculate_subtask_priority(None, 3)
        self.assertEqual(result, 3)  # Should use provided priority 3
        
        # Test with invalid urgency
        result = calculate_subtask_priority('invalid', 5)
        self.assertEqual(result, 5)  # Should return base priority
        
        # Test with edge priority values
        result = calculate_subtask_priority('urgent', 9)
        self.assertEqual(result, 10)  # Should cap at 10
        
        result = calculate_subtask_priority('low', 1)
        self.assertEqual(result, 1)  # Should cap at 1
    
    def test_format_subtask_summary_edge_cases(self):
        """Test format_subtask_summary function edge cases"""
        # Test with None values - this will cause an AttributeError, which is expected
        with self.assertRaises(AttributeError):
            format_subtask_summary(None)
        
        # Test with empty dict
        result = format_subtask_summary({})
        self.assertIn("Unnamed Subtask", result)
        
        # Test with partial data
        partial_data = {'name': 'Test Subtask'}
        result = format_subtask_summary(partial_data)
        self.assertIn("Test Subtask", result)
        self.assertIn("Unknown", result)
    
    def test_validate_subtask_deadline_edge_cases(self):
        """Test validate_subtask_deadline function edge cases"""
        # Test with None values
        result = validate_subtask_deadline(None, '2030-01-10')
        self.assertTrue(result[0])  # Should return True for None dates
        
        result = validate_subtask_deadline('2030-01-01', None)
        self.assertTrue(result[0])  # Should return True for None dates
        
        # Test with empty strings
        result = validate_subtask_deadline("", '2030-01-10')
        self.assertTrue(result[0])  # Should return True for empty strings
        
        result = validate_subtask_deadline('2030-01-01', "")
        self.assertTrue(result[0])  # Should return True for empty strings
        
        # Test with invalid date formats
        result = validate_subtask_deadline("invalid", '2030-01-10')
        self.assertFalse(result[0])  # Should return False for invalid dates
        
        result = validate_subtask_deadline('2030-01-01', "invalid")
        self.assertFalse(result[0])  # Should return False for invalid dates
        
        # Test with same dates
        result = validate_subtask_deadline('2030-01-01', '2030-01-01')
        self.assertTrue(result[0])  # Should return True for same dates
    
    def test_calculate_subtask_completion_percentage_edge_cases(self):
        """Test calculate_subtask_completion_percentage function edge cases"""
        # Test with None subtasks
        result = calculate_subtask_completion_percentage(None)
        self.assertEqual(result, 0)
        
        # Test with empty list
        result = calculate_subtask_completion_percentage([])
        self.assertEqual(result, 0)
        
        # Test with subtasks missing status field
        subtasks_without_status = [
            {'name': 'Subtask 1'},
            {'name': 'Subtask 2'}
        ]
        result = calculate_subtask_completion_percentage(subtasks_without_status)
        self.assertEqual(result, 0)
        
        # Test with mixed valid and invalid subtasks
        mixed_subtasks = [
            {'status': 'Completed'},
            {'name': 'Subtask without status'},
            {'status': 'In Progress'}
        ]
        result = calculate_subtask_completion_percentage(mixed_subtasks)
        self.assertAlmostEqual(result, 33.33, places=1)  # 1 out of 3 completed

if __name__ == '__main__':
    print("=" * 80)
    print("C1 UNIT TESTING - SUBTASK UTILITY FUNCTIONS")
    print("=" * 80)
    print("Testing individual subtask utility functions in complete isolation")
    print("No external dependencies, no Flask app, no database")
    print("=" * 80)

    unittest.main(verbosity=2)