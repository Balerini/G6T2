import unittest
import sys
import os
from datetime import datetime, date, timedelta
from unittest.mock import MagicMock

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.dashboard import (
    _safe_int, _to_date, _add_months, _get_weekly_days,
    _align_weekly, _advance_weekly, _align_monthly, _advance_monthly,
    compute_effective_due_date, WEEKDAY_MAP
)

class TestSafeInt(unittest.TestCase):
    """Test cases for _safe_int helper function"""
    
    def test_safe_int_with_integer(self):
        """Test converting integer to int"""
        self.assertEqual(_safe_int(5), 5)
        self.assertEqual(_safe_int(0), 0)
        self.assertEqual(_safe_int(-10), -10)
    
    def test_safe_int_with_string(self):
        """Test converting string numbers to int"""
        self.assertEqual(_safe_int("42"), 42)
        self.assertEqual(_safe_int("0"), 0)
        self.assertEqual(_safe_int("-5"), -5)
    
    def test_safe_int_with_invalid_string(self):
        """Test converting invalid strings"""
        self.assertIsNone(_safe_int("abc"))
        self.assertIsNone(_safe_int("12.5"))
        self.assertEqual(_safe_int("invalid", default=99), 99)
    
    def test_safe_int_with_none(self):
        """Test converting None"""
        self.assertIsNone(_safe_int(None))
        self.assertEqual(_safe_int(None, default=10), 10)
    
    def test_safe_int_with_float(self):
        """Test converting float to int"""
        self.assertEqual(_safe_int(5.7), 5)
        self.assertEqual(_safe_int(3.14), 3)


class TestToDate(unittest.TestCase):
    """Test cases for _to_date helper function"""
    
    def test_to_date_with_datetime(self):
        """Test converting datetime to date"""
        dt = datetime(2025, 10, 24, 15, 30, 0)
        result = _to_date(dt)
        self.assertEqual(result, date(2025, 10, 24))
    
    def test_to_date_with_date(self):
        """Test with date object"""
        d = date(2025, 10, 24)
        result = _to_date(d)
        self.assertEqual(result, d)
    
    def test_to_date_with_iso_string(self):
        """Test converting ISO format string"""
        result = _to_date("2025-10-24T15:30:00")
        self.assertEqual(result, date(2025, 10, 24))
    
    def test_to_date_with_simple_string(self):
        """Test converting simple date string"""
        result = _to_date("2025-10-24")
        self.assertEqual(result, date(2025, 10, 24))
    
    def test_to_date_with_invalid_string(self):
        """Test converting invalid string"""
        self.assertIsNone(_to_date("invalid date"))
        self.assertIsNone(_to_date("2025/10/24"))
    
    def test_to_date_with_none(self):
        """Test converting None"""
        self.assertIsNone(_to_date(None))


class TestAddMonths(unittest.TestCase):
    """Test cases for _add_months helper function"""
    
    def test_add_months_simple(self):
        """Test adding months without year change"""
        base = date(2025, 1, 15)
        result = _add_months(base, 2)
        self.assertEqual(result, date(2025, 3, 15))
    
    def test_add_months_year_rollover(self):
        """Test adding months with year change"""
        base = date(2025, 10, 15)
        result = _add_months(base, 5)
        self.assertEqual(result, date(2026, 3, 15))
    
    def test_add_months_day_adjustment(self):
        """Test adding months with day adjustment (e.g., Jan 31 + 1 month = Feb 28)"""
        base = date(2025, 1, 31)
        result = _add_months(base, 1)
        self.assertEqual(result, date(2025, 2, 28))  # Feb doesn't have 31 days
    
    def test_add_months_leap_year(self):
        """Test adding months in leap year"""
        base = date(2024, 1, 31)  # 2024 is a leap year
        result = _add_months(base, 1)
        self.assertEqual(result, date(2024, 2, 29))
    
    def test_add_months_negative(self):
        """Test subtracting months (negative value)"""
        base = date(2025, 5, 15)
        result = _add_months(base, -2)
        self.assertEqual(result, date(2025, 3, 15))
    
    def test_add_months_zero(self):
        """Test adding zero months"""
        base = date(2025, 5, 15)
        result = _add_months(base, 0)
        self.assertEqual(result, base)


