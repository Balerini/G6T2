"""
Refined Unit Tests for Dashboard Utility Functions
Tests actual utility functions imported from utils module.
Following the pure function pattern from the example code.
"""
import unittest
import sys
import os
from datetime import datetime, date, timedelta

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import actual utility functions (not redefined ones!)
from utils.dashboard_utils import (
    safe_int,
    to_date,
    add_months,
    get_weekly_days,
    align_weekly,
    advance_weekly,
    align_monthly,
    advance_monthly,
    validate_dashboard_filters
)


class TestDashboardUtilsRefined(unittest.TestCase):
    """Refined unit tests for dashboard utility functions"""
    
    def test_safe_int_valid(self):
        """Test safe_int with valid values"""
        self.assertEqual(safe_int(5), 5)
        self.assertEqual(safe_int("10"), 10)
        self.assertEqual(safe_int(3.7), 3)
    
    def test_safe_int_invalid(self):
        """Test safe_int with invalid values"""
        self.assertIsNone(safe_int("invalid"))
        self.assertIsNone(safe_int(None))
        self.assertEqual(safe_int("invalid", 0), 0)
    
    def test_to_date_valid(self):
        """Test to_date with valid values"""
        dt = datetime(2024, 1, 15, 10, 30)
        self.assertEqual(to_date(dt), date(2024, 1, 15))
        self.assertEqual(to_date("2024-01-15"), date(2024, 1, 15))
    
    def test_to_date_invalid(self):
        """Test to_date with invalid values"""
        self.assertIsNone(to_date(None))
        self.assertIsNone(to_date("invalid-date"))
        self.assertIsNone(to_date(123))
    
    def test_add_months(self):
        """Test add_months function"""
        base_date = date(2024, 1, 15)
        result = add_months(base_date, 1)
        self.assertEqual(result, date(2024, 2, 15))
        
        # Test month-end edge case
        base_date = date(2024, 1, 31)
        result = add_months(base_date, 1)
        self.assertEqual(result, date(2024, 2, 29))  # 2024 is leap year
    
    def test_get_weekly_days(self):
        """Test get_weekly_days function"""
        recurrence = {'weeklyDays': [1, 3, 5]}  # Tue, Thu, Sat
        result = get_weekly_days(recurrence, 0)
        self.assertEqual(result, [1, 3, 5])
        
        # Test with string days
        recurrence = {'weeklyDays': ['mon', 'wed', 'fri']}
        result = get_weekly_days(recurrence, 0)
        self.assertEqual(result, [0, 2, 4])
        
        # Test with empty list
        recurrence = {'weeklyDays': []}
        result = get_weekly_days(recurrence, 3)
        self.assertEqual(result, [3])  # Should use fallback
    
    def test_align_weekly(self):
        """Test align_weekly function"""
        start_date = date(2024, 1, 1)  # Monday
        weekly_days = [1, 3]  # Tuesday, Thursday
        result = align_weekly(start_date, weekly_days, 1)
        self.assertEqual(result, date(2024, 1, 2))  # First Tuesday
    
    def test_advance_weekly(self):
        """Test advance_weekly function"""
        current_date = date(2024, 1, 1)  # Monday
        weekly_days = [1, 3]  # Tuesday, Thursday
        result = advance_weekly(current_date, weekly_days, 1)
        self.assertEqual(result, date(2024, 1, 2))  # Next Tuesday
    
    def test_align_monthly(self):
        """Test align_monthly function"""
        start_date = date(2024, 1, 15)
        result = align_monthly(start_date, 1, 20)
        self.assertEqual(result, date(2024, 1, 20))
        
        # Test with None monthly_day
        result = align_monthly(start_date, 1, None)
        self.assertEqual(result, date(2024, 1, 15))  # Should use current day
    
    def test_advance_monthly(self):
        """Test advance_monthly function"""
        current_date = date(2024, 1, 15)
        result = advance_monthly(current_date, 1, 20)
        self.assertEqual(result, date(2024, 2, 20))
    
    def test_validate_dashboard_filters_valid(self):
        """Test valid dashboard filters"""
        filters = {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'status': 'active'
        }
        is_valid, message = validate_dashboard_filters(filters)
        self.assertTrue(is_valid)
        self.assertEqual(message, "Valid filters")
    
    def test_validate_dashboard_filters_invalid_dates(self):
        """Test invalid date range"""
        filters = {
            'start_date': '2024-01-31',
            'end_date': '2024-01-01'  # End before start
        }
        is_valid, message = validate_dashboard_filters(filters)
        self.assertFalse(is_valid)
        self.assertIn("Start date cannot be after end date", message)
    
    def test_validate_dashboard_filters_invalid_status(self):
        """Test invalid status filter"""
        filters = {'status': 'invalid_status'}
        is_valid, message = validate_dashboard_filters(filters)
        self.assertFalse(is_valid)
        self.assertIn("Invalid status filter", message)
    
    def test_validate_dashboard_filters_empty(self):
        """Test empty filters"""
        is_valid, message = validate_dashboard_filters({})
        self.assertTrue(is_valid)
        self.assertEqual(message, "No filters to validate")


if __name__ == '__main__':
    print("=" * 80)
    print("REFINED UNIT TESTING - DASHBOARD UTILITIES")
    print("=" * 80)
    print("Testing actual utility functions imported from utils module")
    print("Following pure function pattern - no side effects, no external dependencies")
    print("=" * 80)
    
    unittest.main(verbosity=2)
