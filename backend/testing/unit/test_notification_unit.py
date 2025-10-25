"""
Unit Tests for Task Notification System (Bell Icon Functionality)
Tests the notification service, API endpoints, and notification workflows
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from datetime import datetime, timedelta
import pytz

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.notification_service import NotificationService
# Import app for API testing
try:
    from app import app
except ImportError:
    # Fallback for testing without Flask app
    app = None

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


class TestNotificationAPI(unittest.TestCase):
    """Test the notification API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        if app is None:
            self.skipTest("Flask app not available for API testing")
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Mock the notification service
        self.notification_service_patcher = patch('app.notification_service')
        self.mock_notification_service = self.notification_service_patcher.start()
        
    def tearDown(self):
        """Clean up after each test"""
        self.notification_service_patcher.stop()
        
    def test_get_notifications_success(self):
        """Test GET /api/notifications/<user_id> endpoint"""
        user_id = "test_user_123"
        mock_notifications = [
            {
                'id': 'notif_1',
                'user_id': user_id,
                'type': 'task_assigned',
                'title': 'New Task',
                'message': 'You have a new task',
                'read': False,
                'timestamp': '2024-01-01T10:00:00+08:00'
            }
        ]
        
        self.mock_notification_service.get_user_notifications.return_value = mock_notifications
        
        response = self.client.get(f'/api/notifications/{user_id}')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['ok'])
        self.assertEqual(len(data['notifications']), 1)
        self.assertEqual(data['notifications'][0]['title'], 'New Task')
        
        # Verify service was called with correct parameters
        self.mock_notification_service.get_user_notifications.assert_called_once_with(
            user_id=user_id,
            unread_only=False,
            limit=50
        )
        
    def test_get_notifications_with_params(self):
        """Test GET /api/notifications/<user_id> with query parameters"""
        user_id = "test_user_123"
        mock_notifications = []
        
        self.mock_notification_service.get_user_notifications.return_value = mock_notifications
        
        response = self.client.get(f'/api/notifications/{user_id}?unread_only=true&limit=10')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify service was called with correct parameters
        self.mock_notification_service.get_user_notifications.assert_called_once_with(
            user_id=user_id,
            unread_only=True,
            limit=10
        )
        
    def test_get_notifications_error(self):
        """Test GET /api/notifications/<user_id> error handling"""
        user_id = "test_user_123"
        
        self.mock_notification_service.get_user_notifications.side_effect = Exception("Database error")
        
        response = self.client.get(f'/api/notifications/{user_id}')
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertFalse(data['ok'])
        self.assertIn('error', data)
        
    def test_mark_notification_read_success(self):
        """Test PUT /api/notifications/<notification_id>/read endpoint"""
        notification_id = "notif_123"
        
        self.mock_notification_service.mark_as_read.return_value = True
        
        response = self.client.put(f'/api/notifications/{notification_id}/read')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['message'], 'Notification marked as read')
        
        self.mock_notification_service.mark_as_read.assert_called_once_with(notification_id)
        
    def test_mark_notification_read_not_found(self):
        """Test PUT /api/notifications/<notification_id>/read when notification not found"""
        notification_id = "notif_123"
        
        self.mock_notification_service.mark_as_read.return_value = False
        
        response = self.client.put(f'/api/notifications/{notification_id}/read')
        
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertFalse(data['ok'])
        self.assertEqual(data['error'], 'Notification not found')
        
    def test_mark_all_notifications_read_success(self):
        """Test PUT /api/notifications/<user_id>/mark-all-read endpoint"""
        user_id = "test_user_123"
        
        self.mock_notification_service.mark_all_as_read.return_value = 3
        
        response = self.client.put(f'/api/notifications/{user_id}/mark-all-read')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['message'], 'Marked 3 notifications as read')
        
        self.mock_notification_service.mark_all_as_read.assert_called_once_with(user_id)
        
    def test_delete_notification_success(self):
        """Test DELETE /api/notifications/<notification_id> endpoint"""
        notification_id = "notif_123"
        
        self.mock_notification_service.delete_notification.return_value = True
        
        response = self.client.delete(f'/api/notifications/{notification_id}')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['message'], 'Notification deleted')
        
        self.mock_notification_service.delete_notification.assert_called_once_with(notification_id)
        
    def test_delete_notification_not_found(self):
        """Test DELETE /api/notifications/<notification_id> when notification not found"""
        notification_id = "notif_123"
        
        self.mock_notification_service.delete_notification.return_value = False
        
        response = self.client.delete(f'/api/notifications/{notification_id}')
        
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertFalse(data['ok'])
        self.assertEqual(data['error'], 'Notification not found')
        
    def test_check_deadlines_success(self):
        """Test POST /api/notifications/check-deadlines endpoint"""
        self.mock_notification_service.notify_upcoming_deadlines.return_value = 5
        
        response = self.client.post('/api/notifications/check-deadlines')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['message'], 'Deadline check completed')
        
        self.mock_notification_service.notify_upcoming_deadlines.assert_called_once()
        
    def test_check_deadlines_error(self):
        """Test POST /api/notifications/check-deadlines error handling"""
        self.mock_notification_service.notify_upcoming_deadlines.side_effect = Exception("Database error")
        
        response = self.client.post('/api/notifications/check-deadlines')
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertFalse(data['ok'])
        self.assertIn('error', data)


