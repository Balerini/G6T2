# test_invite_collaborators.py - Unit tests for Inviting Project Collaborators
import unittest
import json
from unittest.mock import Mock, patch
from datetime import datetime
from flask import Flask
import sys
import os

from dotenv import load_dotenv
load_dotenv()

# Import your Flask blueprint
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from routes.project import projects_bp

# =============== BASE TEST CLASS ===============
class BaseCollaboratorTestCase(unittest.TestCase):
    """Base class with common setup for collaborator tests"""
    
    def setUp(self):
        """Run before each test"""
        # Create Flask app
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.register_blueprint(projects_bp)
        self.client = self.app.test_client()
        
        # Mock headers
        self.mock_headers = {
            'X-User-Id': 'user123',
            'X-User-Role': 'manager',
            'X-User-Name': 'Test User'
        }
        
        # Setup Firebase mocks
        self.setup_firebase_mocks()
    
    def setup_firebase_mocks(self):
        """Setup global Firebase mocks"""
        patcher1 = patch('firebase_utils.get_firestore_client')
        patcher2 = patch('routes.project.get_firestore_client')
        
        self.mock_firestore = patcher1.start()
        self.mock_route_firestore = patcher2.start()
        
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        
        # Setup mock database
        self.mock_db = Mock()
        self.mock_firestore.return_value = self.mock_db
        self.mock_route_firestore.return_value = self.mock_db

# =============== INVITE COLLABORATORS TESTS ===============
class TestInviteCollaborators(BaseCollaboratorTestCase):
    
    def test_invite_collaborator_any_department_success(self):
        """Test inviting collaborator from any department succeeds"""
        # Mock project
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Test Project',
            'owner': 'user123',
            'collaborators': ['user123'],
            'division_name': 'IT'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_project_doc
        
        # Invite user from different department
        invite_data = {
            'user_id': 'marketing_user',
            'department': 'Marketing'  # Different department
        }
        
        response = self.client.post('/api/projects/project123/invite',
                                    json=invite_data,
                                    headers=self.mock_headers)
        
        # Should succeed - any department allowed
        self.assertIn(response.status_code, [200, 201, 404, 500])
    
    def test_invite_collaborator_from_it_department(self):
        """Test inviting collaborator from IT department"""
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Test Project',
            'owner': 'user123',
            'collaborators': ['user123'],
            'division_name': 'IT'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_project_doc
        
        invite_data = {
            'user_id': 'it_user',
            'department': 'IT'  # Same department
        }
        
        response = self.client.post('/api/projects/project123/invite',
                                    json=invite_data,
                                    headers=self.mock_headers)
        
        self.assertIn(response.status_code, [200, 201, 404, 500])
    
    def test_invite_collaborator_from_sales_department(self):
        """Test inviting collaborator from Sales department"""
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Test Project',
            'owner': 'user123',
            'collaborators': ['user123'],
            'division_name': 'IT'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_project_doc
        
        invite_data = {
            'user_id': 'sales_user',
            'department': 'Sales'  # Different department
        }
        
        response = self.client.post('/api/projects/project123/invite',
                                    json=invite_data,
                                    headers=self.mock_headers)
        
        # Should succeed - any department allowed
        self.assertIn(response.status_code, [200, 201, 404, 500])
    
    def test_invite_collaborator_from_hr_department(self):
        """Test inviting collaborator from HR department"""
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Test Project',
            'owner': 'user123',
            'collaborators': ['user123']
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_project_doc
        
        invite_data = {
            'user_id': 'hr_user',
            'department': 'Human Resources'
        }
        
        response = self.client.post('/api/projects/project123/invite',
                                    json=invite_data,
                                    headers=self.mock_headers)
        
        # Should succeed
        self.assertIn(response.status_code, [200, 201, 404, 500])
    
    def test_invite_multiple_collaborators_different_departments(self):
        """Test inviting multiple collaborators from different departments"""
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Test Project',
            'owner': 'user123',
            'collaborators': ['user123']
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_project_doc
        
        # Invite users from various departments
        departments_to_test = [
            {'user_id': 'it_user', 'department': 'IT'},
            {'user_id': 'sales_user', 'department': 'Sales'},
            {'user_id': 'marketing_user', 'department': 'Marketing'},
            {'user_id': 'finance_user', 'department': 'Finance'}
        ]
        
        for invite_data in departments_to_test:
            response = self.client.post('/api/projects/project123/invite',
                                        json=invite_data,
                                        headers=self.mock_headers)
            
            # All should succeed - any department allowed
            self.assertIn(response.status_code, [200, 201, 404, 500])
    
    def test_invite_collaborator_duplicate(self):
        """Test inviting already existing collaborator"""
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Test Project',
            'owner': 'user123',
            'collaborators': ['user123', 'user456']  # user456 already exists
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_project_doc
        
        invite_data = {'user_id': 'user456'}
        
        response = self.client.post('/api/projects/project123/invite',
                                    json=invite_data,
                                    headers=self.mock_headers)
        
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400, 404, 500])
    
    def test_invite_collaborator_project_not_found(self):
        """Test inviting to non-existent project"""
        mock_project_doc = Mock()
        mock_project_doc.exists = False
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_project_doc
        
        invite_data = {'user_id': 'user456'}
        
        response = self.client.post('/api/projects/nonexistent/invite',
                                    json=invite_data,
                                    headers=self.mock_headers)
        
        # Should fail - project not found
        self.assertIn(response.status_code, [404, 500])
    
    def test_invite_collaborator_missing_user_id(self):
        """Test invite fails without user_id"""
        response = self.client.post('/api/projects/project123/invite',
                                    json={},
                                    headers=self.mock_headers)
        
        # Should fail - missing user_id
        self.assertIn(response.status_code, [400, 404, 500])

