#!/usr/bin/env python3
"""
C1 Unit Tests - Dashboard Utility Functions
Tests individual dashboard utility functions in complete isolation.
Based on actual functions in routes/dashboard.py.
"""

import unittest
import sys
import os
from datetime import datetime, date, timedelta
import calendar

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import individual functions for unit testing
from routes.dashboard import _safe_int, _to_date, _add_months, WEEKDAY_MAP


class TestSafeIntUnit(unittest.TestCase):
    """C1 Unit tests for _safe_int function from dashboard.py"""
    
    def test_safe_int_with_integer(self):
        """Test _safe_int with integer input"""
        result = _safe_int(5)
        self.assertEqual(result, 5)
    
    def test_safe_int_with_string_integer(self):
        """Test _safe_int with string integer"""
        result = _safe_int("10")
        self.assertEqual(result, 10)
    
    def test_safe_int_with_float(self):
        """Test _safe_int with float input"""
        result = _safe_int(3.7)
        self.assertEqual(result, 3)
    
    def test_safe_int_with_string_float(self):
        """Test _safe_int with string float"""
        result = _safe_int("7.9")
        self.assertIsNone(result)  # String float should return None since int("7.9") fails
    
    def test_safe_int_with_invalid_string(self):
        """Test _safe_int with invalid string"""
        result = _safe_int("invalid")
        self.assertIsNone(result)
    
    def test_safe_int_with_none(self):
        """Test _safe_int with None input"""
        result = _safe_int(None)
        self.assertIsNone(result)
    
    def test_safe_int_with_empty_string(self):
        """Test _safe_int with empty string"""
        result = _safe_int("")
        self.assertIsNone(result)
    
    def test_safe_int_with_negative_number(self):
        """Test _safe_int with negative number"""
        result = _safe_int(-5)
        self.assertEqual(result, -5)
    
    def test_safe_int_with_zero(self):
        """Test _safe_int with zero"""
        result = _safe_int(0)
        self.assertEqual(result, 0)
    
    def test_safe_int_with_default_value(self):
        """Test _safe_int with custom default value"""
        result = _safe_int("invalid", default=42)
        self.assertEqual(result, 42)


class TestToDateUnit(unittest.TestCase):
    """C1 Unit tests for _to_date function from dashboard.py"""
    
    def test_to_date_with_date_object(self):
        """Test _to_date with date object"""
        test_date = date(2025, 1, 15)
        result = _to_date(test_date)
        self.assertEqual(result, test_date)
    
    def test_to_date_with_datetime_object(self):
        """Test _to_date with datetime object"""
        test_datetime = datetime(2025, 1, 15, 10, 30, 0)
        result = _to_date(test_datetime)
        self.assertEqual(result, date(2025, 1, 15))
    
    def test_to_date_with_string(self):
        """Test _to_date with string date"""
        result = _to_date("2025-01-15")
        self.assertEqual(result, date(2025, 1, 15))
    
    def test_to_date_with_invalid_string(self):
        """Test _to_date with invalid string"""
        result = _to_date("invalid-date")
        self.assertIsNone(result)
    
    def test_to_date_with_none(self):
        """Test _to_date with None"""
        result = _to_date(None)
        self.assertIsNone(result)


class TestAddMonthsUnit(unittest.TestCase):
    """C1 Unit tests for _add_months function from dashboard.py"""
    
    def test_add_months_positive(self):
        """Test _add_months with positive months"""
        test_date = date(2025, 1, 15)
        result = _add_months(test_date, 3)
        self.assertEqual(result, date(2025, 4, 15))
    
    def test_add_months_negative(self):
        """Test _add_months with negative months"""
        test_date = date(2025, 4, 15)
        result = _add_months(test_date, -3)
        self.assertEqual(result, date(2025, 1, 15))
    
    def test_add_months_zero(self):
        """Test _add_months with zero months"""
        test_date = date(2025, 1, 15)
        result = _add_months(test_date, 0)
        self.assertEqual(result, test_date)
    
    def test_add_months_year_boundary(self):
        """Test _add_months across year boundary"""
        test_date = date(2024, 11, 15)
        result = _add_months(test_date, 2)
        self.assertEqual(result, date(2025, 1, 15))
    
    def test_add_months_leap_year(self):
        """Test _add_months with leap year"""
        test_date = date(2024, 1, 29)  # Leap year
        result = _add_months(test_date, 1)
        self.assertEqual(result, date(2024, 2, 29))
    
    def test_add_months_non_leap_year(self):
        """Test _add_months with non-leap year"""
        test_date = date(2023, 1, 29)  # Non-leap year
        result = _add_months(test_date, 1)
        self.assertEqual(result, date(2023, 2, 28))


class TestWeekdayMapUnit(unittest.TestCase):
    """C1 Unit tests for WEEKDAY_MAP constant from dashboard.py"""
    
    def test_weekday_map_completeness(self):
        """Test that WEEKDAY_MAP contains all weekdays"""
        expected_days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        for day in expected_days:
            self.assertIn(day, WEEKDAY_MAP)
    
    def test_weekday_map_values(self):
        """Test that WEEKDAY_MAP has correct values"""
        expected_mapping = {
            'mon': 0,
            'tue': 1,
            'wed': 2,
            'thu': 3,
            'fri': 4,
            'sat': 5,
            'sun': 6
        }
        for day, expected_value in expected_mapping.items():
            self.assertEqual(WEEKDAY_MAP[day], expected_value)
    
    def test_weekday_map_consistency(self):
        """Test that WEEKDAY_MAP values are consistent"""
        values = list(WEEKDAY_MAP.values())
        self.assertEqual(len(values), 7)
        self.assertEqual(set(values), set(range(7)))


if __name__ == '__main__':
    print("=" * 80)
    print("C1 UNIT TESTING - DASHBOARD UTILITY FUNCTIONS")
    print("=" * 80)
    print("Testing individual dashboard utility functions in complete isolation")
    print("No external dependencies, no Flask app, no database")
    print("=" * 80)

    # Run with verbose output
    unittest.main(verbosity=2)
