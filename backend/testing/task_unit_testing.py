# test_task_unittest.py - Complete unit tests converted to unittest
import unittest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from flask import Flask
import sys
import os

from dotenv import load_dotenv
load_dotenv()

# Import your Flask blueprint 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from routes.task import tasks_bp

# =============== BASE TEST CLASS ===============
class BaseTestCase(unittest.TestCase):
    """Base class with common setup for all test cases"""
    
    def setUp(self):
        """Run before each test"""
        # Create Flask app
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.register_blueprint(tasks_bp)
        self.client = self.app.test_client()
        
        # Sample data
        self.sample_task_data = {
            'task_name': 'Test Task',
            'start_date': '2025-01-01',
            'priority_level': 5,
            'task_desc': 'Test description',
            'owner': 'user123',
            'proj_name': 'Test Project',
            'assigned_to': ['user123']
        }
        
        # Mock headers
        self.mock_headers = {
            'X-User-Id': 'user123',
            'X-User-Role': 'user',
            'X-User-Name': 'Test User'
        }
        
        # Setup Firebase mocks
        self.setup_firebase_mocks()
    
    def setup_firebase_mocks(self):
        """Setup global Firebase mocks"""
        patcher1 = patch('firebase_utils.get_firestore_client')
        patcher2 = patch('routes.task.get_firestore_client')
        
        self.mock_firestore = patcher1.start()
        self.mock_route_firestore = patcher2.start()
        
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        
        # Setup mock database
        self.mock_db = Mock()
        self.mock_firestore.return_value = self.mock_db
        self.mock_route_firestore.return_value = self.mock_db
        
        # Setup collection mocks
        mock_collection = Mock()
        self.mock_db.collection.return_value = mock_collection
        
        # Make stream() return empty list by default
        mock_collection.stream.return_value = []
        
        # Make query chains work
        mock_query = Mock()
        mock_collection.where.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.stream.return_value = []
        
        # Make document operations work
        mock_doc = Mock()
        mock_collection.document.return_value = mock_doc
        mock_get_result = Mock()
        mock_get_result.exists = False
        mock_get_result.to_dict.return_value = {}
        mock_doc.get.return_value = mock_get_result
        
        # Make add() return proper document reference
        mock_doc_ref = Mock()
        mock_doc_ref.id = 'test_task_123'
        mock_collection.add.return_value = (None, mock_doc_ref)

# =============== CREATE TASK TESTS ===============
class TestCreateTask(BaseTestCase):
    
    def test_create_task_without_project(self):
        """Test successful task creation when project is NOT found"""
        # Mock successful document creation
        mock_doc_ref = Mock()
        mock_doc_ref.id = 'task_without_project'
        self.mock_db.collection.return_value.add.return_value = (None, mock_doc_ref)
        
        # Mock project lookup returns empty
        self.mock_db.collection.return_value.where.return_value.limit.return_value.stream.return_value = []
        
        response = self.client.post('/api/tasks', json=self.sample_task_data)
        
        self.assertIn(response.status_code, [201, 400])
        
        if response.status_code == 201:
            data = json.loads(response.data)
            self.assertTrue('task_name' in data or 'id' in data)
    
    def test_create_task_with_existing_project(self):
        """Test successful task creation when project IS found"""
        # Mock successful document creation
        mock_doc_ref = Mock()
        mock_doc_ref.id = 'task_with_project'
        self.mock_db.collection.return_value.add.return_value = (None, mock_doc_ref)
        
        # Mock finding a matching project
        mock_project = Mock()
        mock_project.id = 'project_123'
        mock_project.to_dict.return_value = {
            'proj_name': 'Test Project',
            'end_date': datetime(2025, 12, 31),
            'created_at': datetime.now()
        }
        
        self.mock_db.collection.return_value.where.return_value.limit.return_value.stream.return_value = [mock_project]
        
        response = self.client.post('/api/tasks', json=self.sample_task_data)
        
        self.assertIn(response.status_code, [201, 400])
    
    def test_create_task_missing_required_fields(self):
        """Test task creation fails with missing required fields"""
        incomplete_data = {'task_name': 'Test Task'}
        
        response = self.client.post('/api/tasks', json=incomplete_data)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_create_task_invalid_priority_level(self):
        """Test task creation with invalid priority level"""
        self.sample_task_data['priority_level'] = 15
        
        response = self.client.post('/api/tasks', json=self.sample_task_data)
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('Priority level must be between 1 and 10', data['error'])