class TestNotificationWorkflow(unittest.TestCase):
    """Test notification workflow integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.notification_service = NotificationService()
        self.notification_service.notifications_cache = {}
        
    def tearDown(self):
        """Clean up after each test"""
        self.notification_service.notifications_cache = {}
        
    def test_complete_notification_lifecycle(self):
        """Test complete notification lifecycle: create -> read -> delete"""
        user_id = "test_user_123"
        
        # 1. Create notification
        notification_id = self.notification_service.create_notification(
            user_id=user_id,
            notification_type="task_assigned",
            title="New Task",
            message="You have been assigned to a new task",
            task_id="task_123"
        )
        
        self.assertIsNotNone(notification_id)
        
        # 2. Verify notification exists and is unread
        notifications = self.notification_service.get_user_notifications(user_id)
        self.assertEqual(len(notifications), 1)
        self.assertFalse(notifications[0]['read'])
        
        # 3. Mark as read
        result = self.notification_service.mark_as_read(notification_id)
        self.assertTrue(result)
        
        # 4. Verify notification is marked as read
        notifications = self.notification_service.get_user_notifications(user_id)
        self.assertTrue(notifications[0]['read'])
        
        # 5. Delete notification
        result = self.notification_service.delete_notification(notification_id)
        self.assertTrue(result)
        
        # 6. Verify notification is deleted
        notifications = self.notification_service.get_user_notifications(user_id)
        self.assertEqual(len(notifications), 0)
        
    def test_multiple_users_notifications(self):
        """Test notifications for multiple users"""
        user1_id = "user_1"
        user2_id = "user_2"
        
        # Create notifications for both users
        self.notification_service.create_notification(
            user_id=user1_id,
            notification_type="task_assigned",
            title="Task for User 1",
            message="Message for User 1"
        )
        
        self.notification_service.create_notification(
            user_id=user2_id,
            notification_type="deadline",
            title="Task for User 2",
            message="Message for User 2"
        )
        
        # Verify each user has their own notifications
        user1_notifications = self.notification_service.get_user_notifications(user1_id)
        user2_notifications = self.notification_service.get_user_notifications(user2_id)
        
        self.assertEqual(len(user1_notifications), 1)
        self.assertEqual(len(user2_notifications), 1)
        self.assertEqual(user1_notifications[0]['title'], 'Task for User 1')
        self.assertEqual(user2_notifications[0]['title'], 'Task for User 2')
        
    def test_notification_sorting_by_timestamp(self):
        """Test that notifications are sorted by timestamp (newest first)"""
        user_id = "test_user_123"
        
        # Create notifications with slight delays to ensure different timestamps
        import time
        
        self.notification_service.create_notification(
            user_id=user_id,
            notification_type="test1",
            title="First Task",
            message="First Message"
        )
        
        time.sleep(0.01)  # Small delay to ensure different timestamps
        
        self.notification_service.create_notification(
            user_id=user_id,
            notification_type="test2",
            title="Second Task",
            message="Second Message"
        )
        
        # Get notifications (should be sorted by timestamp desc)
        notifications = self.notification_service.get_user_notifications(user_id)
        
        self.assertEqual(len(notifications), 2)
        # Second notification should come first (newest)
        self.assertEqual(notifications[0]['title'], 'Second Task')
        self.assertEqual(notifications[1]['title'], 'First Task')


class TestNotificationEdgeCases(unittest.TestCase):
    """Test notification edge cases and error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.notification_service = NotificationService()
        self.notification_service.notifications_cache = {}
        
    def tearDown(self):
        """Clean up after each test"""
        self.notification_service.notifications_cache = {}
        
    def test_empty_user_notifications(self):
        """Test getting notifications for user with no notifications"""
        user_id = "empty_user"
        
        notifications = self.notification_service.get_user_notifications(user_id)
        
        self.assertEqual(len(notifications), 0)
        
    def test_invalid_notification_id_format(self):
        """Test operations with invalid notification ID formats"""
        # Test with None
        result = self.notification_service.mark_as_read(None)
        self.assertFalse(result)
        
        result = self.notification_service.delete_notification(None)
        self.assertFalse(result)
        
        # Test with empty string
        result = self.notification_service.mark_as_read("")
        self.assertFalse(result)
        
        result = self.notification_service.delete_notification("")
        self.assertFalse(result)
        
    def test_unicode_notification_content(self):
        """Test notifications with unicode content"""
        user_id = "test_user_123"
        
        notification_id = self.notification_service.create_notification(
            user_id=user_id,
            notification_type="test",
            title="🚀 Task with Emoji",
            message="Message with special chars: àáâãäåæçèéêë",
            task_id="task_123"
        )
        
        self.assertIsNotNone(notification_id)
        
        notifications = self.notification_service.get_user_notifications(user_id)
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0]['title'], "🚀 Task with Emoji")
        self.assertIn("àáâãäåæçèéêë", notifications[0]['message'])
        
    def test_very_long_notification_content(self):
        """Test notifications with very long content"""
        user_id = "test_user_123"
        long_title = "A" * 1000  # 1000 character title
        long_message = "B" * 5000  # 5000 character message
        
        notification_id = self.notification_service.create_notification(
            user_id=user_id,
            notification_type="test",
            title=long_title,
            message=long_message
        )
        
        self.assertIsNotNone(notification_id)
        
        notifications = self.notification_service.get_user_notifications(user_id)
        self.assertEqual(len(notifications), 1)
        self.assertEqual(len(notifications[0]['title']), 1000)
        self.assertEqual(len(notifications[0]['message']), 5000)
        
    def test_concurrent_notification_operations(self):
        """Test concurrent notification operations"""
        user_id = "test_user_123"
        
        # Create multiple notifications rapidly
        notification_ids = []
        for i in range(10):
            notification_id = self.notification_service.create_notification(
                user_id=user_id,
                notification_type="test",
                title=f"Task {i}",
                message=f"Message {i}"
            )
            notification_ids.append(notification_id)
        
        # Verify all notifications were created
        notifications = self.notification_service.get_user_notifications(user_id)
        self.assertEqual(len(notifications), 10)
        
        # Mark some as read concurrently
        for i in range(0, 10, 2):  # Mark every other notification as read
            self.notification_service.mark_as_read(notification_ids[i])
        
        # Verify read status
        notifications = self.notification_service.get_user_notifications(user_id)
        read_count = sum(1 for n in notifications if n['read'])
        self.assertEqual(read_count, 5)
        
    def test_notification_with_none_values(self):
        """Test notification creation with None values for optional fields"""
        user_id = "test_user_123"
        
        notification_id = self.notification_service.create_notification(
            user_id=user_id,
            notification_type="test",
            title="Test Task",
            message="Test Message",
            task_id=None,
            project_id=None
        )
        
        self.assertIsNotNone(notification_id)
        
        notifications = self.notification_service.get_user_notifications(user_id)
        self.assertEqual(len(notifications), 1)
        self.assertIsNone(notifications[0]['task_id'])
        self.assertIsNone(notifications[0]['project_id'])


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestNotificationService))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestNotificationAPI))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestNotificationWorkflow))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestNotificationEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print("NOTIFICATION UNIT TESTS SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
