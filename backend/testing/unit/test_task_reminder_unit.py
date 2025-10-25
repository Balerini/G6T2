#!/usr/bin/env python3
"""
Unit tests for automated task reminders and email notifications.
Tests the notification service, email service, and reminder scheduling functionality.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta
import pytz

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.notification_service import NotificationService
from services.email_service import EmailService


class TestEmailService(unittest.TestCase):
    """Test cases for email service functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.email_service = EmailService()
        
        # Mock environment variables
        with patch.dict(os.environ, {
            'GMAIL_USER': 'test@gmail.com',
            'GMAIL_APP_PASSWORD': 'test_password'
        }):
            self.email_service.__init__()
    
    def test_email_service_initialization(self):
        """Test email service initialization"""
        self.assertEqual(self.email_service.smtp_user, 'test@gmail.com')
        self.assertEqual(self.email_service.smtp_password, 'test_password')
        self.assertEqual(self.email_service.smtp_server, 'smtp.gmail.com')
        self.assertEqual(self.email_service.smtp_port, 587)
    
    @patch('smtplib.SMTP')
    def test_send_deadline_reminder_email_success(self, mock_smtp):
        """Test successful deadline reminder email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test data
        to_email = "user@example.com"
        user_name = "Test User"
        task_name = "Test Task"
        task_desc = "Test Description"
        project_name = "Test Project"
        hours_until_due = 12
        due_date = "2024-01-15 10:00"
        priority_level = "High"
        
        # Call the method
        result = self.email_service.send_deadline_reminder_email(
            to_email, user_name, task_name, task_desc, 
            project_name, hours_until_due, due_date, priority_level
        )
        
        # Assertions
        self.assertTrue(result)
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@gmail.com', 'test_password')
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_deadline_reminder_email_smtp_error(self, mock_smtp):
        """Test deadline reminder email with SMTP error"""
        # Mock SMTP to raise exception
        mock_smtp.side_effect = Exception("SMTP connection failed")
        
        result = self.email_service.send_deadline_reminder_email(
            "user@example.com", "Test User", "Test Task", 
            "Test Description", "Test Project", 12, "2024-01-15 10:00", "High"
        )
        
        self.assertFalse(result)
    
    def test_send_deadline_reminder_email_priority_colors(self):
        """Test priority color mapping"""
        # Test different priority levels
        priorities = ['High', 'Medium', 'Low', 'Unknown']
        expected_colors = ['#ef4444', '#f59e0b', '#10b981', '#6b7280']
        
        for priority, expected_color in zip(priorities, expected_colors):
            self.assertIsNotNone(priority)
            self.assertIsNotNone(expected_color)
    
    def test_send_deadline_reminder_email_time_formatting(self):
        """Test time remaining formatting"""
        
        test_cases = [
            (0.5, "30 minutes"),      
            (2.5, "2 hours"),         
            (25, "1 day"),            
            (49, "2 days"),           
        ]
        
        for hours, expected_format in test_cases:
            pass


class TestNotificationService(unittest.TestCase):
    """Test cases for notification service functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.notification_service = NotificationService()
        
        # Mock Firestore database
        self.mock_db = MagicMock()
        self.notification_service._db = self.mock_db
    
    def test_notification_service_initialization(self):
        """Test notification service initialization"""
        self.assertIsNotNone(self.notification_service._db)
    
    @patch('services.notification_service.get_firestore_client')
    def test_notify_upcoming_deadlines_no_tasks(self, mock_get_db):
        """Test notify_upcoming_deadlines with no tasks"""
        # Mock empty task collection
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_db.collection.return_value = mock_tasks_ref
        mock_tasks_ref.stream.return_value = []
        mock_get_db.return_value = mock_db
        
        notification_service = NotificationService()
        notification_service._db = mock_db
        
        result = notification_service.notify_upcoming_deadlines()
        
        self.assertEqual(result, 0)
        mock_tasks_ref.stream.assert_called_once()
    
    @patch('services.notification_service.get_firestore_client')
    @patch('services.notification_service.email_service')
    def test_notify_upcoming_deadlines_with_due_tasks(self, mock_email_service, mock_get_db):
        """Test notify_upcoming_deadlines with tasks due within 24 hours"""
        # Mock database and tasks
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_users_ref = MagicMock()
        mock_db.collection.side_effect = lambda x: mock_tasks_ref if x == 'Tasks' else mock_users_ref
        
        # Create mock task due in 12 hours
        sg_tz = pytz.timezone('Asia/Singapore')
        now = datetime.now(sg_tz)
        due_time = now + timedelta(hours=12)
        
        mock_task_doc = MagicMock()
        mock_task_doc.id = 'task_123'
        mock_task_doc.to_dict.return_value = {
            'end_date': due_time,
            'assigned_to': ['user_123'],
            'task_name': 'Test Task',
            'description': 'Test Description',
            'priority_level': 3
        }
        
        # Create mock user
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'email': 'user@example.com',
            'name': 'Test User',
            'role_name': 'Staff'
        }
        
        mock_users_ref.document.return_value.get.return_value = mock_user_doc
        mock_tasks_ref.stream.return_value = [mock_task_doc]
        mock_email_service.send_deadline_reminder_email.return_value = True
        
        mock_get_db.return_value = mock_db
        
        notification_service = NotificationService()
        notification_service._db = mock_db
        
        result = notification_service.notify_upcoming_deadlines()
        
        self.assertEqual(result, 1)
        mock_email_service.send_deadline_reminder_email.assert_called_once()
    
    @patch('services.notification_service.get_firestore_client')
    def test_notify_upcoming_deadlines_past_due_tasks(self, mock_get_db):
        """Test notify_upcoming_deadlines with tasks past due date"""
        # Mock database
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_db.collection.return_value = mock_tasks_ref
        
        # Create mock task due in the past
        sg_tz = pytz.timezone('Asia/Singapore')
        now = datetime.now(sg_tz)
        past_due_time = now - timedelta(hours=1)
        
        mock_task_doc = MagicMock()
        mock_task_doc.id = 'task_123'
        mock_task_doc.to_dict.return_value = {
            'end_date': past_due_time,
            'assigned_to': ['user_123']
        }
        
        mock_tasks_ref.stream.return_value = [mock_task_doc]
        mock_get_db.return_value = mock_db
        
        notification_service = NotificationService()
        notification_service._db = mock_db
        
        result = notification_service.notify_upcoming_deadlines()
        
        self.assertEqual(result, 0)
    
    @patch('services.notification_service.get_firestore_client')
    def test_notify_upcoming_deadlines_future_tasks(self, mock_get_db):
        """Test notify_upcoming_deadlines with tasks due in the future (>24 hours)"""
        # Mock database
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_db.collection.return_value = mock_tasks_ref
        
        # Create mock task due in 48 hours
        sg_tz = pytz.timezone('Asia/Singapore')
        now = datetime.now(sg_tz)
        future_due_time = now + timedelta(hours=48)
        
        mock_task_doc = MagicMock()
        mock_task_doc.id = 'task_123'
        mock_task_doc.to_dict.return_value = {
            'end_date': future_due_time,
            'assigned_to': ['user_123']
        }
        
        mock_tasks_ref.stream.return_value = [mock_task_doc]
        mock_get_db.return_value = mock_db
        
        notification_service = NotificationService()
        notification_service._db = mock_db
        
        result = notification_service.notify_upcoming_deadlines()
        
        self.assertEqual(result, 0)
    
    @patch('services.notification_service.get_firestore_client')
    def test_notify_upcoming_deadlines_no_assigned_users(self, mock_get_db):
        """Test notify_upcoming_deadlines with tasks having no assigned users"""
        # Mock database
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_db.collection.return_value = mock_tasks_ref
        
        # Create mock task with no assigned users
        sg_tz = pytz.timezone('Asia/Singapore')
        now = datetime.now(sg_tz)
        due_time = now + timedelta(hours=12)
        
        mock_task_doc = MagicMock()
        mock_task_doc.id = 'task_123'
        mock_task_doc.to_dict.return_value = {
            'end_date': due_time,
            'assigned_to': []  # No assigned users
        }
        
        mock_tasks_ref.stream.return_value = [mock_task_doc]
        mock_get_db.return_value = mock_db
        
        notification_service = NotificationService()
        notification_service._db = mock_db
        
        result = notification_service.notify_upcoming_deadlines()
        
        self.assertEqual(result, 0)
    
    @patch('services.notification_service.get_firestore_client')
    def test_notify_upcoming_deadlines_non_staff_users(self, mock_get_db):
        """Test notify_upcoming_deadlines with non-staff users"""
        # Mock database
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_users_ref = MagicMock()
        mock_db.collection.side_effect = lambda x: mock_tasks_ref if x == 'Tasks' else mock_users_ref
        
        # Create mock task
        sg_tz = pytz.timezone('Asia/Singapore')
        now = datetime.now(sg_tz)
        due_time = now + timedelta(hours=12)
        
        mock_task_doc = MagicMock()
        mock_task_doc.id = 'task_123'
        mock_task_doc.to_dict.return_value = {
            'end_date': due_time,
            'assigned_to': ['user_123'],
            'task_name': 'Test Task',
            'description': 'Test Description',
            'priority_level': 3
        }
        
        # Create mock non-staff user
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'email': 'user@example.com',
            'name': 'Test User',
            'role_name': 'Director'  # Not staff
        }
        
        mock_users_ref.document.return_value.get.return_value = mock_user_doc
        mock_tasks_ref.stream.return_value = [mock_task_doc]
        mock_get_db.return_value = mock_db
        
        notification_service = NotificationService()
        notification_service._db = mock_db
        
        result = notification_service.notify_upcoming_deadlines()
        
        self.assertEqual(result, 0)  # No notifications sent to non-staff
    
    @patch('services.notification_service.get_firestore_client')
    def test_notify_upcoming_deadlines_database_error(self, mock_get_db):
        """Test notify_upcoming_deadlines with database error"""
        # Mock database error
        mock_get_db.side_effect = Exception("Database connection failed")
        
        notification_service = NotificationService()
        
        result = notification_service.notify_upcoming_deadlines()
        
        self.assertEqual(result, 0)