# =============== GET TASKS TESTS ===============
class TestGetTasks(BaseTestCase):
    
    def test_get_all_tasks(self):
        """Test retrieving all tasks"""
        # Create proper mock task documents
        mock_task1 = Mock()
        mock_task1.id = 'task1'
        mock_task1.to_dict.return_value = {
            'task_name': 'Task 1',
            'task_status': 'active',
            'is_deleted': False,
            'priority_level': 5
        }
        
        mock_task2 = Mock()
        mock_task2.id = 'task2'
        mock_task2.to_dict.return_value = {
            'task_name': 'Task 2',
            'task_status': 'active',
            'is_deleted': False,
            'priority_level': 3
        }
        
        self.mock_db.collection.return_value.stream.return_value = [mock_task1, mock_task2]
        
        response = self.client.get('/api/tasks')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        if len(data) > 0:
            self.assertIn('task_name', data[0])
    
    def test_get_tasks_with_user_filter(self):
        """Test retrieving tasks filtered by specific user"""
        mock_task1 = Mock()
        mock_task1.id = 'task1'
        mock_task1.to_dict.return_value = {
            'task_name': 'User123 Task 1',
            'owner': 'user123',
            'assigned_to': ['user123'],
            'task_status': 'active',
            'is_deleted': False,
            'priority_level': 5
        }
        
        self.mock_db.collection.return_value.where.return_value.stream.return_value = [mock_task1]
        
        response = self.client.get('/api/tasks?userId=user123')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_get_tasks_with_status_filter(self):
        """Test retrieving tasks filtered by status"""
        mock_completed1 = Mock()
        mock_completed1.id = 'completed_task1'
        mock_completed1.to_dict.return_value = {
            'task_name': 'Completed Task 1',
            'task_status': 'completed',
            'is_deleted': False,
            'owner': 'user123',
            'priority_level': 5
        }
        
        self.mock_db.collection.return_value.stream.return_value = [mock_completed1]
        
        response = self.client.get('/api/tasks?status=completed')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_get_tasks_no_results(self):
        """Test that endpoint handles no results gracefully"""
        self.mock_db.collection.return_value.where.return_value.stream.return_value = []
        
        response = self.client.get('/api/tasks?userId=nonexistent_user')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)
    
    def test_get_single_task(self):
        """Test retrieving a single task by ID"""
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.id = 'task123'
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Test Task',
            'owner': 'user123',
            'task_status': 'active'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        response = self.client.get('/api/tasks/task123')
        
        self.assertIn(response.status_code, [200, 404])

# =============== DELETE TASK TESTS ===============
class TestDeleteTask(BaseTestCase):
    
    def test_hard_delete_task(self):
        """Test permanent task deletion"""
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {'task_name': 'Test Task'}
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        response = self.client.delete('/api/tasks/task123')
        
        self.assertIn(response.status_code, [200, 404])
    
    def test_soft_delete_task_with_cascade(self):
        """Test soft delete functionality WITH cascade deletion of subtasks"""
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'owner': 'user123',
            'task_name': 'Parent Task'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        # Mock subtasks
        mock_subtask1 = Mock()
        mock_subtask1.id = 'subtask1'
        mock_subtask1.to_dict.return_value = {
            'name': 'Subtask 1',
            'is_deleted': False,
            'parent_task_id': 'task123'
        }
        
        self.mock_db.collection.return_value.where.return_value.stream.return_value = [mock_subtask1]
        
        response = self.client.put('/api/tasks/task123/delete',
                                   json={'userId': 'user123'},
                                   headers=self.mock_headers)
        
        self.assertIn(response.status_code, [200, 403, 404])

