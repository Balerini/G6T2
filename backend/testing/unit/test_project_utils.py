"""
Unit Tests for Project Utility Functions
Tests project-related utility functions in complete isolation
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
    def validate_project_data(data):
        """Validate project data structure and required fields"""
        errors = []
        required_fields = ['proj_name', 'proj_desc', 'start_date', 'end_date']
        
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Required field missing: {field}")
        
        # Validate dates
        if data.get('start_date') and data.get('end_date'):
            try:
                start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
                if end_date < start_date:
                    errors.append("End date must be after start date")
            except ValueError:
                errors.append("Invalid date format")
        
        return errors

    def calculate_project_duration(start_date, end_date):
        """Calculate project duration in days"""
        if not start_date or not end_date:
            return None
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            return (end - start).days
        except ValueError:
            return None

    def is_project_overdue(end_date):
        """Check if project is overdue"""
        if not end_date:
            return False
        
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            return end < date.today()
        except ValueError:
            return False

    def calculate_project_progress(tasks):
        """Calculate project progress based on tasks"""
        if not tasks:
            return 0
        
        completed_tasks = sum(1 for task in tasks if task.get('task_status') == 'Completed')
        return (completed_tasks / len(tasks)) * 100

    def validate_collaborator_assignment(collaborators, max_collaborators=10):
        """Validate collaborator assignment"""
        if not collaborators:
            return True, []
        
        if len(collaborators) > max_collaborators:
            return False, [f"Maximum {max_collaborators} collaborators allowed"]
        
        # Check for duplicate collaborators
        unique_collaborators = set(collaborators)
        if len(unique_collaborators) != len(collaborators):
            return False, ["Duplicate collaborators found"]
        
        return True, []

    def format_project_status(status):
        """Format project status for display"""
        status_map = {
            'active': 'Active',
            'completed': 'Completed',
            'cancelled': 'Cancelled',
            'on_hold': 'On Hold'
        }
        return status_map.get(status.lower(), status.title())

    def calculate_project_priority(deadline_urgency, complexity):
        """Calculate project priority based on deadline and complexity"""
        base_priority = 5
        
        # Adjust for deadline urgency
        if deadline_urgency == 'urgent':
            base_priority += 3
        elif deadline_urgency == 'high':
            base_priority += 2
        elif deadline_urgency == 'normal':
            base_priority += 1
        
        # Adjust for complexity
        if complexity == 'high':
            base_priority += 2
        elif complexity == 'medium':
            base_priority += 1
        
        return min(base_priority, 10)

    def validate_project_name(name):
        """Validate project name"""
        if not name or not name.strip():
            return False, "Project name cannot be empty"
        
        if len(name.strip()) < 3:
            return False, "Project name must be at least 3 characters"
        
        if len(name) > 100:
            return False, "Project name must be less than 100 characters"
        
        return True, "Valid project name"

    def calculate_project_metrics(tasks):
        """Calculate various project metrics"""
        if not tasks:
            return {
                'total_tasks': 0,
                'completed_tasks': 0,
                'in_progress_tasks': 0,
                'not_started_tasks': 0,
                'completion_percentage': 0
            }
        
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task.get('task_status') == 'Completed')
        in_progress_tasks = sum(1 for task in tasks if task.get('task_status') == 'In Progress')
        not_started_tasks = sum(1 for task in tasks if task.get('task_status') == 'Not Started')
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'not_started_tasks': not_started_tasks,
            'completion_percentage': (completed_tasks / total_tasks) * 100
        }

    def format_project_summary(project_data):
        """Format project data for summary display"""
        name = project_data.get('proj_name', 'Unnamed Project')
        status = project_data.get('status', 'Unknown')
        start_date = project_data.get('start_date', '')
        end_date = project_data.get('end_date', '')
        
        summary = f"{name} - {status}"
        if start_date and end_date:
            summary += f" ({start_date} to {end_date})"
        
        return summary

    def validate_project_dates(start_date, end_date):
        """Validate project date logic"""
        if not start_date or not end_date:
            return True, "No dates to validate"
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if end < start:
                return False, "End date must be after start date"
            
            # Check if project duration is reasonable (not more than 5 years)
            duration = (end - start).days
            if duration > 1825:  # 5 years
                return False, "Project duration should not exceed 5 years"
            
            return True, "Valid project dates"
        except ValueError:
            return False, "Invalid date format"

class TestProjectUtilsUnit(unittest.TestCase):
    """C1 Unit tests for project utility functions"""
    
    def test_validate_project_data_valid(self):
        """Test valid project data validation"""
        valid_data = {
            'proj_name': 'Test Project',
            'proj_desc': 'Test Description',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        }
        errors = validate_project_data(valid_data)
        self.assertEqual(len(errors), 0)
    
    def test_validate_project_data_missing_fields(self):
        """Test project data validation with missing fields"""
        invalid_data = {
            'proj_name': 'Test Project'
        }
        errors = validate_project_data(invalid_data)
        self.assertGreater(len(errors), 0)
        self.assertIn("Required field missing: proj_desc", errors)
    
    def test_validate_project_data_invalid_dates(self):
        """Test project data validation with invalid date order"""
        invalid_data = {
            'proj_name': 'Test Project',
            'proj_desc': 'Test Description',
            'start_date': '2024-12-31',
            'end_date': '2024-01-01'
        }
        errors = validate_project_data(invalid_data)
        self.assertIn("End date must be after start date", errors)
    
    def test_calculate_project_duration(self):
        """Test project duration calculation"""
        start_date = '2024-01-01'
        end_date = '2024-12-31'
        duration = calculate_project_duration(start_date, end_date)
        self.assertEqual(duration, 365)
    
    def test_calculate_project_duration_invalid_dates(self):
        """Test project duration calculation with invalid dates"""
        duration = calculate_project_duration('invalid', '2024-12-31')
        self.assertIsNone(duration)
    
    def test_is_project_overdue(self):
        """Test overdue project detection"""
        # Test with past date
        past_date = '2023-01-01'
        self.assertTrue(is_project_overdue(past_date))
        
        # Test with future date
        future_date = '2030-01-01'
        self.assertFalse(is_project_overdue(future_date))
        
        # Test with None
        self.assertFalse(is_project_overdue(None))
    
    def test_calculate_project_progress(self):
        """Test project progress calculation"""
        # Test with no tasks
        self.assertEqual(calculate_project_progress([]), 0)
        
        # Test with all completed
        completed_tasks = [
            {'task_status': 'Completed'},
            {'task_status': 'Completed'}
        ]
        self.assertEqual(calculate_project_progress(completed_tasks), 100)
        
        # Test with mixed statuses
        mixed_tasks = [
            {'task_status': 'Completed'},
            {'task_status': 'In Progress'},
            {'task_status': 'Not Started'}
        ]
        self.assertAlmostEqual(calculate_project_progress(mixed_tasks), 33.333333333333336, places=10)
    
    def test_validate_collaborator_assignment_valid(self):
        """Test valid collaborator assignment"""
        collaborators = ['user1', 'user2', 'user3']
        is_valid, errors = validate_collaborator_assignment(collaborators)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_collaborator_assignment_too_many(self):
        """Test collaborator assignment with too many collaborators"""
        collaborators = ['user' + str(i) for i in range(15)]  # 15 collaborators
        is_valid, errors = validate_collaborator_assignment(collaborators, max_collaborators=10)
        self.assertFalse(is_valid)
        self.assertIn("Maximum 10 collaborators allowed", errors)
    
    def test_validate_collaborator_assignment_duplicates(self):
        """Test collaborator assignment with duplicates"""
        collaborators = ['user1', 'user2', 'user1']  # Duplicate user1
        is_valid, errors = validate_collaborator_assignment(collaborators)
        self.assertFalse(is_valid)
        self.assertIn("Duplicate collaborators found", errors)
    
    def test_format_project_status(self):
        """Test project status formatting"""
        self.assertEqual(format_project_status('active'), 'Active')
        self.assertEqual(format_project_status('completed'), 'Completed')
        self.assertEqual(format_project_status('cancelled'), 'Cancelled')
        self.assertEqual(format_project_status('unknown'), 'Unknown')
    
    def test_calculate_project_priority(self):
        """Test project priority calculation"""
        # Test urgent + high complexity
        priority = calculate_project_priority('urgent', 'high')
        self.assertEqual(priority, 10)  # 5 + 3 + 2 = 10 (capped)
        
        # Test normal + medium complexity
        priority = calculate_project_priority('normal', 'medium')
        self.assertEqual(priority, 7)  # 5 + 1 + 1 = 7
        
        # Test low + low complexity
        priority = calculate_project_priority('low', 'low')
        self.assertEqual(priority, 5)  # 5 + 0 + 0 = 5
    
    def test_validate_project_name_valid(self):
        """Test valid project name validation"""
        is_valid, message = validate_project_name('Valid Project Name')
        self.assertTrue(is_valid)
        self.assertEqual(message, "Valid project name")
    
    def test_validate_project_name_invalid(self):
        """Test invalid project name validation"""
        # Test empty name
        is_valid, message = validate_project_name('')
        self.assertFalse(is_valid)
        self.assertIn("cannot be empty", message)
        
        # Test too short
        is_valid, message = validate_project_name('AB')
        self.assertFalse(is_valid)
        self.assertIn("at least 3 characters", message)
        
        # Test too long
        long_name = 'A' * 101
        is_valid, message = validate_project_name(long_name)
        self.assertFalse(is_valid)
        self.assertIn("less than 100 characters", message)
    
    def test_calculate_project_metrics(self):
        """Test project metrics calculation"""
        tasks = [
            {'task_status': 'Completed'},
            {'task_status': 'In Progress'},
            {'task_status': 'Not Started'}
        ]
        
        metrics = calculate_project_metrics(tasks)
        self.assertEqual(metrics['total_tasks'], 3)
        self.assertEqual(metrics['completed_tasks'], 1)
        self.assertEqual(metrics['in_progress_tasks'], 1)
        self.assertEqual(metrics['not_started_tasks'], 1)
        self.assertAlmostEqual(metrics['completion_percentage'], 33.333333333333336, places=10)
    
    def test_calculate_project_metrics_empty(self):
        """Test project metrics calculation with no tasks"""
        metrics = calculate_project_metrics([])
        self.assertEqual(metrics['total_tasks'], 0)
        self.assertEqual(metrics['completion_percentage'], 0)
    
    def test_format_project_summary(self):
        """Test project summary formatting"""
        project_data = {
            'proj_name': 'Test Project',
            'status': 'Active',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        }
        
        summary = format_project_summary(project_data)
        self.assertIn('Test Project', summary)
        self.assertIn('Active', summary)
        self.assertIn('2024-01-01', summary)
    
    def test_validate_project_dates_valid(self):
        """Test valid project dates validation"""
        is_valid, message = validate_project_dates('2024-01-01', '2024-12-31')
        self.assertTrue(is_valid)
        self.assertEqual(message, "Valid project dates")
    
    def test_calculate_project_priority_comprehensive(self):
        """Test calculate_project_priority with comprehensive scenarios"""
        # Test with high deadline urgency
        result = calculate_project_priority('urgent', 'medium')
        self.assertEqual(result, 8)  # 5 + 3 = 8
        
        # Test with high complexity
        result = calculate_project_priority('normal', 'high')
        self.assertEqual(result, 8)  # 5 + 1 + 2 = 8
        
        # Test with both high urgency and complexity
        result = calculate_project_priority('urgent', 'high')
        self.assertEqual(result, 10)  # 5 + 3 + 2 = 10, capped at 10
        
        # Test with medium complexity
        result = calculate_project_priority('normal', 'medium')
        self.assertEqual(result, 7)  # 5 + 1 + 1 = 7
        
        # Test with low urgency and complexity
        result = calculate_project_priority('low', 'low')
        self.assertEqual(result, 5)  # 5 + 0 + 0 = 5
        
        # Test edge case - priority caps at 10
        result = calculate_project_priority('urgent', 'high')
        self.assertEqual(result, 10)  # 5 + 3 + 2 = 10, capped at 10
    
    def test_validate_project_dates_comprehensive(self):
        """Test validate_project_dates with comprehensive scenarios"""
        # Test with None dates
        result = validate_project_dates(None, '2024-01-10')
        self.assertTrue(result[0])  # Should return True for None dates
        
        result = validate_project_dates('2024-01-01', None)
        self.assertTrue(result[0])  # Should return True for None dates
        
        # Test with empty strings
        result = validate_project_dates("", '2024-01-10')
        self.assertTrue(result[0])  # Should return True for empty strings
        
        result = validate_project_dates('2024-01-01', "")
        self.assertTrue(result[0])  # Should return True for empty strings
        
        # Test with invalid date formats
        result = validate_project_dates("invalid", '2024-01-10')
        self.assertFalse(result[0])  # Should return False for invalid dates
        
        result = validate_project_dates('2024-01-01', "invalid")
        self.assertFalse(result[0])  # Should return False for invalid dates
        
        # Test with same dates
        result = validate_project_dates('2024-01-01', '2024-01-01')
        self.assertTrue(result[0])  # Should return True for same dates
        
        # Test with very long duration (more than 5 years)
        result = validate_project_dates('2020-01-01', '2030-01-01')
        self.assertFalse(result[0])  # Should return False for very long duration
    
    def test_validate_project_dates_invalid_order(self):
        """Test invalid project dates (end before start)"""
        is_valid, message = validate_project_dates('2024-12-31', '2024-01-01')
        self.assertFalse(is_valid)
        self.assertIn("End date must be after start date", message)
    
    def test_validate_project_dates_too_long(self):
        """Test project dates with too long duration"""
        is_valid, message = validate_project_dates('2020-01-01', '2030-01-01')
        self.assertFalse(is_valid)
        self.assertIn("should not exceed 5 years", message)
    
    def test_validate_project_dates_invalid_format(self):
        """Test project dates with invalid format"""
        is_valid, message = validate_project_dates('invalid', '2024-12-31')
        self.assertFalse(is_valid)
        self.assertIn("Invalid date format", message)

if __name__ == '__main__':
    print("=" * 80)
    print("C1 UNIT TESTING - PROJECT UTILITY FUNCTIONS")
    print("=" * 80)
    print("Testing individual project utility functions in complete isolation")
    print("No external dependencies, no Flask app, no database")
    print("=" * 80)

    unittest.main(verbosity=2)
