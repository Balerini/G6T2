import unittest
import sys
import os


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import *


class TestBasicFunctionality(unittest.TestCase):
    """Basic unit tests for core functionality"""
    
    def test_app_import(self):
        """Test that app module can be imported"""
        self.assertTrue(True, "App module imported successfully")
    
    def test_password_validation_exists(self):
        """Test that password validation function exists"""
        self.assertTrue(callable(validate_password), "validate_password function exists")
    
    def test_password_hashing_exists(self):
        """Test that password hashing function exists"""
        self.assertTrue(callable(hash_password), "hash_password function exists")
    
    def test_password_verification_exists(self):
        """Test that password verification function exists"""
        self.assertTrue(callable(verify_password), "verify_password function exists")


# Import the comprehensive password tests
from testing.auth.test_password_unit import *

# Import the registration API tests
from testing.test_registration_api import *

# Import the reset password tests
from testing.auth.test_reset_password_unit import *


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