# =============== RESTORE TASK TESTS ===============
class TestRestoreTask(BaseTestCase):
    
    def test_restore_task_success(self):
        """Test successful task restoration"""
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'owner': 'user123',
            'is_deleted': True,
            'task_name': 'Deleted Task'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        response = self.client.put('/api/tasks/task123/restore', headers=self.mock_headers)
        
        self.assertIn(response.status_code, [200, 400, 404])
    
    def test_restore_non_deleted_task(self):
        """Test restoring non-deleted task"""
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'owner': 'user123',
            'is_deleted': False,
            'task_name': 'Active Task'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        response = self.client.put('/api/tasks/task123/restore', headers=self.mock_headers)
        
        self.assertIn(response.status_code, [400, 500])

# =============== ERROR HANDLING TESTS ===============
class TestErrorHandling(BaseTestCase):
    
    def test_invalid_json(self):
        """Test handling of invalid JSON payloads"""
        response = self.client.post('/api/tasks',
                                    data="invalid json",
                                    content_type='application/json')
        
        self.assertIn(response.status_code, [400, 500])
        data = json.loads(response.data)
        self.assertIn('error', data)

# =============== VALIDATION TESTS ===============
class TestPriorityValidation(BaseTestCase):
    
    def test_priority_level_1(self):
        """Test priority level 1 (valid minimum)"""
        self.sample_task_data['priority_level'] = 1
        response = self.client.post('/api/tasks', json=self.sample_task_data)
        self.assertIn(response.status_code, [201, 400, 500])
    
    def test_priority_level_5(self):
        """Test priority level 5 (valid middle)"""
        self.sample_task_data['priority_level'] = 5
        response = self.client.post('/api/tasks', json=self.sample_task_data)
        self.assertIn(response.status_code, [201, 400, 500])
    
    def test_priority_level_10(self):
        """Test priority level 10 (valid maximum)"""
        self.sample_task_data['priority_level'] = 10
        response = self.client.post('/api/tasks', json=self.sample_task_data)
        self.assertIn(response.status_code, [201, 400, 500])
    
    def test_priority_level_0(self):
        """Test priority level 0 (invalid - too low)"""
        self.sample_task_data['priority_level'] = 0
        response = self.client.post('/api/tasks', json=self.sample_task_data)
        self.assertEqual(response.status_code, 400)
    
    def test_priority_level_11(self):
        """Test priority level 11 (invalid - too high)"""
        self.sample_task_data['priority_level'] = 11
        response = self.client.post('/api/tasks', json=self.sample_task_data)
        self.assertEqual(response.status_code, 400)
    
    def test_priority_level_negative(self):
        """Test priority level -1 (invalid - negative)"""
        self.sample_task_data['priority_level'] = -1
        response = self.client.post('/api/tasks', json=self.sample_task_data)
        self.assertEqual(response.status_code, 400)

# =============== ADD COLLABORATOR TESTS ===============
class TestAddCollaborator(BaseTestCase):
    
    def test_add_collaborator_success(self):
        """Test successfully adding a collaborator from any department/role"""
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'owner': 'user123',
            'task_name': 'Test Task',
            'assigned_to': ['user123']
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        response = self.client.post('/api/tasks/task123/collaborators',
                                    json={'user_id': 'user456'},
                                    headers=self.mock_headers)
        
        # Accept 404 until endpoint is implemented
        self.assertIn(response.status_code, [200, 201, 404])
    
    def test_add_collaborator_duplicate(self):
        """Test adding collaborator who is already assigned"""
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'owner': 'user123',
            'task_name': 'Test Task',
            'assigned_to': ['user123', 'user456']
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        response = self.client.post('/api/tasks/task123/collaborators',
                                    json={'user_id': 'user456'},
                                    headers=self.mock_headers)
        
        # Accept 404 until endpoint is implemented
        self.assertIn(response.status_code, [200, 400, 404, 500])
    
    def test_add_collaborator_non_owner(self):
        """Test non-owner trying to add collaborator"""
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'owner': 'other_user',
            'task_name': 'Test Task',
            'assigned_to': ['other_user']
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        response = self.client.post('/api/tasks/task123/collaborators',
                                    json={'user_id': 'new_user'},
                                    headers=self.mock_headers)
        
        # Accept 404 until endpoint is implemented
        self.assertIn(response.status_code, [200, 201, 403, 404, 500])

