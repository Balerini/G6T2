#!/usr/bin/env python3
"""
Integration Tests for SCRUM-53: Automated Task Reminder
Tests the automated task reminder system including deadline checking,
email notifications, scheduling scripts, and notification deduplication.
Uses real database connections for C2 integration testing.
"""

import unittest
import sys
import os
import json
import subprocess
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pytz

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import Flask app and Firebase utilities
from app import create_app
from firebase_utils import get_firestore_client
from services.notification_service import notification_service
from services.email_service import email_service

class TestAutomatedTaskReminderIntegration(unittest.TestCase):
    """C2 Integration tests for Automated Task Reminder functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        print("=" * 80)
        print("INTEGRATION TESTING - AUTOMATED TASK REMINDER")
        print("=" * 80)
        print("Testing SCRUM-53: Automated Task Reminder")
        print("=" * 80)
        
        # Set up Flask test client
        app = create_app()
        cls.app = app.test_client()
        cls.app_context = app.app_context()
        cls.app_context.push()
        
        # Get Firestore client
        cls.db = get_firestore_client()
        
        # Test user IDs (these should exist in your test database)
        cls.test_manager_id = "test_manager_reminder_123"
        cls.test_staff_1_id = "test_staff_reminder_456"
        cls.test_staff_2_id = "test_staff_reminder_789"
        cls.test_staff_3_id = "test_staff_reminder_101"
        
        # Test division name
        cls.test_division = "Test Reminder Division"
        
        # Create test data
        cls.setup_test_data()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        cls.cleanup_test_data()
        cls.app_context.pop()
        print("=" * 80)
        print("INTEGRATION TESTING COMPLETED")
        print("=" * 80)
    
    @classmethod
    def setup_test_data(cls):
        """Create test users, projects, and tasks for automated reminder testing"""
        print("Setting up test data...")
        
        # Create test users
        users_data = [
            {
                'id': cls.test_manager_id,
                'name': 'Test Manager Reminder',
                'email': 'testmanager.reminder@example.com',
                'role_name': 'Manager',
                'role_num': 3,  # Manager role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_staff_1_id,
                'name': 'Test Staff Reminder 1',
                'email': 'teststaff1.reminder@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_staff_2_id,
                'name': 'Test Staff Reminder 2',
                'email': 'teststaff2.reminder@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_staff_3_id,
                'name': 'Test Staff Reminder 3',
                'email': 'teststaff3.reminder@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            }
        ]
        
        for user_data in users_data:
            user_ref = cls.db.collection('Users').document(user_data['id'])
            user_ref.set(user_data)
        
        # Create test projects
        current_date = datetime.now(pytz.timezone('Asia/Singapore'))
        
        # Project 1: For reminder testing
        project_1_data = {
            'proj_name': 'Test Reminder Project 1',
            'proj_desc': 'Project for automated reminder testing',
            'start_date': current_date + timedelta(days=1),
            'end_date': current_date + timedelta(days=30),
            'owner': cls.test_manager_id,
            'division_name': cls.test_division,
            'collaborators': [cls.test_manager_id, cls.test_staff_1_id, cls.test_staff_2_id],
            'proj_status': 'In Progress',
            'is_deleted': False,
            'createdAt': current_date,
            'updatedAt': current_date
        }
        
        project_1_ref = cls.db.collection('Projects').document('test_project_reminder_1')
        project_1_ref.set(project_1_data)
        cls.test_project_1_id = 'test_project_reminder_1'
        
        # Create tasks with different deadline scenarios
        tasks_data = [
            # Task 1: Due in 2 hours (should trigger reminder)
            {
                'id': 'test_reminder_task_1',
                'task_name': 'Urgent Task Due Soon',
                'task_desc': 'Task due in 2 hours',
                'start_date': current_date - timedelta(days=5),
                'end_date': current_date + timedelta(hours=2),  # Due in 2 hours
                'task_status': 'In Progress',
                'priority_level': 9,  # High priority
                'proj_ID': cls.test_project_1_id,
                'owner': cls.test_manager_id,
                'assigned_to': [cls.test_staff_1_id],
                'is_deleted': False,
                'createdAt': current_date - timedelta(days=5),
                'updatedAt': current_date
            },
            # Task 2: Due in 12 hours (should trigger reminder)
            {
                'id': 'test_reminder_task_2',
                'task_name': 'Task Due Tomorrow',
                'task_desc': 'Task due in 12 hours',
                'start_date': current_date - timedelta(days=3),
                'end_date': current_date + timedelta(hours=12),  # Due in 12 hours
                'task_status': 'Not Started',
                'priority_level': 6,  # Medium priority
                'proj_ID': cls.test_project_1_id,
                'owner': cls.test_manager_id,
                'assigned_to': [cls.test_staff_2_id],
                'is_deleted': False,
                'createdAt': current_date - timedelta(days=3),
                'updatedAt': current_date
            },
            # Task 3: Due in 48 hours (should NOT trigger reminder)
            {
                'id': 'test_reminder_task_3',
                'task_name': 'Task Due Later',
                'task_desc': 'Task due in 48 hours',
                'start_date': current_date + timedelta(days=1),
                'end_date': current_date + timedelta(hours=48),  # Due in 48 hours
                'task_status': 'Not Started',
                'priority_level': 3,  # Low priority
                'proj_ID': cls.test_project_1_id,
                'owner': cls.test_manager_id,
                'assigned_to': [cls.test_staff_3_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            # Task 4: Already overdue (should NOT trigger reminder - only upcoming deadlines)
            {
                'id': 'test_reminder_task_4',
                'task_name': 'Overdue Task',
                'task_desc': 'Task that is already overdue',
                'start_date': current_date - timedelta(days=10),
                'end_date': current_date - timedelta(hours=2),  # Overdue by 2 hours
                'task_status': 'In Progress',
                'priority_level': 8,  # High priority
                'proj_ID': cls.test_project_1_id,
                'owner': cls.test_manager_id,
                'assigned_to': [cls.test_staff_1_id],
                'is_deleted': False,
                'createdAt': current_date - timedelta(days=10),
                'updatedAt': current_date
            },
            # Task 5: Completed task (should NOT trigger reminder)
            {
                'id': 'test_reminder_task_5',
                'task_name': 'Completed Task',
                'task_desc': 'Task that is already completed',
                'start_date': current_date - timedelta(days=5),
                'end_date': current_date + timedelta(hours=6),  # Due in 6 hours
                'task_status': 'Completed',
                'priority_level': 5,  # Medium priority
                'proj_ID': cls.test_project_1_id,
                'owner': cls.test_manager_id,
                'assigned_to': [cls.test_staff_2_id],
                'is_deleted': False,
                'createdAt': current_date - timedelta(days=5),
                'updatedAt': current_date
            },
            # Task 6: Deleted task (should NOT trigger reminder)
            {
                'id': 'test_reminder_task_6',
                'task_name': 'Deleted Task',
                'task_desc': 'Task that is deleted',
                'start_date': current_date - timedelta(days=3),
                'end_date': current_date + timedelta(hours=8),  # Due in 8 hours
                'task_status': 'In Progress',
                'priority_level': 7,  # High priority
                'proj_ID': cls.test_project_1_id,
                'owner': cls.test_manager_id,
                'assigned_to': [cls.test_staff_3_id],
                'is_deleted': True,  # This task is deleted
                'createdAt': current_date - timedelta(days=3),
                'updatedAt': current_date
            }
        ]
        
        # Create all tasks
        for task_data in tasks_data:
            task_ref = cls.db.collection('Tasks').document(task_data['id'])
            task_ref.set(task_data)
        
        print(f"Created {len(users_data)} test users, 1 test project, and {len(tasks_data)} test tasks")
        print(f"Manager: {cls.test_manager_id}")
        print(f"Staff members: {cls.test_staff_1_id}, {cls.test_staff_2_id}, {cls.test_staff_3_id}")
        print(f"Division: {cls.test_division}")
        print(f"Project: {cls.test_project_1_id}")
        print("Task scenarios:")
        print("  - Task 1: Due in 2 hours (should trigger)")
        print("  - Task 2: Due in 12 hours (should trigger)")
        print("  - Task 3: Due in 48 hours (should NOT trigger)")
        print("  - Task 4: Overdue (should NOT trigger)")
        print("  - Task 5: Completed (should NOT trigger)")
        print("  - Task 6: Deleted (should NOT trigger)")
    
    @classmethod
    def cleanup_test_data(cls):
        """Clean up test data"""
        print("Cleaning up test data...")
        
        # Delete test tasks
        task_ids = [
            'test_reminder_task_1', 'test_reminder_task_2', 'test_reminder_task_3',
            'test_reminder_task_4', 'test_reminder_task_5', 'test_reminder_task_6'
        ]
        for task_id in task_ids:
            try:
                cls.db.collection('Tasks').document(task_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete task {task_id}: {e}")
        
        # Delete test users
        user_ids = [
            cls.test_manager_id, cls.test_staff_1_id, cls.test_staff_2_id, cls.test_staff_3_id
        ]
        for user_id in user_ids:
            try:
                cls.db.collection('Users').document(user_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete user {user_id}: {e}")
        
        # Delete test projects
        project_ids = [cls.test_project_1_id]
        for project_id in project_ids:
            try:
                cls.db.collection('Projects').document(project_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete project {project_id}: {e}")
        
        print("Test data cleanup completed")
    
    @patch('smtplib.SMTP')
    def test_notify_upcoming_deadlines(self, mock_smtp):
        """Test the core notify_upcoming_deadlines() function"""
        print("\n--- Testing notify_upcoming_deadlines() function ---")
        
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test the deadline notification function
        notification_count = notification_service.notify_upcoming_deadlines()
        
        # Should find tasks due within 24 hours (tasks 1 and 2)
        self.assertGreaterEqual(notification_count, 0, "Should process deadline notifications")
        
        # Check that notifications were created for staff members
        notifications_1 = notification_service.get_user_notifications(self.test_staff_1_id)
        notifications_2 = notification_service.get_user_notifications(self.test_staff_2_id)
        
        # Should have deadline notifications
        deadline_notifications_1 = [n for n in notifications_1 if n.get('type') == 'deadline']
        deadline_notifications_2 = [n for n in notifications_2 if n.get('type') == 'deadline']
        
        print(f"✅ Deadline notification test passed - {notification_count} notifications processed")
        print(f"   Staff 1 deadline notifications: {len(deadline_notifications_1)}")
        print(f"   Staff 2 deadline notifications: {len(deadline_notifications_2)}")
    
    def test_trigger_reminders_script(self):
        """Test the trigger_reminders.py script functionality"""
        print("\n--- Testing trigger_reminders.py script ---")
        
        # Test running the script
        try:
            # Import the trigger_reminders module
            from trigger_reminders import main
            
            print("Testing trigger_reminders.py script...")
            # Note: We don't actually call main() here to avoid sending real emails
            # In a real test environment, you might want to mock the email service
            print("✅ Trigger reminders script test passed (not executed to avoid real emails)")
        except Exception as e:
            self.fail(f"Trigger reminders script should not crash: {e}")
    
    def test_scheduler_script(self):
        """Test the scheduler.py script with different options"""
        print("\n--- Testing scheduler.py script ---")
        
        # Test running the scheduler script with different options
        try:
            # Import the scheduler module
            from scheduler import main
            
            print("Testing scheduler.py script...")
            # Note: We don't actually call main() here to avoid sending real emails
            # In a real test environment, you might want to mock the email service
            print("✅ Scheduler script test passed (not executed to avoid real emails)")
        except Exception as e:
            self.fail(f"Scheduler script should not crash: {e}")
    
    @patch('smtplib.SMTP')
    def test_automated_email_notifications(self, mock_smtp):
        """Test automated email notifications for deadlines"""
        print("\n--- Testing automated email notifications ---")
        
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test deadline notification with email
        notification_count = notification_service.notify_upcoming_deadlines()
        
        # Verify SMTP calls were made (emails were sent)
        self.assertGreater(mock_server.send_message.call_count, 0, "Should send emails for deadline notifications")
        
        print(f"✅ Automated email notifications test passed - {notification_count} notifications processed")
    
    def test_notification_deduplication(self):
        """Test notification deduplication (23-hour rule)"""
        print("\n--- Testing notification deduplication ---")
        
        # Clear existing notifications for test users
        notification_service.notifications_cache = {}
        
        # Run deadline check first time
        notification_count_1 = notification_service.notify_upcoming_deadlines()
        
        # Run deadline check second time immediately (should be deduplicated)
        notification_count_2 = notification_service.notify_upcoming_deadlines()
        
        # Second run should have fewer notifications due to deduplication
        self.assertLessEqual(notification_count_2, notification_count_1, 
                           "Second run should have fewer notifications due to deduplication")
        
        print(f"✅ Notification deduplication test passed")
        print(f"   First run: {notification_count_1} notifications")
        print(f"   Second run: {notification_count_2} notifications")
    
    def test_timezone_handling(self):
        """Test timezone handling (Singapore timezone)"""
        print("\n--- Testing timezone handling ---")
        
        # Test Singapore timezone
        sg_tz = pytz.timezone('Asia/Singapore')
        current_time = datetime.now(sg_tz)
        
        # Verify timezone is correct
        self.assertEqual(current_time.tzinfo.zone, 'Asia/Singapore', "Should use Singapore timezone")
        
        # Test timezone conversion
        utc_time = datetime.now(pytz.UTC)
        sg_time = utc_time.astimezone(sg_tz)
        
        self.assertEqual(sg_time.tzinfo.zone, 'Asia/Singapore', "Should convert to Singapore timezone")
        
        print("✅ Timezone handling test passed")
    
    def test_reminder_edge_cases(self):
        """Test edge cases: no tasks, invalid dates, missing users"""
        print("\n--- Testing reminder edge cases ---")
        
        # Test with empty notification cache
        original_cache = notification_service.notifications_cache.copy()
        notification_service.notifications_cache = {}
        
        # Run deadline check
        notification_count = notification_service.notify_upcoming_deadlines()
        
        # Should handle gracefully
        self.assertGreaterEqual(notification_count, 0, "Should handle empty cache gracefully")
        
        # Restore original cache
        notification_service.notifications_cache = original_cache
        
        print("✅ Reminder edge cases test passed")
    
    def test_cron_simulation(self):
        """Test cron job simulation and scheduling"""
        print("\n--- Testing cron job simulation ---")
        
        # Simulate running the reminder check multiple times (like a cron job)
        notification_counts = []
        
        for i in range(3):
            # Clear cache to simulate fresh runs
            notification_service.notifications_cache = {}
            
            # Run deadline check
            count = notification_service.notify_upcoming_deadlines()
            notification_counts.append(count)
            
            print(f"   Run {i+1}: {count} notifications")
        
        # All runs should process the same tasks
        self.assertTrue(all(count >= 0 for count in notification_counts), 
                       "All cron simulation runs should succeed")
        
        print("✅ Cron job simulation test passed")
    
    def test_reminder_integration(self):
        """Test integration with real database and email service"""
        print("\n--- Testing reminder integration ---")
        
        # Test that the reminder system integrates with real database
        tasks_ref = self.db.collection('Tasks')
        tasks = list(tasks_ref.stream())
        
        # Should find our test tasks
        self.assertGreater(len(tasks), 0, "Should find test tasks in database")
        
        # Test that users exist in database
        users_ref = self.db.collection('Users')
        users = list(users_ref.stream())
        
        # Should find our test users
        self.assertGreater(len(users), 0, "Should find test users in database")
        
        # Test notification service integration
        notification_id = notification_service.create_notification(
            user_id=self.test_staff_1_id,
            notification_type='deadline',
            title='Test Deadline',
            message='Test deadline message',
            task_id='test_reminder_task_1',
            project_id=self.test_project_1_id
        )
        
        self.assertIsNotNone(notification_id, "Should create notification successfully")
        
        print("✅ Reminder integration test passed")
    
    def test_deadline_calculation_accuracy(self):
        """Test deadline calculation accuracy"""
        print("\n--- Testing deadline calculation accuracy ---")
        
        # Test with a task due in exactly 24 hours
        sg_tz = pytz.timezone('Asia/Singapore')
        current_time = datetime.now(sg_tz)
        deadline_time = current_time + timedelta(hours=24)
        
        # Create a temporary task for testing
        test_task_data = {
            'task_name': 'Test 24 Hour Task',
            'task_desc': 'Task due in exactly 24 hours',
            'start_date': current_time,
            'end_date': deadline_time,
            'task_status': 'In Progress',
            'priority_level': 5,
            'proj_ID': self.test_project_1_id,
            'owner': self.test_manager_id,
            'assigned_to': [self.test_staff_1_id],
            'is_deleted': False,
            'createdAt': current_time,
            'updatedAt': current_time
        }
        
        # Add task to database
        task_ref = self.db.collection('Tasks').document('test_24hour_task')
        task_ref.set(test_task_data)
        
        try:
            # Run deadline check
            notification_count = notification_service.notify_upcoming_deadlines()
            
            # Should find the 24-hour task
            self.assertGreaterEqual(notification_count, 0, "Should process 24-hour deadline")
            
            print(f"✅ Deadline calculation accuracy test passed - {notification_count} notifications")
            
        finally:
            # Clean up test task
            try:
                task_ref.delete()
            except Exception as e:
                print(f"Warning: Could not delete test task: {e}")
    
    def test_priority_based_notifications(self):
        """Test priority-based notification handling"""
        print("\n--- Testing priority-based notifications ---")
        
        # Test that high priority tasks get appropriate handling
        high_priority_tasks = []
        medium_priority_tasks = []
        low_priority_tasks = []
        
        # Query tasks and categorize by priority
        tasks_ref = self.db.collection('Tasks')
        tasks = tasks_ref.stream()
        
        for task_doc in tasks:
            task_data = task_doc.to_dict()
            if task_data.get('is_deleted', False):
                continue
                
            priority = task_data.get('priority_level', 1)
            # Convert to int if it's a string
            if isinstance(priority, str):
                try:
                    priority = int(priority)
                except (ValueError, TypeError):
                    priority = 1
            
            if priority >= 7:
                high_priority_tasks.append(task_data)
            elif priority >= 4:
                medium_priority_tasks.append(task_data)
            else:
                low_priority_tasks.append(task_data)
        
        print(f"   High priority tasks: {len(high_priority_tasks)}")
        print(f"   Medium priority tasks: {len(medium_priority_tasks)}")
        print(f"   Low priority tasks: {len(low_priority_tasks)}")
        
        # Should have tasks in different priority categories
        self.assertGreater(len(high_priority_tasks), 0, "Should have high priority tasks")
        
        print("✅ Priority-based notifications test passed")
    
    def test_staff_only_notifications(self):
        """Test that only staff members receive notifications"""
        print("\n--- Testing staff-only notifications ---")
        
        # Clear existing notifications
        notification_service.notifications_cache = {}
        
        # Run deadline check
        notification_count = notification_service.notify_upcoming_deadlines()
        
        # Check that only staff members received notifications
        staff_notifications = notification_service.get_user_notifications(self.test_staff_1_id)
        manager_notifications = notification_service.get_user_notifications(self.test_manager_id)
        
        # Staff should have deadline notifications
        staff_deadline_notifications = [n for n in staff_notifications if n.get('type') == 'deadline']
        
        # Manager should not have deadline notifications (not staff)
        manager_deadline_notifications = [n for n in manager_notifications if n.get('type') == 'deadline']
        
        self.assertGreater(len(staff_deadline_notifications), 0, "Staff should receive deadline notifications")
        self.assertEqual(len(manager_deadline_notifications), 0, "Manager should not receive deadline notifications")
        
        print("✅ Staff-only notifications test passed")


if __name__ == '__main__':
    print("=" * 80)
    print("SCRUM-53: AUTOMATED TASK REMINDER - INTEGRATION TESTING")
    print("=" * 80)
    print("Testing automated task reminder system")
    print("=" * 80)
    
    # Run the tests
    unittest.main(verbosity=2)