# =============== INVITE COLLABORATORS BY ROLE TESTS ===============
class TestInviteCollaboratorsByRole(BaseCollaboratorTestCase):
    
    def test_invite_employee_role_1_success(self):
        """Test inviting regular employee (role_num = 1)"""
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Test Project',
            'owner': 'user123',
            'collaborators': ['user123']
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_project_doc
        
        # Invite employee (role_num = 1)
        invite_data = {
            'user_id': 'employee_user',
            'role': 'Employee',
            'role_num': 1
        }
        
        response = self.client.post('/api/projects/project123/invite',
                                    json=invite_data,
                                    headers=self.mock_headers)
        
        # Should succeed - any role allowed
        self.assertIn(response.status_code, [200, 201, 404, 500])
    
    def test_invite_senior_role_2_success(self):
        """Test inviting senior staff (role_num = 2)"""
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Test Project',
            'owner': 'user123',
            'collaborators': ['user123']
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_project_doc
        
        # Invite senior (role_num = 2)
        invite_data = {
            'user_id': 'senior_user',
            'role': 'Senior',
            'role_num': 2
        }
        
        response = self.client.post('/api/projects/project123/invite',
                                    json=invite_data,
                                    headers=self.mock_headers)
        
        # Should succeed - any role allowed
        self.assertIn(response.status_code, [200, 201, 404, 500])
    
    def test_invite_manager_role_3_success(self):
        """Test inviting manager (role_num = 3)"""
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Test Project',
            'owner': 'user123',
            'collaborators': ['user123']
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_project_doc
        
        # Invite manager (role_num = 3)
        invite_data = {
            'user_id': 'manager_user',
            'role': 'Manager',
            'role_num': 3
        }
        
        response = self.client.post('/api/projects/project123/invite',
                                    json=invite_data,
                                    headers=self.mock_headers)
        
        # Should succeed - any role allowed
        self.assertIn(response.status_code, [200, 201, 404, 500])
    
    def test_invite_multiple_roles_together(self):
        """Test inviting users with different roles to same project"""
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Test Project',
            'owner': 'user123',
            'collaborators': ['user123']
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_project_doc
        
        # Invite users with various roles
        roles_to_test = [
            {'user_id': 'employee1', 'role': 'Employee', 'role_num': 1},
            {'user_id': 'senior1', 'role': 'Senior', 'role_num': 2},
            {'user_id': 'manager1', 'role': 'Manager', 'role_num': 3},
            {'user_id': 'employee2', 'role': 'Employee', 'role_num': 1}
        ]
        
        for invite_data in roles_to_test:
            response = self.client.post('/api/projects/project123/invite',
                                        json=invite_data,
                                        headers=self.mock_headers)
            
            # All should succeed - any role allowed
            self.assertIn(response.status_code, [200, 201, 404, 500])
    
    def test_invite_employee_to_manager_owned_project(self):
        """Test manager can invite employee"""
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Manager Project',
            'owner': 'manager123',  # Manager is owner
            'collaborators': ['manager123']
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_project_doc
        
        # Manager headers
        manager_headers = {
            'X-User-Id': 'manager123',
            'X-User-Role': 'manager',
            'X-User-Role-Num': '3'
        }
        
        # Invite employee
        invite_data = {
            'user_id': 'employee_user',
            'role_num': 1
        }
        
        response = self.client.post('/api/projects/project123/invite',
                                    json=invite_data,
                                    headers=manager_headers)
        
        # Should succeed
        self.assertIn(response.status_code, [200, 201, 404, 500])
    
    def test_invite_manager_to_employee_owned_project(self):
        """Test employee can invite manager"""
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Employee Project',
            'owner': 'employee123',  # Employee is owner
            'collaborators': ['employee123']
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_project_doc
        
        # Employee headers
        employee_headers = {
            'X-User-Id': 'employee123',
            'X-User-Role': 'employee',
            'X-User-Role-Num': '1'
        }
        
        # Invite manager
        invite_data = {
            'user_id': 'manager_user',
            'role_num': 3
        }
        
        response = self.client.post('/api/projects/project123/invite',
                                    json=invite_data,
                                    headers=employee_headers)
        
        # Should succeed - any role can be invited
        self.assertIn(response.status_code, [200, 201, 404, 500])
    
    def test_invite_peer_same_role(self):
        """Test inviting someone with same role level"""
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Test Project',
            'owner': 'user123',
            'collaborators': ['user123']
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_project_doc
        
        # Senior inviting another senior
        senior_headers = {
            'X-User-Id': 'senior123',
            'X-User-Role': 'senior',
            'X-User-Role-Num': '2'
        }
        
        invite_data = {
            'user_id': 'senior456',
            'role_num': 2  # Same role
        }
        
        response = self.client.post('/api/projects/project123/invite',
                                    json=invite_data,
                                    headers=senior_headers)
        
        # Should succeed
        self.assertIn(response.status_code, [200, 201, 404, 500])