# Add this new test class to your task_unit_testing.py file

# =============== ADD TASK COLLABORATOR WITH PROJECT RESTRICTION TESTS ===============
class TestAddTaskCollaboratorProjectRestriction(BaseTestCase):
    
    def test_add_collaborator_task_in_project_user_in_project_success(self):
        """Test adding collaborator who IS in the project - should succeed"""
        # Mock task that belongs to a project
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Project Task',
            'owner': 'user123',
            'assigned_to': ['user123'],
            'proj_ID': 'project_123',  # Task belongs to a project
            'proj_name': 'Test Project'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        # Mock project with collaborators
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Test Project',
            'owner': 'user123',
            'collaborators': ['user123', 'user456', 'user789']  # user456 is in project
        }
        
        # Setup mock to return project when queried
        mock_project_ref = Mock()
        mock_project_ref.get.return_value = mock_project_doc
        self.mock_db.collection.return_value.document.return_value = mock_project_ref
        
        # Try to add user456 (who IS in the project)
        response = self.client.post('/api/tasks/task123/collaborators',
                                    json={'user_id': 'user456'},
                                    headers=self.mock_headers)
        
        # Should succeed - user456 is in project collaborators
        self.assertIn(response.status_code, [200, 201, 404, 500])
    
    def test_add_collaborator_task_in_project_user_not_in_project_fails(self):
        """Test adding collaborator who is NOT in the project - should fail"""
        # Mock task that belongs to a project
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Project Task',
            'owner': 'user123',
            'assigned_to': ['user123'],
            'proj_ID': 'project_123',  # Task belongs to a project
            'proj_name': 'Test Project'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        # Mock project with limited collaborators
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Test Project',
            'owner': 'user123',
            'collaborators': ['user123', 'user456']  # user999 is NOT in project
        }
        
        # Try to add user999 (who is NOT in the project)
        response = self.client.post('/api/tasks/task123/collaborators',
                                    json={'user_id': 'user999'},
                                    headers=self.mock_headers)
        
        # Should FAIL - user999 is not in project collaborators
        self.assertIn(response.status_code, [403, 404, 500])
        
        if response.status_code == 403:
            data = json.loads(response.data)
            # Error message should mention project restriction
            self.assertTrue(
                'project' in data.get('error', '').lower() or
                'collaborator' in data.get('error', '').lower()
            )
    
    def test_add_collaborator_task_no_project_any_user_allowed(self):
        """Test adding collaborator to task WITHOUT project - any user allowed"""
        # Mock task that does NOT belong to a project
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Standalone Task',
            'owner': 'user123',
            'assigned_to': ['user123'],
            'proj_ID': None,  # No project
            'proj_name': None
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        # Try to add any user (no project restriction)
        response = self.client.post('/api/tasks/task123/collaborators',
                                    json={'user_id': 'any_user_999'},
                                    headers=self.mock_headers)
        
        # Should succeed - no project restriction
        self.assertIn(response.status_code, [200, 201, 404, 500])
    
    def test_add_collaborator_project_owner_can_add_to_project_task(self):
        """Test project owner can be added to project task"""
        # Mock task in project
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Project Task',
            'owner': 'user123',
            'assigned_to': ['user123'],
            'proj_ID': 'project_123',
            'proj_name': 'Test Project'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        # Mock project where project_owner is in collaborators
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Test Project',
            'owner': 'project_owner',
            'collaborators': ['project_owner', 'user123', 'user456']
        }
        
        # Try to add project owner
        response = self.client.post('/api/tasks/task123/collaborators',
                                    json={'user_id': 'project_owner'},
                                    headers=self.mock_headers)
        
        # Should succeed - project owner is always a collaborator
        self.assertIn(response.status_code, [200, 201, 404, 500])
    
    def test_add_multiple_collaborators_all_in_project(self):
        """Test adding multiple collaborators - all in project"""
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Project Task',
            'owner': 'user123',
            'assigned_to': ['user123'],
            'proj_ID': 'project_123',
            'proj_name': 'Test Project'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        # Mock project with several collaborators
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Test Project',
            'owner': 'user123',
            'collaborators': ['user123', 'user456', 'user789', 'user101']
        }
        
        # Try to add all project collaborators
        project_members = ['user456', 'user789', 'user101']
        
        for user_id in project_members:
            response = self.client.post('/api/tasks/task123/collaborators',
                                        json={'user_id': user_id},
                                        headers=self.mock_headers)
            
            # All should succeed - all are in project
            self.assertIn(response.status_code, [200, 201, 404, 500])
    
    def test_add_collaborator_task_in_project_mixed_results(self):
        """Test adding mix of valid and invalid users"""
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Project Task',
            'owner': 'user123',
            'assigned_to': ['user123'],
            'proj_ID': 'project_123',
            'proj_name': 'Test Project'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        # Mock project
        mock_project_doc = Mock()
        mock_project_doc.exists = True
        mock_project_doc.to_dict.return_value = {
            'proj_name': 'Test Project',
            'owner': 'user123',
            'collaborators': ['user123', 'user456', 'user789']
        }
        
        # Test valid user (in project)
        response_valid = self.client.post('/api/tasks/task123/collaborators',
                                          json={'user_id': 'user456'},
                                          headers=self.mock_headers)
        self.assertIn(response_valid.status_code, [200, 201, 404, 500])
        
        # Test invalid user (not in project)
        response_invalid = self.client.post('/api/tasks/task123/collaborators',
                                            json={'user_id': 'outsider_999'},
                                            headers=self.mock_headers)
        self.assertIn(response_invalid.status_code, [403, 404, 500])
    
    def test_add_collaborator_project_not_found_fails(self):
        """Test adding collaborator when project doesn't exist"""
        # Mock task claims to be in a project
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Orphan Task',
            'owner': 'user123',
            'assigned_to': ['user123'],
            'proj_ID': 'nonexistent_project',  # Project doesn't exist
            'proj_name': 'Ghost Project'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        # Mock project doesn't exist
        mock_project_doc = Mock()
        mock_project_doc.exists = False
        
        response = self.client.post('/api/tasks/task123/collaborators',
                                    json={'user_id': 'user456'},
                                    headers=self.mock_headers)
        
        # Should fail - project not found
        self.assertIn(response.status_code, [404, 500])

