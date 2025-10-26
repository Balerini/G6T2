"""
Pure utility functions for task-related operations.
These functions have no side effects and can be easily unit tested.
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any


def parse_date_value(value: Any) -> Optional[date]:
    """Parse various date formats into date objects"""
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


def validate_priority_level(priority_level: Any) -> bool:
    """Validate priority level is between 1 and 10"""
    try:
        priority = int(priority_level)
        return 1 <= priority <= 10
    except (ValueError, TypeError):
        return False


def validate_task_data(data: Dict[str, Any]) -> List[str]:
    """Validate task data structure and required fields"""
    errors = []
    required_fields = ['task_name', 'start_date', 'priority_level']
    
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Required field missing: {field}")
    
    # Validate priority level if present
    if data.get('priority_level') and not validate_priority_level(data['priority_level']):
        errors.append("Priority level must be between 1 and 10")
    
    return errors


def format_task_status(status: str) -> str:
    """Format task status for display"""
    if not status:
        return "Unknown"
    
    status_map = {
        'unassigned': 'Unassigned',
        'ongoing': 'Ongoing',
        'under_review': 'Under Review',
        'completed': 'Completed',
        'cancelled': 'Cancelled',
        'on_hold': 'On Hold'
    }
    return status_map.get(status.lower(), status.title())


def calculate_task_duration(start_date: str, end_date: str) -> int:
    """Calculate task duration in days"""
    try:
        start = parse_date_value(start_date)
        end = parse_date_value(end_date)
        
        if start and end:
            return (end - start).days
        return 0
    except Exception:
        return 0


def is_task_overdue(end_date: str) -> bool:
    """Check if task is overdue"""
    if not end_date:
        return False
    
    try:
        task_end = parse_date_value(end_date)
        if task_end:
            return task_end < date.today()
        return False
    except Exception:
        return False


def validate_subtask_data(data: Dict[str, Any]) -> List[str]:
    """Validate subtask data structure"""
    errors = []
    required_fields = ['subtask_name', 'start_date']
    
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Required field missing: {field}")
    
    return errors
