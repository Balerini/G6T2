#!/usr/bin/env python3
"""
C1 Unit Tests - Recurrence Features
Tests individual recurrence functions in complete isolation.
Based on actual functions in pure_functions.py.
"""

import unittest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import individual functions for unit testing
from routes.task import _compute_next_occurrence_dates, _should_stop_recurrence, _parse_date_value, _add_months
from routes.dashboard import _safe_int, _to_date # Import from dashboard as well for consistency


class TestRecurrenceFeaturesUnit(unittest.TestCase):
    """C1 Unit tests for recurrence functionality"""

    def test_parse_date_value_valid(self):
        """Test _parse_date_value with valid date string"""
        result = _parse_date_value("2024-01-15")
        self.assertEqual(result, datetime(2024, 1, 15).date())

    def test_parse_date_value_none(self):
        """Test _parse_date_value with None input"""
        result = _parse_date_value(None)
        self.assertIsNone(result)

    def test_parse_date_value_datetime_object(self):
        """Test _parse_date_value with datetime object input"""
        dt_obj = datetime(2024, 1, 15, 10, 30, 0)
        result = _parse_date_value(dt_obj)
        self.assertEqual(result, datetime(2024, 1, 15).date())

    def test_parse_date_value_invalid_string(self):
        """Test _parse_date_value with invalid date string"""
        result = _parse_date_value("invalid-date")
        self.assertIsNone(result)

    def test_add_months_basic(self):
        """Test _add_months with basic case"""
        base_date = datetime(2024, 1, 15)
        result = _add_months(base_date, 1)
        self.assertEqual(result, datetime(2024, 2, 15))

    def test_add_months_year_rollover(self):
        """Test _add_months with year rollover"""
        base_date = datetime(2024, 12, 15)
        result = _add_months(base_date, 1)
        self.assertEqual(result, datetime(2025, 1, 15))

    def test_add_months_end_of_month(self):
        """Test _add_months with end of month handling"""
        base_date = datetime(2024, 1, 31)
        result = _add_months(base_date, 1)
        # February has 29 days in 2024 (leap year)
        self.assertEqual(result, datetime(2024, 2, 29))

    def test__compute_next_occurrence_dates_daily(self):
        """Test _compute_next_occurrence_dates with daily frequency"""
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'daily', 'interval': 3}
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        self.assertEqual(next_start, datetime(2024, 1, 18))
        self.assertEqual(next_end, datetime(2024, 1, 23))

    def test__compute_next_occurrence_dates_weekly(self):
        """Test _compute_next_occurrence_dates with weekly frequency"""
        start_date = datetime(2024, 1, 15)  # Monday
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'weekly', 'interval': 1, 'weeklyDays': [2]}  # Wednesday (day 2)
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        self.assertEqual(next_start, datetime(2024, 1, 17))  # Wednesday (day 2)
        self.assertEqual(next_end, datetime(2024, 1, 22))

    def test__compute_next_occurrence_dates_weekly_no_days(self):
        """Test _compute_next_occurrence_dates with weekly frequency but no weekly days"""
        start_date = datetime(2024, 1, 15)  # Monday
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'weekly', 'interval': 1, 'weeklyDays': []}
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        self.assertEqual(next_start, datetime(2024, 1, 22))  # Next Monday
        self.assertEqual(next_end, datetime(2024, 1, 27))

    def test__compute_next_occurrence_dates_monthly(self):
        """Test _compute_next_occurrence_dates with monthly frequency"""
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'monthly', 'interval': 1, 'monthlyDay': 15}
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        self.assertEqual(next_start, datetime(2024, 2, 15))
        self.assertEqual(next_end, datetime(2024, 2, 20))

    def test__compute_next_occurrence_dates_monthly_invalid_day(self):
        """Test _compute_next_occurrence_dates with monthly frequency and invalid day"""
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'monthly', 'interval': 1, 'monthlyDay': 35}  # Invalid day
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        # Should clamp to valid day (February has 29 days in 2024)
        self.assertEqual(next_start, datetime(2024, 2, 29))  # Clamped to max day in Feb
        self.assertEqual(next_end, datetime(2024, 3, 5))

    def test__compute_next_occurrence_dates_custom_days(self):
        """Test _compute_next_occurrence_dates with custom frequency (days)"""
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'custom', 'interval': 10, 'customUnit': 'days'}
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        self.assertEqual(next_start, datetime(2024, 1, 25))
        self.assertEqual(next_end, datetime(2024, 1, 30))

    def test__compute_next_occurrence_dates_custom_weeks(self):
        """Test _compute_next_occurrence_dates with custom frequency (weeks)"""
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'custom', 'interval': 2, 'customUnit': 'weeks'}
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        self.assertEqual(next_start, datetime(2024, 1, 29))
        self.assertEqual(next_end, datetime(2024, 2, 3))

    def test__compute_next_occurrence_dates_custom_months(self):
        """Test _compute_next_occurrence_dates with custom frequency (months)"""
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'custom', 'interval': 3, 'customUnit': 'months'}
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        self.assertEqual(next_start, datetime(2024, 4, 15))
        self.assertEqual(next_end, datetime(2024, 4, 20))

    def test__should_stop_recurrence_never(self):
        """Test _should_stop_recurrence with 'never' condition"""
        recurrence_info = {'endCondition': 'never'}
        result = _should_stop_recurrence(recurrence_info, 5, datetime(2024, 1, 15))
        self.assertFalse(result)

    def test__should_stop_recurrence_after_occurrences_not_reached(self):
        """Test _should_stop_recurrence with 'after' condition (not reached)"""
        recurrence_info = {'endCondition': 'after', 'endAfterOccurrences': 10}
        result = _should_stop_recurrence(recurrence_info, 5, datetime(2024, 1, 15))
        self.assertFalse(result)

    def test__should_stop_recurrence_after_occurrences_reached(self):
        """Test _should_stop_recurrence with 'after' condition (reached)"""
        recurrence_info = {'endCondition': 'after', 'endAfterOccurrences': 5}
        result = _should_stop_recurrence(recurrence_info, 6, datetime(2024, 1, 15))
        self.assertTrue(result)

    def test__should_stop_recurrence_ondate_not_reached(self):
        """Test _should_stop_recurrence with 'ondate' condition (not reached)"""
        recurrence_info = {'endCondition': 'ondate', 'endDate': '2024-01-31'}
        result = _should_stop_recurrence(recurrence_info, 5, datetime(2024, 1, 15))
        self.assertFalse(result)

    def test__should_stop_recurrence_ondate_reached(self):
        """Test _should_stop_recurrence with 'ondate' condition (reached)"""
        recurrence_info = {'endCondition': 'ondate', 'endDate': '2024-01-20'}
        result = _should_stop_recurrence(recurrence_info, 5, datetime(2024, 1, 21))
        self.assertTrue(result)

    def test__should_stop_recurrence_empty_info(self):
        """Test _should_stop_recurrence with empty recurrence info"""
        recurrence_info = {}
        
        result = _should_stop_recurrence(recurrence_info, 5, datetime(2024, 1, 15))
        self.assertFalse(result)  # Should default to 'never'

    def test_recurrence_edge_cases(self):
        """Test recurrence functions with edge cases"""
        # Test with empty recurrence info
        start_date = datetime(2024, 1, 15)
        result = _compute_next_occurrence_dates(start_date, None, {})
        self.assertEqual(result[0], datetime(2024, 1, 16))  # Should default to daily
        
        # Test with zero interval
        recurrence_info = {'frequency': 'daily', 'interval': 0}
        result = _compute_next_occurrence_dates(start_date, None, recurrence_info)
        self.assertEqual(result[0], datetime(2024, 1, 16))  # Should default to 1
    
    def test_recurrence_negative_interval(self):
        """Test recurrence with negative interval"""
        start_date = datetime(2024, 1, 15)
        recurrence_info = {'frequency': 'daily', 'interval': -5}
        result = _compute_next_occurrence_dates(start_date, None, recurrence_info)
        self.assertEqual(result[0], datetime(2024, 1, 16))  # Should default to 1
    
    def test_recurrence_invalid_frequency(self):
        """Test recurrence with invalid frequency"""
        start_date = datetime(2024, 1, 15)
        recurrence_info = {'frequency': 'invalid', 'interval': 1}
        result = _compute_next_occurrence_dates(start_date, None, recurrence_info)
        self.assertEqual(result[0], datetime(2024, 1, 16))  # Should default to daily
    
    def test_recurrence_string_interval(self):
        """Test recurrence with string interval"""
        start_date = datetime(2024, 1, 15)
        recurrence_info = {'frequency': 'daily', 'interval': 'invalid'}
        result = _compute_next_occurrence_dates(start_date, None, recurrence_info)
        self.assertEqual(result[0], datetime(2024, 1, 16))  # Should default to 1
    
    def test_recurrence_none_interval(self):
        """Test recurrence with None interval"""
        start_date = datetime(2024, 1, 15)
        recurrence_info = {'frequency': 'daily', 'interval': None}
        result = _compute_next_occurrence_dates(start_date, None, recurrence_info)
        self.assertEqual(result[0], datetime(2024, 1, 16))  # Should default to 1
    
    def test_recurrence_leap_year(self):
        """Test recurrence across leap year boundary"""
        start_date = datetime(2024, 2, 29)  # Leap year
        recurrence_info = {'frequency': 'yearly', 'interval': 1}
        result = _compute_next_occurrence_dates(start_date, None, recurrence_info)
        # Should handle leap year correctly
        self.assertIsNotNone(result[0])
    
    def test_recurrence_month_end_boundary(self):
        """Test recurrence at month end boundaries"""
        start_date = datetime(2024, 1, 31)
        recurrence_info = {'frequency': 'monthly', 'interval': 1}
        result = _compute_next_occurrence_dates(start_date, None, recurrence_info)
        # Should handle month end correctly
        self.assertEqual(result[0], datetime(2024, 2, 29))  # Feb 29 in leap year
    
    def test_recurrence_weekly_edge_days(self):
        """Test recurrence with edge case weekly days"""
        start_date = datetime(2024, 1, 15)  # Monday
        recurrence_info = {'frequency': 'weekly', 'interval': 1, 'weeklyDays': [6]}  # Sunday
        result = _compute_next_occurrence_dates(start_date, None, recurrence_info)
        # Should find next Sunday
        self.assertEqual(result[0], datetime(2024, 1, 21))  # Next Sunday
    
    def test_recurrence_custom_invalid_unit(self):
        """Test recurrence with invalid custom unit"""
        start_date = datetime(2024, 1, 15)
        recurrence_info = {'frequency': 'custom', 'interval': 1, 'customUnit': 'invalid'}
        result = _compute_next_occurrence_dates(start_date, None, recurrence_info)
        self.assertEqual(result[0], datetime(2024, 1, 16))  # Should default to daily
    
    def test_recurrence_stop_conditions_edge_cases(self):
        """Test recurrence stopping with edge cases"""
        # Test with invalid endAfterOccurrences
        recurrence_info = {'endCondition': 'after', 'endAfterOccurrences': 'invalid'}
        result = _should_stop_recurrence(recurrence_info, 5, datetime(2024, 1, 15))
        self.assertFalse(result)  # Should default to never
        
        # Test with negative endAfterOccurrences
        recurrence_info = {'endCondition': 'after', 'endAfterOccurrences': -1}
        result = _should_stop_recurrence(recurrence_info, 5, datetime(2024, 1, 15))
        self.assertTrue(result)  # Should stop because 5 > 0 (converted from -1)
        
        # Test with invalid endDate format
        recurrence_info = {'endCondition': 'ondate', 'endDate': 'invalid-date'}
        result = _should_stop_recurrence(recurrence_info, 5, datetime(2024, 1, 15))
        self.assertFalse(result)  # Should default to never
    
    def test_parse_date_value_edge_cases(self):
        """Test _parse_date_value function to cover missing lines"""
        # Test with None input (line 31)
        result = _parse_date_value(None)
        self.assertIsNone(result)
        
        # Test with invalid string format (line 31)
        result = _parse_date_value("invalid-date-format")
        self.assertIsNone(result)
        
        # Test with empty string
        result = _parse_date_value("")
        self.assertIsNone(result)
        
        # Test with whitespace string
        result = _parse_date_value("   ")
        self.assertIsNone(result)
        
        # Test with malformed date string
        result = _parse_date_value("2024-13-45")  # Invalid month and day
        self.assertIsNone(result)
        
        # Test with completely invalid string
        result = _parse_date_value("not-a-date-at-all")
        self.assertIsNone(result)
    
    def test_compute_next_occurrence_dates_edge_cases(self):
        """Test _compute_next_occurrence_dates function to cover missing lines"""
        # Test with None current_start_dt (line 44)
        result = _compute_next_occurrence_dates(None, None, {})
        self.assertEqual(result, (None, None))
        
        # Test with empty recurrence_info
        start_date = datetime(2024, 1, 15)
        result = _compute_next_occurrence_dates(start_date, None, {})
        self.assertEqual(result[0], datetime(2024, 1, 16))  # Should default to daily
    
    def test_parse_date_value_comprehensive_edge_cases(self):
        """Test _parse_date_value function to cover line 31 comprehensively"""
        # Test with various invalid inputs that should trigger line 31
        invalid_inputs = [
            None,
            "",
            "   ",
            "invalid-date-format",
            "2024-13-45",  # Invalid month and day
            "2024-02-30",  # Invalid day for February
            "2024-04-31",  # Invalid day for April
            "not-a-date-at-all",
            "2024/01/15",  # Wrong format
            "15-01-2024",  # Wrong format
            "24-01-15",    # Two digit year
            "2024-00-15",  # Zero month
            "2024-01-00",  # Zero day
            "2024-13-01",  # Month > 12
            "2024-01-32",  # Day > 31
        ]
        
        for invalid_input in invalid_inputs:
            with self.subTest(input=invalid_input):
                result = _parse_date_value(invalid_input)
                self.assertIsNone(result, f"Expected None for input: {invalid_input}")
        
        # Additional edge cases to ensure line 31 is covered
        # Test with various malformed strings
        malformed_inputs = [
            "2024-13-45",  # Invalid month and day
            "2024-02-30",  # Invalid day for February (non-leap year)
            "2024-04-31",  # Invalid day for April
            "2024-06-31",  # Invalid day for June
            "2024-09-31",  # Invalid day for September
            "2024-11-31",  # Invalid day for November
            "2024-02-29",  # Invalid for non-leap year (but 2024 is leap year, so this is valid)
            "2023-02-29",  # Invalid for non-leap year
        ]
        
        for malformed_input in malformed_inputs:
            with self.subTest(input=malformed_input):
                result = _parse_date_value(malformed_input)
                # Some might be valid (like 2024-02-29), others invalid
                if malformed_input in ["2024-02-29"]:  # Leap year
                    self.assertIsNotNone(result)
                else:
                    self.assertIsNone(result, f"Expected None for input: {malformed_input}")
        
        # Additional comprehensive test to ensure line 31 is covered
        comprehensive_invalid_inputs = [
            None,
            "",
            "   ",
            "invalid-date-format",
            "2024-13-45",  # Invalid month and day
            "2024-02-30",  # Invalid day for February
            "2024-04-31",  # Invalid day for April
            "2024-06-31",  # Invalid day for June
            "2024-09-31",  # Invalid day for September
            "2024-11-31",  # Invalid day for November
            "2023-02-29",  # Invalid for non-leap year
            "not-a-date-at-all",
            "2024/01/15",  # Wrong format
            "15-01-2024",  # Wrong format
            "24-01-15",    # Two digit year
            "2024-00-15",  # Zero month
            "2024-01-00",  # Zero day
            "2024-13-01",  # Month > 12
            "2024-01-32",  # Day > 31
            "2024-1-15",   # Single digit month (should be valid)
            "2024-01-1",   # Single digit day (should be valid)
        ]
        
        for invalid_input in comprehensive_invalid_inputs:
            with self.subTest(input=invalid_input):
                result = _parse_date_value(invalid_input)
                # Most should be None, but single digit month/day should be valid
                if invalid_input in ["2024-1-15", "2024-01-1"]:
                    self.assertIsNotNone(result)
                else:
                    self.assertIsNone(result, f"Expected None for input: {invalid_input}")

    def test_parse_date_value_line_31_coverage(self):
        """Test _parse_date_value function to specifically cover line 31"""
        # Test with non-string, non-datetime input to trigger line 31
        invalid_inputs = [
            123,  # Integer
            123.45,  # Float
            [],  # List
            {},  # Dict
            True,  # Boolean
            None,  # None
        ]
        
        for invalid_input in invalid_inputs:
            with self.subTest(input=invalid_input):
                result = _parse_date_value(invalid_input)
                self.assertIsNone(result, f"Expected None for input: {invalid_input}")


if __name__ == '__main__':
    print("=" * 80)
    print("C1 UNIT TESTING - RECURRENCE FEATURES")
    print("=" * 80)
    unittest.main(verbosity=2)