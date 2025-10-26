#!/usr/bin/env python3
"""
C1 Unit Tests - App Functions
Tests individual app.py functions in complete isolation.
Based on actual functions in your codebase.
"""

import unittest
import sys
import os
import hashlib

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import individual functions for unit testing
from app import validate_password, hash_password, verify_password


class TestPasswordValidationUnit(unittest.TestCase):
    """C1 Unit tests for validate_password function from app.py"""
    
    def test_password_too_short(self):
        """Test password that is too short"""
        result = validate_password("Abc1!")
        self.assertEqual(result, "Password must be at least 8 characters long")
    
    def test_password_too_long(self):
        """Test password that is too long"""
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
    
    def test_password_valid(self):
        """Test valid password"""
        result = validate_password("Abc123!@")
        self.assertIsNone(result)
    
    def test_password_empty(self):
        """Test empty password"""
        result = validate_password("")
        self.assertEqual(result, "Password must be at least 8 characters long")


class TestPasswordHashingUnit(unittest.TestCase):
    """C1 Unit tests for hash_password function from app.py"""
    
    def test_hash_password_returns_string(self):
        """Test that hash_password returns hex string"""
        password = "Test123!@#"
        hashed = hash_password(password)
        self.assertIsInstance(hashed, str)
        self.assertEqual(len(hashed), 128)  # 64 bytes * 2 hex chars per byte
    
    def test_hash_password_different_salts(self):
        """Test that same password produces different hashes due to different salts"""
        password = "Test123!@#"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        self.assertNotEqual(hash1, hash2)


class TestPasswordVerificationUnit(unittest.TestCase):
    """C1 Unit tests for verify_password function from app.py"""
    
    def test_verify_password_correct(self):
        """Test verification with correct password"""
        password = "Test123!@#"
        hashed = hash_password(password)
        
        result = verify_password(hashed, password)
        self.assertTrue(result)
    
    def test_verify_password_incorrect(self):
        """Test verification with incorrect password"""
        password = "Test123!@#"
        wrong_password = "Wrong123!@#"
        hashed = hash_password(password)
        
        result = verify_password(hashed, wrong_password)
        self.assertFalse(result)
    
    def test_verify_password_invalid_hex(self):
        """Test verification with invalid hex string"""
        result = verify_password("invalid_hex_string", "Test123!@#")
        self.assertFalse(result)
    
    def test_verify_password_empty_stored(self):
        """Test verification with empty stored password"""
        result = verify_password("", "Test123!@#")
        self.assertFalse(result)
    
    def test_verify_password_empty_provided(self):
        """Test verification with empty provided password"""
        password = "Test123!@#"
        hashed = hash_password(password)
        result = verify_password(hashed, "")
        self.assertFalse(result)
    
    def test_verify_password_none_stored(self):
        """Test verification with None stored password"""
        result = verify_password(None, "Test123!@#")
        self.assertFalse(result)
    
    def test_verify_password_none_provided(self):
        """Test verification with None provided password"""
        password = "Test123!@#"
        hashed = hash_password(password)
        result = verify_password(hashed, None)
        self.assertFalse(result)
    
    def test_verify_password_short_hex(self):
        """Test verification with hex string that's too short"""
        result = verify_password("1234567890abcdef", "Test123!@#")
        self.assertFalse(result)
    
    def test_verify_password_unicode(self):
        """Test verification with unicode characters"""
        password = "Test123!@#测试"
        hashed = hash_password(password)
        result = verify_password(hashed, password)
        self.assertTrue(result)
    
    def test_verify_password_special_characters(self):
        """Test verification with various special characters"""
        password = "Test123!@#$%^&*()_+-=[]{}|;:,.<>?"
        hashed = hash_password(password)
        result = verify_password(hashed, password)
        self.assertTrue(result)


