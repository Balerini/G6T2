#!/usr/bin/env python3


import sys
import os
import argparse
from datetime import datetime
import pytz

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize Firebase first
from firebase_utils import get_firebase_app
get_firebase_app()  # Initialize Firebase

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
        print(f"🔔 Checking for upcoming deadlines at {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}...")
        
        if args.deadlines:
            # Check deadlines only
            count = notification_service.notify_upcoming_deadlines()
            total_notifications += count
            print(f"✅ Deadline check completed - {count} notifications created")
            
        elif args.overdue:
            # Check overdue only (not implemented yet)
            print("⚠️  Overdue task notifications not implemented yet")
            count = 0
            total_notifications += count
            print(f"✅ Overdue check completed - {count} notifications created")
         
        else:
            # Check both (only deadlines implemented)
            deadline_count = notification_service.notify_upcoming_deadlines()
            total_notifications += deadline_count
            print(f"✅ Deadline check completed - {deadline_count} notifications created")

            print("⚠️  Overdue task notifications not implemented yet")
            overdue_count = 0
            total_notifications += overdue_count
            print(f"✅ Overdue check completed - {overdue_count} notifications created")
           
        print(f"📊 Total notifications created: {total_notifications}")
        
    except Exception as e:
        print(f"❌ Error checking upcoming deadlines: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
