"""
Comprehensive Notification API Tests
Combines all notification testing functionality into one comprehensive test suite
"""
import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Flask app and notification service
try:
    from app import create_app
    from services.notification_service import notification_service
    app = create_app()
except ImportError:
    app = None
    notification_service = None

class TestNotificationAPIComprehensive(unittest.TestCase):
    """Comprehensive test cases for notification API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        if app is None:
            self.skipTest("Flask app not available for API testing")
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Clear any existing notifications for test users
        if notification_service:
            test_users = [
                "test_user_comprehensive", 
                "test_user_with_data", 
                "test_user_with_notifications",
                "test_user_mock",
                "test_user_error"
            ]
            for user_id in test_users:
                if user_id in notification_service.notifications_cache:
                    del notification_service.notifications_cache[user_id]
        
    def tearDown(self):
        """Clean up after each test"""
        # Clear test notifications
        if notification_service:
            test_users = [
                "test_user_comprehensive", 
                "test_user_with_data", 
                "test_user_with_notifications",
                "test_user_mock",
                "test_user_error"
            ]
            for user_id in test_users:
                if user_id in notification_service.notifications_cache:
                    del notification_service.notifications_cache[user_id]

    # ==================== REAL DATA TESTS ====================
    
    def test_get_notifications_with_real_data(self):
        """Test GET /api/notifications/<user_id> with real notification data"""
        user_id = "test_user_comprehensive"
        
        # Create real notifications first
        if notification_service:
            notification_service.create_notification(
                user_id=user_id,
                notification_type="task_assigned",
                title="Test Task 1",
                message="You have been assigned to a test task",
                task_id="task_123"
            )
            
            notification_service.create_notification(
                user_id=user_id,
                notification_type="deadline",
                title="Test Deadline",
                message="Task is due soon",
                task_id="task_456"
            )
        
        # Now test the API endpoint
        response = self.client.get(f'/api/notifications/{user_id}')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['ok'])
        self.assertIsInstance(data['notifications'], list)
        self.assertEqual(len(data['notifications']), 2)
        
        # Verify notification data
        notifications = data['notifications']
        self.assertEqual(notifications[0]['title'], 'Test Deadline')  # Should be sorted by timestamp
        self.assertEqual(notifications[1]['title'], 'Test Task 1')
        
    def test_get_notifications_with_unread_only(self):
        """Test GET /api/notifications/<user_id> with unread_only=true"""
        user_id = "test_user_with_notifications"
        
        # Create notifications with different read status
        if notification_service:
            notif1_id = notification_service.create_notification(
                user_id=user_id,
                notification_type="task_assigned",
                title="Unread Task",
                message="This is unread",
                task_id="task_1"
            )
            
            notif2_id = notification_service.create_notification(
                user_id=user_id,
                notification_type="deadline",
                title="Read Task",
                message="This is read",
                task_id="task_2"
            )
            
            # Mark second notification as read
            notification_service.mark_as_read(notif2_id)
        
        # Test with unread_only=true
        response = self.client.get(f'/api/notifications/{user_id}?unread_only=true')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['ok'])
        self.assertEqual(len(data['notifications']), 1)
        self.assertEqual(data['notifications'][0]['title'], 'Unread Task')
        
    def test_get_notifications_with_limit(self):
        """Test GET /api/notifications/<user_id> with limit parameter"""
        user_id = "test_user_with_notifications"
        
        # Create multiple notifications
        if notification_service:
            for i in range(5):
                notification_service.create_notification(
                    user_id=user_id,
                    notification_type="test",
                    title=f"Test Task {i}",
                    message=f"Test message {i}",
                    task_id=f"task_{i}"
                )
        
        # Test with limit=3
        response = self.client.get(f'/api/notifications/{user_id}?limit=3')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['ok'])
        self.assertEqual(len(data['notifications']), 3)
        
    def test_mark_notification_read_with_real_data(self):
        """Test PUT /api/notifications/<notification_id>/read with real notification"""
        user_id = "test_user_comprehensive"
        
        # Create a real notification
        if notification_service:
            notif_id = notification_service.create_notification(
                user_id=user_id,
                notification_type="task_assigned",
                title="Test Task",
                message="Test message",
                task_id="task_123"
            )
            
            # Test marking as read
            response = self.client.put(f'/api/notifications/{notif_id}/read')
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['ok'])
            self.assertEqual(data['message'], 'Notification marked as read')
            
            # Verify notification is actually marked as read
            notifications = notification_service.get_user_notifications(user_id)
            self.assertTrue(notifications[0]['read'])
        
    def test_mark_all_notifications_read_with_real_data(self):
        """Test PUT /api/notifications/<user_id>/mark-all-read with real notifications"""
        user_id = "test_user_comprehensive"
        
        # Create multiple notifications
        if notification_service:
            for i in range(3):
                notification_service.create_notification(
                    user_id=user_id,
                    notification_type="test",
                    title=f"Test Task {i}",
                    message=f"Test message {i}",
                    task_id=f"task_{i}"
                )
            
            # Test marking all as read
            response = self.client.put(f'/api/notifications/{user_id}/mark-all-read')
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['ok'])
            self.assertEqual(data['message'], 'Marked 3 notifications as read')
            
            # Verify all notifications are marked as read
            notifications = notification_service.get_user_notifications(user_id)
            for notification in notifications:
                self.assertTrue(notification['read'])
        
    def test_delete_notification_with_real_data(self):
        """Test DELETE /api/notifications/<notification_id> with real notification"""
        user_id = "test_user_comprehensive"
        
        # Create a real notification
        if notification_service:
            notif_id = notification_service.create_notification(
                user_id=user_id,
                notification_type="task_assigned",
                title="Test Task",
                message="Test message",
                task_id="task_123"
            )
            
            # Test deleting notification
            response = self.client.delete(f'/api/notifications/{notif_id}')
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['ok'])
            self.assertEqual(data['message'], 'Notification deleted')
            
            # Verify notification is actually deleted
            notifications = notification_service.get_user_notifications(user_id)
            self.assertEqual(len(notifications), 0)

    # ==================== BASIC FUNCTIONALITY TESTS ====================
    
    def test_get_notifications_empty_user(self):
        """Test GET /api/notifications/<user_id> with user who has no notifications"""
        user_id = "test_user_mock"
        
        response = self.client.get(f"/api/notifications/{user_id}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['ok'])
        self.assertEqual(len(data['notifications']), 0)
    
    def test_mark_all_notifications_read_empty_user(self):
        """Test PUT /api/notifications/<user_id>/mark-all-read with user who has no notifications"""
        user_id = "test_user_mock"
        
        response = self.client.put(f"/api/notifications/{user_id}/mark-all-read")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['ok'])
        self.assertEqual(data['message'], 'Marked 0 notifications as read')

    # ==================== ERROR HANDLING TESTS ====================
    
    def test_get_notifications_not_found(self):
        """Test GET /api/notifications/<user_id> when user has no notifications"""
        user_id = "nonexistent_user"
        
        response = self.client.get(f"/api/notifications/{user_id}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['ok'])
        self.assertEqual(len(data['notifications']), 0)
    
    def test_mark_notification_read_not_found(self):
        """Test PUT /api/notifications/<notification_id>/read when notification doesn't exist"""
        notification_id = "nonexistent_notif"
        
        response = self.client.put(f"/api/notifications/{notification_id}/read")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])
        self.assertEqual(data['error'], 'Notification not found')
    
    def test_delete_notification_not_found(self):
        """Test DELETE /api/notifications/<notification_id> when notification doesn't exist"""
        notification_id = "nonexistent_notif"
        
        response = self.client.delete(f"/api/notifications/{notification_id}")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])
        self.assertEqual(data['error'], 'Notification not found')
    
    def test_get_notifications_invalid_parameters(self):
        """Test GET /api/notifications/<user_id> with invalid parameters"""
        user_id = "test_user_error"
        
        # Test with invalid limit parameter
        response = self.client.get(f'/api/notifications/{user_id}?limit=invalid')
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertFalse(data['ok'])
        self.assertIn('error', data)

    # ==================== INTEGRATION TESTS ====================
    
    def test_complete_notification_workflow(self):
        """Test complete notification workflow from creation to deletion"""
        user_id = "test_user_comprehensive"
        
        if notification_service:
            # 1. Create notification
            notif_id = notification_service.create_notification(
                user_id=user_id,
                notification_type="task_assigned",
                title="Workflow Test",
                message="Testing complete workflow",
                task_id="workflow_task"
            )
            
            # 2. Get notifications
            response = self.client.get(f'/api/notifications/{user_id}')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['ok'])
            self.assertEqual(len(data['notifications']), 1)
            
            # 3. Mark as read
            response = self.client.put(f'/api/notifications/{notif_id}/read')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['ok'])
            
            # 4. Verify it's marked as read
            notifications = notification_service.get_user_notifications(user_id)
            self.assertTrue(notifications[0]['read'])
            
            # 5. Delete notification
            response = self.client.delete(f'/api/notifications/{notif_id}')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['ok'])
            
            # 6. Verify it's deleted
            notifications = notification_service.get_user_notifications(user_id)
            self.assertEqual(len(notifications), 0)
    
    def test_check_deadlines_endpoint(self):
        """Test POST /api/notifications/check-deadlines endpoint"""
        response = self.client.post('/api/notifications/check-deadlines')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['message'], 'Deadline check completed')


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestNotificationAPIComprehensive))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"COMPREHENSIVE NOTIFICATION API TESTS SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}")