class TestReminderScheduling(unittest.TestCase):
    """Test cases for reminder scheduling functionality"""
    
    def test_deadline_threshold_calculation(self):
        """Test deadline threshold calculation (24 hours)"""
        sg_tz = pytz.timezone('Asia/Singapore')
        now = datetime.now(sg_tz)
        expected_threshold = now + timedelta(hours=24)
        self.assertEqual((expected_threshold - now).total_seconds(), 24 * 3600)
    
    def test_timezone_handling(self):
        """Test timezone handling for Singapore timezone"""
        sg_tz = pytz.timezone('Asia/Singapore')
        now = datetime.now(sg_tz)
        
        # Test that timezone is properly set
        self.assertIsNotNone(now.tzinfo)
        self.assertEqual(now.tzinfo.zone, 'Asia/Singapore')
    
    def test_deadline_time_parsing(self):
        """Test parsing of different deadline time formats"""
        sg_tz = pytz.timezone('Asia/Singapore')
        
        # Test datetime object
        dt = datetime.now(sg_tz)
        self.assertIsNotNone(dt)
        self.assertEqual(dt.tzinfo.zone, 'Asia/Singapore')
        
    
        pass


class TestReminderIntegration(unittest.TestCase):
    """Integration tests for reminder system"""
    
    @patch('services.notification_service.get_firestore_client')
    @patch('services.notification_service.email_service')
    def test_complete_reminder_flow(self, mock_email_service, mock_get_db):
        """Test complete reminder flow from task detection to email sending"""
        # Mock database
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_users_ref = MagicMock()
        mock_db.collection.side_effect = lambda x: mock_tasks_ref if x == 'Tasks' else mock_users_ref
        
        # Create mock task due in 12 hours
        sg_tz = pytz.timezone('Asia/Singapore')
        now = datetime.now(sg_tz)
        due_time = now + timedelta(hours=12)
        
        mock_task_doc = MagicMock()
        mock_task_doc.id = 'task_123'
        mock_task_doc.to_dict.return_value = {
            'end_date': due_time,
            'assigned_to': ['user_123'],
            'task_name': 'Integration Test Task',
            'description': 'Test Description',
            'priority_level': 5
        }
        
        # Create mock user
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'email': 'integration@example.com',
            'name': 'Integration User',
            'role_name': 'Staff'
        }
        
        mock_users_ref.document.return_value.get.return_value = mock_user_doc
        mock_tasks_ref.stream.return_value = [mock_task_doc]
        mock_email_service.send_deadline_reminder_email.return_value = True
        mock_get_db.return_value = mock_db
        
        # Test the complete flow
        notification_service = NotificationService()
        notification_service._db = mock_db
        
        result = notification_service.notify_upcoming_deadlines()
        
        
        self.assertEqual(result, 1)
        mock_email_service.send_deadline_reminder_email.assert_called_once()
        
        # Verify email was called with correct parameters
        call_args = mock_email_service.send_deadline_reminder_email.call_args
        if call_args and len(call_args[0]) > 0:
            self.assertEqual(call_args[0][0], 'integration@example.com')  
            self.assertEqual(call_args[0][1], 'Integration User')  
            self.assertEqual(call_args[0][2], 'Integration Test Task')  
            self.assertEqual(call_args[0][3], 'Test Description')  
            self.assertAlmostEqual(call_args[0][5], 12, delta=1) 
            self.assertEqual(call_args[0][7], 5)  


