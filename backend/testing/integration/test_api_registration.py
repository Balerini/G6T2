#!/usr/bin/env python3
"""
API Integration Tests - Registration Feature
Tests API endpoints with mocked dependencies.
Tests Flask app + business logic integration.
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import create_app


class TestRegistrationAPI(unittest.TestCase):
    """API Integration tests for registration API endpoint"""
    
    def setUp(self):
        """Set up test client and mock Firestore"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Mock Firestore client
        self.mock_db = MagicMock()
        self.mock_users_ref = MagicMock()
        self.mock_db.collection.return_value = self.mock_users_ref
        
    def test_registration_success(self):
        """Test successful user registration via API"""
        # Mock data
        registration_data = {
            "name": "John Doe",
            "email": "john.doe@company.com",
            "password": "TestPass123!",
            "division_name": "Sales"
        }
        
        # Mock Firestore responses
        self.mock_users_ref.where.return_value.stream.return_value = []  # No existing user
        self.mock_users_ref.add.return_value = (None, MagicMock(id="test_user_id"))
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
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
        self.assertEqual(response_data['user']['email'], 'john.doe@company.com')
        self.assertEqual(response_data['user']['role_name'], 'Staff')
        self.assertEqual(response_data['user']['division_name'], 'Sales')
    
    def test_registration_missing_fields(self):
        """Test registration with missing required fields via API"""
        # Test missing name
        data = {
            "email": "test@company.com",
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
            "email": "test@company.com",
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
            "email": "test@company.com",
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
            "email": "test@company.com",
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
        """Test registration with existing email via API"""
        data = {
            "name": "John Doe",
            "email": "existing@company.com",
            "password": "TestPass123!",
            "division_name": "Sales"
        }
        
        # Mock existing user
        mock_user = MagicMock()
        self.mock_users_ref.where.return_value.stream.return_value = [mock_user]
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register',
                                      data=json.dumps(data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 409)
        response_data = json.loads(response.data)
        self.assertFalse(response_data['ok'])
        self.assertEqual(response_data['error'], 'Email already exists')
    
    def test_registration_role_assignment_director(self):
        """Test role assignment for director email via API"""
        data = {
            "name": "Director Name",
            "email": "director@company.com",
            "password": "TestPass123!",
            "division_name": "Sales"
        }
        
        # Mock no existing user
        self.mock_users_ref.where.return_value.stream.return_value = []
        self.mock_users_ref.add.return_value = (None, MagicMock(id="test_user_id"))
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register',
                                      data=json.dumps(data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['user']['role_name'], 'Director')
        self.assertEqual(response_data['user']['role_num'], 2)
    
    def test_registration_role_assignment_manager(self):
        """Test role assignment for manager email via API"""
        data = {
            "name": "Manager Name",
            "email": "manager@company.com",
            "password": "TestPass123!",
            "division_name": "Sales"
        }
        
        # Mock no existing user
        self.mock_users_ref.where.return_value.stream.return_value = []
        self.mock_users_ref.add.return_value = (None, MagicMock(id="test_user_id"))
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register',
                                      data=json.dumps(data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['user']['role_name'], 'Manager')
        self.assertEqual(response_data['user']['role_num'], 3)
    
    def test_registration_role_assignment_staff(self):
        """Test role assignment for staff email via API"""
        data = {
            "name": "Staff Name",
            "email": "staff@company.com",
            "password": "TestPass123!",
            "division_name": "Sales"
        }
        
        # Mock no existing user
        self.mock_users_ref.where.return_value.stream.return_value = []
        self.mock_users_ref.add.return_value = (None, MagicMock(id="test_user_id"))
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register',
                                      data=json.dumps(data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['user']['role_name'], 'Staff')
        self.assertEqual(response_data['user']['role_num'], 4)
    
    def test_registration_database_error(self):
        """Test registration with database error via API"""
        data = {
            "name": "John Doe",
            "email": "test@company.com",
            "password": "TestPass123!",
            "division_name": "Sales"
        }
        
        # Mock database error
        self.mock_users_ref.where.return_value.stream.side_effect = Exception("Database error")
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register',
                                      data=json.dumps(data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.data)
        self.assertFalse(response_data['ok'])
        self.assertIn('Database error', response_data['error'])
    
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
    """API Integration tests for registration with password functions"""
    
    def setUp(self):
        """Set up test client"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_registration_password_validation_integration(self):
        """Test that password validation is properly integrated via API"""
        # Test various invalid passwords
        invalid_passwords = [
            "short", 
            "nouppercase123!", 
            "NOLOWERCASE123!", 
            "NoNumbers!",     
            "NoSpecial123"     
        ]
        
        for password in invalid_passwords:
            data = {
                "name": "John Doe",
                "email": f"test{password}@company.com",
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
        """Test that password hashing is properly integrated via API"""
        data = {
            "name": "John Doe",
            "email": "test@company.com",
            "password": "TestPass123!",
            "division_name": "Sales"
        }
        
        # Mock Firestore
        mock_db = MagicMock()
        mock_users_ref = MagicMock()
        mock_db.collection.return_value = mock_users_ref
        mock_users_ref.where.return_value.stream.return_value = []  # No existing user
        mock_users_ref.add.return_value = (None, MagicMock(id="test_user_id"))
        
        with patch('app.get_firestore_client', return_value=mock_db):
            response = self.client.post('/register',
                                      data=json.dumps(data),
                                      content_type='application/json')
        
        # Verify that add was called with hashed password
        self.assertEqual(response.status_code, 201)
        call_args = mock_users_ref.add.call_args[0][0]
        self.assertIn('password', call_args)
        # Password should be hashed (hex string, not plain text)
        self.assertNotEqual(call_args['password'], 'TestPass123!')
        self.assertTrue(len(call_args['password']) > 50)


if __name__ == '__main__':
    print("=" * 80)
    print("API INTEGRATION TESTING - REGISTRATION FEATURE")
    print("=" * 80)
    print("Testing API endpoints with mocked dependencies")
    print("Tests Flask app + business logic integration")
    print("=" * 80)
    
    # Run with verbose output
    unittest.main(verbosity=2)
