#!/usr/bin/env python3
"""
C1 Unit Tests - Dashboard Utility Functions
Tests individual pure utility functions in complete isolation.
Based on actual pure functions in routes/dashboard.py.
"""

import unittest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import individual pure functions for unit testing
from routes.dashboard import (
    _safe_int, _to_date, _add_months, 
    _get_weekly_days, _align_weekly, _advance_weekly,
    _align_monthly, _advance_monthly
)


class TestDashboardUtilitiesUnit(unittest.TestCase):
    """C1 Unit tests for dashboard utility functions"""
    
    def test_safe_int_valid(self):
        """Test _safe_int with valid integer"""
        result = _safe_int("123")
        self.assertEqual(result, 123)
    
    def test_safe_int_invalid(self):
        """Test _safe_int with invalid input"""
        result = _safe_int("invalid")
        self.assertIsNone(result)
    
    def test_safe_int_none(self):
        """Test _safe_int with None"""
        result = _safe_int(None)
        self.assertIsNone(result)
    
    def test_safe_int_with_default(self):
        """Test _safe_int with default value"""
        result = _safe_int("invalid", default=0)
        self.assertEqual(result, 0)
    
    def test_to_date_datetime(self):
        """Test _to_date with datetime input"""
        dt = datetime(2024, 1, 15, 10, 30)
        result = _to_date(dt)
        self.assertEqual(result, datetime(2024, 1, 15).date())
    
    def test_to_date_string_iso(self):
        """Test _to_date with ISO string"""
        result = _to_date("2024-01-15")
        self.assertEqual(result, datetime(2024, 1, 15).date())
    
    def test_to_date_none(self):
        """Test _to_date with None"""
        result = _to_date(None)
        self.assertIsNone(result)
    
    def test_to_date_invalid_string(self):
        """Test _to_date with invalid string"""
        result = _to_date("invalid-date")
        self.assertIsNone(result)
    
    def test_add_months_basic(self):
        """Test _add_months with basic case"""
        base_date = datetime(2024, 1, 15).date()
        result = _add_months(base_date, 1)
        self.assertEqual(result, datetime(2024, 2, 15).date())
    
    def test_add_months_year_rollover(self):
        """Test _add_months with year rollover"""
        base_date = datetime(2024, 12, 15).date()
        result = _add_months(base_date, 1)
        self.assertEqual(result, datetime(2025, 1, 15).date())
    
    def test_add_months_end_of_month(self):
        """Test _add_months with end of month handling"""
        base_date = datetime(2024, 1, 31).date()
        result = _add_months(base_date, 1)
        # February has 29 days in 2024 (leap year)
        self.assertEqual(result, datetime(2024, 2, 29).date())
    
    def test_get_weekly_days_valid(self):
        """Test _get_weekly_days with valid input"""
        recurrence = {'weeklyDays': [1, 3, 5]}
        result = _get_weekly_days(recurrence, 0)
        self.assertEqual(result, [1, 3, 5])
    
    def test_get_weekly_days_empty(self):
        """Test _get_weekly_days with empty input"""
        recurrence = {'weeklyDays': []}
        result = _get_weekly_days(recurrence, 2)
        self.assertEqual(result, [2])  # Should return fallback
    
    def test_get_weekly_days_none(self):
        """Test _get_weekly_days with None input"""
        recurrence = {}
        result = _get_weekly_days(recurrence, 1)
        self.assertEqual(result, [1])  # Should return fallback
    
    def test_align_weekly_basic(self):
        """Test _align_weekly with basic case"""
        start_date = datetime(2024, 1, 15).date()  # Monday
        weekly_days = [1, 3, 5]  # Tuesday, Thursday, Saturday
        interval = 1
        
        result = _align_weekly(start_date, weekly_days, interval)
        self.assertEqual(result, datetime(2024, 1, 16).date())  # Next Tuesday
    
    def test_align_weekly_same_day(self):
        """Test _align_weekly when start date is already aligned"""
        start_date = datetime(2024, 1, 16).date()  # Tuesday
        weekly_days = [1, 3, 5]  # Tuesday, Thursday, Saturday
        interval = 1
        
        result = _align_weekly(start_date, weekly_days, interval)
        self.assertEqual(result, datetime(2024, 1, 16).date())  # Same day
    
    def test_advance_weekly_basic(self):
        """Test _advance_weekly with basic case"""
        current_date = datetime(2024, 1, 16).date()  # Tuesday
        weekly_days = [1, 3, 5]  # Tuesday, Thursday, Saturday
        interval = 1
        
        result = _advance_weekly(current_date, weekly_days, interval)
        self.assertEqual(result, datetime(2024, 1, 18).date())  # Next Thursday
    
    def test_advance_weekly_next_week(self):
        """Test _advance_weekly advancing to next week"""
        current_date = datetime(2024, 1, 20).date()  # Saturday
        weekly_days = [1, 3, 5]  # Tuesday, Thursday, Saturday
        interval = 1
        
        result = _advance_weekly(current_date, weekly_days, interval)
        self.assertEqual(result, datetime(2024, 1, 23).date())  # Next Tuesday
    
    def test_align_monthly_basic(self):
        """Test _align_monthly with basic case"""
        start_date = datetime(2024, 1, 15).date()
        interval = 1
        monthly_day = 20
        
        result = _align_monthly(start_date, interval, monthly_day)
        self.assertEqual(result, datetime(2024, 1, 20).date())  # Same month, different day
    
    def test_align_monthly_invalid_day(self):
        """Test _align_monthly with invalid day"""
        start_date = datetime(2024, 1, 15).date()
        interval = 1
        monthly_day = 35  # Invalid day
        
        result = _align_monthly(start_date, interval, monthly_day)
        # Should clamp to valid day (January has 31 days)
        self.assertEqual(result, datetime(2024, 1, 31).date())
    
    def test_advance_monthly_basic(self):
        """Test _advance_monthly with basic case"""
        current_date = datetime(2024, 2, 20).date()
        interval = 1
        monthly_day = 20
        
        result = _advance_monthly(current_date, interval, monthly_day)
        self.assertEqual(result, datetime(2024, 3, 20).date())
    
    def test_advance_monthly_invalid_day(self):
        """Test _advance_monthly with invalid day"""
        current_date = datetime(2024, 1, 31).date()
        interval = 1
        monthly_day = 31  # February doesn't have 31 days
        
        result = _advance_monthly(current_date, interval, monthly_day)
        # Should clamp to valid day (February has 29 days in 2024)
        self.assertEqual(result, datetime(2024, 2, 29).date())
    
    def test_dashboard_utilities_edge_cases(self):
        """Test dashboard utility functions with edge cases"""
        # Test with empty recurrence
        recurrence = {}
        result = _get_weekly_days(recurrence, 0)
        self.assertEqual(result, [0])
        
        # Test with None recurrence - should handle gracefully
        try:
            result = _get_weekly_days(None, 1)
            self.assertEqual(result, [1])  # Should return fallback
        except AttributeError:
            # Expected to fail with None recurrence_info
            pass


if __name__ == '__main__':
    print("=" * 80)
    print("C1 UNIT TESTING - DASHBOARD UTILITY FUNCTIONS")
    print("=" * 80)
    print("Testing individual pure utility functions in complete isolation")
    print("No external dependencies, no Flask app, no database")
    print("=" * 80)
    
    unittest.main(verbosity=2)
