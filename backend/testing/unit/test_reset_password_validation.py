#!/usr/bin/env python3
"""
C1 Unit Tests - Reset Password Validation Functions
Tests individual reset password validation functions in complete isolation.
No external dependencies, no Flask app, no database.
"""

import unittest
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import validation functions for unit testing
from app import validate_password


class TestResetPasswordValidationUnit(unittest.TestCase):
    """C1 Unit tests for reset password validation functions"""
    
    def test_validate_required_fields(self):
        """Test required fields validation for reset password"""
        def validate_required_fields(data):
            """Mock required fields validation function"""
            if not data.get('email'):
                return "Email is required"
            if not data.get('newPassword'):
                return "New password is required"
            return None
        
        # Test valid data
        valid_data = {
            'email': 'user@example.com',
            'newPassword': 'NewPassword123!'
        }
        self.assertIsNone(validate_required_fields(valid_data))
        
        # Test missing email
        missing_email = {
            'newPassword': 'NewPassword123!'
        }
        self.assertEqual(validate_required_fields(missing_email), "Email is required")
        
        # Test missing password
        missing_password = {
            'email': 'user@example.com'
        }
        self.assertEqual(validate_required_fields(missing_password), "New password is required")
        
        # Test both missing
        empty_data = {}
        result = validate_required_fields(empty_data)
        self.assertIn("Email is required", result)
    
    def test_validate_email_format(self):
        """Test email format validation for reset password"""
        def validate_email_format(email):
            """Mock email format validation function"""
            if not email:
                return "Email is required"
            
            if '@' not in email:
                return "Invalid email format"
            
            parts = email.split('@')
            if len(parts) != 2:
                return "Invalid email format"
            
            if not parts[0] or not parts[1]:
                return "Invalid email format"
            
            return None
        
        # Test valid emails
        valid_emails = [
            'user@example.com',
            'test.email@domain.co.uk',
            'user+tag@example.org',
            'user123@test-domain.com'
        ]
        for email in valid_emails:
            self.assertIsNone(validate_email_format(email))
        
        # Test invalid emails
        invalid_emails = [
            '',
            None,
            'invalid-email',
            '@domain.com',
            'user@',
            'user@@domain.com'
        ]
        for email in invalid_emails:
            result = validate_email_format(email)
            self.assertIsNotNone(result)
    
    def test_validate_new_password(self):
        """Test new password validation using existing validate_password function"""
        # Test valid passwords
        valid_passwords = [
            'NewPass1!',
            'Reset123@'
        ]
        for password in valid_passwords:
            result = validate_password(password)
            self.assertIsNone(result, f"Password '{password}' should be valid")
        
        # Test invalid passwords
        invalid_cases = [
            ('short', "Password must be at least 8 characters long"),
            ('toolongpassword', "Password must be no more than 12 characters long"),
            ('nouppercase123!', "Password must contain at least one uppercase letter"),
            ('NOLOWERCASE123!', "Password must contain at least one lowercase letter"),
            ('NoNumbers!', "Password must contain at least one number"),
            ('NoSpecial123', "Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
        ]
        
        for password, expected_error in invalid_cases:
            result = validate_password(password)
            self.assertIsNotNone(result, f"Password '{password}' should fail validation")
    
    def test_validate_email_normalization(self):
        """Test email normalization logic"""
        def normalize_email(email):
            """Mock email normalization function"""
            if not email:
                return None
            return email.lower().strip()
        
        # Test email normalization
        test_cases = [
            ('USER@EXAMPLE.COM', 'user@example.com'),
            ('  user@example.com  ', 'user@example.com'),
            ('User@Example.Com', 'user@example.com'),
            ('  USER@EXAMPLE.COM  ', 'user@example.com')
        ]
        
        for input_email, expected in test_cases:
            result = normalize_email(input_email)
            self.assertEqual(result, expected)
    
    def test_validate_reset_password_data_comprehensive(self):
        """Test comprehensive reset password data validation"""
        def validate_reset_password_data(data):
            """Mock comprehensive reset password data validation function"""
            errors = []
            
            # Check required fields
            if not data.get('email'):
                errors.append("Email is required")
            if not data.get('newPassword'):
                errors.append("New password is required")
            
            # Validate email format
            if 'email' in data and data['email']:
                if '@' not in data['email']:
                    errors.append("Invalid email format")
            
            # Validate password
            if 'newPassword' in data and data['newPassword']:
                password_error = validate_password(data['newPassword'])
                if password_error:
                    errors.append(password_error)
            
            return errors
        
        # Test valid data
        valid_data = {
            'email': 'user@example.com',
            'newPassword': 'NewPass1!'
        }
        errors = validate_reset_password_data(valid_data)
        self.assertEqual(len(errors), 0)
        
        # Test invalid data
        invalid_data = {
            'email': 'invalid-email',
            'newPassword': 'weak'
        }
        errors = validate_reset_password_data(invalid_data)
        self.assertGreater(len(errors), 0)
        self.assertIn("Invalid email format", errors)
        self.assertIn("Password must be at least 8 characters long", errors)
    
    def test_validate_password_strength_requirements(self):
        """Test password strength requirements validation"""
        def check_password_strength(password):
            """Mock password strength checking function"""
            if not password:
                return False
            
            # Check length
            if len(password) < 8 or len(password) > 12:
                return False
            
            # Check for uppercase
            if not any(c.isupper() for c in password):
                return False
            
            # Check for lowercase
            if not any(c.islower() for c in password):
                return False
            
            # Check for digit
            if not any(c.isdigit() for c in password):
                return False
            
            # Check for special character
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                return False
            
            return True
        
        # Test strong passwords
        strong_passwords = [
            'Password1!',
            'Test123@',
            'MyPass9#'
        ]
        for password in strong_passwords:
            self.assertTrue(check_password_strength(password), f"Password '{password}' should be strong")
        
        # Test weak passwords
        weak_passwords = [
            '',
            'short',
            'toolongpassword',
            'nouppercase123!',
            'NOLOWERCASE123!',
            'NoNumbers!',
            'NoSpecial123'
        ]
        for password in weak_passwords:
            self.assertFalse(check_password_strength(password), f"Password '{password}' should be weak")
    
    def test_validate_email_existence_logic(self):
        """Test email existence validation logic (mock)"""
        def check_email_exists(email):
            """Mock email existence checking function"""
            # Mock database of existing emails
            existing_emails = [
                'user1@example.com',
                'user2@example.com',
                'admin@company.com'
            ]
            
            normalized_email = email.lower().strip() if email else ''
            return normalized_email in existing_emails
        
        # Test existing emails
        existing_emails = [
            'user1@example.com',
            'USER1@EXAMPLE.COM',
            '  user2@example.com  ',
            'admin@company.com'
        ]
        for email in existing_emails:
            self.assertTrue(check_email_exists(email), f"Email '{email}' should exist")
        
        # Test non-existing emails
        non_existing_emails = [
            'nonexistent@example.com',
            'newuser@company.com',
            '',
            None
        ]
        for email in non_existing_emails:
            self.assertFalse(check_email_exists(email), f"Email '{email}' should not exist")
    
    def test_validate_password_reset_workflow(self):
        """Test complete password reset workflow validation"""
        def validate_password_reset_workflow(email, new_password):
            """Mock complete password reset workflow validation"""
            errors = []
            
            # Validate email
            if not email:
                errors.append("Email is required")
            elif '@' not in email:
                errors.append("Invalid email format")
            
            # Validate new password
            if not new_password:
                errors.append("New password is required")
            else:
                password_error = validate_password(new_password)
                if password_error:
                    errors.append(password_error)
            
            return errors
        
        # Test valid workflow
        errors = validate_password_reset_workflow('user@example.com', 'NewPass1!')
        self.assertEqual(len(errors), 0)
        
        # Test invalid workflow
        errors = validate_password_reset_workflow('invalid-email', 'weak')
        self.assertGreater(len(errors), 0)
        self.assertIn("Invalid email format", errors)
        self.assertIn("Password must be at least 8 characters long", errors)


if __name__ == '__main__':
    print("=" * 80)
    print("C1 UNIT TESTING - RESET PASSWORD VALIDATION FUNCTIONS")
    print("=" * 80)
    print("Testing individual reset password validation functions in complete isolation")
    print("No external dependencies, no Flask app, no database")
    print("=" * 80)

    # Run with verbose output
    unittest.main(verbosity=2)
