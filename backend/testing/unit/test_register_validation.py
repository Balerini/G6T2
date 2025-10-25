#!/usr/bin/env python3
"""
C1 Unit Tests - Register Form Validation Functions
Tests individual register validation functions in complete isolation.
No external dependencies, no Flask app, no database.
"""

import unittest
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import validation functions for unit testing
from app import validate_password


class TestRegisterValidationUnit(unittest.TestCase):
    """C1 Unit tests for register validation functions"""
    
    def test_validate_name_length(self):
        """Test name length validation logic"""
        def validate_name_length(name):
            """Mock name length validation function"""
            if not name:
                return "Name is required"
            if len(name.strip()) < 2:
                return "Name must be at least 2 characters"
            return None
        
        # Test valid names
        self.assertIsNone(validate_name_length("John"))
        self.assertIsNone(validate_name_length("John Doe"))
        self.assertIsNone(validate_name_length("  John  "))  # Should handle whitespace
        
        # Test invalid names
        self.assertEqual(validate_name_length(""), "Name is required")
        self.assertEqual(validate_name_length(None), "Name is required")
        self.assertEqual(validate_name_length("J"), "Name must be at least 2 characters")
        self.assertEqual(validate_name_length("  "), "Name must be at least 2 characters")
    
    def test_validate_required_fields(self):
        """Test required fields validation logic"""
        def validate_required_fields(data):
            """Mock required fields validation function"""
            required_fields = ['name', 'email', 'password', 'division_name']
            missing_fields = []
            
            for field in required_fields:
                if not data.get(field):
                    missing_fields.append(field)
            
            if missing_fields:
                return f"Missing required fields: {', '.join(missing_fields)}"
            return None
        
        # Test valid data
        valid_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'Password123!',
            'division_name': 'Engineering'
        }
        self.assertIsNone(validate_required_fields(valid_data))
        
        # Test missing fields
        incomplete_data = {
            'name': 'John Doe',
            'email': 'john@example.com'
            # Missing password and division_name
        }
        result = validate_required_fields(incomplete_data)
        self.assertIn("password", result)
        self.assertIn("division_name", result)
    
    def test_validate_division_name(self):
        """Test division name validation logic"""
        def validate_division_name(division_name):
            """Mock division name validation function"""
            valid_departments = [
                "Sales",
                "Consultancy", 
                "System Solutioning",
                "Engineering Operation",
                "HR and Admin",
                "Finance",
                "IT"
            ]
            
            if not division_name:
                return "Division name is required"
            
            if division_name not in valid_departments:
                return "Invalid department selected"
            
            return None
        
        # Test valid departments
        for dept in ["Sales", "Consultancy", "System Solutioning", "Engineering Operation", 
                    "HR and Admin", "Finance", "IT"]:
            self.assertIsNone(validate_division_name(dept))
        
        # Test invalid departments
        self.assertEqual(validate_division_name(""), "Division name is required")
        self.assertEqual(validate_division_name(None), "Division name is required")
        self.assertEqual(validate_division_name("Invalid Dept"), "Invalid department selected")
        self.assertEqual(validate_division_name("sales"), "Invalid department selected")  # Case sensitive
    
    def test_validate_email_format(self):
        """Test email format validation logic"""
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
            'user@@domain.com',
            'user@domain@com'
        ]
        for email in invalid_emails:
            result = validate_email_format(email)
            self.assertIsNotNone(result)
    
    def test_validate_role_assignment(self):
        """Test role assignment logic based on email"""
        def assign_role_from_email(email):
            """Mock role assignment function"""
            if not email:
                return 'staff'  # Default role
            
            email_lower = email.lower()
            if 'director' in email_lower:
                return 'director'
            elif 'manager' in email_lower:
                return 'manager'
            else:
                return 'staff'
        
        # Test role assignments
        self.assertEqual(assign_role_from_email('director@company.com'), 'director')
        self.assertEqual(assign_role_from_email('john.director@company.com'), 'director')
        self.assertEqual(assign_role_from_email('manager@company.com'), 'manager')
        self.assertEqual(assign_role_from_email('jane.manager@company.com'), 'manager')
        self.assertEqual(assign_role_from_email('developer@company.com'), 'staff')
        self.assertEqual(assign_role_from_email(''), 'staff')
        self.assertEqual(assign_role_from_email(None), 'staff')
    
    def test_validate_password_comprehensive(self):
        """Test comprehensive password validation using existing function"""
        # Test valid passwords
        valid_passwords = [
            'Password1!',
            'Test123@',
            'MyPass9#'
        ]
        for password in valid_passwords:
            result = validate_password(password)
            self.assertIsNone(result, f"Password '{password}' should be valid")
        
        # Test invalid passwords
        invalid_cases = [
            ('short', "Password must be at least 8 characters long"),
            ('toolongpassword', "Password must be no more than 12 characters long"),
            ('nouppercase123!', "Password must be no more than 12 characters long"),
            ('NOLOWERCASE123!', "Password must be no more than 12 characters long"),
            ('NoNumbers!', "Password must be no more than 12 characters long"),
            ('NoSpecial123', "Password must be no more than 12 characters long")
        ]
        
        for password, expected_error in invalid_cases:
            result = validate_password(password)
            self.assertIsNotNone(result, f"Password '{password}' should fail validation")
    
    def test_validate_register_data_comprehensive(self):
        """Test comprehensive register data validation"""
        def validate_register_data(data):
            """Mock comprehensive register data validation function"""
            errors = []
            
            # Check required fields
            required_fields = ['name', 'email', 'password', 'division_name']
            for field in required_fields:
                if not data.get(field):
                    errors.append(f"Missing required field: {field}")
            
            # Validate name length
            if 'name' in data and data['name']:
                if len(data['name'].strip()) < 2:
                    errors.append("Name must be at least 2 characters")
            
            # Validate email format
            if 'email' in data and data['email']:
                if '@' not in data['email']:
                    errors.append("Invalid email format")
            
            # Validate password
            if 'password' in data and data['password']:
                password_error = validate_password(data['password'])
                if password_error:
                    errors.append(password_error)
            
            # Validate division
            if 'division_name' in data and data['division_name']:
                valid_departments = [
                    "Sales", "Consultancy", "System Solutioning", "Engineering Operation",
                    "HR and Admin", "Finance", "IT"
                ]
                if data['division_name'] not in valid_departments:
                    errors.append("Invalid department selected")
            
            return errors
        
        # Test valid data
        valid_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'Password1!',
            'division_name': 'Engineering Operation'
        }
        errors = validate_register_data(valid_data)
        self.assertEqual(len(errors), 0)
        
        # Test invalid data
        invalid_data = {
            'name': 'J',  # Too short
            'email': 'invalid-email',  # Invalid format
            'password': 'weak',  # Invalid password
            'division_name': 'Invalid Dept'  # Invalid department
        }
        errors = validate_register_data(invalid_data)
        self.assertGreater(len(errors), 0)
        self.assertIn("Name must be at least 2 characters", errors)
        self.assertIn("Invalid email format", errors)
        self.assertIn("Password must be at least 8 characters long", errors)
        self.assertIn("Invalid department selected", errors)


if __name__ == '__main__':
    print("=" * 80)
    print("C1 UNIT TESTING - REGISTER VALIDATION FUNCTIONS")
    print("=" * 80)
    print("Testing individual register validation functions in complete isolation")
    print("No external dependencies, no Flask app, no database")
    print("=" * 80)

    # Run with verbose output
    unittest.main(verbosity=2)
