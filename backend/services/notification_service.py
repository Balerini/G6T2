"""
Notification Service for Staff Members
Handles notifications for task assignments, upcoming deadlines, and task updates
Uses in-memory storage (no Firestore)
"""
from datetime import datetime, timedelta
import sys
import os
import uuid
import pytz

# Add parent directory to path to import firebase_utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from firebase_utils import get_firestore_client

class NotificationService:
    def __init__(self):
        self._db = None
        # In-memory notification storage: {user_id: [notifications]}
        self.notifications_cache = {}
        self.notification_counter = 0
    
    @property
    def db(self):
        """Lazy-load Firestore client (only for user role checking)"""
        if self._db is None:
            self._db = get_firestore_client()
        return self._db
        
    def create_notification(self, user_id, notification_type, title, message, task_id=None, project_id=None):
        """
        Create a notification for a user (stored in memory)
        
        Args:
            user_id: ID of the user to notify
            notification_type: Type of notification (task_assigned, deadline, update)
            title: Notification title
            message: Notification message
            task_id: Optional task ID
            project_id: Optional project ID
        
        Returns:
            Notification ID
        """
        try:
            # Generate unique notification ID
            notification_id = str(uuid.uuid4())
            
            # Use Singapore timezone
            sg_tz = pytz.timezone('Asia/Singapore')
            sg_time = datetime.now(sg_tz)
            
            notification_data = {
                'id': notification_id,
                'user_id': user_id,
                'type': notification_type,
                'title': title,
                'message': message,
                'task_id': task_id,
                'project_id': project_id,
                'read': False,
                'timestamp': sg_time.isoformat()
            }
            
            # Store in memory
            if user_id not in self.notifications_cache:
                self.notifications_cache[user_id] = []
            
            self.notifications_cache[user_id].append(notification_data)
            
            print(f"✅ In-memory notification created for user {user_id}: {title} (ID: {notification_id})")
            return notification_id
            
        except Exception as e:
            print(f"❌ Error creating notification: {str(e)}")
            return None
    
    def notify_task_assigned(self, task_data, assigned_user_ids):
        """
        Notify staff members when they are assigned to a task
        
        Args:
            task_data: Task information (dict with task_name, task_ID, etc.)
            assigned_user_ids: List of user IDs assigned to the task
        """
        try:
            print(f"🔔 notify_task_assigned called for {len(assigned_user_ids)} users")
            # Get user details to check if they are staff
            users_ref = self.db.collection('Users')
            
            for user_id in assigned_user_ids:
                print(f"🔍 Checking user {user_id}...")
                # Get user document
                user_doc = users_ref.document(user_id).get()
                
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    role_name = user_data.get('role_name', '')
                    role_num = user_data.get('role_num')
                    
                    # Convert role_num to int if it's a string
                    if isinstance(role_num, str):
                        role_num = int(role_num)
                    
                    print(f"   User role_name: {role_name}, role_num: {role_num} (type: {type(role_num).__name__})")
                    
                    # Only notify staff members (role_num = 4)
                    if role_num == 4 or role_name.lower() == 'staff':
                        print(f"   ✅ User is staff - creating notification")
                        title = "New Task Assigned"
                        message = f'You have been assigned to "{task_data.get("task_name", "a task")}"'
                        
                        notification_id = self.create_notification(
                            user_id=user_id,
                            notification_type='task_assigned',
                            title=title,
                            message=message,
                            task_id=task_data.get('task_ID') or task_data.get('id'),
                            project_id=task_data.get('proj_ID')
                        )
                        print(f"   📬 Notification {notification_id} created for user {user_id}")
                    else:
                        print(f"   ⏭️  User is not staff (role_num={role_num}) - skipping")
                else:
                    print(f"   ⚠️  User document not found for {user_id}")
                        
        except Exception as e:
            print(f"❌ Error notifying task assignment: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def notify_upcoming_deadlines(self):
        """
        Check for tasks due within 24 hours and notify assigned staff members
        This should be run periodically (e.g., every hour via cron job)
        """
        try:
            print("🔔 Checking for upcoming deadlines...")
            # Get all tasks from Tasks collection
            tasks_ref = self.db.collection('Tasks')
            tasks = tasks_ref.stream()
            
            # Use Singapore timezone
            sg_tz = pytz.timezone('Asia/Singapore')
            now = datetime.now(sg_tz)
            deadline_threshold = now + timedelta(hours=24)
            
            notification_count = 0
            
            for task_doc in tasks:
                task_data = task_doc.to_dict()
                task_id = task_doc.id
                
                # Parse end_date
                end_date = task_data.get('end_date')
                if not end_date:
                    continue
                
                try:
                    # Handle datetime object from Firestore
                    if hasattr(end_date, 'replace'):
                        # Already a datetime object, ensure it has timezone
                        if end_date.tzinfo is None:
                            end_date = sg_tz.localize(end_date)
                        else:
                            end_date = end_date.astimezone(sg_tz)
                    
                    # Check if task is due within 24 hours
                    if now < end_date <= deadline_threshold:
                        assigned_users = task_data.get('assigned_to', [])
                        
                        # Notify each assigned staff member
                        for user_id in assigned_users:
                            # Check if user is staff
                            user_doc = self.db.collection('Users').document(user_id).get()
                            
                            if user_doc.exists:
                                user_data = user_doc.to_dict()
                                role_num = user_data.get('role_num')
                                if isinstance(role_num, str):
                                    role_num = int(role_num)
                                
                                # Only notify staff members
                                if role_num == 4 or user_data.get('role_name', '').lower() == 'staff':
                                    # Check if we already sent this notification in the last 23 hours
                                    # Using in-memory cache
                                    user_notifications = self.notifications_cache.get(user_id, [])
                                    should_notify = True
                                    
                                    for notif in user_notifications:
                                        if (notif.get('task_id') == task_id and 
                                            notif.get('type') == 'deadline'):
                                            # Check if sent in last 23 hours
                                            notif_time = datetime.fromisoformat(notif.get('timestamp'))
                                            if (now - notif_time).total_seconds() < 23 * 3600:
                                                should_notify = False
                                                break
                                    
                                    if should_notify:
                                        hours_remaining = int((end_date - now).total_seconds() / 3600)
                                        title = "❗ Deadline Approaching!"
                                        message = f'{task_data.get("task_name", "A task")} is due in {hours_remaining} hours'
                                        
                                        self.create_notification(
                                            user_id=user_id,
                                            notification_type='deadline',
                                            title=title,
                                            message=message,
                                            task_id=task_id,
                                            project_id=task_data.get('proj_ID')
                                        )
                                        notification_count += 1
                
                except Exception as date_error:
                    print(f"❌ Error parsing date for task {task_data.get('task_name')}: {str(date_error)}")
                    continue
            
            print(f"✅ Deadline check completed - {notification_count} notifications created")
            return notification_count
            
        except Exception as e:
            print(f"❌ Error checking upcoming deadlines: {str(e)}")
            import traceback
            traceback.print_exc()
            return 0
    
    def notify_task_updated(self, task_data, assigned_user_ids, updated_fields, old_values=None, new_values=None):
        """
        Notify staff members when a task they're assigned to is updated
        
        Args:
            task_data: Updated task information
            assigned_user_ids: List of user IDs assigned to the task
            updated_fields: List of fields that were updated
            old_values: Dict of old field values (optional)
            new_values: Dict of new field values (optional)
        """
        try:
            users_ref = self.db.collection('Users')
            task_name = task_data.get('task_name', 'A task')
            
            # Generate specific, user-friendly message based on what changed
            title, message = self._generate_update_message(task_name, updated_fields, task_data, old_values, new_values)
            
            for user_id in assigned_user_ids:
                # Get user document
                user_doc = users_ref.document(user_id).get()
                
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    role_num = user_data.get('role_num')
                    if isinstance(role_num, str):
                        role_num = int(role_num)
                    
                    # Only notify staff members (role_num = 4)
                    if role_num == 4 or user_data.get('role_name', '').lower() == 'staff':
                        self.create_notification(
                            user_id=user_id,
                            notification_type='task_updated',
                            title=title,
                            message=message,
                            task_id=task_data.get('task_ID') or task_data.get('id'),
                            project_id=task_data.get('proj_ID')
                        )
                        
        except Exception as e:
            print(f"Error notifying task update: {str(e)}")
    
    def _generate_update_message(self, task_name, updated_fields, task_data, old_values=None, new_values=None):
        """
        Generate a user-friendly notification message based on what was updated
        
        Args:
            task_name: Name of the task
            updated_fields: List of field names that were updated
            task_data: Task data with new values
            old_values: Dict of old field values (optional)
            new_values: Dict of new field values (optional)
            
        Returns:
            Tuple of (title, message)
        """
        # Map field names to natural descriptions
        field_messages = {
            'task_name': 'Task name has been changed',
            'task_desc': 'Task description has been edited',
            'start_date': 'Start date has been changed',
            'end_date': 'Deadline has been changed',
            'task_status': 'Status has been updated',
            'priority_level': 'Priority has been changed',
            'attachments': 'Attachments have been updated',
            'proj_name': 'Project has been changed',
            'owner': 'Task owner has been changed'
        }
        
        title = "Task Updated"
        
        if len(updated_fields) == 1:
            # Single field - use specific message
            field = updated_fields[0]
            field_msg = field_messages.get(field, 'Task has been updated')
            message = f'{task_name}: {field_msg}'
        else:
            # Multiple fields - generic message
            message = f'{task_name} has been updated'
        
        return title, message
    
    def get_user_notifications(self, user_id, limit=50, unread_only=False):
        """
        Get notifications for a specific user (from memory)
        
        Args:
            user_id: User ID
            limit: Maximum number of notifications to return
            unread_only: If True, only return unread notifications
        
        Returns:
            List of notifications
        """
        try:
            # Get user's notifications from memory
            user_notifications = self.notifications_cache.get(user_id, [])
            
            # Filter by read status if needed
            if unread_only:
                user_notifications = [n for n in user_notifications if not n.get('read', False)]
            
            # Sort by timestamp descending (newest first)
            sorted_notifications = sorted(
                user_notifications, 
                key=lambda x: x.get('timestamp', ''), 
                reverse=True
            )
            
            # Apply limit
            limited_notifications = sorted_notifications[:limit]
            
            print(f"📬 Retrieved {len(limited_notifications)} in-memory notifications for user {user_id}")
            return limited_notifications
            
        except Exception as e:
            print(f"❌ Error getting user notifications: {str(e)}")
            return []
    
    def mark_as_read(self, notification_id):
        """
        Mark a notification as read (in memory)
        
        Args:
            notification_id: Notification ID
        """
        try:
            # Find and update notification in memory
            for user_id, notifications in self.notifications_cache.items():
                for notification in notifications:
                    if notification.get('id') == notification_id:
                        notification['read'] = True
                        print(f"✅ Marked notification {notification_id} as read")
                        return True
            
            print(f"⚠️ Notification {notification_id} not found")
            return False
            
        except Exception as e:
            print(f"❌ Error marking notification as read: {str(e)}")
            return False
    
    def mark_all_as_read(self, user_id):
        """
        Mark all notifications for a user as read (in memory)
        
        Args:
            user_id: User ID
        """
        try:
            user_notifications = self.notifications_cache.get(user_id, [])
            
            count = 0
            for notification in user_notifications:
                if not notification.get('read', False):
                    notification['read'] = True
                    count += 1
            
            print(f"✅ Marked {count} notifications as read for user {user_id}")
            return count
            
        except Exception as e:
            print(f"❌ Error marking all notifications as read: {str(e)}")
            return 0
    
    def delete_notification(self, notification_id):
        """
        Delete a notification (from memory)
        
        Args:
            notification_id: Notification ID
        """
        try:
            # Find and remove notification from memory
            for user_id, notifications in self.notifications_cache.items():
                for i, notification in enumerate(notifications):
                    if notification.get('id') == notification_id:
                        del notifications[i]
                        print(f"✅ Deleted notification {notification_id}")
                        return True
            
            print(f"⚠️ Notification {notification_id} not found for deletion")
            return False
            
        except Exception as e:
            print(f"❌ Error deleting notification: {str(e)}")
            return False

# Create singleton instance
notification_service = NotificationService()

