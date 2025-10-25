#!/usr/bin/env python3
"""
Additional edge case tests for reminder notifications.
Tests scenarios that might not be covered in the main test suite.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pytz


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.notification_service import NotificationService
from services.email_service import EmailService


class TestReminderEdgeCases(unittest.TestCase):
    """Test edge cases for reminder notifications"""
    
    def setUp(self):
        """Set up test environment"""
        self.sg_tz = pytz.timezone('Asia/Singapore')
        self.notification_service = NotificationService()
    
    @patch('services.notification_service.get_firestore_client')
    @patch('services.notification_service.email_service')
    def test_reminder_boundary_23_hours_59_minutes(self, mock_email_service, mock_get_db):
        """Test reminder for task due in 23 hours 59 minutes (boundary case)"""
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_users_ref = MagicMock()
        
        # Task due in 23 hours 59 minutes
        now = datetime.now(self.sg_tz)
        due_time = now + timedelta(hours=23, minutes=59)
        
        mock_task_doc = MagicMock()
        mock_task_doc.id = 'task_123'
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Boundary Task',
            'description': 'Test Description',
            'end_date': due_time,
            'assigned_to': ['user_123'],
            'proj_ID': 'project_abc',
            'priority_level': 3
        }
        
        mock_tasks_ref.stream.return_value = [mock_task_doc]
        mock_db.collection.side_effect = lambda name: {
            'Tasks': mock_tasks_ref,
            'Users': mock_users_ref,
            'Projects': MagicMock(document=MagicMock(return_value=MagicMock(exists=True, to_dict=lambda: {'project_name': 'Test Project'})))
        }.get(name)
        mock_get_db.return_value = mock_db
        
        # Mock user data
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'name': 'Test User',
            'email': 'user@example.com',
            'role_name': 'Staff',
            'role_num': 4
        }
        mock_users_ref.document.return_value.get.return_value = mock_user_doc
        
        # Mock email service
        mock_email_service.send_deadline_reminder_email.return_value = True
        
        with patch('services.notification_service.datetime') as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
            mock_dt.timedelta = timedelta
            
            result = self.notification_service.notify_upcoming_deadlines()
            
            
            self.assertEqual(result, 1)
            mock_email_service.send_deadline_reminder_email.assert_called_once()
    
    @patch('services.notification_service.get_firestore_client')
    @patch('services.notification_service.email_service')
    def test_reminder_boundary_24_hours_1_minute(self, mock_email_service, mock_get_db):
        """Test reminder for task due in 24 hours 1 minute (should NOT trigger)"""
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        
        # Task due in 24 hours 1 minute
        now = datetime.now(self.sg_tz)
        due_time = now + timedelta(hours=24, minutes=1)
        
        mock_task_doc = MagicMock()
        mock_task_doc.id = 'task_123'
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Future Task',
            'description': 'Test Description',
            'end_date': due_time,
            'assigned_to': ['user_123'],
            'priority_level': 3
        }
        
        mock_tasks_ref.stream.return_value = [mock_task_doc]
        mock_db.collection.return_value = mock_tasks_ref
        mock_get_db.return_value = mock_db
        
        with patch('services.notification_service.datetime') as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
            mock_dt.timedelta = timedelta
            
            result = self.notification_service.notify_upcoming_deadlines()
            
            
            self.assertEqual(result, 0)
            mock_email_service.send_deadline_reminder_email.assert_not_called()
    
    @patch('services.notification_service.get_firestore_client')
    def test_reminder_missing_task_fields(self, mock_get_db):
        """Test reminder with tasks missing required fields"""
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        
        # Task with missing fields
        mock_task_doc = MagicMock()
        mock_task_doc.id = 'task_123'
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Incomplete Task',
            
        }
        
        mock_tasks_ref.stream.return_value = [mock_task_doc]
        mock_db.collection.return_value = mock_tasks_ref
        mock_get_db.return_value = mock_db
        
        with patch('services.notification_service.datetime') as mock_dt:
            mock_dt.now.return_value = datetime.now(self.sg_tz)
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
            mock_dt.timedelta = timedelta
            
            result = self.notification_service.notify_upcoming_deadlines()
            
            
            self.assertEqual(result, 0)
    
    @patch('services.notification_service.get_firestore_client')
    def test_reminder_invalid_date_format(self, mock_get_db):
        """Test reminder with invalid date format"""
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        
        
        mock_task_doc = MagicMock()
        mock_task_doc.id = 'task_123'
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Invalid Date Task',
            'description': 'Test Description',
            'end_date': 'invalid-date-format',  
            'assigned_to': ['user_123'],
            'priority_level': 3
        }
        
        mock_tasks_ref.stream.return_value = [mock_task_doc]
        mock_db.collection.return_value = mock_tasks_ref
        mock_get_db.return_value = mock_db
        
        with patch('services.notification_service.datetime') as mock_dt:
            mock_dt.now.return_value = datetime.now(self.sg_tz)
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
            mock_dt.timedelta = timedelta
            
            result = self.notification_service.notify_upcoming_deadlines()
            
            
            self.assertEqual(result, 0)
    
    @patch('services.notification_service.get_firestore_client')
    @patch('services.notification_service.email_service')
    def test_reminder_duplicate_notifications(self, mock_email_service, mock_get_db):
        """Test that duplicate notifications are not sent"""
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_users_ref = MagicMock()
        
        
        now = datetime.now(self.sg_tz)
        due_time = now + timedelta(hours=12)
        
        mock_task_doc = MagicMock()
        mock_task_doc.id = 'task_123'
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Duplicate Test Task',
            'description': 'Test Description',
            'end_date': due_time,
            'assigned_to': ['user_123'],
            'proj_ID': 'project_abc',
            'priority_level': 3
        }
        
        mock_tasks_ref.stream.return_value = [mock_task_doc]
        mock_db.collection.side_effect = lambda name: {
            'Tasks': mock_tasks_ref,
            'Users': mock_users_ref,
            'Projects': MagicMock(document=MagicMock(return_value=MagicMock(exists=True, to_dict=lambda: {'project_name': 'Test Project'})))
        }.get(name)
        mock_get_db.return_value = mock_db
        
        # Mock user data
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'name': 'Test User',
            'email': 'user@example.com',
            'role_name': 'Staff',
            'role_num': 4
        }
        mock_users_ref.document.return_value.get.return_value = mock_user_doc
        
        # Mock email service
        mock_email_service.send_deadline_reminder_email.return_value = True
        
        with patch('services.notification_service.datetime') as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
            mock_dt.timedelta = timedelta
            
            # Run notification twice
            result1 = self.notification_service.notify_upcoming_deadlines()
            result2 = self.notification_service.notify_upcoming_deadlines()
            
            
            self.assertEqual(result1, 1)
            self.assertEqual(result2, 0)  
            self.assertEqual(mock_email_service.send_deadline_reminder_email.call_count, 1)
    
    @patch('services.notification_service.get_firestore_client')
    def test_reminder_multiple_users_same_task(self, mock_get_db):
        """Test reminder for task assigned to multiple users"""
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_users_ref = MagicMock()
        
        
        now = datetime.now(self.sg_tz)
        due_time = now + timedelta(hours=12)
        
        mock_task_doc = MagicMock()
        mock_task_doc.id = 'task_123'
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Multi-User Task',
            'description': 'Test Description',
            'end_date': due_time,
            'assigned_to': ['user_123', 'user_456', 'user_789'],
            'proj_ID': 'project_abc',
            'priority_level': 3
        }
        
        mock_tasks_ref.stream.return_value = [mock_task_doc]
        mock_db.collection.side_effect = lambda name: {
            'Tasks': mock_tasks_ref,
            'Users': mock_users_ref,
            'Projects': MagicMock(document=MagicMock(return_value=MagicMock(exists=True, to_dict=lambda: {'project_name': 'Test Project'})))
        }.get(name)
        mock_get_db.return_value = mock_db
        
        # Mock multiple users
        def mock_user_doc(user_id):
            doc = MagicMock()
            doc.exists = True
            doc.to_dict.return_value = {
                'name': f'User {user_id}',
                'email': f'user{user_id}@example.com',
                'role_name': 'Staff',
                'role_num': 4
            }
            return doc
        
        mock_users_ref.document.side_effect = lambda user_id: MagicMock(get=MagicMock(return_value=mock_user_doc(user_id)))
        
        with patch('services.notification_service.datetime') as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
            mock_dt.timedelta = timedelta
            
            result = self.notification_service.notify_upcoming_deadlines()
            
            
            self.assertEqual(result, 3)
    
    @patch('services.notification_service.get_firestore_client')
    def test_reminder_very_short_deadline(self, mock_get_db):
        """Test reminder for task due in very short time (e.g., 1 minute)"""
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_users_ref = MagicMock()
        
        # Task due in 1 minute
        now = datetime.now(self.sg_tz)
        due_time = now + timedelta(minutes=1)
        
        mock_task_doc = MagicMock()
        mock_task_doc.id = 'task_123'
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Urgent Task',
            'description': 'Test Description',
            'end_date': due_time,
            'assigned_to': ['user_123'],
            'proj_ID': 'project_abc',
            'priority_level': 5 
        }
        
        mock_tasks_ref.stream.return_value = [mock_task_doc]
        mock_db.collection.side_effect = lambda name: {
            'Tasks': mock_tasks_ref,
            'Users': mock_users_ref,
            'Projects': MagicMock(document=MagicMock(return_value=MagicMock(exists=True, to_dict=lambda: {'project_name': 'Test Project'})))
        }.get(name)
        mock_get_db.return_value = mock_db
        
        # Mock user data
        mock_user_doc = MagicMock()
        mock_user_doc.exists = True
        mock_user_doc.to_dict.return_value = {
            'name': 'Test User',
            'email': 'user@example.com',
            'role_name': 'Staff',
            'role_num': 4
        }
        mock_users_ref.document.return_value.get.return_value = mock_user_doc
        
        with patch('services.notification_service.datetime') as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
            mock_dt.timedelta = timedelta
            
            result = self.notification_service.notify_upcoming_deadlines()
            
            self.assertEqual(result, 1)
    
    @patch('services.notification_service.get_firestore_client')
    def test_reminder_mixed_user_roles(self, mock_get_db):
        """Test reminder with mixed user roles (staff and non-staff)"""
        mock_db = MagicMock()
        mock_tasks_ref = MagicMock()
        mock_users_ref = MagicMock()
        
        now = datetime.now(self.sg_tz)
        due_time = now + timedelta(hours=12)
        
        mock_task_doc = MagicMock()
        mock_task_doc.id = 'task_123'
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Mixed Role Task',
            'description': 'Test Description',
            'end_date': due_time,
            'assigned_to': ['staff_user', 'manager_user', 'director_user'],
            'proj_ID': 'project_abc',
            'priority_level': 3
        }
        
        mock_tasks_ref.stream.return_value = [mock_task_doc]
        mock_db.collection.side_effect = lambda name: {
            'Tasks': mock_tasks_ref,
            'Users': mock_users_ref,
            'Projects': MagicMock(document=MagicMock(return_value=MagicMock(exists=True, to_dict=lambda: {'project_name': 'Test Project'})))
        }.get(name)
        mock_get_db.return_value = mock_db
        
        # Mock users with different roles
        def mock_user_doc(user_id):
            doc = MagicMock()
            doc.exists = True
            if user_id == 'staff_user':
                doc.to_dict.return_value = {
                    'name': 'Staff User',
                    'email': 'staff@example.com',
                    'role_name': 'Staff',
                    'role_num': 4
                }
            elif user_id == 'manager_user':
                doc.to_dict.return_value = {
                    'name': 'Manager User',
                    'email': 'manager@example.com',
                    'role_name': 'Manager',
                    'role_num': 3
                }
            else:  
                doc.to_dict.return_value = {
                    'name': 'Director User',
                    'email': 'director@example.com',
                    'role_name': 'Director',
                    'role_num': 2
                }
            return doc
        
        mock_users_ref.document.side_effect = lambda user_id: MagicMock(get=MagicMock(return_value=mock_user_doc(user_id)))
        
        with patch('services.notification_service.datetime') as mock_dt:
            mock_dt.now.return_value = now
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
            mock_dt.timedelta = timedelta
            
            result = self.notification_service.notify_upcoming_deadlines()
            
            
            self.assertEqual(result, 1)


if __name__ == '__main__':
    unittest.main()
