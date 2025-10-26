"""
Utils package for pure utility functions.

This package contains pure utility functions that have no side effects
and can be easily unit tested. These functions follow the pattern of
taking inputs and returning outputs without external dependencies.

Modules:
- task_utils: Task-related utility functions
- dashboard_utils: Dashboard-related utility functions
"""

# Import commonly used functions for easy access
from .task_utils import (
    parse_date_value,
    validate_priority_level,
    validate_task_data,
    format_task_status,
    calculate_task_duration,
    is_task_overdue,
    validate_subtask_data
)

from .dashboard_utils import (
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

__all__ = [
    # Task utilities
    'parse_date_value',
    'validate_priority_level', 
    'validate_task_data',
    'format_task_status',
    'calculate_task_duration',
    'is_task_overdue',
    'validate_subtask_data',
    
    # Dashboard utilities
    'safe_int',
    'to_date',
    'add_months',
    'get_weekly_days',
    'align_weekly',
    'advance_weekly',
    'align_monthly',
    'advance_monthly',
    'validate_dashboard_filters'
]