class TestGetWeeklyDays(unittest.TestCase):
    """Test cases for _get_weekly_days helper function"""
    
    def test_get_weekly_days_with_integers(self):
        """Test with integer weekdays"""
        recurrence = {'weeklyDays': [0, 2, 4]}  # Mon, Wed, Fri
        result = _get_weekly_days(recurrence, 1)
        self.assertEqual(result, [0, 2, 4])
    
    def test_get_weekly_days_with_strings(self):
        """Test with string weekday names"""
        recurrence = {'weeklyDays': ['mon', 'wed', 'fri']}
        result = _get_weekly_days(recurrence, 1)
        self.assertEqual(result, [0, 2, 4])
    
    def test_get_weekly_days_mixed_case(self):
        """Test with mixed case strings"""
        recurrence = {'weeklyDays': ['Mon', 'WED', 'Friday']}
        result = _get_weekly_days(recurrence, 1)
        self.assertEqual(result, [0, 2, 4])
    
    def test_get_weekly_days_empty_fallback(self):
        """Test with empty list uses fallback"""
        recurrence = {'weeklyDays': []}
        result = _get_weekly_days(recurrence, 3)  # Thursday
        self.assertEqual(result, [3])
    
    def test_get_weekly_days_snake_case_key(self):
        """Test with snake_case key"""
        recurrence = {'weekly_days': [1, 3, 5]}  # Tue, Thu, Sat
        result = _get_weekly_days(recurrence, 0)
        self.assertEqual(result, [1, 3, 5])
    
    def test_get_weekly_days_duplicates_removed(self):
        """Test that duplicates are removed"""
        recurrence = {'weeklyDays': [1, 1, 3, 3, 5]}
        result = _get_weekly_days(recurrence, 0)
        self.assertEqual(result, [1, 3, 5])
    
    def test_get_weekly_days_sorted(self):
        """Test that result is sorted"""
        recurrence = {'weeklyDays': [5, 1, 3]}
        result = _get_weekly_days(recurrence, 0)
        self.assertEqual(result, [1, 3, 5])


class TestAlignWeekly(unittest.TestCase):
    """Test cases for _align_weekly helper function"""
    
    def test_align_weekly_same_day(self):
        """Test aligning when start day is in weekly days"""
        start = date(2025, 10, 20)  # Monday
        weekly_days = [0, 2, 4]  # Mon, Wed, Fri
        result = _align_weekly(start, weekly_days, 1)
        self.assertEqual(result, date(2025, 10, 20))  # Same Monday
    
    def test_align_weekly_next_day_this_week(self):
        """Test aligning to next day in same week"""
        start = date(2025, 10, 20)  # Monday
        weekly_days = [2, 4]  # Wed, Fri (no Monday)
        result = _align_weekly(start, weekly_days, 1)
        self.assertEqual(result, date(2025, 10, 22))  # Wednesday
    
    def test_align_weekly_next_week(self):
        """Test aligning to next week"""
        start = date(2025, 10, 24)  # Friday
        weekly_days = [0, 2]  # Mon, Wed
        result = _align_weekly(start, weekly_days, 1)
        self.assertEqual(result, date(2025, 10, 27))  # Next Monday
    
    def test_align_weekly_with_interval(self):
        """Test aligning with interval > 1"""
        start = date(2025, 10, 24)  # Friday
        weekly_days = [0]  # Monday only
        result = _align_weekly(start, weekly_days, 2)  # Every 2 weeks
        self.assertEqual(result, date(2025, 11, 3))  # Monday in 2 weeks


