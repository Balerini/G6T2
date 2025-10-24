#!/usr/bin/env python3
"""
Additional registration tests to achieve 100% coverage of the registration function.
These tests cover the missing lines identified in coverage analysis.
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app


class TestRegistrationCoverage(unittest.TestCase):
    """Test cases to achieve 100% coverage of registration function"""
    
    def setUp(self):
        """Set up test client and mock Firestore"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Mock Firestore client
        self.mock_db = MagicMock()
        self.mock_users_ref = MagicMock()
        self.mock_db.collection.return_value = self.mock_users_ref
        
    def test_registration_missing_name_field(self):
        """Test registration with missing name field (line 175)"""
        registration_data = {
            "email": "test@example.com",
            "password": "TestPass123!",
            "division_name": "IT"
            # Missing 'name' field
        }
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register', 
                                      data=json.dumps(registration_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])
        self.assertIn('All fields are required', data['error'])
    
    def test_registration_missing_email_field(self):
        """Test registration with missing email field (line 175)"""
        registration_data = {
            "name": "Test User",
            "password": "TestPass123!",
            "division_name": "IT"
            # Missing 'email' field
        }
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register', 
                                      data=json.dumps(registration_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])
        self.assertIn('All fields are required', data['error'])
    
    def test_registration_missing_password_field(self):
        """Test registration with missing password field (line 175)"""
        registration_data = {
            "name": "Test User",
            "email": "test@example.com",
            "division_name": "IT"
            # Missing 'password' field
        }
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register', 
                                      data=json.dumps(registration_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])
        self.assertIn('All fields are required', data['error'])
    
    def test_registration_missing_division_field(self):
        """Test registration with missing division field (line 175)"""
        registration_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "TestPass123!"
            # Missing 'division_name' field
        }
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register', 
                                      data=json.dumps(registration_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])
        self.assertIn('All fields are required', data['error'])
    
    def test_registration_name_too_short(self):
        """Test registration with name too short (line 179)"""
        registration_data = {
            "name": "A",  # Only 1 character
            "email": "test@example.com",
            "password": "TestPass123!",
            "division_name": "IT"
        }
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register', 
                                      data=json.dumps(registration_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])
        self.assertIn('Name must be at least 2 characters', data['error'])
    
    def test_registration_invalid_password_validation(self):
        """Test registration with invalid password (line 184)"""
        registration_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "weak",  # Invalid password
            "division_name": "IT"
        }
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register', 
                                      data=json.dumps(registration_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])
        self.assertIn('Password must be at least 8 characters long', data['error'])
    
    def test_registration_director_role_assignment(self):
        """Test registration with director email (line 189)"""
        registration_data = {
            "name": "Director User",
            "email": "director@company.com",  # Contains 'director'
            "password": "TestPass123!",
            "division_name": "IT"
        }
        
        # Mock Firestore responses
        self.mock_users_ref.where.return_value.stream.return_value = []  # No existing user
        self.mock_users_ref.add.return_value = (None, MagicMock(id="director_user_id"))
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register', 
                                      data=json.dumps(registration_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['ok'])
        self.assertEqual(data['user']['role_name'], 'Director')
        self.assertEqual(data['user']['role_num'], 2)
    
    def test_registration_manager_role_assignment(self):
        """Test registration with manager email (line 191)"""
        registration_data = {
            "name": "Manager User",
            "email": "manager@company.com",  # Contains 'manager'
            "password": "TestPass123!",
            "division_name": "IT"
        }
        
        # Mock Firestore responses
        self.mock_users_ref.where.return_value.stream.return_value = []  # No existing user
        self.mock_users_ref.add.return_value = (None, MagicMock(id="manager_user_id"))
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register', 
                                      data=json.dumps(registration_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['ok'])
        self.assertEqual(data['user']['role_name'], 'Manager')
        self.assertEqual(data['user']['role_num'], 3)
    
    def test_registration_invalid_department(self):
        """Test registration with invalid department (line 206)"""
        registration_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "TestPass123!",
            "division_name": "Invalid Department"  # Not in valid list
        }
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register', 
                                      data=json.dumps(registration_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])
        self.assertIn('Invalid department selected', data['error'])
    
    def test_registration_duplicate_email_exists(self):
        """Test registration with existing email (line 217)"""
        registration_data = {
            "name": "Test User",
            "email": "existing@example.com",
            "password": "TestPass123!",
            "division_name": "IT"
        }
        
        # Mock existing user found
        mock_existing_user = MagicMock()
        self.mock_users_ref.where.return_value.stream.return_value = [mock_existing_user]
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register', 
                                      data=json.dumps(registration_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])
        self.assertIn('Email already exists', data['error'])
    
    def test_registration_database_error(self):
        """Test registration with database error (lines 249-250)"""
        registration_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "TestPass123!",
            "division_name": "IT"
        }
        
        # Mock database error
        self.mock_users_ref.where.return_value.stream.side_effect = Exception("Database connection failed")
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register', 
                                      data=json.dumps(registration_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])
        self.assertIn('Database error', data['error'])
    
    def test_registration_successful_staff_role(self):
        """Test successful registration with staff role (default case)"""
        registration_data = {
            "name": "Staff User",
            "email": "staff@company.com",  # No 'director' or 'manager' in email
            "password": "TestPass123!",
            "division_name": "IT"
        }
        
        # Mock Firestore responses
        self.mock_users_ref.where.return_value.stream.return_value = []  # No existing user
        self.mock_users_ref.add.return_value = (None, MagicMock(id="staff_user_id"))
        
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register', 
                                      data=json.dumps(registration_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['ok'])
        self.assertEqual(data['user']['role_name'], 'Staff')
        self.assertEqual(data['user']['role_num'], 4)


if __name__ == '__main__':
    unittest.main()
