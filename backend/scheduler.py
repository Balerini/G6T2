#!/usr/bin/env python3


import sys
import os
import argparse
from datetime import datetime
import pytz

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.notification_service import notification_service

def main():
    parser = argparse.ArgumentParser(description='Run notification checks for task deadlines and overdue tasks')
    parser.add_argument('--deadlines', action='store_true', help='Check upcoming deadlines only')
    parser.add_argument('--overdue', action='store_true', help='Check overdue tasks only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Get Singapore timezone
    sg_tz = pytz.timezone('Asia/Singapore')
    current_time = datetime.now(sg_tz)
    
    
    total_notifications = 0
    
    try:
        if args.deadlines:
            # Check deadlines only
         
            count = notification_service.notify_upcoming_deadlines()
            total_notifications += count
           
            
        elif args.overdue:
            # Check overdue only
            count = notification_service.notify_overdue_tasks()
            total_notifications += count
         
        else:
            # Check both
            deadline_count = notification_service.notify_upcoming_deadlines()
            total_notifications += deadline_count

            overdue_count = notification_service.notify_overdue_tasks()
            total_notifications += overdue_count
           
        
    except Exception as e:
       
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