class TestAdvanceWeekly(unittest.TestCase):
    """Test cases for _advance_weekly helper function"""
    
    def test_advance_weekly_next_day_same_week(self):
        """Test advancing to next day in same week"""
        current = date(2025, 10, 20)  # Monday
        weekly_days = [0, 2, 4]  # Mon, Wed, Fri
        result = _advance_weekly(current, weekly_days, 1)
        self.assertEqual(result, date(2025, 10, 22))  # Wednesday
    
    def test_advance_weekly_next_week(self):
        """Test advancing to next week"""
        current = date(2025, 10, 24)  # Friday
        weekly_days = [0, 2, 4]  # Mon, Wed, Fri
        result = _advance_weekly(current, weekly_days, 1)
        self.assertEqual(result, date(2025, 10, 27))  # Next Monday
    
    def test_advance_weekly_with_interval(self):
        """Test advancing with interval > 1"""
        current = date(2025, 10, 20)  # Monday
        weekly_days = [0]  # Monday only
        result = _advance_weekly(current, weekly_days, 2)  # Every 2 weeks
        self.assertEqual(result, date(2025, 11, 3))  # Monday 2 weeks later


class TestAlignMonthly(unittest.TestCase):
    """Test cases for _align_monthly helper function"""
    
    def test_align_monthly_same_month(self):
        """Test aligning within same month"""
        start = date(2025, 10, 5)
        result = _align_monthly(start, 1, 15)
        self.assertEqual(result, date(2025, 10, 15))
    
    def test_align_monthly_next_month(self):
        """Test aligning to next month when day passed"""
        start = date(2025, 10, 20)
        result = _align_monthly(start, 1, 15)  # 15th already passed
        self.assertEqual(result, date(2025, 11, 15))
    
    def test_align_monthly_day_adjustment(self):
        """Test day adjustment for months with fewer days"""
        start = date(2025, 1, 5)
        result = _align_monthly(start, 1, 31)  # Target day 31
        # Should align to Jan 31
        self.assertEqual(result, date(2025, 1, 31))
        
        # Advancing to Feb should adjust to Feb 28
        result = _align_monthly(date(2025, 2, 1), 1, 31)
        self.assertEqual(result, date(2025, 2, 28))
    
    def test_align_monthly_with_interval(self):
        """Test aligning with interval > 1"""
        start = date(2025, 1, 20)
        result = _align_monthly(start, 3, 15)  # Every 3 months, day 15 passed
        self.assertEqual(result, date(2025, 4, 15))


class TestAdvanceMonthly(unittest.TestCase):
    """Test cases for _advance_monthly helper function"""
    
    def test_advance_monthly_simple(self):
        """Test advancing by one month"""
        current = date(2025, 10, 15)
        result = _advance_monthly(current, 1, 15)
        self.assertEqual(result, date(2025, 11, 15))
    
    def test_advance_monthly_with_interval(self):
        """Test advancing by multiple months"""
        current = date(2025, 10, 15)
        result = _advance_monthly(current, 3, 15)
        self.assertEqual(result, date(2026, 1, 15))
    
    def test_advance_monthly_day_adjustment(self):
        """Test day adjustment for months with fewer days"""
        current = date(2025, 1, 31)
        result = _advance_monthly(current, 1, 31)
        self.assertEqual(result, date(2025, 2, 28))  # Feb doesn't have 31 days


