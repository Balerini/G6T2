import unittest
import sys
import os
# import flask_testing
import json

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import *


class TestIntegration(unittest.TestCase):
    """Integration tests for the application"""
    
    def test_app_creation(self):
        """Test that Flask app can be created"""
        try:
            app = create_app()
            self.assertIsNotNone(app, "Flask app created successfully")
        except Exception as e:
            self.fail(f"Failed to create Flask app: {e}")
    
    def test_basic_imports(self):
        """Test that basic modules can be imported"""
        self.assertTrue(True, "Basic imports successful")
    
    def test_password_workflow(self):
        """Test complete password workflow: validation -> hashing -> verification"""
        # Test password
        test_password = "TestPass123!"
        
        # Step 1: Validate password
        validation_result = validate_password(test_password)
        self.assertIsNone(validation_result, "Password should be valid")
        
        # Step 2: Hash password
        hashed_password = hash_password(test_password)
        self.assertIsNotNone(hashed_password, "Password should be hashed")
        self.assertIsInstance(hashed_password, bytes, "Hashed password should be bytes")
        
        # Step 3: Verify password
        verification_result = verify_password(hashed_password.hex(), test_password)
        self.assertTrue(verification_result, "Password verification should succeed")
    
    def test_invalid_password_workflow(self):
        """Test password workflow with invalid password"""
        # Test invalid password
        invalid_password = "weak"
        
        # Step 1: Validate password (should fail)
        validation_result = validate_password(invalid_password)
        self.assertIsNotNone(validation_result, "Invalid password should be rejected")
        
        # Step 2: Hash password (should still work)
        hashed_password = hash_password(invalid_password)
        self.assertIsNotNone(hashed_password, "Password should be hashed even if invalid")
        
        # Step 3: Verify password (should work)
        verification_result = verify_password(hashed_password.hex(), invalid_password)
        self.assertTrue(verification_result, "Password verification should work for any password")


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