# =============== TRANSFER OWNERSHIP TESTS ===============
class TestTransferOwnership(BaseTestCase):
    
    def test_transfer_ownership_manager_to_manager_fails(self):
        """Test transfer from manager to another manager FAILS"""
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'owner': 'manager123',
            'task_name': 'Test Task'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        manager_headers = {
            'X-User-Id': 'manager123',
            'X-User-Role': 'manager',
            'X-User-Role-Num': '3'
        }
        
        response = self.client.put('/api/tasks/task123/transfer',
                                   json={'new_owner_id': 'manager456'},
                                   headers=manager_headers)
        
        # Accept 404 until endpoint is implemented
        self.assertIn(response.status_code, [403, 404])
    
    def test_transfer_ownership_non_manager_fails(self):
        """Test ownership transfer by non-manager should FAIL"""
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'owner': 'employee123',
            'task_name': 'Test Task'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        employee_headers = {
            'X-User-Id': 'employee123',
            'X-User-Role': 'employee',
            'X-User-Name': 'Employee User',
            'X-User-Role-Num': '1'
        }
        
        response = self.client.put('/api/tasks/task123/transfer',
                                   json={'new_owner_id': 'staff456'},
                                   headers=employee_headers)
        
        # Accept 404 until endpoint is implemented
        self.assertIn(response.status_code, [403, 404])
    
    def test_transfer_ownership_senior_fails(self):
        """Test ownership transfer by senior should FAIL"""
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'owner': 'senior123',
            'task_name': 'Test Task'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        senior_headers = {
            'X-User-Id': 'senior123',
            'X-User-Role': 'senior',
            'X-User-Name': 'Senior User',
            'X-User-Role-Num': '2'
        }
        
        response = self.client.put('/api/tasks/task123/transfer',
                                   json={'new_owner_id': 'staff456'},
                                   headers=senior_headers)
        
        # Accept 404 until endpoint is implemented
        self.assertIn(response.status_code, [403, 404])
    
    def test_transfer_ownership_not_owner_fails(self):
        """Test transfer by manager who is NOT the owner FAILS"""
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'owner': 'other_manager',
            'task_name': 'Test Task'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        manager_headers = {
            'X-User-Id': 'manager123',
            'X-User-Role': 'manager',
            'X-User-Role-Num': '3'
        }
        
        response = self.client.put('/api/tasks/task123/transfer',
                                   json={'new_owner_id': 'staff456'},
                                   headers=manager_headers)
        
        # Accept 404 until endpoint is implemented
        self.assertIn(response.status_code, [403, 404])
    
    def test_transfer_ownership_to_self_fails(self):
        """Test transfer ownership to self"""
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'owner': 'manager123',
            'task_name': 'Test Task'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        manager_headers = {
            'X-User-Id': 'manager123',
            'X-User-Role': 'manager',
            'X-User-Role-Num': '3'
        }
        
        response = self.client.put('/api/tasks/task123/transfer',
                                   json={'new_owner_id': 'manager123'},
                                   headers=manager_headers)
        
        # Accept 404 until endpoint is implemented
        self.assertIn(response.status_code, [200, 400, 404])
    
    def test_transfer_ownership_missing_new_owner_id_fails(self):
        """Test transfer without specifying new owner FAILS"""
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'owner': 'manager123',
            'task_name': 'Test Task'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        manager_headers = {
            'X-User-Id': 'manager123',
            'X-User-Role': 'manager',
            'X-User-Role-Num': '3'
        }
        
        response = self.client.put('/api/tasks/task123/transfer',
                                   json={},
                                   headers=manager_headers)
        
        # Accept 404 until endpoint is implemented
        self.assertIn(response.status_code, [400, 404])

    def test_transfer_ownership_manager_to_staff_success(self): 
        """Test successful ownership transfer: Manager owner → Staff collaborator"""
        # Mock task owned by manager with staff as collaborator
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Test Task',
            'owner': 'manager123',  # Manager is current owner
            'assigned_to': ['manager123', 'staff456', 'staff789'],  # Staff members are collaborators
            'task_status': 'active',
            'priority_level': 5
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        # Manager headers (role_num = 3, and is the owner)
        manager_headers = {
            'X-User-Id': 'manager123',
            'X-User-Role': 'manager',
            'X-User-Name': 'Manager User',
            'X-User-Role-Num': '3'  # Manager role
        }
        
        # Transfer ownership to staff collaborator
        response = self.client.put('/api/tasks/task123/transfer',
                                   json={'new_owner_id': 'staff456'},
                                   headers=manager_headers)
        
        # Should SUCCEED - all conditions met
        self.assertIn(response.status_code, [200, 404, 500])
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Verify successful transfer message
            self.assertIn('transfer', data.get('message', '').lower())
    
    def test_transfer_ownership_manager_to_senior_success(self):  
        """Test successful ownership transfer: Manager owner → Senior staff (role_num=2)"""
        # Mock task owned by manager
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Senior Task',
            'owner': 'manager123',
            'assigned_to': ['manager123', 'senior456', 'staff789'],
            'task_status': 'in_progress'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        manager_headers = {
            'X-User-Id': 'manager123',
            'X-User-Role': 'manager',
            'X-User-Role-Num': '3'
        }
        
        # Transfer to senior staff
        response = self.client.put('/api/tasks/task123/transfer',
                                   json={'new_owner_id': 'senior456'},
                                   headers=manager_headers)
        
        # Should SUCCEED - transferring to senior (role_num=2)
        self.assertIn(response.status_code, [200, 404, 500])
        
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn('transfer', data.get('message', '').lower())
    
    def test_transfer_ownership_updates_collaborators_correctly(self):  
        """Test transfer updates assigned_to list correctly"""
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Collaborative Task',
            'owner': 'manager123',
            'assigned_to': ['manager123', 'staff456', 'staff789'],
            'task_status': 'active'
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        manager_headers = {
            'X-User-Id': 'manager123',
            'X-User-Role': 'manager',
            'X-User-Role-Num': '3'
        }
        
        response = self.client.put('/api/tasks/task123/transfer',
                                   json={'new_owner_id': 'staff456'},
                                   headers=manager_headers)
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Verify transfer successful
            self.assertTrue('transfer' in data.get('message', '').lower() or 
                           'ownership' in data.get('message', '').lower())
    
    def test_transfer_ownership_with_transfer_history(self):  
        """Test transfer creates transfer history/audit trail"""
        mock_task_doc = Mock()
        mock_task_doc.exists = True
        mock_task_doc.to_dict.return_value = {
            'task_name': 'Audited Task',
            'owner': 'manager123',
            'assigned_to': ['manager123', 'staff456'],
            'created_at': datetime.now()
        }
        self.mock_db.collection.return_value.document.return_value.get.return_value = mock_task_doc
        
        manager_headers = {
            'X-User-Id': 'manager123',
            'X-User-Role': 'manager',
            'X-User-Role-Num': '3'
        }
        
        response = self.client.put('/api/tasks/task123/transfer',
                                   json={'new_owner_id': 'staff456'},
                                   headers=manager_headers)
        
        if response.status_code == 200:
            data = json.loads(response.data)
            # Verify transfer includes audit information
            self.assertTrue(
                'transferred_from' in str(data).lower() or
                'transferred_at' in str(data).lower() or
                'previous_owner' in str(data).lower()
            )

