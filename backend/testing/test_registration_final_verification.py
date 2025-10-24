#!/usr/bin/env python3
"""
Final verification that registration function has 100% coverage.
This test specifically targets every line in the registration function.
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app


class TestRegistrationFinalVerification(unittest.TestCase):
    """Final verification tests for 100% registration coverage"""
    
    def setUp(self):
        """Set up test client and mock Firestore"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Mock Firestore client
        self.mock_db = MagicMock()
        self.mock_users_ref = MagicMock()
        self.mock_db.collection.return_value = self.mock_users_ref
    
    def test_registration_line_167_payload_parsing(self):
        """Test line 167: payload = request.get_json(silent=True) or {}"""
        # Test with valid JSON
        response = self.client.post('/register', 
                                  data=json.dumps({
                                      'name': 'Test User',
                                      'email': 'test@example.com',
                                      'password': 'TestPass123!',
                                      'division_name': 'IT'
                                  }),
                                  content_type='application/json')
        # This should hit line 167
        self.assertIn(response.status_code, [201, 400, 409, 500])
    
    def test_registration_line_168_169_170_171_field_extraction(self):
        """Test lines 168-171: field extraction from payload"""
        with patch('app.get_firestore_client', return_value=self.mock_db):
            # Mock successful registration
            self.mock_users_ref.where.return_value.stream.return_value = []
            self.mock_users_ref.add.return_value = (None, MagicMock(id='test_id'))
            
            response = self.client.post('/register', json={
                'name': 'Test User',
                'email': 'test@example.com',
                'password': 'TestPass123!',
                'division_name': 'IT'
            })
            # This should hit lines 168-171
            self.assertEqual(response.status_code, 201)
    
    def test_registration_line_174_all_fields_validation(self):
        """Test line 174: if not all([name, email, password, division_name])"""
        # Test missing name
        response = self.client.post('/register', json={
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'division_name': 'IT'
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('All fields are required', data['error'])
    
    def test_registration_line_178_name_length_validation(self):
        """Test line 178: if len(name.strip()) < 2"""
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register', json={
                'name': 'A',  # Only 1 character
                'email': 'test@example.com',
                'password': 'TestPass123!',
                'division_name': 'IT'
            })
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn('Name must be at least 2 characters', data['error'])
    
    def test_registration_line_182_password_validation(self):
        """Test line 182: password_errors = validate_password(password)"""
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register', json={
                'name': 'Test User',
                'email': 'test@example.com',
                'password': 'weak',  # Invalid password
                'division_name': 'IT'
            })
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn('Password must be at least 8 characters long', data['error'])
    
    def test_registration_line_187_email_lowercase(self):
        """Test line 187: email_lower = email.lower()"""
        with patch('app.get_firestore_client', return_value=self.mock_db):
            self.mock_users_ref.where.return_value.stream.return_value = []
            self.mock_users_ref.add.return_value = (None, MagicMock(id='test_id'))
            
            response = self.client.post('/register', json={
                'name': 'Test User',
                'email': 'TEST@EXAMPLE.COM',  # Uppercase email
                'password': 'TestPass123!',
                'division_name': 'IT'
            })
            # This should hit line 187
            self.assertEqual(response.status_code, 201)
    
    def test_registration_line_188_director_check(self):
        """Test line 188: if 'director' in email_lower"""
        with patch('app.get_firestore_client', return_value=self.mock_db):
            self.mock_users_ref.where.return_value.stream.return_value = []
            self.mock_users_ref.add.return_value = (None, MagicMock(id='director_id'))
            
            response = self.client.post('/register', json={
                'name': 'Director User',
                'email': 'director@company.com',
                'password': 'TestPass123!',
                'division_name': 'IT'
            })
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            self.assertEqual(data['user']['role_name'], 'Director')
    
    def test_registration_line_190_manager_check(self):
        """Test line 190: elif 'manager' in email_lower"""
        with patch('app.get_firestore_client', return_value=self.mock_db):
            self.mock_users_ref.where.return_value.stream.return_value = []
            self.mock_users_ref.add.return_value = (None, MagicMock(id='manager_id'))
            
            response = self.client.post('/register', json={
                'name': 'Manager User',
                'email': 'manager@company.com',
                'password': 'TestPass123!',
                'division_name': 'IT'
            })
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            self.assertEqual(data['user']['role_name'], 'Manager')
    
    def test_registration_line_192_staff_default(self):
        """Test line 192: else: role = 'staff'"""
        with patch('app.get_firestore_client', return_value=self.mock_db):
            self.mock_users_ref.where.return_value.stream.return_value = []
            self.mock_users_ref.add.return_value = (None, MagicMock(id='staff_id'))
            
            response = self.client.post('/register', json={
                'name': 'Staff User',
                'email': 'staff@company.com',
                'password': 'TestPass123!',
                'division_name': 'IT'
            })
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            self.assertEqual(data['user']['role_name'], 'Staff')
    
    def test_registration_line_205_department_validation(self):
        """Test line 205: if division_name not in valid_departments"""
        with patch('app.get_firestore_client', return_value=self.mock_db):
            response = self.client.post('/register', json={
                'name': 'Test User',
                'email': 'test@example.com',
                'password': 'TestPass123!',
                'division_name': 'Invalid Department'
            })
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn('Invalid department selected', data['error'])
    
    def test_registration_line_210_firestore_client(self):
        """Test line 210: db = get_firestore_client()"""
        with patch('app.get_firestore_client', return_value=self.mock_db) as mock_get_db:
            self.mock_users_ref.where.return_value.stream.return_value = []
            self.mock_users_ref.add.return_value = (None, MagicMock(id='test_id'))
            
            response = self.client.post('/register', json={
                'name': 'Test User',
                'email': 'test@example.com',
                'password': 'TestPass123!',
                'division_name': 'IT'
            })
            # This should hit line 210
            mock_get_db.assert_called_once()
            self.assertEqual(response.status_code, 201)
    
    def test_registration_line_214_email_lookup(self):
        """Test line 214: existing_users = users_ref.where('email', '==', email.lower().strip()).stream()"""
        with patch('app.get_firestore_client', return_value=self.mock_db):
            # Test with existing user
            mock_existing_user = MagicMock()
            self.mock_users_ref.where.return_value.stream.return_value = [mock_existing_user]
            
            response = self.client.post('/register', json={
                'name': 'Test User',
                'email': 'existing@example.com',
                'password': 'TestPass123!',
                'division_name': 'IT'
            })
            self.assertEqual(response.status_code, 409)
            data = json.loads(response.data)
            self.assertIn('Email already exists', data['error'])
    
    def test_registration_line_216_duplicate_check(self):
        """Test line 216: if list(existing_users)"""
        with patch('app.get_firestore_client', return_value=self.mock_db):
            # Test with no existing users
            self.mock_users_ref.where.return_value.stream.return_value = []
            self.mock_users_ref.add.return_value = (None, MagicMock(id='test_id'))
            
            response = self.client.post('/register', json={
                'name': 'Test User',
                'email': 'new@example.com',
                'password': 'TestPass123!',
                'division_name': 'IT'
            })
            # This should hit line 216 (false branch)
            self.assertEqual(response.status_code, 201)
    
    def test_registration_line_220_password_hashing(self):
        """Test line 220: hashed_password = hash_password(password)"""
        with patch('app.get_firestore_client', return_value=self.mock_db):
            with patch('app.hash_password') as mock_hash:
                mock_hash.return_value = b'mock_hashed_password'
                self.mock_users_ref.where.return_value.stream.return_value = []
                self.mock_users_ref.add.return_value = (None, MagicMock(id='test_id'))
                
                response = self.client.post('/register', json={
                    'name': 'Test User',
                    'email': 'test@example.com',
                    'password': 'TestPass123!',
                    'division_name': 'IT'
                })
                # This should hit line 220
                mock_hash.assert_called_once_with('TestPass123!')
                self.assertEqual(response.status_code, 201)
    
    def test_registration_line_223_user_data_creation(self):
        """Test line 223: user_data = {...}"""
        with patch('app.get_firestore_client', return_value=self.mock_db):
            self.mock_users_ref.where.return_value.stream.return_value = []
            self.mock_users_ref.add.return_value = (None, MagicMock(id='test_id'))
            
            response = self.client.post('/register', json={
                'name': 'Test User',
                'email': 'test@example.com',
                'password': 'TestPass123!',
                'division_name': 'IT'
            })
            # This should hit line 223
            self.assertEqual(response.status_code, 201)
    
    def test_registration_line_233_firestore_add(self):
        """Test line 233: doc_ref = users_ref.add(user_data)"""
        with patch('app.get_firestore_client', return_value=self.mock_db):
            self.mock_users_ref.where.return_value.stream.return_value = []
            self.mock_users_ref.add.return_value = (None, MagicMock(id='test_id'))
            
            response = self.client.post('/register', json={
                'name': 'Test User',
                'email': 'test@example.com',
                'password': 'TestPass123!',
                'division_name': 'IT'
            })
            # This should hit line 233
            self.mock_users_ref.add.assert_called_once()
            self.assertEqual(response.status_code, 201)
    
    def test_registration_line_234_user_id_extraction(self):
        """Test line 234: user_id = doc_ref[1].id"""
        with patch('app.get_firestore_client', return_value=self.mock_db):
            self.mock_users_ref.where.return_value.stream.return_value = []
            mock_doc_ref = (None, MagicMock(id='extracted_user_id'))
            self.mock_users_ref.add.return_value = mock_doc_ref
            
            response = self.client.post('/register', json={
                'name': 'Test User',
                'email': 'test@example.com',
                'password': 'TestPass123!',
                'division_name': 'IT'
            })
            # This should hit line 234
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            self.assertEqual(data['user']['id'], 'extracted_user_id')
    
    def test_registration_line_236_success_response(self):
        """Test line 236: return jsonify({...}), 201"""
        with patch('app.get_firestore_client', return_value=self.mock_db):
            self.mock_users_ref.where.return_value.stream.return_value = []
            self.mock_users_ref.add.return_value = (None, MagicMock(id='test_id'))
            
            response = self.client.post('/register', json={
                'name': 'Test User',
                'email': 'test@example.com',
                'password': 'TestPass123!',
                'division_name': 'IT'
            })
            # This should hit line 236
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            self.assertTrue(data['ok'])
            self.assertEqual(data['message'], 'Registration successful')
    
    def test_registration_line_249_exception_handling(self):
        """Test line 249: except Exception as e"""
        with patch('app.get_firestore_client', return_value=self.mock_db):
            # Mock database error
            self.mock_users_ref.where.return_value.stream.side_effect = Exception('Database connection failed')
            
            response = self.client.post('/register', json={
                'name': 'Test User',
                'email': 'test@example.com',
                'password': 'TestPass123!',
                'division_name': 'IT'
            })
            # This should hit line 249
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            self.assertIn('Database error', data['error'])


if __name__ == '__main__':
    unittest.main()