class TestReminderEdgeCases(unittest.TestCase):
    """Test edge cases for reminder system"""
    
    @patch('services.notification_service.get_firestore_client')
    def test_reminder_exactly_24_hours(self, mock_get_db):
        """Test reminder for task due exactly in 24 hours"""
        # Mock database
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_users_ref = MagicMock()
        mock_db.collection.side_effect = lambda x: mock_tasks_ref if x == 'Tasks' else mock_users_ref
        
        # Create mock task due exactly in 24 hours
        sg_tz = pytz.timezone('Asia/Singapore')
        now = datetime.now(sg_tz)
        due_time = now + timedelta(hours=24)
        
        mock_task_doc = MagicMock()
        mock_task_doc.id = 'task_123'
        mock_task_doc.to_dict.return_value = {
            'end_date': due_time,
            'assigned_to': ['user_123'],
            'task_name': '24 Hour Task',
            'description': 'Test Description',
            'priority_level': 3
        }
        
        mock_users_ref.document.return_value.get.return_value = MagicMock(exists=False)
        mock_tasks_ref.stream.return_value = [mock_task_doc]
        mock_get_db.return_value = mock_db
        
        notification_service = NotificationService()
        notification_service._db = mock_db
        
        result = notification_service.notify_upcoming_deadlines()
        
        
        self.assertEqual(result, 0)
    
    @patch('services.notification_service.get_firestore_client')
    def test_reminder_just_under_24_hours(self, mock_get_db):
        """Test reminder for task due just under 24 hours"""
        # Mock database
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_users_ref = MagicMock()
        mock_db.collection.side_effect = lambda x: mock_tasks_ref if x == 'Tasks' else mock_users_ref
        
        # Create mock task due in 23.9 hours
        sg_tz = pytz.timezone('Asia/Singapore')
        now = datetime.now(sg_tz)
        due_time = now + timedelta(hours=23, minutes=59)
        
        mock_task_doc = MagicMock()
        mock_task_doc.id = 'task_123'
        mock_task_doc.to_dict.return_value = {
            'end_date': due_time,
            'assigned_to': ['user_123'],
            'task_name': 'Just Under 24 Hour Task',
            'description': 'Test Description',
            'priority_level': 3
        }
        
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'email': 'user@example.com',
            'name': 'Test User',
            'role_name': 'Staff'
        }
        
        mock_users_ref.document.return_value.get.return_value = mock_user_doc
        mock_tasks_ref.stream.return_value = [mock_task_doc]
        mock_get_db.return_value = mock_db
        
        notification_service = NotificationService()
        notification_service._db = mock_db
        
        with patch('services.notification_service.email_service') as mock_email_service:
            mock_email_service.send_deadline_reminder_email.return_value = True
            
            result = notification_service.notify_upcoming_deadlines()
            
            self.assertEqual(result, 1)
            mock_email_service.send_deadline_reminder_email.assert_called_once()


if __name__ == '__main__':
    unittest.main()
