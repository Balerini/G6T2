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
    
    def test_hash_password_returns_bytes(self):
        """Test that hash_password returns bytes"""
        password = "Test123!@#"
        hashed = hash_password(password)
        self.assertIsInstance(hashed, bytes)
        self.assertEqual(len(hashed), 64)  # 32 bytes salt + 32 bytes hash
    
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
    
    def test_verify_password_invalid_hex(self):
        """Test verification with invalid hex string"""
        result = verify_password("invalid_hex_string", "Test123!@#")
        self.assertFalse(result)


if __name__ == '__main__':
    print("=" * 80)
    print("C1 UNIT TESTING - APP FUNCTIONS")
    print("=" * 80)
    print("Testing individual app.py functions in complete isolation")
    print("No external dependencies, no Flask app, no database")
    print("=" * 80)
    
    # Run with verbose output
    unittest.main(verbosity=2)
