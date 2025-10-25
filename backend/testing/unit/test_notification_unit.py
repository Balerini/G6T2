"""
Unit Tests for Task Notification System (Bell Icon Functionality)
Tests the notification service core functionality only (no API integration)
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from datetime import datetime, timedelta
import pytz

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the database and email service before importing
with patch('firebase_utils.get_firestore_client') as mock_get_firestore_client, \
     patch('services.email_service.email_service') as mock_email_service:
    
    # Set up mock database
    mock_db = MagicMock()
    mock_get_firestore_client.return_value = mock_db
    
    # Set up mock email service
    mock_email_service.send_deadline_reminder_email.return_value = True
    
    from services.notification_service import NotificationService

class TestNotificationService(unittest.TestCase):
    """Test the NotificationService class core functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.notification_service = NotificationService()
        # Clear the cache for each test
        self.notification_service.notifications_cache = {}
        self.notification_service.notification_counter = 0
        
    def tearDown(self):
        """Clean up after each test"""
        self.notification_service.notifications_cache = {}
        
    def test_create_notification_success(self):
        """Test successful notification creation"""
        user_id = "test_user_123"
        notification_type = "task_assigned"
        title = "New Task Assigned"
        message = "You have been assigned to a new task"
        task_id = "task_456"
        project_id = "project_789"
        
        notification_id = self.notification_service.create_notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            task_id=task_id,
            project_id=project_id
        )
        
        # Verify notification was created
        self.assertIsNotNone(notification_id)
        self.assertIsInstance(notification_id, str)
        
        # Verify notification is stored in cache
        user_notifications = self.notification_service.notifications_cache.get(user_id, [])
        self.assertEqual(len(user_notifications), 1)
        
        notification = user_notifications[0]
        self.assertEqual(notification['id'], notification_id)
        self.assertEqual(notification['user_id'], user_id)
        self.assertEqual(notification['type'], notification_type)
        self.assertEqual(notification['title'], title)
        self.assertEqual(notification['message'], message)
        self.assertEqual(notification['task_id'], task_id)
        self.assertEqual(notification['project_id'], project_id)
        self.assertFalse(notification['read'])
        self.assertIsNotNone(notification['timestamp'])
        
    def test_create_notification_minimal_data(self):
        """Test notification creation with minimal required data"""
        user_id = "test_user_123"
        notification_type = "deadline"
        title = "Deadline Approaching"
        message = "Task is due soon"
        
        notification_id = self.notification_service.create_notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message
        )
        
        self.assertIsNotNone(notification_id)
        
        # Verify notification is stored
        user_notifications = self.notification_service.notifications_cache.get(user_id, [])
        self.assertEqual(len(user_notifications), 1)
        
        notification = user_notifications[0]
        self.assertEqual(notification['user_id'], user_id)
        self.assertEqual(notification['type'], notification_type)
        self.assertIsNone(notification.get('task_id'))
        self.assertIsNone(notification.get('project_id'))
        
    def test_create_notification_error_handling(self):
        """Test notification creation error handling"""
        # Test with invalid data that might cause errors
        with patch('uuid.uuid4', side_effect=Exception("UUID generation failed")):
            notification_id = self.notification_service.create_notification(
                user_id="test_user",
                notification_type="test",
                title="Test",
                message="Test message"
            )
            
            self.assertIsNone(notification_id)
            
    def test_get_user_notifications_basic(self):
        """Test getting user notifications"""
        user_id = "test_user_123"
        
        # Create test notifications
        self.notification_service.create_notification(
            user_id=user_id,
            notification_type="task_assigned",
            title="Task 1",
            message="Message 1"
        )
        
        self.notification_service.create_notification(
            user_id=user_id,
            notification_type="deadline",
            title="Task 2",
            message="Message 2"
        )
        
        # Get notifications
        notifications = self.notification_service.get_user_notifications(user_id)
        
        self.assertEqual(len(notifications), 2)
        self.assertEqual(notifications[0]['title'], "Task 2")  # Should be sorted by timestamp desc
        
    def test_get_user_notifications_with_limit(self):
        """Test getting user notifications with limit"""
        user_id = "test_user_123"
        
        # Create 5 notifications
        for i in range(5):
            self.notification_service.create_notification(
                user_id=user_id,
                notification_type="test",
                title=f"Task {i}",
                message=f"Message {i}"
            )
        
        # Get with limit of 3
        notifications = self.notification_service.get_user_notifications(user_id, limit=3)
        
        self.assertEqual(len(notifications), 3)
        
    def test_get_user_notifications_unread_only(self):
        """Test getting only unread notifications"""
        user_id = "test_user_123"
        
        # Create notifications
        notif1_id = self.notification_service.create_notification(
            user_id=user_id,
            notification_type="test1",
            title="Task 1",
            message="Message 1"
        )
        
        notif2_id = self.notification_service.create_notification(
            user_id=user_id,
            notification_type="test2",
            title="Task 2",
            message="Message 2"
        )
        
        # Mark first notification as read
        self.notification_service.mark_as_read(notif1_id)
        
        # Get only unread notifications
        unread_notifications = self.notification_service.get_user_notifications(
            user_id, unread_only=True
        )
        
        self.assertEqual(len(unread_notifications), 1)
        self.assertEqual(unread_notifications[0]['id'], notif2_id)
        
    def test_mark_as_read_success(self):
        """Test marking notification as read"""
        user_id = "test_user_123"
        
        notification_id = self.notification_service.create_notification(
            user_id=user_id,
            notification_type="test",
            title="Test Task",
            message="Test Message"
        )
        
        # Mark as read
        result = self.notification_service.mark_as_read(notification_id)
        
        self.assertTrue(result)
        
        # Verify notification is marked as read
        notifications = self.notification_service.get_user_notifications(user_id)
        self.assertTrue(notifications[0]['read'])
        
    def test_mark_as_read_not_found(self):
        """Test marking non-existent notification as read"""
        result = self.notification_service.mark_as_read("non_existent_id")
        self.assertFalse(result)
        
    def test_mark_all_as_read_success(self):
        """Test marking all notifications as read for a user"""
        user_id = "test_user_123"
        
        # Create multiple notifications
        for i in range(3):
            self.notification_service.create_notification(
                user_id=user_id,
                notification_type="test",
                title=f"Task {i}",
                message=f"Message {i}"
            )
        
        # Mark all as read
        count = self.notification_service.mark_all_as_read(user_id)
        
        self.assertEqual(count, 3)
        
        # Verify all are marked as read
        notifications = self.notification_service.get_user_notifications(user_id)
        for notification in notifications:
            self.assertTrue(notification['read'])
            
    def test_mark_all_as_read_no_notifications(self):
        """Test marking all as read when user has no notifications"""
        user_id = "test_user_123"
        
        count = self.notification_service.mark_all_as_read(user_id)
        
        self.assertEqual(count, 0)
        
    def test_delete_notification_success(self):
        """Test deleting a notification"""
        user_id = "test_user_123"
        
        notification_id = self.notification_service.create_notification(
            user_id=user_id,
            notification_type="test",
            title="Test Task",
            message="Test Message"
        )
        
        # Delete notification
        result = self.notification_service.delete_notification(notification_id)
        
        self.assertTrue(result)
        
        # Verify notification is deleted
        notifications = self.notification_service.get_user_notifications(user_id)
        self.assertEqual(len(notifications), 0)
        
    def test_delete_notification_not_found(self):
        """Test deleting non-existent notification"""
        result = self.notification_service.delete_notification("non_existent_id")
        self.assertFalse(result)
        
    def test_notification_timestamp_format(self):
        """Test that notification timestamps are in correct format"""
        user_id = "test_user_123"
        
        notification_id = self.notification_service.create_notification(
            user_id=user_id,
            notification_type="test",
            title="Test Task",
            message="Test Message"
        )
        
        notifications = self.notification_service.get_user_notifications(user_id)
        timestamp = notifications[0]['timestamp']
        
        # Should be ISO format string
        self.assertIsInstance(timestamp, str)
        self.assertIn('T', timestamp)  # ISO format includes 'T'
        
        # Should be parseable as datetime
        parsed_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        self.assertIsInstance(parsed_time, datetime)
    
    @patch('services.notification_service.get_firestore_client')
    def test_notify_task_assigned(self, mock_get_firestore_client):
        """Test notifying staff members when assigned to a task"""
        # Set up mock database
        mock_db = MagicMock()
        mock_get_firestore_client.return_value = mock_db
        
        # Mock user document
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role_name': 'staff',
            'role_num': 4,
            'name': 'Test User',
            'email': 'test@example.com'
        }
        
        # Mock users collection
        mock_users_ref = MagicMock()
        mock_users_ref.document.return_value.get.return_value = mock_user_doc
        mock_db.collection.return_value = mock_users_ref
        
        # Test data
        task_data = {
            'task_name': 'Test Task',
            'task_ID': 'task_123',
            'proj_ID': 'project_456'
        }
        assigned_user_ids = ['user_123']
        
        # Call the method
        self.notification_service.notify_task_assigned(task_data, assigned_user_ids)
        
        # Verify database was queried
        mock_db.collection.assert_called_with('Users')
        mock_users_ref.document.assert_called_with('user_123')
        
        # Verify notification was created
        notifications = self.notification_service.get_user_notifications('user_123')
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0]['type'], 'task_assigned')
        self.assertEqual(notifications[0]['title'], 'New Task Assigned')
    
    @patch('services.notification_service.get_firestore_client')
    def test_notify_upcoming_deadlines(self, mock_get_firestore_client):
        """Test checking for upcoming deadlines"""
        # Set up mock database
        mock_db = MagicMock()
        mock_get_firestore_client.return_value = mock_db
        
        # Mock task document
        mock_task_doc = MagicMock()
        mock_task_doc.id = 'task_123'
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Test Task',
            'end_date': datetime.now() + timedelta(hours=12),  # Due in 12 hours
            'assigned_to': ['user_123'],
            'proj_ID': 'project_456'
        }
        
        # Mock user document
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role_name': 'staff',
            'role_num': 4,
            'name': 'Test User',
            'email': 'test@example.com'
        }
        
        # Mock collections
        mock_tasks_ref = MagicMock()
        mock_tasks_ref.stream.return_value = [mock_task_doc]
        mock_users_ref = MagicMock()
        mock_users_ref.document.return_value.get.return_value = mock_user_doc
        mock_projects_ref = MagicMock()
        mock_project_doc = MagicMock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {'project_name': 'Test Project'}
        mock_projects_ref.document.return_value.get.return_value = mock_project_doc
        
        mock_db.collection.side_effect = lambda name: {
            'Tasks': mock_tasks_ref,
            'Users': mock_users_ref,
            'Projects': mock_projects_ref
        }[name]
        
        # Call the method
        result = self.notification_service.notify_upcoming_deadlines()
        
        # Verify result
        self.assertGreaterEqual(result, 0)
    
    @patch('services.notification_service.get_firestore_client')
    def test_notify_task_updated(self, mock_get_firestore_client):
        """Test notifying staff members when a task is updated"""
        # Set up mock database
        mock_db = MagicMock()
        mock_get_firestore_client.return_value = mock_db
        
        # Mock user document
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role_name': 'staff',
            'role_num': 4,
            'name': 'Test User',
            'email': 'test@example.com'
        }
        
        # Mock users collection
        mock_users_ref = MagicMock()
        mock_users_ref.document.return_value.get.return_value = mock_user_doc
        mock_db.collection.return_value = mock_users_ref
        
        # Test data
        task_data = {
            'task_name': 'Updated Task',
            'task_ID': 'task_123',
            'proj_ID': 'project_456'
        }
        assigned_user_ids = ['user_123']
        updated_fields = ['task_name', 'end_date']
        
        # Call the method
        self.notification_service.notify_task_updated(
            task_data, assigned_user_ids, updated_fields
        )
        
        # Verify database was queried
        mock_db.collection.assert_called_with('Users')
        
        # Verify notification was created
        notifications = self.notification_service.get_user_notifications('user_123')
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0]['type'], 'task_updated')
        self.assertEqual(notifications[0]['title'], 'Task Updated')
    
    def test_generate_update_message_single_field(self):
        """Test generating update message for single field"""
        task_name = "Test Task"
        updated_fields = ["task_name"]
        task_data = {"task_name": "New Task Name"}
        
        title, message = self.notification_service._generate_update_message(
            task_name, updated_fields, task_data
        )
        
        self.assertEqual(title, "Task Updated")
        self.assertEqual(message, "Test Task: Task name has been changed")
    
    def test_generate_update_message_multiple_fields(self):
        """Test generating update message for multiple fields"""
        task_name = "Test Task"
        updated_fields = ["task_name", "end_date", "priority_level"]
        task_data = {"task_name": "New Task Name"}
        
        title, message = self.notification_service._generate_update_message(
            task_name, updated_fields, task_data
        )
        
        self.assertEqual(title, "Task Updated")
        self.assertEqual(message, "Test Task has been updated")
    
    def test_generate_update_message_unknown_field(self):
        """Test generating update message for unknown field"""
        task_name = "Test Task"
        updated_fields = ["unknown_field"]
        task_data = {"unknown_field": "value"}
        
        title, message = self.notification_service._generate_update_message(
            task_name, updated_fields, task_data
        )
        
        self.assertEqual(title, "Task Updated")
        self.assertEqual(message, "Test Task: Task has been updated")
    
    @patch('services.notification_service.get_firestore_client')
    def test_notify_task_assigned_non_staff_user(self, mock_get_firestore_client):
        """Test notifying non-staff users (should be skipped)"""
        # Set up mock database
        mock_db = MagicMock()
        mock_get_firestore_client.return_value = mock_db
        
        # Mock user document for non-staff user
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'role_name': 'manager',
            'role_num': 2,  # Not staff (4)
            'name': 'Test Manager',
            'email': 'manager@example.com'
        }
        
        # Mock users collection
        mock_users_ref = MagicMock()
        mock_users_ref.document.return_value.get.return_value = mock_user_doc
        mock_db.collection.return_value = mock_users_ref
        
        # Test data
        task_data = {
            'task_name': 'Test Task',
            'task_ID': 'task_123',
            'proj_ID': 'project_456'
        }
        assigned_user_ids = ['manager_123']
        
        # Call the method
        self.notification_service.notify_task_assigned(task_data, assigned_user_ids)
        
        # Verify no notification was created for non-staff user
        notifications = self.notification_service.get_user_notifications('manager_123')
        self.assertEqual(len(notifications), 0)
    
    @patch('services.notification_service.get_firestore_client')
    def test_notify_task_assigned_user_not_found(self, mock_get_firestore_client):
        """Test notifying when user document doesn't exist"""
        # Set up mock database
        mock_db = MagicMock()
        mock_get_firestore_client.return_value = mock_db
        
        # Mock user document that doesn't exist
        mock_user_doc = MagicMock()
        mock_user_doc.exists = False
        
        # Mock users collection
        mock_users_ref = MagicMock()
        mock_users_ref.document.return_value.get.return_value = mock_user_doc
        mock_db.collection.return_value = mock_users_ref
        
        # Test data
        task_data = {
            'task_name': 'Test Task',
            'task_ID': 'task_123',
            'proj_ID': 'project_456'
        }
        assigned_user_ids = ['nonexistent_user']
        
        # Call the method
        self.notification_service.notify_task_assigned(task_data, assigned_user_ids)
        
        # Verify no notification was created
        notifications = self.notification_service.get_user_notifications('nonexistent_user')
        self.assertEqual(len(notifications), 0)
    
    @patch('services.notification_service.get_firestore_client')
    def test_notify_task_assigned_exception_handling(self, mock_get_firestore_client):
        """Test exception handling in notify_task_assigned"""
        # Set up mock database to raise exception
        mock_db = MagicMock()
        mock_db.collection.side_effect = Exception("Database error")
        mock_get_firestore_client.return_value = mock_db
        
        # Test data
        task_data = {
            'task_name': 'Test Task',
            'task_ID': 'task_123',
            'proj_ID': 'project_456'
        }
        assigned_user_ids = ['user_123']
        
        # Call the method - should not raise exception
        self.notification_service.notify_task_assigned(task_data, assigned_user_ids)
        
        # Verify no notification was created due to error
        notifications = self.notification_service.get_user_notifications('user_123')
        self.assertEqual(len(notifications), 0)
    
    @patch('services.notification_service.get_firestore_client')
    def test_notify_upcoming_deadlines_exception_handling(self, mock_get_firestore_client):
        """Test exception handling in notify_upcoming_deadlines"""
        # Set up mock database to raise exception
        mock_db = MagicMock()
        mock_db.collection.side_effect = Exception("Database error")
        mock_get_firestore_client.return_value = mock_db
        
        # Call the method - should not raise exception
        result = self.notification_service.notify_upcoming_deadlines()
        
        # Should return 0 due to error
        self.assertEqual(result, 0)
    
    @patch('services.notification_service.get_firestore_client')
    def test_notify_task_updated_exception_handling(self, mock_get_firestore_client):
        """Test exception handling in notify_task_updated"""
        # Set up mock database to raise exception
        mock_db = MagicMock()
        mock_db.collection.side_effect = Exception("Database error")
        mock_get_firestore_client.return_value = mock_db
        
        # Test data
        task_data = {
            'task_name': 'Updated Task',
            'task_ID': 'task_123',
            'proj_ID': 'project_456'
        }
        assigned_user_ids = ['user_123']
        updated_fields = ['task_name']
        
        # Call the method - should not raise exception
        self.notification_service.notify_task_updated(
            task_data, assigned_user_ids, updated_fields
        )
        
        # Verify no notification was created due to error
        notifications = self.notification_service.get_user_notifications('user_123')
        self.assertEqual(len(notifications), 0)
    
    def test_get_user_notifications_exception_handling(self):
        """Test exception handling in get_user_notifications"""
        # This test is already covered by the existing tests, but let's add one more edge case
        user_id = "test_user_123"
        
        # Test with invalid user_id that might cause issues
        notifications = self.notification_service.get_user_notifications(None)
        self.assertEqual(len(notifications), 0)
    
    def test_mark_as_read_exception_handling(self):
        """Test exception handling in mark_as_read"""
        # Test with invalid notification_id
        result = self.notification_service.mark_as_read(None)
        self.assertFalse(result)
    
    def test_delete_notification_exception_handling(self):
        """Test exception handling in delete_notification"""
        # Test with invalid notification_id
        result = self.notification_service.delete_notification(None)
        self.assertFalse(result)


if __name__ == '__main__':
    print("=" * 80)
    print("C1 UNIT TESTING - NOTIFICATION SERVICE")
    print("=" * 80)
    print("Testing individual NotificationService methods in complete isolation")
    print("No external dependencies, no Flask app, no database")
    print("=" * 80)
    
    # Run with verbose output
    unittest.main(verbosity=2)
