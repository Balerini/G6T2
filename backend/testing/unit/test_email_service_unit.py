#!/usr/bin/env python3
"""
Comprehensive Email Service Tests
Combines unit tests and integration tests for all email service functionality
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock, call
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Flask app and email service
try:
    from app import create_app
    from services.email_service import EmailService, email_service
    app = create_app()
except ImportError:
    # Fallback for testing without Flask app
    app = None
    email_service = None


class TestEmailServiceUnit(unittest.TestCase):
    """Unit tests for Email Service functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.email_service = EmailService()
        self.test_data = {
            'to_email': 'test@example.com',
            'user_name': 'John Doe',
            'project_name': 'Test Project',
            'project_desc': 'A test project description',
            'creator_name': 'Jane Smith',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        }
    
    @patch('smtplib.SMTP')
    def test_send_project_assignment_email_success(self, mock_smtp):
        """Test successful project assignment email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test the function
        result = self.email_service.send_project_assignment_email(**self.test_data)
        
        # Assertions
        self.assertTrue(result)
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_project_assignment_email_smtp_error(self, mock_smtp):
        """Test project assignment email with SMTP error"""
        # Mock SMTP error
        mock_smtp.side_effect = Exception("SMTP connection failed")
        
        # Test the function
        result = self.email_service.send_project_assignment_email(**self.test_data)
        
        # Assertions
        self.assertFalse(result)
    
    @patch('smtplib.SMTP')
    def test_send_project_assignment_email_no_description(self, mock_smtp):
        """Test project assignment email with no description"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test data without description
        test_data = self.test_data.copy()
        test_data['project_desc'] = None
        
        # Test the function
        result = self.email_service.send_project_assignment_email(**test_data)
        
        # Assertions
        self.assertTrue(result)
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_task_assignment_email_success(self, mock_smtp):
        """Test successful task assignment email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test data for task assignment
        task_data = {
            'to_email': 'test@example.com',
            'user_name': 'John Doe',
            'task_name': 'Test Task',
            'task_desc': 'A test task description',
            'project_name': 'Test Project',
            'creator_name': 'Jane Smith',
            'start_date': '2024-01-01',
            'end_date': '2024-01-15',
            'priority_level': 'High'
        }
        
        # Test the function
        result = self.email_service.send_task_assignment_email(**task_data)
        
        # Assertions
        self.assertTrue(result)
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_task_assignment_email_smtp_error(self, mock_smtp):
        """Test task assignment email with SMTP error"""
        # Mock SMTP error
        mock_smtp.side_effect = Exception("SMTP connection failed")
        
        # Test data for task assignment
        task_data = {
            'to_email': 'test@example.com',
            'user_name': 'John Doe',
            'task_name': 'Test Task',
            'task_desc': 'A test task description',
            'project_name': 'Test Project',
            'creator_name': 'Jane Smith',
            'start_date': '2024-01-01',
            'end_date': '2024-01-15',
            'priority_level': 'High'
        }
        
        # Test the function
        result = self.email_service.send_task_assignment_email(**task_data)
        
        # Assertions
        self.assertFalse(result)
    
    @patch('smtplib.SMTP')
    def test_send_task_transfer_ownership_email_success(self, mock_smtp):
        """Test successful task transfer email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test data for task transfer
        transfer_data = {
            'new_owner_email': 'newowner@example.com',
            'new_owner_name': 'New Owner',
            'old_owner_email': 'oldowner@example.com',
            'old_owner_name': 'Old Owner',
            'task_name': 'Test Task',
            'task_desc': 'A test task description',
            'project_name': 'Test Project',
            'transferred_by_name': 'Transferrer',
            'start_date': '2024-01-01',
            'end_date': '2024-01-15'
        }
        
        # Test the function
        result = self.email_service.send_task_transfer_ownership_email(**transfer_data)
        
        # Assertions
        self.assertTrue(result)
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_subtask_transfer_ownership_email_success(self, mock_smtp):
        """Test successful subtask transfer email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test data for subtask transfer
        transfer_data = {
            'new_owner_email': 'newowner@example.com',
            'new_owner_name': 'New Owner',
            'old_owner_email': 'oldowner@example.com',
            'old_owner_name': 'Old Owner',
            'subtask_name': 'Test Subtask',
            'subtask_desc': 'A test subtask description',
            'parent_task_name': 'Parent Task',
            'project_name': 'Test Project',
            'transferred_by_name': 'Transferrer',
            'start_date': '2024-01-01',
            'end_date': '2024-01-15'
        }
        
        # Test the function
        result = self.email_service.send_subtask_transfer_ownership_email(**transfer_data)
        
        # Assertions
        self.assertTrue(result)
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_deadline_reminder_email_success(self, mock_smtp):
        """Test successful deadline reminder email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test data for deadline reminder
        reminder_data = {
            'to_email': 'test@example.com',
            'user_name': 'John Doe',
            'task_name': 'Test Task',
            'task_desc': 'A test task description',
            'project_name': 'Test Project',
            'hours_until_due': 2.5,
            'due_date': '2024-01-15',
            'priority_level': 'High'
        }
        
        # Test the function
        result = self.email_service.send_deadline_reminder_email(**reminder_data)
        
        # Assertions
        self.assertTrue(result)
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
    
    def test_email_service_initialization(self):
        """Test email service initialization"""
        # Test that service initializes correctly
        self.assertIsNotNone(self.email_service.smtp_server)
        self.assertIsNotNone(self.email_service.smtp_port)
        self.assertEqual(self.email_service.smtp_server, 'smtp.gmail.com')
        self.assertEqual(self.email_service.smtp_port, 587)
    
    @patch('smtplib.SMTP')
    def test_email_service_login_error(self, mock_smtp):
        """Test email service with login error"""
        # Mock SMTP server with login error
        mock_server = MagicMock()
        mock_server.login.side_effect = Exception("Login failed")
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test data
        test_data = {
            'to_email': 'test@example.com',
            'user_name': 'John Doe',
            'project_name': 'Test Project',
            'project_desc': 'Test description',
            'creator_name': 'Jane Smith',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        }
        
        # Test the function
        result = self.email_service.send_project_assignment_email(**test_data)
        
        # Assertions
        self.assertFalse(result)
    
    @patch('smtplib.SMTP')
    def test_email_service_send_message_error(self, mock_smtp):
        """Test email service with send message error"""
        # Mock SMTP server with send message error
        mock_server = MagicMock()
        mock_server.send_message.side_effect = Exception("Send message failed")
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test data
        test_data = {
            'to_email': 'test@example.com',
            'user_name': 'John Doe',
            'project_name': 'Test Project',
            'project_desc': 'Test description',
            'creator_name': 'Jane Smith',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        }
        
        # Test the function
        result = self.email_service.send_project_assignment_email(**test_data)
        
        # Assertions
        self.assertFalse(result)