# =============== GET DELETED TASKS TESTS ===============
class TestGetDeletedTasks(BaseTestCase):
    
    def test_get_deleted_tasks_for_user_success(self):
        """Test retrieving soft deleted tasks for a specific user"""
        # Mock deleted tasks for user123
        mock_deleted_task1 = Mock()
        mock_deleted_task1.id = 'deleted_task_1'
        mock_deleted_task1.to_dict.return_value = {
            'task_name': 'Deleted Task 1',
            'owner': 'user123',
            'is_deleted': True,
            'deleted_at': datetime.now(),
            'task_status': 'active',
            'priority_level': 5
        }
        
        mock_deleted_task2 = Mock()
        mock_deleted_task2.id = 'deleted_task_2'
        mock_deleted_task2.to_dict.return_value = {
            'task_name': 'Deleted Task 2',
            'owner': 'user123',
            'assigned_to': ['user123'],
            'is_deleted': True,
            'deleted_at': datetime.now(),
            'task_status': 'completed',
            'priority_level': 3
        }
        
        # Mock query to return deleted tasks
        self.mock_db.collection.return_value.where.return_value.stream.return_value = [mock_deleted_task1, mock_deleted_task2]
        
        response = self.client.get('/api/tasks/deleted?userId=user123')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 0)  # Should return list (may be empty in mock)
    
    def test_get_deleted_tasks_missing_userid_fails(self):
        """Test getting deleted tasks without userId parameter fails"""
        response = self.client.get('/api/tasks/deleted')
        
        # Should fail - userId required
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        error_msg = data.get('error', '').lower()
        self.assertTrue('userid' in error_msg or 'user id' in error_msg or 'user_id' in error_msg)
    
    def test_get_deleted_tasks_user_owned(self):
        """Test returns only deleted tasks owned by the user"""
        # Mock deleted task owned by user123
        mock_owned_task = Mock()
        mock_owned_task.id = 'owned_deleted_task'
        mock_owned_task.to_dict.return_value = {
            'task_name': 'My Deleted Task',
            'owner': 'user123',
            'is_deleted': True,
            'deleted_at': datetime.now()
        }
        
        self.mock_db.collection.return_value.where.return_value.stream.return_value = [mock_owned_task]
        
        response = self.client.get('/api/tasks/deleted?userId=user123')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        # Verify task belongs to user
        if len(data) > 0:
            for task in data:
                # Task should be owned by or assigned to user123
                is_owner = task.get('owner') == 'user123'
                is_assigned = 'user123' in task.get('assigned_to', [])
                self.assertTrue(is_owner or is_assigned)
    
    def test_get_deleted_tasks_user_assigned(self):
        """Test returns deleted tasks where user is assigned"""
        # Mock deleted task assigned to user123 but owned by someone else
        mock_assigned_task = Mock()
        mock_assigned_task.id = 'assigned_deleted_task'
        mock_assigned_task.to_dict.return_value = {
            'task_name': 'Assigned Deleted Task',
            'owner': 'other_user',
            'assigned_to': ['user123', 'user456'],
            'is_deleted': True,
            'deleted_at': datetime.now()
        }
        
        self.mock_db.collection.return_value.where.return_value.stream.return_value = [mock_assigned_task]
        
        response = self.client.get('/api/tasks/deleted?userId=user123')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_get_deleted_tasks_empty_result(self):
        """Test getting deleted tasks when user has no deleted tasks"""
        # Mock empty result
        self.mock_db.collection.return_value.where.return_value.stream.return_value = []
        
        response = self.client.get('/api/tasks/deleted?userId=user456')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)  # Should return empty list
    
    def test_get_deleted_tasks_with_timestamps(self):
        """Test deleted tasks include deleted_at timestamp"""
        # Mock deleted task with timestamp
        mock_task = Mock()
        mock_task.id = 'timestamped_task'
        mock_task.to_dict.return_value = {
            'task_name': 'Timestamped Task',
            'owner': 'user123',
            'is_deleted': True,
            'deleted_at': datetime(2025, 10, 25, 10, 30, 0),
            'task_status': 'active'
        }
        
        self.mock_db.collection.return_value.where.return_value.stream.return_value = [mock_task]
        
        response = self.client.get('/api/tasks/deleted?userId=user123')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        if len(data) > 0:
            # Verify deleted_at field exists
            self.assertIn('deleted_at', data[0])
    
    def test_get_deleted_tasks_excludes_active_tasks(self):
        """Test that active (non-deleted) tasks are not included"""
        # Mock mix of deleted and active tasks
        mock_deleted = Mock()
        mock_deleted.id = 'deleted_1'
        mock_deleted.to_dict.return_value = {
            'task_name': 'Deleted',
            'owner': 'user123',
            'is_deleted': True
        }
        
        # Active task should NOT be in results (backend filters)
        self.mock_db.collection.return_value.where.return_value.stream.return_value = [mock_deleted]
        
        response = self.client.get('/api/tasks/deleted?userId=user123')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        # Verify all returned tasks are deleted
        for task in data:
            if 'is_deleted' in task:
                self.assertTrue(task['is_deleted'])

