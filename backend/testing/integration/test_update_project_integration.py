#!/usr/bin/env python3
"""
REAL Integration tests for Update Project Details (SCRUM-73).
Tests the complete flow: API → Backend → Firebase Database
"""

import unittest
import sys
import os
import json
from datetime import datetime, timedelta
import time

# FIXED PATH SETUP - This will definitely work
# Get absolute path to this file
current_file = os.path.abspath(__file__)
print(f"Test file location: {current_file}")

# Go up from integration/ -> testing/ -> backend/
integration_dir = os.path.dirname(current_file)
testing_dir = os.path.dirname(integration_dir)
backend_dir = os.path.dirname(testing_dir)

print(f"Backend directory: {backend_dir}")

# Add backend to Python path
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Verify app.py exists
app_py_path = os.path.join(backend_dir, 'app.py')
print(f"Looking for app.py at: {app_py_path}")
print(f"app.py exists: {os.path.exists(app_py_path)}")

# Set Firebase credentials
service_account_path = os.path.join(backend_dir, 'service-account.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path
print(f"Firebase credentials path: {service_account_path}")
print(f"service-account.json exists: {os.path.exists(service_account_path)}")

# Now try imports
print("\nAttempting imports...")
try:
    from app import create_app
    print("✅ Successfully imported create_app from app")
except ImportError as e:
    print(f"❌ Failed to import app: {e}")
    print("\nFiles in backend directory:")
    for f in os.listdir(backend_dir):
        if f.endswith('.py'):
            print(f"  - {f}")
    sys.exit(1)

try:
    from firebase_utils import get_firestore_client
    print("✅ Successfully imported get_firestore_client from firebase_utils")
except ImportError as e:
    print(f"❌ Failed to import firebase_utils: {e}")
    sys.exit(1)


class TestUpdateProjectIntegration(unittest.TestCase):
    """REAL Integration tests for updating project details (SCRUM-73)"""
    
    def setUp(self):
        """Set up test client with REAL database"""
        print("\n" + "="*60)
        print("Setting up test...")
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Use REAL Firestore client
        self.db = get_firestore_client()
        
        # Track test data for cleanup
        self.test_project_ids = []
        self.test_user_ids = []
        
        # Set up real test data
        self.setup_test_users()
        self.setup_test_project()
        print("Test setup complete!")
    
    def tearDown(self):
        """Clean up REAL test data from database"""
        print("\nCleaning up test data...")
        for project_id in self.test_project_ids:
            try:
                self.db.collection('Projects').document(project_id).delete()
            except:
                pass
        
        for user_id in self.test_user_ids:
            try:
                self.db.collection('Users').document(user_id).delete()
            except:
                pass
        print("Cleanup complete!")
    
    def setup_test_users(self):
        """Create REAL test users"""
        users = [
            {
                "id": "update_proj_owner_123", 
                "name": "Update Project Owner", 
                "email": "owner@test.com", 
                "role_name": "Manager",
                "role_num": 3,
                "division_name": "Engineering"
            },
            {
                "id": "update_proj_collab_456", 
                "name": "Project Collaborator", 
                "email": "collab@test.com", 
                "role_name": "Staff",
                "role_num": 4,
                "division_name": "Engineering"
            },
            {
                "id": "update_proj_collab_789", 
                "name": "Another Collaborator", 
                "email": "collab2@test.com", 
                "role_name": "Staff",
                "role_num": 4,
                "division_name": "Engineering"
            }
        ]
        
        for user in users:
            user_id = user.pop("id")
            user["created_at"] = datetime.now()
            self.db.collection('Users').document(user_id).set(user)
            self.test_user_ids.append(user_id)
    
    def setup_test_project(self):
        """Create REAL test project"""
        future_start = datetime.now() + timedelta(days=1)
        future_end = datetime.now() + timedelta(days=30)
        
        project_data = {
            "proj_name": "Original Test Project",
            "proj_desc": "Original description for testing",
            "start_date": future_start,
            "end_date": future_end,
            "owner": "update_proj_owner_123",
            "collaborators": ["update_proj_owner_123", "update_proj_collab_456"],
            "division_name": "Engineering",
            "proj_status": "Not Started",
            "createdAt": datetime.now()
        }
        doc_ref = self.db.collection('Projects').add(project_data)[1]
        self.test_project_ids.append(doc_ref.id)
        return doc_ref.id

    # ==================== AC TEST 1: Valid Update with All Required Fields ====================
    def test_update_project_all_required_fields_integration(self):
        """
        AC: Owner must fill in all required fields before saving
        AC: Updated details reflected on screen upon saving
        AC: Updates saved within 3 seconds
        Test API → Backend → Database integration for valid update
        """
        project_id = self.test_project_ids[0]
        
        # Verify project exists before update
        project_doc = self.db.collection('Projects').document(project_id).get()
        self.assertTrue(project_doc.exists)
        original_data = project_doc.to_dict()
        self.assertEqual(original_data['proj_name'], "Original Test Project")
        
        # Prepare valid update data
        future_start = datetime.now() + timedelta(days=2)
        future_end = datetime.now() + timedelta(days=60)
        
        update_data = {
            "proj_name": "Updated Test Project Name",
            "proj_desc": "Updated project description",
            "start_date": future_start.isoformat(),
            "end_date": future_end.isoformat(),
            "owner": "update_proj_owner_123",
            "collaborators": ["update_proj_owner_123", "update_proj_collab_456", "update_proj_collab_789"],
            "division_name": "Engineering",
            "proj_status": "In Progress"
        }
        
        # Measure response time (AC: within 3 seconds)
        start_time = time.time()
        
        # Update via API
        response = self.client.put(
            f'/api/projects/{project_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Should succeed
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Project updated successfully')
        
        # AC: Response time under 3 seconds
        self.assertLess(response_time, 3.0, 
                       f"Response took {response_time:.2f}s, should be < 3s")
        
        # Verify API → Database integration by checking database directly
        project_doc_after = self.db.collection('Projects').document(project_id).get()
        self.assertTrue(project_doc_after.exists)
        updated_data = project_doc_after.to_dict()
        
        # AC: Updated details immediately reflected
        self.assertEqual(updated_data['proj_name'], "Updated Test Project Name")
        self.assertEqual(updated_data['proj_desc'], "Updated project description")
        self.assertEqual(updated_data['owner'], "update_proj_owner_123")
        self.assertEqual(updated_data['proj_status'], "In Progress")
        self.assertEqual(len(updated_data['collaborators']), 3)
        self.assertIn("update_proj_collab_789", updated_data['collaborators'])
        
        print(f"✅ API → Database integration verified: Update completed in {response_time:.2f}s")

    # ==================== AC TEST 2: Missing Project Name ====================
    def test_update_project_missing_required_field_integration(self):
        """
        AC: Inline validation shows which required fields are missing
        Test error handling when project_name is missing
        """
        project_id = self.test_project_ids[0]
        
        # Missing required field: proj_name
        invalid_data = {
            "proj_desc": "Description without name",
            "start_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=60)).isoformat(),
            "owner": "update_proj_owner_123",
            "collaborators": ["update_proj_owner_123"]
        }
        
        response = self.client.put(
            f'/api/projects/{project_id}',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        # Should return 400 Bad Request
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('proj_name', response_data['error'].lower())
        
        # Verify database unchanged
        project_doc = self.db.collection('Projects').document(project_id).get()
        project_data = project_doc.to_dict()
        self.assertEqual(project_data['proj_name'], "Original Test Project")
        
        print("✅ Missing required field rejected, database unchanged")

    # ==================== AC TEST 3: Empty Collaborators ====================
    def test_update_project_empty_collaborators_integration(self):
        """
        AC: At least 1 collaborator required
        Test validation for empty collaborators list
        """
        project_id = self.test_project_ids[0]
        
        invalid_data = {
            "proj_name": "Test Project",
            "proj_desc": "Description",
            "start_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=60)).isoformat(),
            "owner": "update_proj_owner_123",
            "collaborators": []  # Empty collaborators
        }
        
        response = self.client.put(
            f'/api/projects/{project_id}',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        # Should return 400
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('collaborator', response_data['error'].lower())
        
        print("✅ Empty collaborators rejected")

    # ==================== AC TEST 4: Invalid Date Range ====================
    def test_update_project_invalid_date_range_integration(self):
        """
        AC: End date must be after start date
        Test date validation integration
        """
        project_id = self.test_project_ids[0]
        
        # End date before start date
        invalid_data = {
            "proj_name": "Test Project",
            "proj_desc": "Description",
            "start_date": (datetime.now() + timedelta(days=60)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=2)).isoformat(),  # Before start
            "owner": "update_proj_owner_123",
            "collaborators": ["update_proj_owner_123"]
        }
        
        response = self.client.put(
            f'/api/projects/{project_id}',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        # Should return 400
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertTrue('after' in response_data['error'].lower() or 
                       'date' in response_data['error'].lower())
        
        print("✅ Invalid date range rejected")

    # ==================== AC TEST 5: Project Name Too Short ====================
    def test_update_project_name_too_short_integration(self):
        """
        AC: Project name must be at least 3 characters
        Test name length validation
        """
        project_id = self.test_project_ids[0]
        
        invalid_data = {
            "proj_name": "AB",  # Only 2 characters
            "proj_desc": "Description",
            "start_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=60)).isoformat(),
            "owner": "update_proj_owner_123",
            "collaborators": ["update_proj_owner_123"]
        }
        
        response = self.client.put(
            f'/api/projects/{project_id}',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        # Should return 400
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('3', response_data['error'])
        
        print("✅ Short project name rejected")

    # ==================== AC TEST 6: Nonexistent Project ====================
    def test_update_nonexistent_project_integration(self):
        """
        AC: Proper error handling
        Test error handling for non-existent project
        """
        fake_project_id = "nonexistent_project_12345"
        
        valid_data = {
            "proj_name": "Test Project",
            "proj_desc": "Description",
            "start_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=60)).isoformat(),
            "owner": "update_proj_owner_123",
            "collaborators": ["update_proj_owner_123"]
        }
        
        response = self.client.put(
            f'/api/projects/{fake_project_id}',
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        
        # Should return 404
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.data)
        self.assertIn('not found', response_data['error'].lower())
        
        print("✅ Nonexistent project returns 404")

    # ==================== AC TEST 7: Data Persistence ====================
    def test_update_project_data_persistence_integration(self):
        """
        AC: Updated details are immediately reflected on screen
        Test that updates persist by fetching after update
        """
        project_id = self.test_project_ids[0]
        
        # Update project
        update_data = {
            "proj_name": "Persistence Test Project",
            "proj_desc": "Testing data persistence",
            "start_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=60)).isoformat(),
            "owner": "update_proj_owner_123",
            "collaborators": ["update_proj_owner_123", "update_proj_collab_456"]
        }
        
        update_response = self.client.put(
            f'/api/projects/{project_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(update_response.status_code, 200)
        
        # Fetch project again via API
        get_response = self.client.get(f'/api/projects/{project_id}')
        self.assertEqual(get_response.status_code, 200)
        fetched_data = json.loads(get_response.data)
        
        # Verify data persisted
        self.assertEqual(fetched_data['proj_name'], "Persistence Test Project")
        self.assertEqual(fetched_data['proj_desc'], "Testing data persistence")
        
        # Also verify in database directly
        db_doc = self.db.collection('Projects').document(project_id).get()
        db_data = db_doc.to_dict()
        self.assertEqual(db_data['proj_name'], "Persistence Test Project")
        
        print("✅ Data persistence verified: API → Database → API")

    # ==================== AC TEST 8: Owner Auto-Added to Collaborators ====================
    def test_update_project_owner_auto_added_integration(self):
        """
        Test that owner is automatically added to collaborators if not present
        """
        project_id = self.test_project_ids[0]
        
        update_data = {
            "proj_name": "Auto-Add Owner Test",
            "proj_desc": "Testing owner auto-add",
            "start_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=60)).isoformat(),
            "owner": "update_proj_owner_123",
            "collaborators": ["update_proj_collab_456"]  # Owner not in list
        }
        
        response = self.client.put(
            f'/api/projects/{project_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify owner added to collaborators
        db_doc = self.db.collection('Projects').document(project_id).get()
        db_data = db_doc.to_dict()
        self.assertIn("update_proj_owner_123", db_data['collaborators'])
        
        print("✅ Owner automatically added to collaborators")

    # ==================== AC TEST 9: Response Time with Large Data ====================
    def test_update_project_large_data_performance_integration(self):
        """
        AC: Updates saved within 3 seconds (even with many collaborators)
        Test performance with large collaborator list
        """
        project_id = self.test_project_ids[0]
        
        # Create update with many collaborators
        large_collab_list = ["update_proj_owner_123"] + [f"collab_{i}" for i in range(50)]
        
        update_data = {
            "proj_name": "Large Data Test",
            "proj_desc": "Testing with many collaborators",
            "start_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=60)).isoformat(),
            "owner": "update_proj_owner_123",
            "collaborators": large_collab_list
        }
        
        start_time = time.time()
        
        response = self.client.put(
            f'/api/projects/{project_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        response_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 3.0,
                       f"Large data update took {response_time:.2f}s, exceeds 3s limit")
        
        print(f"✅ Large data update completed in {response_time:.2f}s")

    # ==================== AC TEST 10: Multiple Sequential Updates ====================
    def test_multiple_updates_integration(self):
        """
        AC: Each update completes within 3 seconds
        Test multiple sequential updates
        """
        project_id = self.test_project_ids[0]
        update_count = 3
        
        for i in range(update_count):
            update_data = {
                "proj_name": f"Update Iteration {i+1}",
                "proj_desc": f"Description for iteration {i+1}",
                "start_date": (datetime.now() + timedelta(days=2+i)).isoformat(),
                "end_date": (datetime.now() + timedelta(days=60+i)).isoformat(),
                "owner": "update_proj_owner_123",
                "collaborators": ["update_proj_owner_123"]
            }
            
            start_time = time.time()
            
            response = self.client.put(
                f'/api/projects/{project_id}',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            response_time = time.time() - start_time
            
            self.assertEqual(response.status_code, 200)
            self.assertLess(response_time, 3.0,
                           f"Update {i+1} took {response_time:.2f}s")
            
            # Verify each update persisted
            db_doc = self.db.collection('Projects').document(project_id).get()
            db_data = db_doc.to_dict()
            self.assertEqual(db_data['proj_name'], f"Update Iteration {i+1}")
        
        print(f"✅ {update_count} sequential updates all under 3s")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("SCRUM-73 INTEGRATION TESTS: Update Project Details")
    print("="*60)
    unittest.main(verbosity=2)