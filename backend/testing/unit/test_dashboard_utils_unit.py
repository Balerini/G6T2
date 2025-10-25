#!/usr/bin/env python3
"""
C1 Unit Tests - Dashboard Utility Functions
Tests individual dashboard utility functions in complete isolation.
Based on actual functions in your routes/dashboard.py.
"""

import unittest
import sys
import os
from datetime import datetime, date, timedelta
import calendar

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import individual functions for unit testing
from routes.dashboard import _safe_int, _to_date, _add_months, _get_weekly_days, _align_weekly, _advance_weekly, _align_monthly, _advance_monthly, compute_effective_due_date, WEEKDAY_MAP


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
        self.assertEqual(result, 7)
    
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


class TestGetWeeklyDaysUnit(unittest.TestCase):
    """C1 Unit tests for _get_weekly_days function from dashboard.py"""
    
    def test_get_weekly_days_single_day(self):
        """Test _get_weekly_days with single day"""
        result = _get_weekly_days("Monday")
        self.assertEqual(result, [1])  # Monday = 1
    
    def test_get_weekly_days_multiple_days(self):
        """Test _get_weekly_days with multiple days"""
        result = _get_weekly_days("Monday,Wednesday,Friday")
        self.assertEqual(result, [1, 3, 5])
    
    def test_get_weekly_days_all_days(self):
        """Test _get_weekly_days with all days"""
        result = _get_weekly_days("Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday")
        self.assertEqual(result, [1, 2, 3, 4, 5, 6, 7])
    
    def test_get_weekly_days_empty_string(self):
        """Test _get_weekly_days with empty string"""
        result = _get_weekly_days("")
        self.assertEqual(result, [])
    
    def test_get_weekly_days_invalid_day(self):
        """Test _get_weekly_days with invalid day"""
        result = _get_weekly_days("InvalidDay")
        self.assertEqual(result, [])


class TestAlignWeeklyUnit(unittest.TestCase):
    """C1 Unit tests for _align_weekly function from dashboard.py"""
    
    def test_align_weekly_monday(self):
        """Test _align_weekly with Monday"""
        test_date = date(2025, 1, 15)  # Wednesday
        result = _align_weekly(test_date, 1)  # Monday
        self.assertEqual(result, date(2025, 1, 13))  # Previous Monday
    
    def test_align_weekly_friday(self):
        """Test _align_weekly with Friday"""
        test_date = date(2025, 1, 15)  # Wednesday
        result = _align_weekly(test_date, 5)  # Friday
        self.assertEqual(result, date(2025, 1, 17))  # Next Friday
    
    def test_align_weekly_same_day(self):
        """Test _align_weekly with same day"""
        test_date = date(2025, 1, 15)  # Wednesday
        result = _align_weekly(test_date, 3)  # Wednesday
        self.assertEqual(result, test_date)


class TestAdvanceWeeklyUnit(unittest.TestCase):
    """C1 Unit tests for _advance_weekly function from dashboard.py"""
    
    def test_advance_weekly_positive_weeks(self):
        """Test _advance_weekly with positive weeks"""
        test_date = date(2025, 1, 15)  # Wednesday
        result = _advance_weekly(test_date, 2)
        self.assertEqual(result, date(2025, 1, 29))  # 2 weeks later
    
    def test_advance_weekly_negative_weeks(self):
        """Test _advance_weekly with negative weeks"""
        test_date = date(2025, 1, 15)  # Wednesday
        result = _advance_weekly(test_date, -1)
        self.assertEqual(result, date(2025, 1, 8))  # 1 week earlier
    
    def test_advance_weekly_zero_weeks(self):
        """Test _advance_weekly with zero weeks"""
        test_date = date(2025, 1, 15)
        result = _advance_weekly(test_date, 0)
        self.assertEqual(result, test_date)