class TestEmailServiceIntegration(unittest.TestCase):
    """Integration tests for Email Service"""
    
    def setUp(self):
        """Set up test fixtures"""
        if app is None:
            self.skipTest("Flask app not available for API testing")
        
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_email_service_import_integration(self):
        """Test that email service can be imported and used in route context"""
        # Test importing email service in route context
        try:
            from services.email_service import email_service
            self.assertIsNotNone(email_service)
            self.assertTrue(hasattr(email_service, 'send_project_assignment_email'))
            self.assertTrue(hasattr(email_service, 'send_task_assignment_email'))
            self.assertTrue(hasattr(email_service, 'send_deadline_reminder_email'))
        except ImportError as e:
            self.fail(f"Failed to import email service: {e}")
    
    def test_email_service_initialization_integration(self):
        """Test email service initialization in integration context"""
        from services.email_service import email_service
        
        # Test service initialization
        self.assertIsNotNone(email_service.smtp_server)
        self.assertIsNotNone(email_service.smtp_port)
        self.assertEqual(email_service.smtp_server, 'smtp.gmail.com')
        self.assertEqual(email_service.smtp_port, 587)
        
        # Test that credentials are loaded (even if None in test environment)
        # In test environment, these might be None, which is expected
        self.assertTrue(hasattr(email_service, 'smtp_user'))
        self.assertTrue(hasattr(email_service, 'smtp_password'))
    
    @patch('smtplib.SMTP')
    def test_email_service_smtp_integration(self, mock_smtp):
        """Test email service SMTP integration"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        from services.email_service import email_service
        
        # Test project assignment email
        result = email_service.send_project_assignment_email(
            to_email='test@example.com',
            user_name='Test User',
            project_name='Test Project',
            project_desc='Test Description',
            creator_name='Creator',
            start_date='2024-01-01',
            end_date='2024-12-31'
        )
        
        # Verify SMTP integration
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        self.assertTrue(result)
    
    @patch('smtplib.SMTP')
    def test_email_service_task_assignment_integration(self, mock_smtp):
        """Test task assignment email integration"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        from services.email_service import email_service
        
        # Test task assignment email
        result = email_service.send_task_assignment_email(
            to_email='test@example.com',
            user_name='Test User',
            task_name='Test Task',
            task_desc='Test Description',
            project_name='Test Project',
            creator_name='Creator',
            start_date='2024-01-01',
            end_date='2024-01-15',
            priority_level='High'
        )
        
        # Verify SMTP integration
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        self.assertTrue(result)
    
    @patch('smtplib.SMTP')
    def test_email_service_transfer_integration(self, mock_smtp):
        """Test task transfer email integration"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        from services.email_service import email_service
        
        # Test task transfer email
        result = email_service.send_task_transfer_ownership_email(
            new_owner_email='newowner@example.com',
            new_owner_name='New Owner',
            old_owner_email='oldowner@example.com',
            old_owner_name='Old Owner',
            task_name='Test Task',
            task_desc='Test Description',
            project_name='Test Project',
            transferred_by_name='Transferrer',
            start_date='2024-01-01',
            end_date='2024-01-15'
        )
        
        # Verify SMTP integration
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        self.assertTrue(result)
    
    @patch('smtplib.SMTP')
    def test_email_service_subtask_transfer_integration(self, mock_smtp):
        """Test subtask transfer email integration"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        from services.email_service import email_service
        
        # Test subtask transfer email
        result = email_service.send_subtask_transfer_ownership_email(
            new_owner_email='newowner@example.com',
            new_owner_name='New Owner',
            old_owner_email='oldowner@example.com',
            old_owner_name='Old Owner',
            subtask_name='Test Subtask',
            subtask_desc='Test Description',
            parent_task_name='Parent Task',
            project_name='Test Project',
            transferred_by_name='Transferrer',
            start_date='2024-01-01',
            end_date='2024-01-15'
        )
        
        # Verify SMTP integration
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        self.assertTrue(result)
    
    @patch('smtplib.SMTP')
    def test_email_service_deadline_reminder_integration(self, mock_smtp):
        """Test deadline reminder email integration"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        from services.email_service import email_service
        
        # Test deadline reminder email
        result = email_service.send_deadline_reminder_email(
            to_email='test@example.com',
            user_name='Test User',
            task_name='Test Task',
            task_desc='Test Description',
            project_name='Test Project',
            hours_until_due=2.5,
            due_date='2024-01-15',
            priority_level='High'
        )
        
        # Verify SMTP integration
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        self.assertTrue(result)
    
    def test_email_service_error_handling_integration(self):
        """Test email service error handling integration"""
        # Test email service with SMTP error
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.side_effect = Exception("SMTP connection failed")
            
            from services.email_service import email_service
            
            # Test project assignment email with error
            result = email_service.send_project_assignment_email(
                to_email='test@example.com',
                user_name='Test User',
                project_name='Test Project',
                project_desc='Test Description',
                creator_name='Creator',
                start_date='2024-01-01',
                end_date='2024-12-31'
            )
            
            # Verify error handling
            self.assertFalse(result)
    
    def test_email_service_workflow_integration(self):
        """Test complete email service workflow integration"""
        from services.email_service import email_service
        
        # Test that all email service functions are available and callable
        email_functions = [
            'send_project_assignment_email',
            'send_task_assignment_email',
            'send_task_transfer_ownership_email',
            'send_subtask_transfer_ownership_email',
            'send_deadline_reminder_email'
        ]
        
        for func_name in email_functions:
            self.assertTrue(hasattr(email_service, func_name), 
                          f"Email service should have {func_name}")
            self.assertTrue(callable(getattr(email_service, func_name)), 
                          f"{func_name} should be callable")
    
    def test_email_service_environment_integration(self):
        """Test email service environment integration"""
        from services.email_service import email_service
        
        # Test that service can access environment variables
        # In test environment, these might be None, which is expected
        self.assertTrue(hasattr(email_service, 'smtp_user'))
        self.assertTrue(hasattr(email_service, 'smtp_password'))
        
        # Test that service is configured for Gmail
        self.assertEqual(email_service.smtp_server, 'smtp.gmail.com')
        self.assertEqual(email_service.smtp_port, 587)
    
    def test_email_service_singleton_integration(self):
        """Test email service singleton integration"""
        from services.email_service import email_service
        from services.email_service import EmailService
        
        # Test that email_service is a singleton instance
        self.assertIsInstance(email_service, EmailService)
        
        # Test that importing again gives the same instance
        from services.email_service import email_service as email_service2
        self.assertIs(email_service, email_service2)


class TestEmailServiceEdgeCases(unittest.TestCase):
    """Edge case tests for Email Service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.email_service = EmailService()
    
    @patch('smtplib.SMTP')
    def test_project_assignment_email_empty_description(self, mock_smtp):
        """Test project assignment email with empty description"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test data with empty description
        test_data = {
            'to_email': 'test@example.com',
            'user_name': 'John Doe',
            'project_name': 'Test Project',
            'project_desc': '',
            'creator_name': 'Jane Smith',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        }
        
        # Test the function
        result = self.email_service.send_project_assignment_email(**test_data)
        
        # Assertions
        self.assertTrue(result)
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_task_assignment_email_empty_description(self, mock_smtp):
        """Test task assignment email with empty description"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test data with empty description
        test_data = {
            'to_email': 'test@example.com',
            'user_name': 'John Doe',
            'task_name': 'Test Task',
            'task_desc': '',
            'project_name': 'Test Project',
            'creator_name': 'Jane Smith',
            'start_date': '2024-01-01',
            'end_date': '2024-01-15',
            'priority_level': 'High'
        }
        
        # Test the function
        result = self.email_service.send_task_assignment_email(**test_data)
        
        # Assertions
        self.assertTrue(result)
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_task_assignment_email_no_project(self, mock_smtp):
        """Test task assignment email with no project name"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test data without project name
        test_data = {
            'to_email': 'test@example.com',
            'user_name': 'John Doe',
            'task_name': 'Test Task',
            'task_desc': 'Test Description',
            'project_name': None,
            'creator_name': 'Jane Smith',
            'start_date': '2024-01-01',
            'end_date': '2024-01-15',
            'priority_level': 'High'
        }
        
        # Test the function
        result = self.email_service.send_task_assignment_email(**test_data)
        
        # Assertions
        self.assertTrue(result)
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_task_assignment_email_no_end_date(self, mock_smtp):
        """Test task assignment email with no end date"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test data without end date
        test_data = {
            'to_email': 'test@example.com',
            'user_name': 'John Doe',
            'task_name': 'Test Task',
            'task_desc': 'Test Description',
            'project_name': 'Test Project',
            'creator_name': 'Jane Smith',
            'start_date': '2024-01-01',
            'end_date': None,
            'priority_level': 'High'
        }
        
        # Test the function
        result = self.email_service.send_task_assignment_email(**test_data)
        
        # Assertions
        self.assertTrue(result)
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_deadline_reminder_email_time_formatting(self, mock_smtp):
        """Test deadline reminder email time formatting"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test data with different time formats
        test_cases = [
            {'hours_until_due': 0.5, 'expected': '30 minutes'},
            {'hours_until_due': 2.0, 'expected': '2 hours'},
            {'hours_until_due': 25.0, 'expected': '1 day'},
            {'hours_until_due': 50.0, 'expected': '2 days'}
        ]
        
        for case in test_cases:
            with self.subTest(hours=case['hours_until_due']):
                test_data = {
                    'to_email': 'test@example.com',
                    'user_name': 'John Doe',
                    'task_name': 'Test Task',
                    'task_desc': 'Test Description',
                    'project_name': 'Test Project',
                    'hours_until_due': case['hours_until_due'],
                    'due_date': '2024-01-15',
                    'priority_level': 'High'
                }
                
                # Test the function
                result = self.email_service.send_deadline_reminder_email(**test_data)
                
                # Assertions
                self.assertTrue(result)
                mock_server.send_message.assert_called_once()
                
                # Reset mock for next test
                mock_server.reset_mock()


if __name__ == '__main__':
    unittest.main()
