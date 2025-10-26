"""
Pure utility functions for dashboard-related operations.
These functions have no side effects and can be easily unit tested.
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import calendar


def safe_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    """Safely convert value to int, return default if conversion fails"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_date(value: Any) -> Optional[date]:
    """Convert various date formats to date object"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                return None
    return None


def add_months(base_date: date, months: int) -> date:
    """Add months to a date, handling month-end edge cases"""
    month_index = base_date.month - 1 + months
    year = base_date.year + month_index // 12
    month = month_index % 12 + 1
    day = min(base_date.day, calendar.monthrange(year, month)[1])
    return base_date.replace(year=year, month=month, day=day)


def get_weekly_days(recurrence: Dict[str, Any], fallback_weekday: int) -> List[int]:
    """Extract weekly days from recurrence configuration"""
    weekly_days = recurrence.get('weeklyDays') or recurrence.get('weekly_days', [])
    
    if not weekly_days:
        return [fallback_weekday]
    
    processed_days = []
    weekday_map = {
        'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3,
        'fri': 4, 'sat': 5, 'sun': 6
    }
    
    for day in weekly_days:
        if isinstance(day, int) and 0 <= day <= 6:
            processed_days.append(day)
        elif isinstance(day, str) and day.lower() in weekday_map:
            processed_days.append(weekday_map[day.lower()])
    
    return processed_days if processed_days else [fallback_weekday]


def align_weekly(start_date: date, weekly_days: List[int], interval: int) -> date:
    """Align date to the first occurrence of weekly pattern"""
    if not weekly_days:
        return start_date
    
    current_date = start_date
    iterations = 0
    max_iterations = 500
    
    while iterations < max_iterations:
        if current_date.weekday() in weekly_days:
            return current_date
        current_date += timedelta(days=1)
        iterations += 1
    
    return start_date


def advance_weekly(current_date: date, weekly_days: List[int], interval: int) -> date:
    """Advance to next occurrence of weekly pattern"""
    if not weekly_days:
        return current_date + timedelta(days=max(1, interval))
    
    next_date = current_date + timedelta(days=1)
    iterations = 0
    max_iterations = 500
    
    while iterations < max_iterations:
        if next_date.weekday() in weekly_days:
            return next_date
        next_date += timedelta(days=1)
        iterations += 1
    
    return current_date + timedelta(days=max(1, interval))


def align_monthly(start_date: date, interval: int, monthly_day: Optional[int]) -> date:
    """Align date to monthly pattern"""
    if monthly_day is None:
        monthly_day = start_date.day
    
    # Clamp to valid day for the month
    max_day = calendar.monthrange(start_date.year, start_date.month)[1]
    monthly_day = min(monthly_day, max_day)
    
    return start_date.replace(day=monthly_day)


def advance_monthly(current_date: date, interval: int, monthly_day: Optional[int]) -> date:
    """Advance to next monthly occurrence"""
    if monthly_day is None:
        monthly_day = current_date.day
    
    # Calculate next month
    next_date = add_months(current_date, interval)
    
    # Clamp to valid day for the month
    max_day = calendar.monthrange(next_date.year, next_date.month)[1]
    monthly_day = min(monthly_day, max_day)
    
    return next_date.replace(day=monthly_day)


def validate_dashboard_filters(filters: Dict[str, Any]) -> tuple[bool, str]:
    """Validate dashboard filter parameters"""
    if not filters:
        return True, "No filters to validate"
    
    # Validate date range
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    
    if start_date and end_date:
        start = to_date(start_date)
        end = to_date(end_date)
        
        if start and end and start > end:
            return False, "Start date cannot be after end date"
    
    # Validate status
    status = filters.get('status')
    valid_statuses = {'active', 'completed', 'cancelled', 'all'}
    if status and status.lower() not in valid_statuses:
        return False, "Invalid status filter"
    
    return True, "Valid filters"
