#!/usr/bin/env python3
"""
Unit tests for password validation in the sign-up feature.
Tests password requirements, hashing, and verification functionality.
"""

import unittest
import sys
import os
import hashlib
from unittest.mock import patch, MagicMock

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the password functions from app.py
from app import validate_password, hash_password, verify_password


class TestPasswordValidation(unittest.TestCase):
    """Test cases for password validation function"""
    
    def test_password_too_short(self):
        """Test password that is too short (less than 8 characters)"""
        result = validate_password("Abc1!")
        self.assertEqual(result, "Password must be at least 8 characters long")
    
    def test_password_too_long(self):
        """Test password that is too long (more than 12 characters)"""
        result = validate_password("Abcdefgh1!@#$")
        self.assertEqual(result, "Password must be no more than 12 characters long")
    
    def test_password_no_uppercase(self):
        """Test password without uppercase letter"""
        result = validate_password("abc123!@#")
        self.assertEqual(result, "Password must contain at least one uppercase letter")
    
    def test_password_no_lowercase(self):
        """Test password without lowercase letter"""
        result = validate_password("ABC123!@#")
        self.assertEqual(result, "Password must contain at least one lowercase letter")
    
    def test_password_no_digit(self):
        """Test password without digit"""
        result = validate_password("Abcdefg!@#")
        self.assertEqual(result, "Password must contain at least one number")
    
    def test_password_no_special_char(self):
        """Test password without special character"""
        result = validate_password("Abc123456")
        self.assertEqual(result, "Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
    
    def test_password_valid_minimum(self):
        """Test valid password with minimum requirements"""
        result = validate_password("Abc123!@")
        self.assertIsNone(result)
    
    def test_password_valid_maximum(self):
        """Test valid password with maximum length"""
        result = validate_password("Abc123!@#$%^")
        self.assertIsNone(result)
    
    def test_password_valid_middle_length(self):
        """Test valid password with middle length"""
        result = validate_password("Abc123!@#")
        self.assertIsNone(result)
    
    def test_password_empty_string(self):
        """Test empty password"""
        result = validate_password("")
        self.assertEqual(result, "Password must be at least 8 characters long")
    
    def test_password_none(self):
        """Test None password"""
        with self.assertRaises(TypeError):
            validate_password(None)
    
    def test_password_only_special_chars(self):
        """Test password with only special characters"""
        result = validate_password("!@#$%^&*()")
        self.assertEqual(result, "Password must contain at least one uppercase letter")
    
    def test_password_only_numbers(self):
        """Test password with only numbers"""
        result = validate_password("12345678")
        self.assertEqual(result, "Password must contain at least one uppercase letter")
    
    def test_password_missing_multiple_requirements(self):
        """Test password missing multiple requirements (should return first error)"""
        result = validate_password("abc")  # Too short, no uppercase, no digit, no special
        self.assertEqual(result, "Password must be at least 8 characters long")
    
    def test_password_edge_case_8_chars(self):
        """Test password with exactly 8 characters"""
        result = validate_password("Abc123!@")
        self.assertIsNone(result)
    
    def test_password_edge_case_12_chars(self):
        """Test password with exactly 12 characters"""
        result = validate_password("Abc123!@#$%^")
        self.assertIsNone(result)
    
    def test_password_13_chars(self):
        """Test password with 13 characters (over limit)"""
        result = validate_password("Abc123!@#$%^&")
        self.assertEqual(result, "Password must be no more than 12 characters long")
    
    def test_password_7_chars(self):
        """Test password with 7 characters (under limit)"""
        result = validate_password("Abc123!")
        self.assertEqual(result, "Password must be at least 8 characters long")


class TestPasswordHashing(unittest.TestCase):
    """Test cases for password hashing function"""
    
    def test_hash_password_returns_bytes(self):
        """Test that hash_password returns bytes"""
        password = "Test123!@#"
        hashed = hash_password(password)
        self.assertIsInstance(hashed, bytes)
    
    def test_hash_password_has_salt(self):
        """Test that hashed password includes salt (first 32 bytes)"""
        password = "Test123!@#"
        hashed = hash_password(password)
        self.assertEqual(len(hashed), 64)  # 32 bytes salt + 32 bytes hash
    
    def test_hash_password_different_salts(self):
        """Test that same password produces different hashes due to different salts"""
        password = "Test123!@#"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        self.assertNotEqual(hash1, hash2)
    
    def test_hash_password_hex_conversion(self):
        """Test that hex conversion works correctly"""
        password = "Test123!@#"
        hashed = hash_password(password)
        hex_string = hashed.hex()
        self.assertIsInstance(hex_string, str)
        self.assertEqual(len(hex_string), 128)  # 64 bytes * 2 hex chars per byte
    
    def test_hash_password_consistency(self):
        """Test that hashing the same password multiple times produces valid hashes"""
        password = "Test123!@#"
        for _ in range(5):
            hashed = hash_password(password)
            self.assertIsInstance(hashed, bytes)
            self.assertEqual(len(hashed), 64)


class TestPasswordVerification(unittest.TestCase):
    """Test cases for password verification function"""
    
    def test_verify_password_correct(self):
        """Test verification with correct password"""
        password = "Test123!@#"
        hashed = hash_password(password)
        hex_hashed = hashed.hex()
        
        result = verify_password(hex_hashed, password)
        self.assertTrue(result)
    
    def test_verify_password_incorrect(self):
        """Test verification with incorrect password"""
        password = "Test123!@#"
        wrong_password = "Wrong123!@#"
        hashed = hash_password(password)
        hex_hashed = hashed.hex()
        
        result = verify_password(hex_hashed, wrong_password)
        self.assertFalse(result)
    
    def test_verify_password_empty(self):
        """Test verification with empty password"""
        password = "Test123!@#"
        hashed = hash_password(password)
        hex_hashed = hashed.hex()
        
        result = verify_password(hex_hashed, "")
        self.assertFalse(result)
    
    def test_verify_password_none(self):
        """Test verification with None password"""
        password = "Test123!@#"
        hashed = hash_password(password)
        hex_hashed = hashed.hex()
        
        result = verify_password(hex_hashed, None)
        self.assertFalse(result)
    
    def test_verify_password_invalid_hex(self):
        """Test verification with invalid hex string"""
        result = verify_password("invalid_hex_string", "Test123!@#")
        self.assertFalse(result)
    
    def test_verify_password_short_hex(self):
        """Test verification with hex string that's too short"""
        result = verify_password("short", "Test123!@#")
        self.assertFalse(result)
    
    def test_verify_password_case_sensitive(self):
        """Test that password verification is case sensitive"""
        password = "Test123!@#"
        hashed = hash_password(password)
        hex_hashed = hashed.hex()
        
        # Test with different case
        result = verify_password(hex_hashed, "test123!@#")
        self.assertFalse(result)
    
    def test_verify_password_special_chars(self):
        """Test verification with special characters"""
        password = "Test123!@#$%^&*()"
        hashed = hash_password(password)
        hex_hashed = hashed.hex()
        
        result = verify_password(hex_hashed, password)
        self.assertTrue(result)
    
    def test_verify_password_unicode(self):
        """Test verification with unicode characters"""
        password = "Tëst123!@#"
        hashed = hash_password(password)
        hex_hashed = hashed.hex()
        
        result = verify_password(hex_hashed, password)
        self.assertTrue(result)


class TestPasswordIntegration(unittest.TestCase):
    """Integration tests for the complete password flow"""
    
    def test_complete_password_flow_valid(self):
        """Test complete flow: validate -> hash -> verify with valid password"""
        password = "Valid123!@#"
        
        # Step 1: Validate password
        validation_error = validate_password(password)
        self.assertIsNone(validation_error)
        
        # Step 2: Hash password
        hashed = hash_password(password)
        hex_hashed = hashed.hex()
        
        # Step 3: Verify password
        verification_result = verify_password(hex_hashed, password)
        self.assertTrue(verification_result)
    
    def test_complete_password_flow_invalid_validation(self):
        """Test complete flow with invalid password that fails validation"""
        password = "invalid"
        
        # Step 1: Validate password (should fail)
        validation_error = validate_password(password)
        self.assertIsNotNone(validation_error)
        self.assertIn("Password must be at least 8 characters long", validation_error)
    
    def test_password_storage_simulation(self):
        """Test simulating password storage and retrieval"""
        # Simulate user registration
        password = "UserPass123!"  # 12 characters - valid length
        
        # Validate password
        validation_error = validate_password(password)
        self.assertIsNone(validation_error)
        
        # Hash and store (simulate database storage)
        hashed = hash_password(password)
        stored_password = hashed.hex()
        
        # Simulate user login
        login_password = "UserPass123!"
        verification_result = verify_password(stored_password, login_password)
        self.assertTrue(verification_result)
        
        # Test wrong password
        wrong_password = "WrongPass123!"
        wrong_verification = verify_password(stored_password, wrong_password)
        self.assertFalse(wrong_verification)


class TestPasswordEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_password_exactly_8_chars_all_requirements(self):
        """Test password with exactly 8 characters meeting all requirements"""
        password = "Abc123!@"
        result = validate_password(password)
        self.assertIsNone(result)
    
    def test_password_exactly_12_chars_all_requirements(self):
        """Test password with exactly 12 characters meeting all requirements"""
        password = "Abc123!@#$%^"
        result = validate_password(password)
        self.assertIsNone(result)
    
    def test_password_special_chars_boundary(self):
        """Test all valid special characters"""
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        for char in special_chars:
            password = f"Abc123{char}x"  # 7 chars + special + x = 9 total
            result = validate_password(password)
            self.assertIsNone(result, f"Failed for special character: {char}")
    
    def test_password_unicode_special_chars(self):
        """Test password with unicode special characters (should fail)"""
        password = "Abc123€£¥"  # Unicode special chars not in allowed list
        result = validate_password(password)
        self.assertIsNotNone(result)
        self.assertIn("special character", result)
    
    def test_password_whitespace_only(self):
        """Test password with only whitespace"""
        password = "        "  # 8 spaces
        result = validate_password(password)
        self.assertIsNotNone(result)
        self.assertIn("uppercase", result)
    
    def test_password_newlines_and_tabs(self):
        """Test password with newlines and tabs"""
        password = "Abc123!\n\t"
        result = validate_password(password)
        # Newlines and tabs are not in the allowed special characters list
        # The password should be valid because it has all required characters
        # The \n and \t are not in the special chars list, but the ! is
        self.assertIsNone(result)


if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestPasswordValidation,
        TestPasswordHashing,
        TestPasswordVerification,
        TestPasswordIntegration,
        TestPasswordEdgeCases
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"TESTS RUN: {result.testsRun}")
    print(f"FAILURES: {len(result.failures)}")
    print(f"ERRORS: {len(result.errors)}")
    print(f"SUCCESS RATE: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