class TestComputeEffectiveDueDate(unittest.TestCase):
    """Test cases for compute_effective_due_date function"""
    
    def test_non_recurring_task(self):
        """Test non-recurring task returns base due date"""
        task_data = {
            'end_date': '2025-10-30',
            'start_date': '2025-10-20',
            'recurrence': {'enabled': False}
        }
        current = date(2025, 10, 24)
        
        due_date, is_recurring = compute_effective_due_date(task_data, current)
        
        self.assertEqual(due_date, date(2025, 10, 30))
        self.assertFalse(is_recurring)
    
    def test_no_recurrence_field(self):
        """Test task without recurrence field"""
        task_data = {
            'end_date': '2025-10-30',
            'start_date': '2025-10-20'
        }
        current = date(2025, 10, 24)
        
        due_date, is_recurring = compute_effective_due_date(task_data, current)
        
        self.assertEqual(due_date, date(2025, 10, 30))
        self.assertFalse(is_recurring)
    
    def test_daily_recurring_task(self):
        """Test daily recurring task"""
        task_data = {
            'end_date': '2025-10-20',
            'start_date': '2025-10-20',
            'recurrence': {
                'enabled': True,
                'frequency': 'daily',
                'interval': 1,
                'endCondition': 'never'
            }
        }
        current = date(2025, 10, 24)
        
        due_date, is_recurring = compute_effective_due_date(task_data, current)
        
        self.assertGreaterEqual(due_date, current)
        self.assertTrue(is_recurring)
    
    def test_weekly_recurring_task(self):
        """Test weekly recurring task"""
        task_data = {
            'end_date': '2025-10-20',  # Monday
            'start_date': '2025-10-20',
            'recurrence': {
                'enabled': True,
                'frequency': 'weekly',
                'interval': 1,
                'weeklyDays': [0, 2, 4],  # Mon, Wed, Fri
                'endCondition': 'never'
            }
        }
        current = date(2025, 10, 24)  # Friday
        
        due_date, is_recurring = compute_effective_due_date(task_data, current)
        
        self.assertGreaterEqual(due_date, current)
        self.assertTrue(is_recurring)
        # Should be the next occurrence (Mon, Wed, or Fri)
        self.assertIn(due_date.weekday(), [0, 2, 4])
    
    def test_monthly_recurring_task(self):
        """Test monthly recurring task"""
        task_data = {
            'end_date': '2025-09-15',
            'start_date': '2025-09-15',
            'recurrence': {
                'enabled': True,
                'frequency': 'monthly',
                'interval': 1,
                'monthlyDay': 15,
                'endCondition': 'never'
            }
        }
        current = date(2025, 10, 24)
        
        due_date, is_recurring = compute_effective_due_date(task_data, current)
        
        self.assertGreaterEqual(due_date, current)
        self.assertTrue(is_recurring)
        # Should be on the 15th
        self.assertEqual(due_date.day, 15)
    
    def test_recurring_with_max_occurrences(self):
        """Test recurring task with max occurrences"""
        task_data = {
            'end_date': '2025-10-20',
            'start_date': '2025-10-20',
            'recurrence': {
                'enabled': True,
                'frequency': 'daily',
                'interval': 1,
                'endCondition': 'after',
                'endAfterOccurrences': 5
            }
        }
        current = date(2025, 10, 30)  # After 5 occurrences
        
        due_date, is_recurring = compute_effective_due_date(task_data, current)
        
        # Should return the last occurrence
        self.assertIsNotNone(due_date)
        self.assertTrue(is_recurring)
    
    def test_recurring_with_end_date(self):
        """Test recurring task with end date"""
        task_data = {
            'end_date': '2025-10-20',
            'start_date': '2025-10-20',
            'recurrence': {
                'enabled': True,
                'frequency': 'daily',
                'interval': 1,
                'endCondition': 'ondate',
                'endDate': '2025-10-25'
            }
        }
        current = date(2025, 10, 30)  # After end date
        
        due_date, is_recurring = compute_effective_due_date(task_data, current)
        
        # Should return the end date or last valid occurrence
        self.assertLessEqual(due_date, date(2025, 10, 25))
        self.assertTrue(is_recurring)
    
    def test_task_without_dates(self):
        """Test task without dates"""
        task_data = {
            'recurrence': {
                'enabled': True,
                'frequency': 'daily',
                'interval': 1
            }
        }
        current = date(2025, 10, 24)
        
        due_date, is_recurring = compute_effective_due_date(task_data, current)
        
        self.assertIsNone(due_date)
        self.assertTrue(is_recurring)


class TestWeekdayMap(unittest.TestCase):
    """Test the WEEKDAY_MAP constant"""
    
    def test_weekday_map_exists(self):
        """Test that WEEKDAY_MAP is defined"""
        self.assertIsNotNone(WEEKDAY_MAP)
        self.assertIsInstance(WEEKDAY_MAP, dict)
    
    def test_weekday_map_values(self):
        """Test WEEKDAY_MAP has correct values"""
        self.assertEqual(WEEKDAY_MAP['mon'], 0)
        self.assertEqual(WEEKDAY_MAP['tue'], 1)
        self.assertEqual(WEEKDAY_MAP['wed'], 2)
        self.assertEqual(WEEKDAY_MAP['thu'], 3)
        self.assertEqual(WEEKDAY_MAP['fri'], 4)
        self.assertEqual(WEEKDAY_MAP['sat'], 5)
        self.assertEqual(WEEKDAY_MAP['sun'], 6)


if __name__ == '__main__':
    unittest.main()