class TestPasswordValidationEdgeCases(unittest.TestCase):
    """Additional edge case tests for password validation"""
    
    def test_validate_password_boundary_length_8(self):
        """Test password exactly 8 characters (minimum)"""
        self.assertIsNone(validate_password("Test1!@#"))
    
    def test_validate_password_boundary_length_12(self):
        """Test password exactly 12 characters (maximum)"""
        self.assertIsNone(validate_password("Test123!@#$%"))
    
    def test_validate_password_length_7(self):
        """Test password 7 characters (just below minimum)"""
        result = validate_password("Test1!")
        self.assertEqual(result, "Password must be at least 8 characters long")
    
    def test_validate_password_length_13(self):
        """Test password 13 characters (just above maximum)"""
        result = validate_password("Test123!@#$%^")
        self.assertEqual(result, "Password must be no more than 12 characters long")
    
    def test_validate_password_only_uppercase(self):
        """Test password with only uppercase letters"""
        result = validate_password("TESTING")
        self.assertEqual(result, "Password must be at least 8 characters long")
    
    def test_validate_password_only_lowercase(self):
        """Test password with only lowercase letters"""
        result = validate_password("testing")
        self.assertEqual(result, "Password must be at least 8 characters long")
    
    def test_validate_password_only_numbers(self):
        """Test password with only numbers"""
        result = validate_password("12345678")
        self.assertEqual(result, "Password must contain at least one uppercase letter")
    
    def test_validate_password_only_special(self):
        """Test password with only special characters"""
        result = validate_password("!@#$%^&*")
        self.assertEqual(result, "Password must contain at least one uppercase letter")
    
    def test_validate_password_mixed_case_no_special(self):
        """Test password with mixed case but no special characters"""
        result = validate_password("Test1234")
        self.assertEqual(result, "Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
    
    def test_validate_password_mixed_case_no_numbers(self):
        """Test password with mixed case but no numbers"""
        result = validate_password("Test!@#$")
        self.assertEqual(result, "Password must contain at least one number")
    
    def test_validate_password_whitespace_only(self):
        """Test password with only whitespace characters"""
        result = validate_password("        ")
        self.assertEqual(result, "Password must contain at least one uppercase letter")
    
    def test_validate_password_tabs_and_spaces(self):
        """Test password with tabs and spaces"""
        result = validate_password("\t\t\t\t\t\t\t\t")
        self.assertEqual(result, "Password must contain at least one uppercase letter")
    
    def test_validate_password_newlines(self):
        """Test password with newline characters"""
        result = validate_password("Test\n123!")
        self.assertIsNone(result)  # Should be valid (8+ chars, has all requirements)
    
    def test_validate_password_unicode_characters(self):
        """Test password with unicode characters"""
        result = validate_password("Test123!测试")
        self.assertIsNone(result)  # Should be valid
    
    def test_validate_password_comprehensive_edge_cases(self):
        """Test password validation with comprehensive edge cases"""
        # Test boundary conditions
        boundary_tests = [
            ("Test1!@#", None),  # Exactly 8 characters
            ("Test123!@#$%", None),  # Exactly 12 characters
            ("Test1!", "Password must be at least 8 characters long"),  # 7 characters
            ("Test123!@#$%^", "Password must be no more than 12 characters long"),  # 13 characters
        ]
        
        for password, expected in boundary_tests:
            with self.subTest(password=password):
                result = validate_password(password)
                self.assertEqual(result, expected)
        
        # Test character requirement combinations
        requirement_tests = [
            ("TESTING!", "Password must contain at least one lowercase letter"),
            ("testing!1", "Password must contain at least one uppercase letter"),
            ("12345678!", "Password must contain at least one uppercase letter"),
            ("!@#$%^&*", "Password must contain at least one uppercase letter"),
            ("Test1234", "Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)"),
            ("Test!@#$", "Password must contain at least one number"),
        ]
        
        for password, expected in requirement_tests:
            with self.subTest(password=password):
                result = validate_password(password)
                self.assertEqual(result, expected)
        
        # Test special characters
        special_char_tests = [
            ("Test123!", None),  # Exclamation
            ("Test123@", None),  # At symbol
            ("Test123#", None),  # Hash
            ("Test123$", None),  # Dollar
            ("Test123%", None),  # Percent
            ("Test123^", None),  # Caret
            ("Test123&", None),  # Ampersand
            ("Test123*", None),  # Asterisk
            ("Test123(", None),  # Parentheses
            ("Test123)", None),  # Parentheses
            ("Test123_", None),  # Underscore
            ("Test123+", None),  # Plus
            ("Test123-", None),  # Minus
            ("Test123=", None),  # Equals
            ("Test123[", None),  # Square brackets
            ("Test123]", None),  # Square brackets
            ("Test123{", None),  # Curly brackets
            ("Test123}", None),  # Curly brackets
            ("Test123|", None),  # Pipe
            ("Test123;", None),  # Semicolon
            ("Test123:", None),  # Colon
            ("Test123,", None),  # Comma
            ("Test123.", None),  # Period
            ("Test123<", None),  # Less than
            ("Test123>", None),  # Greater than
            ("Test123?", None),  # Question mark
        ]
        
        for password, expected in special_char_tests:
            with self.subTest(password=password):
                result = validate_password(password)
                self.assertEqual(result, expected)
        
        # Test whitespace and control characters
        whitespace_tests = [
            ("        ", "Password must contain at least one uppercase letter"),  # Spaces
            ("\t\t\t\t\t\t\t\t", "Password must contain at least one uppercase letter"),  # Tabs
            ("Test\n123!", None),  # Newline (should be valid)
            ("Test\t123!", None),  # Tab (should be valid)
        ]
        
        for password, expected in whitespace_tests:
            with self.subTest(password=password):
                result = validate_password(password)
                self.assertEqual(result, expected)


if __name__ == '__main__':
    print("=" * 80)
    print("C1 UNIT TESTING - APP FUNCTIONS")
    print("=" * 80)
    print("Testing individual app.py functions in complete isolation")
    print("No external dependencies, no Flask app, no database")
    print("=" * 80)
    
    # Run with verbose output
    unittest.main(verbosity=2)