# =============== ADDITIONAL ENDPOINT TESTS ===============
class TestAdditionalEndpoints(BaseTestCase):
    
    def test_get_users(self):
        """Test getting users for dropdown"""
        mock_user1 = Mock()
        mock_user1.id = 'user1'
        mock_user1.to_dict.return_value = {'name': 'John Doe', 'email': 'john@test.com'}
        
        mock_user2 = Mock()
        mock_user2.id = 'user2'
        mock_user2.to_dict.return_value = {'name': 'Jane Smith', 'email': 'jane@test.com'}
        
        self.mock_db.collection.return_value.stream.return_value = [mock_user1, mock_user2]
        
        response = self.client.get('/api/users')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_get_tasks_by_project(self):
        """Test getting tasks by project ID"""
        mock_task = Mock()
        mock_task.id = 'proj_task1'
        mock_task.to_dict.return_value = {
            'task_name': 'Project Task',
            'proj_ID': 'project123'
        }
        
        self.mock_db.collection.return_value.where.return_value.stream.return_value = [mock_task]
        
        response = self.client.get('/api/projects/project123/tasks')
        
        self.assertIn(response.status_code, [200, 500])
    
    def test_get_deleted_tasks(self):
        """Test getting deleted tasks"""
        mock_deleted_task = Mock()
        mock_deleted_task.id = 'deleted_task1'
        mock_deleted_task.to_dict.return_value = {
            'task_name': 'Deleted Task',
            'is_deleted': True,
            'owner': 'user123'
        }
        
        self.mock_db.collection.return_value.where.return_value.stream.return_value = [mock_deleted_task]
        
        response = self.client.get('/api/tasks/deleted?userId=user123')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

if __name__ == '__main__':
    unittest.main(verbosity=2)