class TestAlignMonthlyUnit(unittest.TestCase):
    """C1 Unit tests for _align_monthly function from dashboard.py"""
    
    def test_align_monthly_same_day(self):
        """Test _align_monthly with same day"""
        test_date = date(2025, 1, 15)
        result = _align_monthly(test_date, 1, 15)
        self.assertEqual(result, test_date)
    
    def test_align_monthly_different_day(self):
        """Test _align_monthly with different day"""
        test_date = date(2025, 1, 15)
        result = _align_monthly(test_date, 1, 10)
        self.assertEqual(result, date(2025, 1, 10))
    
    def test_align_monthly_day_too_high(self):
        """Test _align_monthly with day too high for month"""
        test_date = date(2025, 1, 15)
        result = _align_monthly(test_date, 1, 31)  # January has 31 days
        self.assertEqual(result, date(2025, 1, 31))
    
    def test_align_monthly_february(self):
        """Test _align_monthly with February"""
        test_date = date(2025, 2, 15)
        result = _align_monthly(test_date, 1, 29)  # February 2025 has 28 days
        self.assertEqual(result, date(2025, 2, 28))


class TestAdvanceMonthlyUnit(unittest.TestCase):
    """C1 Unit tests for _advance_monthly function from dashboard.py"""
    
    def test_advance_monthly_positive_months(self):
        """Test _advance_monthly with positive months"""
        test_date = date(2025, 1, 15)
        result = _advance_monthly(test_date, 3, 15)
        self.assertEqual(result, date(2025, 4, 15))
    
    def test_advance_monthly_negative_months(self):
        """Test _advance_monthly with negative months"""
        test_date = date(2025, 4, 15)
        result = _advance_monthly(test_date, -3, 15)
        self.assertEqual(result, date(2025, 1, 15))
    
    def test_advance_monthly_zero_months(self):
        """Test _advance_monthly with zero months"""
        test_date = date(2025, 1, 15)
        result = _advance_monthly(test_date, 0, 15)
        self.assertEqual(result, test_date)


class TestComputeEffectiveDueDateUnit(unittest.TestCase):
    """C1 Unit tests for compute_effective_due_date function from dashboard.py"""
    
    def test_compute_effective_due_date_daily(self):
        """Test compute_effective_due_date with daily recurrence"""
        start_date = date(2025, 1, 15)
        result = compute_effective_due_date(start_date, "daily", 1, 1, None, None)
        self.assertEqual(result, start_date)
    
    def test_compute_effective_due_date_weekly(self):
        """Test compute_effective_due_date with weekly recurrence"""
        start_date = date(2025, 1, 15)  # Wednesday
        result = compute_effective_due_date(start_date, "weekly", 1, 1, "Monday", None)
        self.assertEqual(result, date(2025, 1, 13))  # Previous Monday
    
    def test_compute_effective_due_date_monthly(self):
        """Test compute_effective_due_date with monthly recurrence"""
        start_date = date(2025, 1, 15)
        result = compute_effective_due_date(start_date, "monthly", 1, 1, None, 10)
        self.assertEqual(result, date(2025, 1, 10))
    
    def test_compute_effective_due_date_invalid_recurrence(self):
        """Test compute_effective_due_date with invalid recurrence"""
        start_date = date(2025, 1, 15)
        result = compute_effective_due_date(start_date, "invalid", 1, 1, None, None)
        self.assertEqual(result, start_date)


class TestWeekdayMapUnit(unittest.TestCase):
    """C1 Unit tests for WEEKDAY_MAP constant from dashboard.py"""
    
    def test_weekday_map_completeness(self):
        """Test that WEEKDAY_MAP contains all weekdays"""
        expected_days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        for day in expected_days:
            self.assertIn(day, WEEKDAY_MAP)
    
    def test_weekday_map_values(self):
        """Test that WEEKDAY_MAP has correct values"""
        expected_mapping = {
            "mon": 0,
            "tue": 1,
            "wed": 2,
            "thu": 3,
            "fri": 4,
            "sat": 5,
            "sun": 6
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
