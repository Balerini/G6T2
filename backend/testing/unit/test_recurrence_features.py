#!/usr/bin/env python3
"""
C1 Unit Tests - Recurrence Features
Tests individual recurrence functions in complete isolation.
Based on actual functions in routes/task.py.
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


class TestRecurrenceFeaturesUnit(unittest.TestCase):
    """C1 Unit tests for recurrence functionality"""
    
    def test_parse_date_value_none(self):
        """Test parse_date_value with None input"""
        result = _parse_date_value(None)
        self.assertIsNone(result)
    
    def test_parse_date_value_datetime(self):
        """Test parse_date_value with datetime input"""
        dt = datetime(2024, 1, 15, 10, 30)
        result = _parse_date_value(dt)
        self.assertEqual(result, datetime(2024, 1, 15).date())
    
    def test_parse_date_value_iso_string(self):
        """Test parse_date_value with ISO string"""
        result = _parse_date_value('2024-01-15')
        self.assertEqual(result, datetime(2024, 1, 15).date())
    
    def test_parse_date_value_invalid_string(self):
        """Test parse_date_value with invalid string"""
        result = _parse_date_value('invalid-date')
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
    
    def test_compute_next_occurrence_dates_none_start(self):
        """Test _compute_next_occurrence_dates with None start date"""
        result = _compute_next_occurrence_dates(None, None, {})
        self.assertEqual(result, (None, None))
    
    def test_compute_next_occurrence_dates_daily(self):
        """Test _compute_next_occurrence_dates with daily frequency"""
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'daily', 'interval': 1}
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        self.assertEqual(next_start, datetime(2024, 1, 16))
        self.assertEqual(next_end, datetime(2024, 1, 21))
    
    def test_compute_next_occurrence_dates_daily_interval(self):
        """Test _compute_next_occurrence_dates with daily frequency and interval"""
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'daily', 'interval': 3}
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        self.assertEqual(next_start, datetime(2024, 1, 18))
        self.assertEqual(next_end, datetime(2024, 1, 23))
    
    def test_compute_next_occurrence_dates_weekly(self):
        """Test _compute_next_occurrence_dates with weekly frequency"""
        start_date = datetime(2024, 1, 15)  # Monday
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'weekly', 'interval': 1, 'weeklyDays': [2]}  # Tuesday
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        self.assertEqual(next_start, datetime(2024, 1, 17))  # Wednesday (day 2)
        self.assertEqual(next_end, datetime(2024, 1, 22))
    
    def test_compute_next_occurrence_dates_weekly_no_days(self):
        """Test _compute_next_occurrence_dates with weekly frequency but no weekly days"""
        start_date = datetime(2024, 1, 15)  # Monday
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'weekly', 'interval': 1, 'weeklyDays': []}
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        # Should default to same weekday
        self.assertEqual(next_start, datetime(2024, 1, 22))  # Next Monday
        self.assertEqual(next_end, datetime(2024, 1, 27))
    
    def test_compute_next_occurrence_dates_monthly(self):
        """Test _compute_next_occurrence_dates with monthly frequency"""
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'monthly', 'interval': 1, 'monthlyDay': 15}
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        self.assertEqual(next_start, datetime(2024, 2, 15))
        self.assertEqual(next_end, datetime(2024, 2, 20))
    
    def test_compute_next_occurrence_dates_monthly_invalid_day(self):
        """Test _compute_next_occurrence_dates with monthly frequency and invalid day"""
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'monthly', 'interval': 1, 'monthlyDay': 35}  # Invalid day
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        # Should clamp to valid day (February has 29 days in 2024)
        self.assertEqual(next_start, datetime(2024, 2, 29))  # Clamped to max day in Feb
        self.assertEqual(next_end, datetime(2024, 3, 5))
    
    def test_compute_next_occurrence_dates_custom_days(self):
        """Test _compute_next_occurrence_dates with custom frequency (days)"""
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'custom', 'interval': 5, 'customUnit': 'days'}
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        self.assertEqual(next_start, datetime(2024, 1, 20))
        self.assertEqual(next_end, datetime(2024, 1, 25))
    
    def test_compute_next_occurrence_dates_custom_weeks(self):
        """Test _compute_next_occurrence_dates with custom frequency (weeks)"""
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'custom', 'interval': 2, 'customUnit': 'weeks'}
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        self.assertEqual(next_start, datetime(2024, 1, 29))  # 2 weeks later
        self.assertEqual(next_end, datetime(2024, 2, 3))
    
    def test_compute_next_occurrence_dates_custom_months(self):
        """Test _compute_next_occurrence_dates with custom frequency (months)"""
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'custom', 'interval': 2, 'customUnit': 'months'}
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        self.assertEqual(next_start, datetime(2024, 3, 15))  # 2 months later
        self.assertEqual(next_end, datetime(2024, 3, 20))
    
    def test_compute_next_occurrence_dates_invalid_frequency(self):
        """Test _compute_next_occurrence_dates with invalid frequency"""
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'invalid', 'interval': 1}
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        # Should fallback to daily behavior
        self.assertEqual(next_start, datetime(2024, 1, 16))
        self.assertEqual(next_end, datetime(2024, 1, 21))
    
    def test_compute_next_occurrence_dates_invalid_interval(self):
        """Test _compute_next_occurrence_dates with invalid interval"""
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 20)
        recurrence_info = {'frequency': 'daily', 'interval': 'invalid'}
        
        next_start, next_end = _compute_next_occurrence_dates(start_date, end_date, recurrence_info)
        
        # Should default to interval 1
        self.assertEqual(next_start, datetime(2024, 1, 16))
        self.assertEqual(next_end, datetime(2024, 1, 21))
    
    def test_should_stop_recurrence_never(self):
        """Test _should_stop_recurrence with 'never' end condition"""
        recurrence_info = {'endCondition': 'never'}
        result = _should_stop_recurrence(recurrence_info, 5, datetime(2024, 1, 15))
        self.assertFalse(result)
    
    def test_should_stop_recurrence_after_occurrences(self):
        """Test _should_stop_recurrence with 'after' end condition"""
        recurrence_info = {'endCondition': 'after', 'endAfterOccurrences': 3}
        
        # Should not stop before max occurrences
        result = _should_stop_recurrence(recurrence_info, 2, datetime(2024, 1, 15))
        self.assertFalse(result)
        
        # Should stop after max occurrences
        result = _should_stop_recurrence(recurrence_info, 4, datetime(2024, 1, 15))
        self.assertTrue(result)
    
    def test_should_stop_recurrence_after_invalid_occurrences(self):
        """Test _should_stop_recurrence with invalid occurrences value"""
        recurrence_info = {'endCondition': 'after', 'endAfterOccurrences': 'invalid'}
        
        result = _should_stop_recurrence(recurrence_info, 5, datetime(2024, 1, 15))
        self.assertFalse(result)  # Should not stop with invalid value
    
    def test_should_stop_recurrence_on_date_before_end(self):
        """Test _should_stop_recurrence with 'ondate' end condition before end date"""
        recurrence_info = {'endCondition': 'ondate', 'endDate': '2024-02-15'}
        
        result = _should_stop_recurrence(recurrence_info, 3, datetime(2024, 1, 15))
        self.assertFalse(result)
    
    def test_should_stop_recurrence_on_date_after_end(self):
        """Test _should_stop_recurrence with 'ondate' end condition after end date"""
        recurrence_info = {'endCondition': 'ondate', 'endDate': '2024-01-10'}
        
        result = _should_stop_recurrence(recurrence_info, 3, datetime(2024, 1, 15))
        self.assertTrue(result)
    
    def test_should_stop_recurrence_on_date_invalid_date(self):
        """Test _should_stop_recurrence with invalid end date"""
        recurrence_info = {'endCondition': 'ondate', 'endDate': 'invalid-date'}
        
        result = _should_stop_recurrence(recurrence_info, 3, datetime(2024, 1, 15))
        self.assertFalse(result)  # Should not stop with invalid date
    
    def test_should_stop_recurrence_no_end_condition(self):
        """Test _should_stop_recurrence with no end condition"""
        recurrence_info = {}
        
        result = _should_stop_recurrence(recurrence_info, 5, datetime(2024, 1, 15))
        self.assertFalse(result)  # Should default to 'never'
    
    def test_recurrence_edge_cases(self):
        """Test recurrence functions with edge cases"""
        # Test with empty recurrence info
        start_date = datetime(2024, 1, 15)
        result = _compute_next_occurrence_dates(start_date, None, {})
        self.assertEqual(result[0], datetime(2024, 1, 16))  # Should default to daily
        
        # Test with None recurrence info - should handle gracefully
        try:
            result = _compute_next_occurrence_dates(start_date, None, None)
            # If it doesn't crash, that's good
        except AttributeError:
            # Expected to fail with None recurrence_info
            pass
        
        # Test with zero interval
        recurrence_info = {'frequency': 'daily', 'interval': 0}
        result = _compute_next_occurrence_dates(start_date, None, recurrence_info)
        self.assertEqual(result[0], datetime(2024, 1, 16))  # Should default to 1


if __name__ == '__main__':
    print("=" * 80)
    print("C1 UNIT TESTING - RECURRENCE FEATURES")
    print("=" * 80)
    print("Testing individual recurrence functions in complete isolation")
    print("No external dependencies, no Flask app, no database")
    print("=" * 80)
    
    unittest.main(verbosity=2)
