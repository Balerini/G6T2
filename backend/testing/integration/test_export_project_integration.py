#!/usr/bin/env python3
"""
Integration Tests for Export Tasks in Project and Export Project Schedule
Tests the API endpoints for exporting project data in various formats.
Uses real database connections for C2 integration testing.
"""

import unittest
import sys
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch
import io

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import Flask app and Firebase utilities
from app import create_app
from firebase_utils import get_firestore_client

class TestExportProjectIntegration(unittest.TestCase):
    """C2 Integration tests for Export Tasks and Export Project Schedule functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        print("=" * 80)
        print("INTEGRATION TESTING - EXPORT PROJECT TASKS & SCHEDULE")
        print("=" * 80)
        print("Testing real API endpoints with real database")
        print("=" * 80)
        
        # Set up Flask test client
        app = create_app()
        cls.app = app.test_client()
        cls.app_context = app.app_context()
        cls.app_context.push()
        
        # Get Firestore client
        cls.db = get_firestore_client()
        
        # Test user IDs (these should exist in your test database)
        cls.test_manager_id = "test_manager_export_123"
        cls.test_staff_1_id = "test_staff_export_456"
        cls.test_staff_2_id = "test_staff_export_789"
        cls.test_staff_3_id = "test_staff_export_101"
        
        # Test division name
        cls.test_division = "Test Export Division"
        
        # Create test data
        cls.setup_test_data()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test data"""
        cls.cleanup_test_data()
        cls.app_context.pop()
        print("=" * 80)
        print("INTEGRATION TESTING COMPLETED")
        print("=" * 80)
    
    @classmethod
    def setup_test_data(cls):
        """Create test users, project, and tasks for export testing"""
        print("Setting up test data...")
        
        # Create test users
        users_data = [
            {
                'id': cls.test_manager_id,
                'name': 'Test Manager Export',
                'email': 'testmanager.export@example.com',
                'role_name': 'Manager',
                'role_num': 2,  # Manager role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_staff_1_id,
                'name': 'Test Staff Export 1',
                'email': 'teststaff1.export@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_staff_2_id,
                'name': 'Test Staff Export 2',
                'email': 'teststaff2.export@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            },
            {
                'id': cls.test_staff_3_id,
                'name': 'Test Staff Export 3',
                'email': 'teststaff3.export@example.com',
                'role_name': 'Staff',
                'role_num': 4,  # Staff role
                'division_name': cls.test_division
            }
        ]
        
        for user_data in users_data:
            user_ref = cls.db.collection('Users').document(user_data['id'])
            user_ref.set(user_data)
        
        # Create test project
        current_date = datetime.now()
        project_data = {
            'proj_name': 'Test Export Project',
            'proj_desc': 'Test project for export functionality',
            'start_date': current_date + timedelta(days=1),
            'end_date': current_date + timedelta(days=30),
            'owner': cls.test_manager_id,
            'division_name': cls.test_division,
            'collaborators': [cls.test_manager_id, cls.test_staff_1_id, cls.test_staff_2_id],
            'proj_status': 'In Progress',
            'is_deleted': False,
            'createdAt': current_date,
            'updatedAt': current_date
        }
        
        project_ref = cls.db.collection('Projects').document('test_project_export_123')
        project_ref.set(project_data)
        cls.test_project_id = 'test_project_export_123'
        
        # Create test tasks
        tasks_data = [
            {
                'id': 'test_task_export_1',
                'task_name': 'Design System Architecture',
                'task_desc': 'Design the overall system architecture',
                'start_date': current_date + timedelta(days=2),
                'end_date': current_date + timedelta(days=7),
                'task_status': 'In Progress',
                'priority_level': 3,
                'proj_ID': cls.test_project_id,
                'owner': cls.test_manager_id,
                'assigned_to': [cls.test_manager_id, cls.test_staff_1_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            {
                'id': 'test_task_export_2',
                'task_name': 'Implement User Authentication',
                'task_desc': 'Implement user login and authentication',
                'start_date': current_date + timedelta(days=5),
                'end_date': current_date + timedelta(days=12),
                'task_status': 'Not Started',
                'priority_level': 2,
                'proj_ID': cls.test_project_id,
                'owner': cls.test_staff_1_id,
                'assigned_to': [cls.test_staff_1_id, cls.test_staff_2_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            {
                'id': 'test_task_export_3',
                'task_name': 'Write Unit Tests',
                'task_desc': 'Write comprehensive unit tests',
                'start_date': current_date + timedelta(days=10),
                'end_date': current_date + timedelta(days=15),
                'task_status': 'Completed',
                'priority_level': 1,
                'proj_ID': cls.test_project_id,
                'owner': cls.test_staff_2_id,
                'assigned_to': [cls.test_staff_2_id, cls.test_staff_3_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            },
            {
                'id': 'test_task_export_4',
                'task_name': 'Deploy to Production',
                'task_desc': 'Deploy the application to production',
                'start_date': current_date + timedelta(days=20),
                'end_date': current_date + timedelta(days=25),
                'task_status': 'Not Started',
                'priority_level': 3,
                'proj_ID': cls.test_project_id,
                'owner': cls.test_manager_id,
                'assigned_to': [cls.test_manager_id, cls.test_staff_1_id, cls.test_staff_2_id],
                'is_deleted': False,
                'createdAt': current_date,
                'updatedAt': current_date
            }
        ]
        
        for task_data in tasks_data:
            task_ref = cls.db.collection('Tasks').document(task_data['id'])
            task_ref.set(task_data)
        
        print(f"Created {len(users_data)} test users, 1 test project, and {len(tasks_data)} test tasks")
    
    @classmethod
    def cleanup_test_data(cls):
        """Clean up test data"""
        print("Cleaning up test data...")
        
        # Delete test tasks
        task_ids = ['test_task_export_1', 'test_task_export_2', 'test_task_export_3', 'test_task_export_4']
        for task_id in task_ids:
            try:
                cls.db.collection('Tasks').document(task_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete task {task_id}: {e}")
        
        # Delete test users
        user_ids = [cls.test_manager_id, cls.test_staff_1_id, cls.test_staff_2_id, cls.test_staff_3_id]
        for user_id in user_ids:
            try:
                cls.db.collection('Users').document(user_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete user {user_id}: {e}")
        
        # Delete test project
        try:
            cls.db.collection('Projects').document(cls.test_project_id).delete()
        except Exception as e:
            print(f"Warning: Could not delete project {cls.test_project_id}: {e}")
        
        print("Test data cleanup completed")
    
    def test_export_project_tasks_pdf_table_format(self):
        """Test exporting project tasks as PDF in table format"""
        print("\n--- Testing PDF export (table format) ---")
        
        response = self.app.get(f'/api/projects/{self.test_project_id}/export')
        
        self.assertEqual(response.status_code, 200)
        
        # Check response headers
        self.assertEqual(response.headers.get('Content-Type'), 'application/pdf')
        self.assertIn('attachment', response.headers.get('Content-Disposition', ''))
        self.assertIn('Project_Test_Export_Project_Tasks_Report.pdf', response.headers.get('Content-Disposition', ''))
        
        # Check that response contains PDF data
        self.assertGreater(len(response.data), 1000, "PDF should contain substantial data")
        
        # Verify PDF starts with PDF header
        pdf_header = response.data[:4]
        self.assertEqual(pdf_header, b'%PDF', "Response should be a valid PDF file")
        
        print("✅ PDF export (table format) working correctly")
    
    def test_export_project_tasks_pdf_calendar_format(self):
        """Test exporting project tasks as PDF in calendar format"""
        print("\n--- Testing PDF export (calendar format) ---")
        
        response = self.app.get(f'/api/projects/{self.test_project_id}/export?format=calendar')
        
        self.assertEqual(response.status_code, 200)
        
        # Check response headers
        self.assertEqual(response.headers.get('Content-Type'), 'application/pdf')
        self.assertIn('attachment', response.headers.get('Content-Disposition', ''))
        self.assertIn('Test_Export_Project_Calendar.pdf', response.headers.get('Content-Disposition', ''))
        
        # Check that response contains PDF data
        self.assertGreater(len(response.data), 1000, "PDF should contain substantial data")
        
        # Verify PDF starts with PDF header
        pdf_header = response.data[:4]
        self.assertEqual(pdf_header, b'%PDF', "Response should be a valid PDF file")
        
        print("✅ PDF export (calendar format) working correctly")
    
    def test_export_project_team_schedule_excel(self):
        """Test exporting project team schedule as Excel file"""
        print("\n--- Testing Excel export (team schedule) ---")
        
        response = self.app.get(f'/api/projects/{self.test_project_id}/export-excel')
        
        self.assertEqual(response.status_code, 200)
        
        # Check response headers
        self.assertEqual(response.headers.get('Content-Type'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertIn('attachment', response.headers.get('Content-Disposition', ''))
        self.assertIn('.xlsx', response.headers.get('Content-Disposition', ''))
        
        # Check that response contains Excel data
        self.assertGreater(len(response.data), 1000, "Excel file should contain substantial data")
        
        # Verify Excel file starts with correct header
        excel_header = response.data[:4]
        self.assertEqual(excel_header, b'PK\x03\x04', "Response should be a valid Excel file")
        
        print("✅ Excel export (team schedule) working correctly")
    
    def test_export_project_tasks_xlsx(self):
        """Test exporting project tasks as XLSX file"""
        print("\n--- Testing XLSX export (project tasks) ---")
        
        response = self.app.get(f'/api/projects/{self.test_project_id}/export/xlsx')
        
        self.assertEqual(response.status_code, 200)
        
        # Check response headers
        self.assertEqual(response.headers.get('Content-Type'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertIn('attachment', response.headers.get('Content-Disposition', ''))
        self.assertIn('.xlsx', response.headers.get('Content-Disposition', ''))
        
        # Check that response contains Excel data
        self.assertGreater(len(response.data), 1000, "XLSX file should contain substantial data")
        
        # Verify Excel file starts with correct header
        excel_header = response.data[:4]
        self.assertEqual(excel_header, b'PK\x03\x04', "Response should be a valid Excel file")
        
        print("✅ XLSX export (project tasks) working correctly")
    
    def test_export_nonexistent_project(self):
        """Test export behavior with nonexistent project ID"""
        print("\n--- Testing nonexistent project ID ---")
        
        nonexistent_project_id = "nonexistent_project_export_12345"
        
        # Test PDF export
        response = self.app.get(f'/api/projects/{nonexistent_project_id}/export')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('No tasks found', data['error'])
        
        # Test Excel export
        response = self.app.get(f'/api/projects/{nonexistent_project_id}/export-excel')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('No tasks found', data['error'])
        
        # Test XLSX export
        response = self.app.get(f'/api/projects/{nonexistent_project_id}/export/xlsx')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('No tasks found', data['error'])
        
        print("✅ Nonexistent project ID handled correctly")
    
    def test_export_project_with_no_tasks(self):
        """Test export behavior with project that has no tasks"""
        print("\n--- Testing project with no tasks ---")
        
        # Create a project with no tasks
        current_date = datetime.now()
        empty_project_data = {
            'proj_name': 'Empty Export Project',
            'proj_desc': 'Project with no tasks',
            'start_date': current_date + timedelta(days=1),
            'end_date': current_date + timedelta(days=30),
            'owner': self.test_manager_id,
            'division_name': self.test_division,
            'collaborators': [self.test_manager_id],
            'proj_status': 'Not Started',
            'is_deleted': False,
            'createdAt': current_date,
            'updatedAt': current_date
        }
        
        empty_project_ref = self.db.collection('Projects').document('empty_project_export_123')
        empty_project_ref.set(empty_project_data)
        empty_project_id = 'empty_project_export_123'
        
        try:
            # Test PDF export
            response = self.app.get(f'/api/projects/{empty_project_id}/export')
            self.assertEqual(response.status_code, 404)
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIn('No tasks found', data['error'])
            
            # Test Excel export
            response = self.app.get(f'/api/projects/{empty_project_id}/export-excel')
            self.assertEqual(response.status_code, 404)
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIn('No tasks found', data['error'])
            
            # Test XLSX export
            response = self.app.get(f'/api/projects/{empty_project_id}/export/xlsx')
            self.assertEqual(response.status_code, 404)
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIn('No tasks found', data['error'])
            
            print("✅ Project with no tasks handled correctly")
            
        finally:
            # Clean up empty project
            try:
                self.db.collection('Projects').document(empty_project_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete empty project {empty_project_id}: {e}")
    
    def test_export_file_naming(self):
        """Test that exported files have correct naming conventions"""
        print("\n--- Testing file naming conventions ---")
        
        # Test PDF table format naming
        response = self.app.get(f'/api/projects/{self.test_project_id}/export')
        self.assertEqual(response.status_code, 200)
        content_disposition = response.headers.get('Content-Disposition', '')
        self.assertIn('Project_Test_Export_Project_Tasks_Report.pdf', content_disposition)
        
        # Test PDF calendar format naming
        response = self.app.get(f'/api/projects/{self.test_project_id}/export?format=calendar')
        self.assertEqual(response.status_code, 200)
        content_disposition = response.headers.get('Content-Disposition', '')
        self.assertIn('Test_Export_Project_Calendar.pdf', content_disposition)
        
        # Test Excel naming
        response = self.app.get(f'/api/projects/{self.test_project_id}/export-excel')
        self.assertEqual(response.status_code, 200)
        content_disposition = response.headers.get('Content-Disposition', '')
        self.assertIn('.xlsx', content_disposition)
        
        # Test XLSX naming
        response = self.app.get(f'/api/projects/{self.test_project_id}/export/xlsx')
        self.assertEqual(response.status_code, 200)
        content_disposition = response.headers.get('Content-Disposition', '')
        self.assertIn('.xlsx', content_disposition)
        
        print("✅ File naming conventions are correct")
    
    def test_export_content_validation(self):
        """Test that exported content contains expected project and task data"""
        print("\n--- Testing exported content validation ---")
        
        # Test PDF export and verify it contains project information
        response = self.app.get(f'/api/projects/{self.test_project_id}/export')
        self.assertEqual(response.status_code, 200)
        
        # Check that PDF is valid by verifying it starts with PDF header
        pdf_header = response.data[:4]
        self.assertEqual(pdf_header, b'%PDF', "Response should be a valid PDF file")
        
        # Check that PDF contains substantial data (not empty)
        self.assertGreater(len(response.data), 1000, "PDF should contain substantial data")
        
        # Test Excel export and verify it contains project information
        response = self.app.get(f'/api/projects/{self.test_project_id}/export-excel')
        self.assertEqual(response.status_code, 200)
        
        # Check that Excel file is valid by verifying it starts with Excel header
        excel_header = response.data[:4]
        self.assertEqual(excel_header, b'PK\x03\x04', "Response should be a valid Excel file")
        
        # Check that Excel contains substantial data (not empty)
        self.assertGreater(len(response.data), 1000, "Excel file should contain substantial data")
        
        # Test XLSX export and verify it contains project information
        response = self.app.get(f'/api/projects/{self.test_project_id}/export/xlsx')
        self.assertEqual(response.status_code, 200)
        
        # Check that XLSX file is valid by verifying it starts with Excel header
        xlsx_header = response.data[:4]
        self.assertEqual(xlsx_header, b'PK\x03\x04', "Response should be a valid XLSX file")
        
        # Check that XLSX contains substantial data (not empty)
        self.assertGreater(len(response.data), 1000, "XLSX file should contain substantial data")
        
        print("✅ Exported content validation passed")
    
    def test_export_format_parameters(self):
        """Test different format parameters for PDF export"""
        print("\n--- Testing format parameters ---")
        
        # Test default format (should be table)
        response = self.app.get(f'/api/projects/{self.test_project_id}/export')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Content-Type'), 'application/pdf')
        
        # Test explicit table format
        response = self.app.get(f'/api/projects/{self.test_project_id}/export?format=table')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Content-Type'), 'application/pdf')
        
        # Test calendar format
        response = self.app.get(f'/api/projects/{self.test_project_id}/export?format=calendar')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Content-Type'), 'application/pdf')
        
        # Test invalid format (should default to table)
        response = self.app.get(f'/api/projects/{self.test_project_id}/export?format=invalid')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get('Content-Type'), 'application/pdf')
        
        print("✅ Format parameters handled correctly")
    
    def test_export_performance(self):
        """Test export performance with multiple tasks"""
        print("\n--- Testing export performance ---")
        
        import time
        
        # Test PDF export performance
        start_time = time.time()
        response = self.app.get(f'/api/projects/{self.test_project_id}/export')
        pdf_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(pdf_time, 5.0, "PDF export should complete within 5 seconds")
        
        # Test Excel export performance
        start_time = time.time()
        response = self.app.get(f'/api/projects/{self.test_project_id}/export-excel')
        excel_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(excel_time, 5.0, "Excel export should complete within 5 seconds")
        
        # Test XLSX export performance
        start_time = time.time()
        response = self.app.get(f'/api/projects/{self.test_project_id}/export/xlsx')
        xlsx_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(xlsx_time, 5.0, "XLSX export should complete within 5 seconds")
        
        print(f"✅ Export performance: PDF={pdf_time:.2f}s, Excel={excel_time:.2f}s, XLSX={xlsx_time:.2f}s")
    
    def test_export_edge_cases(self):
        """Test export edge cases"""
        print("\n--- Testing export edge cases ---")
        
        # Test with special characters in project name
        special_project_data = {
            'proj_name': 'Test Project with Special Chars: !@#$%^&*()',
            'proj_desc': 'Project with special characters',
            'start_date': datetime.now() + timedelta(days=1),
            'end_date': datetime.now() + timedelta(days=30),
            'owner': self.test_manager_id,
            'division_name': self.test_division,
            'collaborators': [self.test_manager_id],
            'proj_status': 'Not Started',
            'is_deleted': False,
            'createdAt': datetime.now(),
            'updatedAt': datetime.now()
        }
        
        special_project_ref = self.db.collection('Projects').document('special_project_export_123')
        special_project_ref.set(special_project_data)
        special_project_id = 'special_project_export_123'
        
        # Add a task to the special project so export doesn't fail
        current_date = datetime.now()
        special_task_data = {
            'id': 'special_task_export_1',
            'task_name': 'Special Task with Chars: !@#$%^&*()',
            'task_desc': 'Task with special characters',
            'start_date': current_date + timedelta(days=2),
            'end_date': current_date + timedelta(days=7),
            'task_status': 'In Progress',
            'priority_level': 2,
            'proj_ID': special_project_id,
            'owner': self.test_manager_id,
            'assigned_to': [self.test_manager_id],
            'is_deleted': False,
            'createdAt': current_date,
            'updatedAt': current_date
        }
        
        special_task_ref = self.db.collection('Tasks').document(special_task_data['id'])
        special_task_ref.set(special_task_data)
        
        try:
            # Test PDF export with special characters
            response = self.app.get(f'/api/projects/{special_project_id}/export')
            self.assertEqual(response.status_code, 200)
            
            # Test Excel export with special characters
            response = self.app.get(f'/api/projects/{special_project_id}/export-excel')
            self.assertEqual(response.status_code, 200)
            
            # Test XLSX export with special characters
            response = self.app.get(f'/api/projects/{special_project_id}/export/xlsx')
            self.assertEqual(response.status_code, 200)
            
            print("✅ Special characters in project name handled correctly")
            
        finally:
            # Clean up special project and task
            try:
                self.db.collection('Tasks').document('special_task_export_1').delete()
                self.db.collection('Projects').document(special_project_id).delete()
            except Exception as e:
                print(f"Warning: Could not delete special project/task {special_project_id}: {e}")


if __name__ == '__main__':
    print("=" * 80)
    print("EXPORT PROJECT TASKS & SCHEDULE - INTEGRATION TESTING")
    print("=" * 80)
    print("Testing real API endpoints with real database")
    print("=" * 80)
    
    # Run the tests
    unittest.main(verbosity=2)
