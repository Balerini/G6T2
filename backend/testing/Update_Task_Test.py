import unittest
from copy import deepcopy
from datetime import datetime

from .remove_completed_tasks_test import TaskApiTestCaseBase


class TestUpdateTaskFlow(TaskApiTestCaseBase):
    """Regression suite for task update behaviours."""

    OWNER_HEADERS = {
        'X-User-Id': 'user-1',
        'X-User-Role': '4',
        'X-User-Name': 'Owner One',
    }

    def test_owner_can_update_all_fields(self):
        payload = {
            'task_name': 'Revised Task Name',
            'task_desc': 'Updated description for the task.',
            'task_status': 'Under Review',
            'start_date': '2025-02-01',
            'end_date': '2025-02-10',
            'assigned_to': ['user-1', 'user-3'],
        }

        response = self.client.put(
            '/api/tasks/task-review',
            json=payload,
            headers=self.OWNER_HEADERS,
        )
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body['task_name'], payload['task_name'])
        self.assertEqual(body['task_desc'], payload['task_desc'])
        self.assertEqual(body['task_status'], payload['task_status'])

        stored = (
            self.fake_firestore
            .collection('Tasks')
            .document('task-review')
            .get()
            .to_dict()
        )
        self.assertEqual(stored['task_name'], payload['task_name'])
        self.assertEqual(stored['task_desc'], payload['task_desc'])
        self.assertEqual(stored['task_status'], payload['task_status'])
        self.assertEqual(stored['assigned_to'], payload['assigned_to'])
        self.assertEqual(stored['start_date'].date(), datetime(2025, 2, 1).date())
        self.assertEqual(stored['end_date'].date(), datetime(2025, 2, 10).date())

    def test_update_with_no_fields_returns_noop(self):
        before = (
            self.fake_firestore
            .collection('Tasks')
            .document('task-review')
            .get()
            .to_dict()
        )
        response = self.client.put(
            '/api/tasks/task-review',
            json={},
            headers=self.OWNER_HEADERS,
        )
        self.assertEqual(response.status_code, 200)
        stored = (
            self.fake_firestore
            .collection('Tasks')
            .document('task-review')
            .get()
            .to_dict()
        )
        for key in ('task_name', 'task_desc', 'task_status', 'assigned_to'):
            self.assertEqual(stored.get(key), before.get(key))

    def test_invalid_payload_format_returns_400(self):
        response = self.client.put(
            '/api/tasks/task-review',
            data='"not-an-object"',
            headers=self.OWNER_HEADERS,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid payload format', response.get_json()['error'])

    def test_collaborator_can_update_description_and_status(self):
        # Add collaborator to the task
        self.fake_firestore._data['Tasks']['task-review']['assigned_to'] = ['user-1', 'user-2']

        collaborator_headers = {
            'X-User-Id': 'user-2',
            'X-User-Role': '4',
            'X-User-Name': 'Collaborator Two',
        }
        payload = {
            'task_desc': 'Collaborator amended the description.',
            'task_status': 'Ongoing',
        }

        response = self.client.put(
            '/api/tasks/task-review',
            json=payload,
            headers=collaborator_headers,
        )
        self.assertEqual(response.status_code, 200)

        stored = (
            self.fake_firestore
            .collection('Tasks')
            .document('task-review')
            .get()
            .to_dict()
        )
        self.assertEqual(stored['task_desc'], payload['task_desc'])
        self.assertEqual(stored['task_status'], payload['task_status'])
        self.assertEqual(stored['task_name'], 'Draft SOP')

    def test_collaborator_cannot_edit_restricted_fields(self):
        self.fake_firestore._data['Tasks']['task-review']['assigned_to'] = ['user-1', 'user-2']

        collaborator_headers = {
            'X-User-Id': 'user-2',
            'X-User-Role': '4',
            'X-User-Name': 'Collaborator Two',
        }
        payload = {'task_name': 'Unauthorized change'}

        response = self.client.put(
            '/api/tasks/task-review',
            json=payload,
            headers=collaborator_headers,
        )
        self.assertEqual(response.status_code, 200)
        stored = (
            self.fake_firestore
            .collection('Tasks')
            .document('task-review')
            .get()
            .to_dict()
        )
        self.assertEqual(stored['task_name'], 'Draft SOP')

    def test_status_change_logged_with_staff_details(self):
        payload = {'task_status': 'Completed'}

        response = self.client.put(
            '/api/tasks/task-review',
            json=payload,
            headers=self.OWNER_HEADERS,
        )
        self.assertEqual(response.status_code, 200)

        stored = (
            self.fake_firestore
            .collection('Tasks')
            .document('task-review')
            .get()
            .to_dict()
        )
        history_entry = stored['status_history'][-1]
        self.assertEqual(history_entry['staff_name'], self.OWNER_HEADERS['X-User-Name'])
        self.assertEqual(history_entry['new_status'], 'Completed')
        self.assertIn('T', history_entry['timestamp'])

        # status_log should also contain the entry appended via ArrayUnion
        log_entry = stored['status_log'][-1]
        self.assertEqual(log_entry['new_status'], 'Completed')
        self.assertEqual(log_entry['staff_name'], self.OWNER_HEADERS['X-User-Name'])

    def test_non_collaborator_cannot_update(self):
        outsider_headers = {
            'X-User-Id': 'user-9',
            'X-User-Role': '4',
            'X-User-Name': 'Outsider',
        }
        before = deepcopy(
            self.fake_firestore
            .collection('Tasks')
            .document('task-review')
            .get()
            .to_dict()
        )
        response = self.client.put(
            '/api/tasks/task-review',
            json={'task_desc': 'Should not be allowed'},
            headers=outsider_headers,
        )
        self.assertEqual(response.status_code, 403)
        stored_after = (
            self.fake_firestore
            .collection('Tasks')
            .document('task-review')
            .get()
            .to_dict()
        )
        self.assertEqual(stored_after, before)

    def test_status_log_payload_appended(self):
        self.fake_firestore._data['Tasks']['task-review']['status_history'] = []
        entry = {
            'timestamp': '2025-01-05T10:00:00Z',
            'old_status': 'Under Review',
            'new_status': 'Completed',
            'staff_name': 'Owner One',
            'changed_by': 'user-1',
        }
        response = self.client.put(
            '/api/tasks/task-review',
            json={'task_status': 'Completed', 'status_log': [entry]},
            headers=self.OWNER_HEADERS,
        )
        self.assertEqual(response.status_code, 200)
        stored = (
            self.fake_firestore
            .collection('Tasks')
            .document('task-review')
            .get()
            .to_dict()
        )
        self.assertGreaterEqual(len(stored['status_log']), 1)
        self.assertDictEqual(stored['status_log'][-1], entry)
        history_entry = stored['status_history'][-1]
        self.assertEqual(history_entry['new_status'], 'Completed')
        self.assertEqual(history_entry['staff_name'], 'Owner One')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
