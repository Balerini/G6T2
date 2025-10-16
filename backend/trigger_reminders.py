#!/usr/bin/env python3
"""
Simple script to trigger 24-hour deadline reminders
Can be run manually or via cron job
"""

import sys
import os
from datetime import datetime
import pytz

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.notification_service import notification_service

def main():
    # Get Singapore timezone
    sg_tz = pytz.timezone('Asia/Singapore')
    current_time = datetime.now(sg_tz)
    
    
    try:
        # Check for upcoming deadlines (24-hour reminders)
        notification_count = notification_service.notify_upcoming_deadlines()
        

        
        if notification_count > 0:
            print(f"📧 {notification_count} email reminders sent to staff members")
        else:
            print("ℹ️  No tasks due within 24 hours")
            
    except Exception as e:
      
        sys.exit(1)

if __name__ == '__main__':
    main()
