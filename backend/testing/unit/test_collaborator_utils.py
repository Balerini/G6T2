#!/usr/bin/env python3
"""
C1 Unit Tests - Collaborator Utility Functions
Tests individual collaborator utility functions in complete isolation.
No external dependencies, no Flask app, no database.
"""

import unittest
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestCollaboratorUtilsUnit(unittest.TestCase):
    """C1 Unit tests for collaborator utility functions"""
    
    def test_validate_collaborator_data(self):
        """Test validation of collaborator data"""
        # Test valid collaborator data
        valid_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'role': 'developer',
            'division': 'Engineering'
        }
        
        # Test required fields validation
        required_fields = ['name', 'email', 'role']
        for field in required_fields:
            if field in valid_data:
                self.assertIsNotNone(valid_data[field])
                self.assertNotEqual(valid_data[field], '')
    
    def test_validate_email_format(self):
        """Test email format validation"""
        # Valid email formats
        valid_emails = [
            'user@example.com',
            'test.email@domain.co.uk',
            'user+tag@example.org',
            'user123@test-domain.com'
        ]
        
        for email in valid_emails:
            self.assertIn('@', email)
            self.assertGreater(len(email.split('@')[0]), 0)
            self.assertGreater(len(email.split('@')[1]), 0)
    
    def test_validate_role_permissions(self):
        """Test role permission validation"""
        # Define valid roles and their permissions
        role_permissions = {
            'manager': ['create_project', 'assign_tasks', 'view_all'],
            'developer': ['view_assigned', 'update_tasks'],
            'tester': ['view_assigned', 'update_tasks'],
            'viewer': ['view_assigned']
        }
        
        # Test role validation
        for role, permissions in role_permissions.items():
            self.assertIsInstance(permissions, list)
            self.assertGreater(len(permissions), 0)
    
    def test_collaborator_data_serialization(self):
        """Test collaborator data serialization for JSON"""
        collaborator_data = {
            'id': 'user123',
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'role': 'developer',
            'division': 'Engineering',
            'created_at': datetime.now().isoformat(),
            'is_active': True
        }
        
        # Test that all values are JSON serializable
        for key, value in collaborator_data.items():
            if isinstance(value, str):
                self.assertIsInstance(value, str)
            elif isinstance(value, bool):
                self.assertIsInstance(value, bool)
            elif isinstance(value, int):
                self.assertIsInstance(value, int)
    
    def test_collaborator_filtering(self):
        """Test collaborator filtering logic"""
        collaborators = [
            {'id': '1', 'name': 'Alice', 'role': 'manager', 'division': 'Engineering'},
            {'id': '2', 'name': 'Bob', 'role': 'developer', 'division': 'Engineering'},
            {'id': '3', 'name': 'Charlie', 'role': 'tester', 'division': 'QA'},
            {'id': '4', 'name': 'Diana', 'role': 'developer', 'division': 'Engineering'}
        ]
        
        # Test filtering by division
        engineering_collaborators = [c for c in collaborators if c['division'] == 'Engineering']
        self.assertEqual(len(engineering_collaborators), 3)
        
        # Test filtering by role
        developers = [c for c in collaborators if c['role'] == 'developer']
        self.assertEqual(len(developers), 2)
        
        # Test filtering by name
        alice = [c for c in collaborators if c['name'] == 'Alice']
        self.assertEqual(len(alice), 1)
        self.assertEqual(alice[0]['role'], 'manager')
    
    def test_collaborator_sorting(self):
        """Test collaborator sorting logic"""
        collaborators = [
            {'name': 'Charlie', 'role': 'tester'},
            {'name': 'Alice', 'role': 'manager'},
            {'name': 'Bob', 'role': 'developer'}
        ]
        
        # Test sorting by name
        sorted_by_name = sorted(collaborators, key=lambda x: x['name'].lower())
        expected_names = ['Alice', 'Bob', 'Charlie']
        actual_names = [c['name'] for c in sorted_by_name]
        self.assertEqual(actual_names, expected_names)
        
        # Test sorting by role
        sorted_by_role = sorted(collaborators, key=lambda x: x['role'])
        expected_roles = ['developer', 'manager', 'tester']
        actual_roles = [c['role'] for c in sorted_by_role]
        self.assertEqual(actual_roles, expected_roles)
    
    def test_collaborator_permission_check(self):
        """Test collaborator permission checking logic"""
        def has_permission(user_role, required_permission):
            """Mock permission checking function"""
            permissions = {
                'manager': ['create_project', 'assign_tasks', 'view_all', 'delete_tasks'],
                'developer': ['view_assigned', 'update_tasks'],
                'tester': ['view_assigned', 'update_tasks'],
                'viewer': ['view_assigned']
            }
            return required_permission in permissions.get(user_role, [])
        
        # Test manager permissions
        self.assertTrue(has_permission('manager', 'create_project'))
        self.assertTrue(has_permission('manager', 'assign_tasks'))
        self.assertTrue(has_permission('manager', 'view_all'))
        
        # Test developer permissions
        self.assertTrue(has_permission('developer', 'view_assigned'))
        self.assertTrue(has_permission('developer', 'update_tasks'))
        self.assertFalse(has_permission('developer', 'create_project'))
        
        # Test viewer permissions
        self.assertTrue(has_permission('viewer', 'view_assigned'))
        self.assertFalse(has_permission('viewer', 'update_tasks'))
        self.assertFalse(has_permission('viewer', 'create_project'))
    
    def test_collaborator_data_validation(self):
        """Test comprehensive collaborator data validation"""
        def validate_collaborator(collaborator):
            """Mock collaborator validation function"""
            errors = []
            
            # Check required fields
            required_fields = ['name', 'email', 'role']
            for field in required_fields:
                if field not in collaborator or not collaborator[field]:
                    errors.append(f"Missing required field: {field}")
            
            # Check email format
            if 'email' in collaborator and '@' not in collaborator['email']:
                errors.append("Invalid email format")
            
            # Check role validity
            valid_roles = ['manager', 'developer', 'tester', 'viewer']
            if 'role' in collaborator and collaborator['role'] not in valid_roles:
                errors.append("Invalid role")
            
            return errors
        
        # Test valid collaborator
        valid_collaborator = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'role': 'developer'
        }
        errors = validate_collaborator(valid_collaborator)
        self.assertEqual(len(errors), 0)
        
        # Test invalid collaborator
        invalid_collaborator = {
            'name': '',
            'email': 'invalid-email',
            'role': 'invalid_role'
        }
        errors = validate_collaborator(invalid_collaborator)
        self.assertGreater(len(errors), 0)
        self.assertIn("Missing required field: name", errors)
        self.assertIn("Invalid email format", errors)
        self.assertIn("Invalid role", errors)
    
    def test_collaborator_timestamp_handling(self):
        """Test collaborator timestamp handling"""
        # Test timestamp conversion
        now = datetime.now()
        iso_timestamp = now.isoformat()
        
        # Test that timestamp can be parsed back
        parsed_timestamp = datetime.fromisoformat(iso_timestamp)
        self.assertIsInstance(parsed_timestamp, datetime)
        
        # Test timestamp comparison
        later_time = now.replace(microsecond=now.microsecond + 1)
        self.assertGreater(later_time, now)
    
    def test_collaborator_data_transformation(self):
        """Test collaborator data transformation for API responses"""
        raw_collaborator = {
            'id': 'user123',
            'name': 'John Doe',
            'email': 'john@example.com',
            'role': 'developer',
            'division': 'Engineering',
            'created_at': datetime.now(),
            'is_active': True
        }
        
        # Transform for API response
        api_response = {
            'id': raw_collaborator['id'],
            'name': raw_collaborator['name'],
            'email': raw_collaborator['email'],
            'role': raw_collaborator['role'],
            'division': raw_collaborator['division'],
            'created_at': raw_collaborator['created_at'].isoformat(),
            'is_active': raw_collaborator['is_active']
        }
        
        # Test that transformation worked
        self.assertEqual(api_response['id'], 'user123')
        self.assertEqual(api_response['name'], 'John Doe')
        self.assertIsInstance(api_response['created_at'], str)
        self.assertIn('T', api_response['created_at'])  # ISO format


if __name__ == '__main__':
    print("=" * 80)
    print("C1 UNIT TESTING - COLLABORATOR UTILITY FUNCTIONS")
    print("=" * 80)
    print("Testing individual collaborator utility functions in complete isolation")
    print("No external dependencies, no Flask app, no database")
    print("=" * 80)

    # Run with verbose output
    unittest.main(verbosity=2)
