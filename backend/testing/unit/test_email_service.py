#!/usr/bin/env python3
"""
C1 Unit Tests - Email Service
Tests individual EmailService methods in complete isolation.
No external dependencies, no Flask app, no database.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import EmailService for unit testing
from services.email_service import EmailService


class TestEmailServiceUnit(unittest.TestCase):
    """C1 Unit tests for EmailService class"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock environment variables
        with patch.dict(os.environ, {
            'GMAIL_USER': 'test@gmail.com',
            'GMAIL_APP_PASSWORD': 'test_password'
        }):
            self.email_service = EmailService()
    
    def test_email_service_initialization(self):
        """Test EmailService initialization"""
        self.assertEqual(self.email_service.smtp_user, 'test@gmail.com')
        self.assertEqual(self.email_service.smtp_password, 'test_password')
        self.assertEqual(self.email_service.smtp_server, 'smtp.gmail.com')
        self.assertEqual(self.email_service.smtp_port, 587)
    
    @patch('smtplib.SMTP')
    def test_send_project_assignment_email_success(self, mock_smtp):
        """Test successful project assignment email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = self.email_service.send_project_assignment_email(
            to_email="test@example.com",
            user_name="John Doe",
            project_name="Test Project",
            project_desc="Test Description",
            creator_name="Creator",
            start_date="2025-01-01",
            end_date="2025-01-31"
        )
        
        self.assertTrue(result)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@gmail.com', 'test_password')
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_project_assignment_email_failure(self, mock_smtp):
        """Test project assignment email sending failure"""
        # Mock SMTP server to raise exception
        mock_smtp.side_effect = Exception("SMTP Error")
        
        result = self.email_service.send_project_assignment_email(
            to_email="test@example.com",
            user_name="John Doe",
            project_name="Test Project",
            project_desc="Test Description",
            creator_name="Creator",
            start_date="2025-01-01",
            end_date="2025-01-31"
        )
        
        self.assertFalse(result)
    
    @patch('smtplib.SMTP')
    def test_send_task_assignment_email_success(self, mock_smtp):
        """Test successful task assignment email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = self.email_service.send_task_assignment_email(
            to_email="test@example.com",
            user_name="John Doe",
            task_name="Test Task",
            task_desc="Test Description",
            project_name="Test Project",
            creator_name="Creator",
            start_date="2025-01-01",
            end_date="2025-01-31",
            priority_level="High"
        )
        
        self.assertTrue(result)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@gmail.com', 'test_password')
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_task_transfer_ownership_email_success(self, mock_smtp):
        """Test successful task ownership transfer email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = self.email_service.send_task_transfer_ownership_email(
            new_owner_email="new@example.com",
            new_owner_name="New Owner",
            old_owner_email="old@example.com",
            old_owner_name="Old Owner",
            task_name="Test Task",
            task_desc="Test Description",
            project_name="Test Project",
            transferred_by_name="Transferrer",
            start_date="2025-01-01",
            end_date="2025-01-31"
        )
        
        self.assertTrue(result)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@gmail.com', 'test_password')
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_subtask_transfer_ownership_email_success(self, mock_smtp):
        """Test successful subtask ownership transfer email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = self.email_service.send_subtask_transfer_ownership_email(
            new_owner_email="new@example.com",
            new_owner_name="New Owner",
            old_owner_email="old@example.com",
            old_owner_name="Old Owner",
            subtask_name="Test Subtask",
            subtask_desc="Test Description",
            parent_task_name="Parent Task",
            project_name="Test Project",
            transferred_by_name="Transferrer",
            start_date="2025-01-01",
            end_date="2025-01-31"
        )
        
        self.assertTrue(result)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@gmail.com', 'test_password')
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_deadline_reminder_email_success(self, mock_smtp):
        """Test successful deadline reminder email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = self.email_service.send_deadline_reminder_email(
            to_email="test@example.com",
            user_name="John Doe",
            task_name="Test Task",
            task_desc="Test Description",
            project_name="Test Project",
            hours_until_due=24.0,
            due_date="2025-01-31",
            priority_level="High"
        )
        
        self.assertTrue(result)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@gmail.com', 'test_password')
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_deadline_reminder_email_less_than_hour(self, mock_smtp):
        """Test deadline reminder email with less than 1 hour remaining"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = self.email_service.send_deadline_reminder_email(
            to_email="test@example.com",
            user_name="John Doe",
            task_name="Test Task",
            task_desc="Test Description",
            project_name="Test Project",
            hours_until_due=0.5,  # 30 minutes
            due_date="2025-01-31",
            priority_level="High"
        )
        
        self.assertTrue(result)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@gmail.com', 'test_password')
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_deadline_reminder_email_multiple_days(self, mock_smtp):
        """Test deadline reminder email with multiple days remaining"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = self.email_service.send_deadline_reminder_email(
            to_email="test@example.com",
            user_name="John Doe",
            task_name="Test Task",
            task_desc="Test Description",
            project_name="Test Project",
            hours_until_due=72.0,  # 3 days
            due_date="2025-01-31",
            priority_level="Medium"
        )
        
        self.assertTrue(result)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@gmail.com', 'test_password')
        mock_server.send_message.assert_called_once()
    
    def test_priority_colors_mapping(self):
        """Test priority level color mapping in deadline reminder"""
        # This tests the internal logic of priority color assignment
        priority_colors = {
            'High': '#ef4444',
            'Medium': '#f59e0b', 
            'Low': '#10b981'
        }
        
        # Test all priority levels
        for priority, expected_color in priority_colors.items():
            # We can't directly test the internal logic, but we can verify
            # that the method handles different priority levels
            with patch('smtplib.SMTP') as mock_smtp:
                mock_server = MagicMock()
                mock_smtp.return_value.__enter__.return_value = mock_server
                
                result = self.email_service.send_deadline_reminder_email(
                    to_email="test@example.com",
                    user_name="John Doe",
                    task_name="Test Task",
                    task_desc="Test Description",
                    project_name="Test Project",
                    hours_until_due=24.0,
                    due_date="2025-01-31",
                    priority_level=priority
                )
                
                self.assertTrue(result)


if __name__ == '__main__':
    print("=" * 80)
    print("C1 UNIT TESTING - EMAIL SERVICE")
    print("=" * 80)
    print("Testing individual EmailService methods in complete isolation")
    print("No external dependencies, no Flask app, no database")
    print("=" * 80)

    # Run with verbose output
    unittest.main(verbosity=2)