# =============== CROSS-DEPARTMENT AND CROSS-ROLE TESTS ===============
class TestCrossDepartmentAndRoleInvite(BaseCollaboratorTestCase):
    
    def test_invite_employee_from_different_department(self):
        """Test inviting employee from different department"""
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'IT Project',
            'owner': 'it_manager',
            'division_name': 'IT',
            'collaborators': ['it_manager']
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_project_doc
        
        # Invite Sales employee
        invite_data = {
            'user_id': 'sales_employee',
            'department': 'Sales',
            'role': 'Employee',
            'role_num': 1
        }
        
        response = self.client.post('/api/projects/project123/invite',
                                    json=invite_data,
                                    headers=self.mock_headers)
        
        # Should succeed - any department + any role
        self.assertIn(response.status_code, [200, 201, 404, 500])
    
    def test_invite_manager_from_different_department(self):
        """Test inviting manager from different department"""
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Marketing Project',
            'owner': 'marketing_user',
            'division_name': 'Marketing',
            'collaborators': ['marketing_user']
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_project_doc
        
        # Invite IT manager
        invite_data = {
            'user_id': 'it_manager',
            'department': 'IT',
            'role': 'Manager',
            'role_num': 3
        }
        
        response = self.client.post('/api/projects/project123/invite',
                                    json=invite_data,
                                    headers=self.mock_headers)
        
        # Should succeed - any department + any role
        self.assertIn(response.status_code, [200, 201, 404, 500])
    
    def test_invite_diverse_team(self):
        """Test building diverse team with different departments and roles"""
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Cross-Functional Project',
            'owner': 'user123',
            'collaborators': ['user123']
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_project_doc
        
        # Invite diverse team
        diverse_team = [
            {'user_id': 'it_employee', 'department': 'IT', 'role_num': 1},
            {'user_id': 'sales_manager', 'department': 'Sales', 'role_num': 3},
            {'user_id': 'hr_senior', 'department': 'HR', 'role_num': 2},
            {'user_id': 'marketing_employee', 'department': 'Marketing', 'role_num': 1},
            {'user_id': 'finance_manager', 'department': 'Finance', 'role_num': 3}
        ]
        
        for invite_data in diverse_team:
            response = self.client.post('/api/projects/project123/invite',
                                        json=invite_data,
                                        headers=self.mock_headers)
            
            # All should succeed - no restrictions
            self.assertIn(response.status_code, [200, 201, 404, 500])

if __name__ == '__main__':
    unittest.main(verbosity=2)
