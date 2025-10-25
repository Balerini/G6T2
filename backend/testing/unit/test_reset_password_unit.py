#!/usr/bin/env python3
"""
Unit tests for reset password functionality.
Tests the reset password API endpoint with various scenarios.
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, validate_password, hash_password, verify_password


class TestResetPasswordAPI(unittest.TestCase):
    """Test cases for reset password API endpoint"""
    
    def setUp(self):
        """Set up test client and mock Firestore"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Mock Firestore client
        self.mock_db = MagicMock()
        self.mock_users_ref = MagicMock()
        self.mock_db.collection.return_value = self.mock_users_ref
        
        # Mock user document
        self.mock_user_doc = MagicMock()
        self.mock_user_doc.id = 'test_user_id'
        self.mock_user_doc.to_dict.return_value = {
            'email': 'test@example.com',
            'name': 'Test User',
            'role_name': 'Staff'
        }
        
    def test_reset_password_success(self):
        """Test successful password reset"""
        # Mock data
        reset_data = {
            "email": "test@example.com",
            "newPassword": "NewPass123!"
        }
        
        # Mock Firestore responses
        self.mock_users_ref.where.return_value.stream.return_value = [self.mock_user_doc]
        self.mock_users_ref.document.return_value.update.return_value = None
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/api/auth/reset-password', 
                                      data=json.dumps(reset_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['ok'])
        self.assertEqual(data['message'], 'Password reset successful')
        
        # Verify Firestore was called
        self.mock_users_ref.where.assert_called_once_with('email', '==', 'test@example.com')
        self.mock_users_ref.document.assert_called_once_with('test_user_id')
    
    def test_reset_password_missing_email(self):
        """Test reset password with missing email"""
        reset_data = {
            "newPassword": "NewPass123!"
            # Missing email
        }
        
        response = self.client.post('/api/auth/reset-password', 
                                  data=json.dumps(reset_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])
        self.assertIn('Email and new password are required', data['error'])
    
    def test_reset_password_missing_new_password(self):
        """Test reset password with missing new password"""
        reset_data = {
            "email": "test@example.com"
            # Missing newPassword
        }
        
        response = self.client.post('/api/auth/reset-password', 
                                  data=json.dumps(reset_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])
        self.assertIn('Email and new password are required', data['error'])
    
    def test_reset_password_invalid_password(self):
        """Test reset password with invalid new password"""
        reset_data = {
            "email": "test@example.com",
            "newPassword": "weak"  # Too short
        }
        
        response = self.client.post('/api/auth/reset-password', 
                                  data=json.dumps(reset_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])
        self.assertIn('Password must be at least 8 characters long', data['error'])
    
    def test_reset_password_user_not_found(self):
        """Test reset password with non-existent email"""
        reset_data = {
            "email": "nonexistent@example.com",
            "newPassword": "NewPass123!"
        }
        
        # Mock no user found
        self.mock_users_ref.where.return_value.stream.return_value = []
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/api/auth/reset-password', 
                                      data=json.dumps(reset_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])
        self.assertIn('No account found with this email address', data['error'])
    
    def test_reset_password_email_case_insensitive(self):
        """Test reset password with different email case"""
        reset_data = {
            "email": "TEST@EXAMPLE.COM",  # Uppercase
            "newPassword": "NewPass123!"
        }
        
        # Mock user found (email should be lowercased)
        self.mock_users_ref.where.return_value.stream.return_value = [self.mock_user_doc]
        self.mock_users_ref.document.return_value.update.return_value = None
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/api/auth/reset-password', 
                                      data=json.dumps(reset_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        # Verify email was lowercased in query
        self.mock_users_ref.where.assert_called_once_with('email', '==', 'test@example.com')
    
    def test_reset_password_email_whitespace_handling(self):
        """Test reset password with email containing whitespace"""
        reset_data = {
            "email": "  test@example.com  ",  # With whitespace
            "newPassword": "NewPass123!"
        }
        
        # Mock user found
        self.mock_users_ref.where.return_value.stream.return_value = [self.mock_user_doc]
        self.mock_users_ref.document.return_value.update.return_value = None
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/api/auth/reset-password', 
                                      data=json.dumps(reset_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        # Verify email was stripped in query
        self.mock_users_ref.where.assert_called_once_with('email', '==', 'test@example.com')
    
    def test_reset_password_database_error(self):
        """Test reset password with database error"""
        reset_data = {
            "email": "test@example.com",
            "newPassword": "NewPass123!"
        }
        
        # Mock database error
        self.mock_users_ref.where.return_value.stream.side_effect = Exception("Database error")
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/api/auth/reset-password', 
                                      data=json.dumps(reset_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])
        self.assertIn('Failed to reset password', data['error'])
    
    def test_reset_password_invalid_json(self):
        """Test reset password with invalid JSON"""
        response = self.client.post('/api/auth/reset-password', 
                                  data="invalid json",
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])
        self.assertIn('Email and new password are required', data['error'])
    
    def test_reset_password_empty_request(self):
        """Test reset password with empty request body"""
        response = self.client.post('/api/auth/reset-password', 
                                  data=json.dumps({}),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])
        self.assertIn('Email and new password are required', data['error'])
    
    def test_reset_password_password_validation_integration(self):
        """Test that password validation is properly integrated"""
        invalid_passwords = [
            ("short", "Password must be at least 8 characters long"),
            ("nouppercase!", "Password must contain at least one uppercase letter"),
            ("NOLOWERCASE!", "Password must contain at least one lowercase letter"),
            ("NoNumbers!", "Password must contain at least one number"),
            ("NoSpecial123", "Password must contain at least one special character")
        ]
        
        for invalid_pass, expected_error in invalid_passwords:
            reset_data = {
                "email": "test@example.com",
                "newPassword": invalid_pass
            }
            
            response = self.client.post('/api/auth/reset-password', 
                                      data=json.dumps(reset_data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertFalse(data['ok'])
            self.assertIn(expected_error, data['error'])
    
    def test_reset_password_password_hashing_integration(self):
        """Test that password hashing is properly integrated"""
        reset_data = {
            "email": "test@example.com",
            "newPassword": "NewPass123!"
        }
        
        # Mock user found
        self.mock_users_ref.where.return_value.stream.return_value = [self.mock_user_doc]
        self.mock_users_ref.document.return_value.update.return_value = None
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/api/auth/reset-password', 
                                      data=json.dumps(reset_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify that update was called with hashed password
        update_call = self.mock_users_ref.document.return_value.update.call_args[0][0]
        self.assertIn('password', update_call)
        
        # Verify password was hashed (should be hex string, not plain text)
        hashed_password = update_call['password']
        self.assertNotEqual(hashed_password, 'NewPass123!')
        self.assertTrue(len(hashed_password) > 50)  # Hashed password should be long
    
    def test_reset_password_valid_passwords(self):
        """Test reset password with various valid passwords"""
        valid_passwords = [
            "Test123!",      # 8 characters
            "TestPass123!",  # 12 characters
            "Abc123!@#",     # With special chars
            "MyPass1!",      # 9 characters
        ]
        
        for valid_pass in valid_passwords:
            reset_data = {
                "email": "test@example.com",
                "newPassword": valid_pass
            }
            
            # Mock user found
            self.mock_users_ref.where.return_value.stream.return_value = [self.mock_user_doc]
            self.mock_users_ref.document.return_value.update.return_value = None
            
            with patch('app.get_firestore_client', return_value=self.mock_db):
                response = self.client.post('/api/auth/reset-password', 
                                          data=json.dumps(reset_data),
                                          content_type='application/json')
            
            self.assertEqual(response.status_code, 200, f"Failed for password: {valid_pass}")
            data = json.loads(response.data)
            self.assertTrue(data['ok'], f"Failed for password: {valid_pass}")


class TestResetPasswordValidation(unittest.TestCase):
    """Test cases for reset password validation logic"""
    
    def test_reset_password_email_validation(self):
        """Test email validation in reset password"""
        # Test with valid email
        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        reset_data = {
            "email": "valid@example.com",
            "newPassword": "TestPass123!"
        }
        
        # Mock successful response
        with patch('app.get_firestore_client') as mock_db:
            mock_users_ref = MagicMock()
            mock_db.return_value.collection.return_value = mock_users_ref
            mock_users_ref.where.return_value.stream.return_value = [MagicMock(id='test_id')]
            mock_users_ref.document.return_value.update.return_value = None
            
            response = client.post('/api/auth/reset-password', 
                                data=json.dumps(reset_data),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
    
    def test_reset_password_password_requirements(self):
        """Test that reset password enforces same password requirements as registration"""
        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Test password that would fail registration validation
        reset_data = {
            "email": "test@example.com",
            "newPassword": "weak"  # Too short
        }
        
        response = client.post('/api/auth/reset-password', 
                            data=json.dumps(reset_data),
                            content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Password must be at least 8 characters long', data['error'])


if __name__ == '__main__':
    unittest.main()
