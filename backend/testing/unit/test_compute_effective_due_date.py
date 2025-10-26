#!/usr/bin/env python3
"""
C1 Unit Tests for compute_effective_due_date function
Tests the pure function that determines effective due dates considering recurrence rules.
"""

import unittest
import sys
import os
from datetime import datetime, date, timedelta

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the function for unit testing
from routes.dashboard import compute_effective_due_date


class TestComputeEffectiveDueDateUnit(unittest.TestCase):
    """C1 Unit tests for compute_effective_due_date function"""

    def test_compute_effective_due_date_no_recurrence(self):
        """Test with no recurrence enabled"""
        task_data = {
            'end_date': '2024-01-15',
            'start_date': '2024-01-10',
            'recurrence': {'enabled': False}
        }
        current_date = datetime(2024, 1, 12).date()
        
        due_date, is_recurring = compute_effective_due_date(task_data, current_date)
        
        self.assertEqual(due_date, date(2024, 1, 15))
        self.assertFalse(is_recurring)

    def test_compute_effective_due_date_no_recurrence_data(self):
        """Test with no recurrence data"""
        task_data = {
            'end_date': '2024-01-15',
            'start_date': '2024-01-10'
        }
        current_date = datetime(2024, 1, 12).date()
        
        due_date, is_recurring = compute_effective_due_date(task_data, current_date)
        
        self.assertEqual(due_date, date(2024, 1, 15))
        self.assertFalse(is_recurring)

    def test_compute_effective_due_date_no_end_date(self):
        """Test with no end date, using start date"""
        task_data = {
            'start_date': '2024-01-15',
            'recurrence': {'enabled': False}
        }
        current_date = datetime(2024, 1, 12).date()
        
        due_date, is_recurring = compute_effective_due_date(task_data, current_date)
        
        self.assertEqual(due_date, date(2024, 1, 15))
        self.assertFalse(is_recurring)

    def test_compute_effective_due_date_no_dates(self):
        """Test with no dates at all"""
        task_data = {
            'recurrence': {'enabled': False}
        }
        current_date = datetime(2024, 1, 12).date()
        
        due_date, is_recurring = compute_effective_due_date(task_data, current_date)
        
        self.assertIsNone(due_date)
        self.assertFalse(is_recurring)

    def test_compute_effective_due_date_recurrence_no_base_date(self):
        """Test recurrence with no base due date"""
        task_data = {
            'recurrence': {
                'enabled': True,
                'frequency': 'daily',
                'interval': 1
            }
        }
        current_date = datetime(2024, 1, 12).date()
        
        due_date, is_recurring = compute_effective_due_date(task_data, current_date)
        
        self.assertIsNone(due_date)
        self.assertTrue(is_recurring)

    def test_compute_effective_due_date_daily_recurrence(self):
        """Test daily recurrence"""
        task_data = {
            'end_date': '2024-01-10',
            'start_date': '2024-01-10',
            'recurrence': {
                'enabled': True,
                'frequency': 'daily',
                'interval': 1
            }
        }
        current_date = datetime(2024, 1, 12).date()
        
        due_date, is_recurring = compute_effective_due_date(task_data, current_date)
        
        self.assertIsNotNone(due_date)
        self.assertTrue(is_recurring)
        self.assertGreaterEqual(due_date, current_date)

    def test_compute_effective_due_date_weekly_recurrence(self):
        """Test weekly recurrence"""
        task_data = {
            'end_date': '2024-01-10',
            'start_date': '2024-01-10',
            'recurrence': {
                'enabled': True,
                'frequency': 'weekly',
                'interval': 1,
                'weeklyDays': [1, 3, 5]  # Tue, Thu, Sat
            }
        }
        current_date = datetime(2024, 1, 12).date()
        
        due_date, is_recurring = compute_effective_due_date(task_data, current_date)
        
        self.assertIsNotNone(due_date)
        self.assertTrue(is_recurring)
        self.assertGreaterEqual(due_date, current_date)

    def test_compute_effective_due_date_monthly_recurrence(self):
        """Test monthly recurrence"""
        task_data = {
            'end_date': '2024-01-15',
            'start_date': '2024-01-15',
            'recurrence': {
                'enabled': True,
                'frequency': 'monthly',
                'interval': 1,
                'monthlyDay': 15
            }
        }
        current_date = datetime(2024, 1, 12).date()
        
        due_date, is_recurring = compute_effective_due_date(task_data, current_date)
        
        self.assertIsNotNone(due_date)
        self.assertTrue(is_recurring)
        self.assertGreaterEqual(due_date, current_date)

    def test_compute_effective_due_date_end_after_occurrences(self):
        """Test recurrence with end after occurrences"""
        task_data = {
            'end_date': '2024-01-10',
            'start_date': '2024-01-10',
            'recurrence': {
                'enabled': True,
                'frequency': 'daily',
                'interval': 1,
                'endCondition': 'after',
                'endAfterOccurrences': 5
            }
        }
        current_date = datetime(2024, 1, 12).date()
        
        due_date, is_recurring = compute_effective_due_date(task_data, current_date)
        
        self.assertIsNotNone(due_date)
        self.assertTrue(is_recurring)

    def test_compute_effective_due_date_end_on_date(self):
        """Test recurrence with end on specific date"""
        task_data = {
            'end_date': '2024-01-10',
            'start_date': '2024-01-10',
            'recurrence': {
                'enabled': True,
                'frequency': 'daily',
                'interval': 1,
                'endCondition': 'ondate',
                'endDate': '2024-01-20'
            }
        }
        current_date = datetime(2024, 1, 12).date()
        
        due_date, is_recurring = compute_effective_due_date(task_data, current_date)
        
        self.assertIsNotNone(due_date)
        self.assertTrue(is_recurring)
        self.assertLessEqual(due_date, date(2024, 1, 20))

    def test_compute_effective_due_date_end_after_invalid(self):
        """Test recurrence with invalid end after occurrences"""
        task_data = {
            'end_date': '2024-01-10',
            'start_date': '2024-01-10',
            'recurrence': {
                'enabled': True,
                'frequency': 'daily',
                'interval': 1,
                'endCondition': 'after',
                'endAfterOccurrences': 0  # Invalid - should be ignored
            }
        }
        current_date = datetime(2024, 1, 12).date()
        
        due_date, is_recurring = compute_effective_due_date(task_data, current_date)
        
        self.assertIsNotNone(due_date)
        self.assertTrue(is_recurring)

    def test_compute_effective_due_date_edge_cases(self):
        """Test edge cases"""
        # Test with empty task data
        due_date, is_recurring = compute_effective_due_date({}, datetime(2024, 1, 12).date())
        self.assertIsNone(due_date)
        self.assertFalse(is_recurring)
        
        # Test with None task data - this should cause an AttributeError
        with self.assertRaises(AttributeError):
            compute_effective_due_date(None, datetime(2024, 1, 12).date())
        
        # Test with invalid date strings
        task_data = {
            'end_date': 'invalid-date',
            'start_date': 'also-invalid',
            'recurrence': {'enabled': False}
        }
        due_date, is_recurring = compute_effective_due_date(task_data, datetime(2024, 1, 12).date())
        self.assertIsNone(due_date)
        self.assertFalse(is_recurring)

    def test_compute_effective_due_date_custom_frequency(self):
        """Test custom frequency recurrence"""
        task_data = {
            'end_date': '2024-01-10',
            'start_date': '2024-01-10',
            'recurrence': {
                'enabled': True,
                'frequency': 'custom',
                'interval': 3,
                'customUnit': 'days'
            }
        }
        current_date = datetime(2024, 1, 12).date()
        
        due_date, is_recurring = compute_effective_due_date(task_data, current_date)
        
        self.assertIsNotNone(due_date)
        self.assertTrue(is_recurring)

    def test_compute_effective_due_date_invalid_frequency(self):
        """Test with invalid frequency"""
        task_data = {
            'end_date': '2024-01-10',
            'start_date': '2024-01-10',
            'recurrence': {
                'enabled': True,
                'frequency': 'invalid',
                'interval': 1
            }
        }
        current_date = datetime(2024, 1, 12).date()
        
        due_date, is_recurring = compute_effective_due_date(task_data, current_date)
        
        # Should return current date or later when frequency is invalid
        self.assertIsNotNone(due_date)
        self.assertTrue(is_recurring)
        self.assertGreaterEqual(due_date, current_date)

    def test_compute_effective_due_date_zero_interval(self):
        """Test with zero interval"""
        task_data = {
            'end_date': '2024-01-10',
            'start_date': '2024-01-10',
            'recurrence': {
                'enabled': True,
                'frequency': 'daily',
                'interval': 0  # Should default to 1
            }
        }
        current_date = datetime(2024, 1, 12).date()
        
        due_date, is_recurring = compute_effective_due_date(task_data, current_date)
        
        self.assertIsNotNone(due_date)
        self.assertTrue(is_recurring)

    def test_compute_effective_due_date_negative_interval(self):
        """Test with negative interval"""
        task_data = {
            'end_date': '2024-01-10',
            'start_date': '2024-01-10',
            'recurrence': {
                'enabled': True,
                'frequency': 'daily',
                'interval': -5  # Should default to 1
            }
        }
        current_date = datetime(2024, 1, 12).date()
        
        due_date, is_recurring = compute_effective_due_date(task_data, current_date)
        
        self.assertIsNotNone(due_date)
        self.assertTrue(is_recurring)


if __name__ == '__main__':
    print("=" * 80)
    print("C1 UNIT TESTING - COMPUTE EFFECTIVE DUE DATE")
    print("=" * 80)
    print("Testing individual compute_effective_due_date function in complete isolation")
    print("No external dependencies, no Flask app, no database")
    print("=" * 80)

    # Run with verbose output
    unittest.main(verbosity=2)
