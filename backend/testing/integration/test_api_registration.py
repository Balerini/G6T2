#!/usr/bin/env python3
"""
REAL Integration Tests - Registration Feature
Tests API endpoints with REAL database integration.
Tests Flask app + business logic + real database integration.
"""

import unittest
import sys
import os
import json
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set Firebase credentials with relative path
service_account_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'service-account.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path

from app import create_app
from firebase_utils import get_firestore_client


class TestRegistrationAPI(unittest.TestCase):
    """REAL Integration tests for registration API endpoint with real database"""
    
    def setUp(self):
        """Set up test client with REAL database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Use REAL Firestore client
        self.db = get_firestore_client()
        
        # Track test data for cleanup
        self.test_user_ids = []
        
        # Generate unique test emails to avoid conflicts
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def tearDown(self):
        """Clean up REAL test data from database"""
        # Clean up test users
        for user_id in self.test_user_ids:
            try:
                self.db.collection('Users').document(user_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete test user {user_id}: {e}")
        
        self.test_user_ids.clear()
        
    def test_registration_success(self):
        """Test successful user registration via API with REAL database"""
        # Real test data with unique email
        registration_data = {
            "name": "John Doe",
            "email": f"john.doe.{self.timestamp}@company.com",
            "password": "TestPass123!",
            "division_name": "Sales"
        }
        
        response = self.client.post('/register', 
                                  data=json.dumps(registration_data),
                                  content_type='application/json')
        
        # Assertions
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertTrue(response_data['ok'])
        self.assertEqual(response_data['message'], 'Registration successful')
        self.assertIn('user', response_data)
        self.assertEqual(response_data['user']['name'], 'John Doe')
        self.assertEqual(response_data['user']['email'], registration_data['email'])
        self.assertEqual(response_data['user']['role_name'], 'Staff')
        self.assertEqual(response_data['user']['division_name'], 'Sales')
        
        # Track user for cleanup
        if 'user' in response_data and 'id' in response_data['user']:
            self.test_user_ids.append(response_data['user']['id'])
    
    def test_registration_missing_fields(self):
        """Test registration with missing required fields via API"""
        # Test missing name
        data = {
            "email": f"test.{self.timestamp}@company.com",
            "password": "TestPass123!",
            "division_name": "Sales"
        }
        
        response = self.client.post('/register',
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertFalse(response_data['ok'])
        self.assertEqual(response_data['error'], 'All fields are required')
    
    def test_registration_short_name(self):
        """Test registration with name too short via API"""
        data = {
            "name": "J",  # Too short
            "email": f"test.{self.timestamp}@company.com",
            "password": "TestPass123!",
            "division_name": "Sales"
        }
        
        response = self.client.post('/register',
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertFalse(response_data['ok'])
        self.assertEqual(response_data['error'], 'Name must be at least 2 characters')
    
    def test_registration_invalid_password(self):
        """Test registration with invalid password via API"""
        data = {
            "name": "John Doe",
            "email": f"test.{self.timestamp}@company.com",
            "password": "weak",  # Invalid password
            "division_name": "Sales"
        }
        
        response = self.client.post('/register',
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertFalse(response_data['ok'])
        self.assertIn('Password must be at least 8 characters long', response_data['error'])
    
    def test_registration_invalid_department(self):
        """Test registration with invalid department via API"""
        data = {
            "name": "John Doe",
            "email": f"test.{self.timestamp}@company.com",
            "password": "TestPass123!",
            "division_name": "InvalidDepartment"
        }
        
        response = self.client.post('/register',
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertFalse(response_data['ok'])
        self.assertEqual(response_data['error'], 'Invalid department selected')
    
    def test_registration_duplicate_email(self):
        """Test registration with existing email via API with REAL database"""
        # First, create a user
        registration_data = {
            "name": "First User",
            "email": f"duplicate.{self.timestamp}@company.com",
            "password": "TestPass123!",
            "division_name": "Sales"
        }
        
        response1 = self.client.post('/register',
                                   data=json.dumps(registration_data),
                                   content_type='application/json')
        
        self.assertEqual(response1.status_code, 201)
        response1_data = json.loads(response1.data)
        if 'user' in response1_data and 'id' in response1_data['user']:
            self.test_user_ids.append(response1_data['user']['id'])
        
        # Now try to register with the same email
        duplicate_data = {
            "name": "Second User",
            "email": f"duplicate.{self.timestamp}@company.com",  # Same email
            "password": "TestPass123!",
            "division_name": "Sales"
        }
        
        response2 = self.client.post('/register',
                                   data=json.dumps(duplicate_data),
                                   content_type='application/json')
        
        self.assertEqual(response2.status_code, 409)
        response2_data = json.loads(response2.data)
        self.assertFalse(response2_data['ok'])
        self.assertEqual(response2_data['error'], 'Email already exists')
    
    def test_registration_role_assignment_director(self):
        """Test role assignment for director email via API with REAL database"""
        data = {
            "name": "Director Name",
            "email": f"director.{self.timestamp}@company.com",
            "password": "TestPass123!",
            "division_name": "Sales"
        }
        
        response = self.client.post('/register',
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['user']['role_name'], 'Director')
        self.assertEqual(response_data['user']['role_num'], 2)
        
        # Track user for cleanup
        if 'user' in response_data and 'id' in response_data['user']:
            self.test_user_ids.append(response_data['user']['id'])
    
    def test_registration_role_assignment_manager(self):
        """Test role assignment for manager email via API with REAL database"""
        data = {
            "name": "Manager Name",
            "email": f"manager.{self.timestamp}@company.com",
            "password": "TestPass123!",
            "division_name": "Sales"
        }
        
        response = self.client.post('/register',
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['user']['role_name'], 'Manager')
        self.assertEqual(response_data['user']['role_num'], 3)
        
        # Track user for cleanup
        if 'user' in response_data and 'id' in response_data['user']:
            self.test_user_ids.append(response_data['user']['id'])
    
    def test_registration_role_assignment_staff(self):
        """Test role assignment for staff email via API with REAL database"""
        data = {
            "name": "Staff Name",
            "email": f"staff.{self.timestamp}@company.com",
            "password": "TestPass123!",
            "division_name": "Sales"
        }
        
        response = self.client.post('/register',
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['user']['role_name'], 'Staff')
        self.assertEqual(response_data['user']['role_num'], 4)
        
        # Track user for cleanup
        if 'user' in response_data and 'id' in response_data['user']:
            self.test_user_ids.append(response_data['user']['id'])
    
    def test_registration_empty_request(self):
        """Test registration with empty request body via API"""
        response = self.client.post('/register',
                                  data=json.dumps({}),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertFalse(response_data['ok'])
        self.assertEqual(response_data['error'], 'All fields are required')
    
    def test_registration_invalid_json(self):
        """Test registration with invalid JSON via API"""
        response = self.client.post('/register',
                                  data="invalid json",
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertFalse(response_data['ok'])
        self.assertEqual(response_data['error'], 'All fields are required')


class TestRegistrationIntegration(unittest.TestCase):
    """REAL Integration tests for registration with password functions"""
    
    def setUp(self):
        """Set up test client with REAL database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Use REAL Firestore client
        self.db = get_firestore_client()
        
        # Track test data for cleanup
        self.test_user_ids = []
        
        # Generate unique test emails to avoid conflicts
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def tearDown(self):
        """Clean up REAL test data from database"""
        # Clean up test users
        for user_id in self.test_user_ids:
            try:
                self.db.collection('Users').document(user_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete test user {user_id}: {e}")
        
        self.test_user_ids.clear()
    
    def test_registration_password_validation_integration(self):
        """Test that password validation is properly integrated via API with REAL database"""
        # Test various invalid passwords
        invalid_passwords = [
            "short", 
            "nouppercase123!", 
            "NOLOWERCASE123!", 
            "NoNumbers!",     
            "NoSpecial123"     
        ]
        
        for i, password in enumerate(invalid_passwords):
            data = {
                "name": "John Doe",
                "email": f"test{i}.{self.timestamp}@company.com",
                "password": password,
                "division_name": "Sales"
            }
            
            response = self.client.post('/register',
                                      data=json.dumps(data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 400)
            response_data = json.loads(response.data)
            self.assertFalse(response_data['ok'])
            self.assertIn('Password', response_data['error'])
    
    def test_registration_password_hashing_integration(self):
        """Test that password hashing is properly integrated via API with REAL database"""
        data = {
            "name": "John Doe",
            "email": f"hash.test.{self.timestamp}@company.com",
            "password": "TestPass123!",
            "division_name": "Sales"
        }
        
        response = self.client.post('/register',
                                  data=json.dumps(data),
                                  content_type='application/json')
        
        # Verify registration was successful
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertTrue(response_data['ok'])
        
        # Track user for cleanup
        if 'user' in response_data and 'id' in response_data['user']:
            self.test_user_ids.append(response_data['user']['id'])
            
            # Verify password was hashed in database
            user_doc = self.db.collection('Users').document(response_data['user']['id']).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                stored_password = user_data.get('password', '')
                # Password should be hashed (not plain text)
                self.assertNotEqual(stored_password, 'TestPass123!')
                self.assertTrue(len(stored_password) > 50)  # bcrypt hashes are long


if __name__ == '__main__':
    print("=" * 80)
    print("REAL INTEGRATION TESTING - REGISTRATION FEATURE")
    print("=" * 80)
    print("Testing API endpoints with REAL database integration")
    print("Tests Flask app + business logic + real database")
    print("=" * 80)
    
    # Run with verbose output
    unittest.main(verbosity=2)