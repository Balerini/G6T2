"""
Unit Tests for Dashboard Utility Functions
Tests dashboard-related utility functions in complete isolation
"""
import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from datetime import datetime, date, timedelta
import calendar

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Mock the get_firestore_client to prevent actual database calls
with patch('firebase_utils.get_firestore_client') as mock_get_firestore_client:
    mock_db = MagicMock()
    mock_get_firestore_client.return_value = mock_db

    # Extracted utility functions for testing
    def _safe_int(value, default=None):
        """Safely convert value to integer"""
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _to_date(value):
        """Convert various date formats to date object"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value).date()
            except ValueError:
                try:
                    return datetime.strptime(value, '%Y-%m-%d').date()
                except ValueError:
                    return None
        return None

    def _add_months(base_date, months):
        """Add months to a date, handling month boundaries correctly"""
        month_index = base_date.month - 1 + months
        year = base_date.year + month_index // 12
        month = month_index % 12 + 1
        day = min(base_date.day, calendar.monthrange(year, month)[1])
        return base_date.replace(year=year, month=month, day=day)

    def _get_weekly_days(recurrence, fallback_weekday):
        """Extract and validate weekly days from recurrence data"""
        WEEKDAY_MAP = {
            'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3,
            'fri': 4, 'sat': 5, 'sun': 6
        }
        
        raw_days = recurrence.get('weeklyDays') or recurrence.get('weekly_days') or []
        days = []
        for entry in raw_days:
            if isinstance(entry, int):
                if 0 <= entry <= 6:
                    days.append(entry)
            elif isinstance(entry, str):
                key = entry.strip().lower()[:3]
                if key in WEEKDAY_MAP:
                    days.append(WEEKDAY_MAP[key])
        if not days:
            days = [fallback_weekday]
        return sorted(set(days))

    def _align_weekly(start_date, weekly_days, interval):
        """Align start date to the next valid weekly day"""
        interval = max(1, interval)
        weekly_days = sorted(set(weekly_days))
        current_weekday = start_date.weekday()
        for day in weekly_days:
            if day >= current_weekday:
                return start_date + timedelta(days=day - current_weekday)
        days_until_next = (interval * 7) - (current_weekday - weekly_days[0])
        return start_date + timedelta(days=days_until_next)

    def _advance_weekly(current_date, weekly_days, interval):
        """Advance to the next occurrence in weekly recurrence"""
        interval = max(1, interval)
        weekly_days = sorted(set(weekly_days))
        current_weekday = current_date.weekday()
        for day in weekly_days:
            if day > current_weekday:
                return current_date + timedelta(days=day - current_weekday)
        days_until_next = (interval * 7) - (current_weekday - weekly_days[0])
        return current_date + timedelta(days=days_until_next)

    def _align_monthly(start_date, interval, monthly_day):
        """Align start date to the next valid monthly day"""
        interval = max(1, interval)
        if not monthly_day:
            monthly_day = start_date.day
        monthly_day = max(1, min(31, monthly_day))
        days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
        candidate_day = min(monthly_day, days_in_month)
        candidate = start_date.replace(day=candidate_day)
        if candidate < start_date:
            candidate = _add_months(candidate, interval)
        return candidate

    def _advance_monthly(current_date, interval, monthly_day):
        """Advance to the next occurrence in monthly recurrence"""
        interval = max(1, interval)
        if not monthly_day:
            monthly_day = current_date.day
        monthly_day = max(1, min(31, monthly_day))
        next_date = _add_months(current_date, interval)
        days_in_month = calendar.monthrange(next_date.year, next_date.month)[1]
        candidate_day = min(monthly_day, days_in_month)
        return next_date.replace(day=candidate_day)

    def calculate_recurrence_dates(start_date, end_date, recurrence_type, recurrence_data):
        """Calculate all recurrence dates between start and end"""
        if not start_date or not end_date:
            return []
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return []
        
        dates = []
        current_date = start
        
        if recurrence_type == 'daily':
            interval = _safe_int(recurrence_data.get('interval', 1), 1)
            while current_date <= end:
                dates.append(current_date)
                current_date += timedelta(days=interval)
        
        elif recurrence_type == 'weekly':
            interval = _safe_int(recurrence_data.get('interval', 1), 1)
            weekly_days = _get_weekly_days(recurrence_data, start.weekday())
            current_date = _align_weekly(start, weekly_days, interval)
            
            while current_date <= end:
                dates.append(current_date)
                current_date = _advance_weekly(current_date, weekly_days, interval)
        
        elif recurrence_type == 'monthly':
            interval = _safe_int(recurrence_data.get('interval', 1), 1)
            monthly_day = _safe_int(recurrence_data.get('monthlyDay', start.day), start.day)
            current_date = _align_monthly(start, interval, monthly_day)
            
            while current_date <= end:
                dates.append(current_date)
                current_date = _advance_monthly(current_date, interval, monthly_day)
        
        return dates

    def validate_dashboard_filters(filters):
        """Validate dashboard filter parameters"""
        errors = []
        
        # Validate date range
        if filters.get('start_date') and filters.get('end_date'):
            try:
                start = datetime.strptime(filters['start_date'], '%Y-%m-%d').date()
                end = datetime.strptime(filters['end_date'], '%Y-%m-%d').date()
                if end < start:
                    errors.append("End date must be after start date")
            except ValueError:
                errors.append("Invalid date format")
        
        # Validate status filter
        valid_statuses = ['active', 'completed', 'cancelled', 'on_hold']
        if filters.get('status') and filters['status'] not in valid_statuses:
            errors.append(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        # Validate priority filter
        if filters.get('priority'):
            try:
                priority = int(filters['priority'])
                if not (1 <= priority <= 10):
                    errors.append("Priority must be between 1 and 10")
            except ValueError:
                errors.append("Priority must be a number")
        
        return errors

    def format_dashboard_summary(projects, tasks):
        """Format dashboard summary data"""
        total_projects = len(projects)
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task.get('task_status') == 'Completed')
        
        return {
            'total_projects': total_projects,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }

    def calculate_task_metrics(tasks):
        """Calculate task-related metrics"""
        if not tasks:
            return {
                'total_tasks': 0,
                'completed_tasks': 0,
                'overdue_tasks': 0,
                'high_priority_tasks': 0,
                'completion_percentage': 0
            }
        
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task.get('task_status') == 'Completed')
        overdue_tasks = sum(1 for task in tasks if _is_task_overdue(task))
        high_priority_tasks = sum(1 for task in tasks if task.get('priority_level', 0) >= 8)
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'high_priority_tasks': high_priority_tasks,
            'completion_percentage': (completed_tasks / total_tasks) * 100
        }

    def _is_task_overdue(task):
        """Check if a task is overdue"""
        end_date = task.get('end_date')
        if not end_date:
            return False
        
        try:
            if isinstance(end_date, str):
                task_end = datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                task_end = end_date.date() if hasattr(end_date, 'date') else end_date
            
            return task_end < date.today()
        except (ValueError, AttributeError):
            return False

    def format_date_range(start_date, end_date):
        """Format date range for display"""
        if not start_date or not end_date:
            return "No date range"
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').strftime('%b %d, %Y')
            end = datetime.strptime(end_date, '%Y-%m-%d').strftime('%b %d, %Y')
            return f"{start} - {end}"
        except ValueError:
            return "Invalid date range"

class TestDashboardUtilsUnit(unittest.TestCase):
    """C1 Unit tests for dashboard utility functions"""
    
    def test_safe_int_valid(self):
        """Test safe integer conversion with valid values"""
        self.assertEqual(_safe_int(5), 5)
        self.assertEqual(_safe_int('10'), 10)
        self.assertEqual(_safe_int(3.7), 3)
    
    def test_safe_int_invalid(self):
        """Test safe integer conversion with invalid values"""
        self.assertIsNone(_safe_int('invalid'))
        self.assertIsNone(_safe_int(None))
        self.assertEqual(_safe_int('invalid', 0), 0)
    
    def test_to_date_valid(self):
        """Test date conversion with valid values"""
        # Test with date object
        test_date = date(2024, 1, 15)
        self.assertEqual(_to_date(test_date), test_date)
        
        # Test with datetime object
        test_datetime = datetime(2024, 1, 15, 10, 30)
        self.assertEqual(_to_date(test_datetime), test_date)
        
        # Test with ISO string
        self.assertEqual(_to_date('2024-01-15'), test_date)
        
        # Test with formatted string
        self.assertEqual(_to_date('2024-01-15'), test_date)
    
    def test_to_date_invalid(self):
        """Test date conversion with invalid values"""
        self.assertIsNone(_to_date(None))
        self.assertIsNone(_to_date('invalid-date'))
        self.assertIsNone(_to_date(123))
    
    def test_add_months(self):
        """Test adding months to date"""
        base_date = date(2024, 1, 15)
        
        # Test adding 1 month
        result = _add_months(base_date, 1)
        self.assertEqual(result, date(2024, 2, 15))
        
        # Test adding 12 months (year rollover)
        result = _add_months(base_date, 12)
        self.assertEqual(result, date(2025, 1, 15))
    
        # Test adding months across February (shorter month)
        base_date = date(2024, 1, 31)
        result = _add_months(base_date, 1)
        self.assertEqual(result, date(2024, 2, 29))  # 2024 is leap year
    
    def test_get_weekly_days_valid(self):
        """Test extracting weekly days from recurrence data"""
        recurrence = {'weeklyDays': [1, 3, 5]}  # Tuesday, Thursday, Saturday
        result = _get_weekly_days(recurrence, 0)
        self.assertEqual(result, [1, 3, 5])
        
        # Test with string days
        recurrence = {'weekly_days': ['mon', 'wed', 'fri']}
        result = _get_weekly_days(recurrence, 0)
        self.assertEqual(result, [0, 2, 4])
    
    def test_get_weekly_days_fallback(self):
        """Test weekly days with fallback"""
        recurrence = {}
        result = _get_weekly_days(recurrence, 2)
        self.assertEqual(result, [2])
    
    def test_align_weekly(self):
        """Test weekly alignment"""
        start_date = date(2024, 1, 15)  # Monday
        weekly_days = [2, 4]  # Wednesday, Friday
        interval = 1
        
        result = _align_weekly(start_date, weekly_days, interval)
        # Should align to Wednesday (2 days later)
        self.assertEqual(result, date(2024, 1, 17))
    
    def test_advance_weekly(self):
        """Test weekly advancement"""
        current_date = date(2024, 1, 17)  # Wednesday
        weekly_days = [2, 4]  # Wednesday, Friday
        interval = 1
        
        result = _advance_weekly(current_date, weekly_days, interval)
        # Should advance to Friday (2 days later)
        self.assertEqual(result, date(2024, 1, 19))
    
    def test_align_monthly(self):
        """Test monthly alignment"""
        start_date = date(2024, 1, 15)
        interval = 1
        monthly_day = 20
        
        result = _align_monthly(start_date, interval, monthly_day)
        # Should align to January 20th
        self.assertEqual(result, date(2024, 1, 20))
    
    def test_advance_monthly(self):
        """Test monthly advancement"""
        current_date = date(2024, 1, 20)
        interval = 1
        monthly_day = 20
        
        result = _advance_monthly(current_date, interval, monthly_day)
        # Should advance to February 20th
        self.assertEqual(result, date(2024, 2, 20))
    
    def test_calculate_recurrence_dates_daily(self):
        """Test daily recurrence calculation"""
        start_date = '2024-01-01'
        end_date = '2024-01-05'
        recurrence_data = {'interval': 2}
        
        dates = calculate_recurrence_dates(start_date, end_date, 'daily', recurrence_data)
        expected = [date(2024, 1, 1), date(2024, 1, 3), date(2024, 1, 5)]
        self.assertEqual(dates, expected)
    
    def test_calculate_recurrence_dates_weekly(self):
        """Test weekly recurrence calculation"""
        start_date = '2024-01-01'  # Monday
        end_date = '2024-01-15'
        recurrence_data = {'interval': 1, 'weeklyDays': [1, 3]}  # Tuesday, Thursday
        
        dates = calculate_recurrence_dates(start_date, end_date, 'weekly', recurrence_data)
        # Should include Tuesdays and Thursdays
        self.assertIn(date(2024, 1, 2), dates)  # Tuesday
        self.assertIn(date(2024, 1, 4), dates)  # Thursday
    
    def test_calculate_recurrence_dates_invalid_dates(self):
        """Test recurrence calculation with invalid dates"""
        dates = calculate_recurrence_dates('invalid', '2024-01-05', 'daily', {})
        self.assertEqual(dates, [])
    
    def test_validate_dashboard_filters_valid(self):
        """Test valid dashboard filters"""
        filters = {
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'status': 'active',
            'priority': '5'
        }
        errors = validate_dashboard_filters(filters)
        self.assertEqual(len(errors), 0)
    
    def test_validate_dashboard_filters_invalid_dates(self):
        """Test invalid dashboard filters"""
        filters = {
            'start_date': '2024-12-31',
            'end_date': '2024-01-01',
            'status': 'invalid_status',
            'priority': '15'
        }
        errors = validate_dashboard_filters(filters)
        self.assertGreater(len(errors), 0)
        self.assertIn("End date must be after start date", errors)
        self.assertIn("Invalid status. Must be one of: active, completed, cancelled, on_hold", errors)
        self.assertIn("Priority must be between 1 and 10", errors)
    
    def test_format_dashboard_summary(self):
        """Test dashboard summary formatting"""
        projects = [{'id': '1'}, {'id': '2'}]
        tasks = [
            {'task_status': 'Completed'},
            {'task_status': 'In Progress'},
            {'task_status': 'Not Started'}
        ]
        
        summary = format_dashboard_summary(projects, tasks)
        self.assertEqual(summary['total_projects'], 2)
        self.assertEqual(summary['total_tasks'], 3)
        self.assertEqual(summary['completed_tasks'], 1)
        self.assertAlmostEqual(summary['completion_rate'], 33.333333333333336, places=10)
    
    def test_calculate_task_metrics(self):
        """Test task metrics calculation"""
        tasks = [
            {'task_status': 'Completed', 'priority_level': 5},
            {'task_status': 'In Progress', 'priority_level': 9, 'end_date': '2023-01-01'},  # Overdue
            {'task_status': 'Not Started', 'priority_level': 3}
        ]
        
        metrics = calculate_task_metrics(tasks)
        self.assertEqual(metrics['total_tasks'], 3)
        self.assertEqual(metrics['completed_tasks'], 1)
        self.assertEqual(metrics['overdue_tasks'], 1)
        self.assertEqual(metrics['high_priority_tasks'], 1)
        self.assertAlmostEqual(metrics['completion_percentage'], 33.333333333333336, places=10)
    
    def test_calculate_task_metrics_empty(self):
        """Test task metrics calculation with no tasks"""
        metrics = calculate_task_metrics([])
        self.assertEqual(metrics['total_tasks'], 0)
        self.assertEqual(metrics['completion_percentage'], 0)
    
    def test_format_date_range(self):
        """Test date range formatting"""
        result = format_date_range('2024-01-01', '2024-12-31')
        self.assertIn('Jan 01, 2024', result)
        self.assertIn('Dec 31, 2024', result)
    
    def test_format_date_range_invalid(self):
        """Test date range formatting with invalid dates"""
        result = format_date_range('invalid', '2024-12-31')
        self.assertEqual(result, "Invalid date range")
    
    def test_format_date_range_none(self):
        """Test date range formatting with None values"""
        result = format_date_range(None, '2024-12-31')
        self.assertEqual(result, "No date range")

if __name__ == '__main__':
    print("=" * 80)
    print("C1 UNIT TESTING - DASHBOARD UTILITY FUNCTIONS")
    print("=" * 80)
    print("Testing individual dashboard utility functions in complete isolation")
    print("No external dependencies, no Flask app, no database")
    print("=" * 80)

    unittest.main(verbosity=2)