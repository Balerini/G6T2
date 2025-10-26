import unittest
from datetime import datetime, timedelta

from .remove_completed_tasks_test import TaskApiTestCaseBase


class TestRecurringTaskConfiguration(TaskApiTestCaseBase):
    """Validates recurrence setup, validation, and toggle behaviours."""

    def test_create_task_with_weekly_recurrence(self):
        payload = {
            'task_name': 'Weekly Standup',
            'task_desc': 'Team alignment session',
            'start_date': '2025-01-06',
            'priority_level': 3,
            'task_status': 'Ongoing',
            'owner': 'user-1',
            'assigned_to': ['user-1'],
            'proj_name': 'Ops Excellence',
            'recurrence': {
                'enabled': True,
                'frequency': 'weekly',
                'interval': 1,
                'weeklyDays': [1, 3],
                'endCondition': 'never',
            }
        }

        response = self.client.post('/api/tasks', json=payload)
        self.assertEqual(response.status_code, 201)

        data = response.get_json()
        self.assertTrue(data['recurrence']['enabled'])
        self.assertEqual(data['recurrence']['frequency'], 'weekly')
        self.assertEqual(data['recurrence']['interval'], 1)
        self.assertEqual(data['recurrence']['weeklyDays'], ['1', '3'])

        stored = (
            self.fake_firestore
            .collection('Tasks')
            .document(data['id'])
            .get()
            .to_dict()
        )
        self.assertEqual(stored['recurrence']['frequency'], 'weekly')
        self.assertEqual(stored['recurrence']['weeklyDays'], ['1', '3'])

    def test_recurring_task_requires_frequency(self):
        payload = {
            'task_name': 'Unnamed Recurring Task',
            'start_date': '2025-01-15',
            'priority_level': 2,
            'task_status': 'Ongoing',
            'owner': 'user-1',
            'assigned_to': ['user-1'],
            'proj_name': 'Ops Excellence',
            'recurrence': {
                'enabled': True,
                'interval': 1,
                'endCondition': 'never',
            }
        }

        response = self.client.post('/api/tasks', json=payload)
        self.assertEqual(response.status_code, 400)
        error = response.get_json()
        self.assertIn('frequency', error['error'].lower())

    def test_create_task_invalid_frequency_rejected(self):
        payload = {
            'task_name': 'Bad Recurrence Task',
            'start_date': '2025-03-01',
            'priority_level': 4,
            'task_status': 'Ongoing',
            'owner': 'user-1',
            'assigned_to': ['user-1'],
            'proj_name': 'Ops Excellence',
            'recurrence': {
                'enabled': True,
                'frequency': 'biweekly',
                'interval': 1,
                'endCondition': 'never',
            }
        }

        response = self.client.post('/api/tasks', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('invalid recurrence frequency', response.get_json()['error'].lower())

    def test_update_recurring_task_toggle_off(self):
        enable_payload = {
            'recurrence': {
                'enabled': True,
                'frequency': 'daily',
                'interval': 1,
                'endCondition': 'never',
            }
        }
        response = self.client.put(
            '/api/tasks/task-review',
            json=enable_payload,
            headers={
                'X-User-Id': 'user-1',
                'X-User-Role': '4',
                'X-User-Name': 'Alex Staff',
            }
        )
        self.assertEqual(response.status_code, 200)

        stored_enabled = (
            self.fake_firestore
            .collection('Tasks')
            .document('task-review')
            .get()
            .to_dict()
        )
        self.assertTrue(stored_enabled['recurrence']['enabled'])
        self.assertEqual(stored_enabled['recurrence']['frequency'], 'daily')

        disable_payload = {'recurrence': {'enabled': False}}
        response = self.client.put(
            '/api/tasks/task-review',
            json=disable_payload,
            headers={
                'X-User-Id': 'user-1',
                'X-User-Role': '4',
                'X-User-Name': 'Alex Staff',
            }
        )
        self.assertEqual(response.status_code, 200)

        stored_disabled = (
            self.fake_firestore
            .collection('Tasks')
            .document('task-review')
            .get()
            .to_dict()
        )
        self.assertEqual(stored_disabled['recurrence'], {'enabled': False})

    def test_update_recurrence_invalid_frequency(self):
        payload = {
            'recurrence': {
                'enabled': True,
                'frequency': 'yearly-ish',
                'interval': 1,
                'endCondition': 'never',
            }
        }
        response = self.client.put(
            '/api/tasks/task-review',
            json=payload,
            headers={
                'X-User-Id': 'user-1',
                'X-User-Role': '4',
                'X-User-Name': 'Alex Staff',
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('invalid recurrence frequency', response.get_json()['error'].lower())

        stored = (
            self.fake_firestore
            .collection('Tasks')
            .document('task-review')
            .get()
            .to_dict()
        )
        self.assertFalse(stored['recurrence']['enabled'])

    def test_get_task_returns_recurrence_details(self):
        update_payload = {
            'recurrence': {
                'enabled': True,
                'frequency': 'custom',
                'interval': 3,
                'customUnit': 'days',
                'endCondition': 'onDate',
                'endDate': '2025-02-15',
            }
        }
        response = self.client.put(
            '/api/tasks/task-review',
            json=update_payload,
            headers={
                'X-User-Id': 'user-1',
                'X-User-Role': '4',
                'X-User-Name': 'Alex Staff',
            }
        )
        self.assertEqual(response.status_code, 200)

        get_response = self.client.get('/api/tasks/task-review')
        self.assertEqual(get_response.status_code, 200)
        data = get_response.get_json()

        recurrence = data.get('recurrence', {})
        self.assertTrue(recurrence.get('enabled'))
        self.assertEqual(recurrence.get('frequency'), 'custom')
        self.assertEqual(recurrence.get('interval'), 3)
        self.assertEqual(recurrence.get('customUnit'), 'days')
        self.assertEqual(recurrence.get('endCondition'), 'onDate')
        self.assertTrue(recurrence.get('endDate', '').startswith('2025-02-15'))

    def test_completed_recurring_task_generates_next_instance(self):
        base_task = self.fake_firestore._data['Tasks']['task-review']
        base_task['recurrence'] = {
            'enabled': True,
            'frequency': 'daily',
            'interval': 1,
            'endCondition': 'never'
        }
        base_task['recurrence_occurrence'] = 1
        base_task['recurrence_series_id'] = 'task-review'

        response = self.client.put(
            '/api/tasks/task-review',
            json={'task_status': 'Completed'},
            headers={
                'X-User-Id': 'user-1',
                'X-User-Role': '4',
                'X-User-Name': 'Alex Staff',
            }
        )
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertIn('next_instance', body)
        next_instance = body['next_instance']
        self.assertEqual(next_instance['task_status'], 'Unassigned')

        original_start = base_task['start_date']
        expected_start = (original_start + timedelta(days=1)).date()
        self.assertTrue(next_instance['start_date'].startswith(expected_start.isoformat()))

        created_tasks = [key for key in self.fake_firestore._data['Tasks'].keys() if key not in ('task-active', 'task-complete', 'task-review')]
        self.assertTrue(created_tasks)
        new_task_id = created_tasks[0]
        new_task_doc = self.fake_firestore._data['Tasks'][new_task_id]
        self.assertEqual(new_task_doc['recurrence_occurrence'], 2)
        self.assertEqual(new_task_doc['recurrence_series_id'], 'task-review')

    def test_completed_task_respects_end_after_condition(self):
        base_task = self.fake_firestore._data['Tasks']['task-review']
        base_task['recurrence'] = {
            'enabled': True,
            'frequency': 'daily',
            'interval': 1,
            'endCondition': 'after',
            'endAfterOccurrences': 1
        }
        base_task['recurrence_occurrence'] = 1
        base_task['recurrence_series_id'] = 'task-review'

        response = self.client.put(
            '/api/tasks/task-review',
            json={'task_status': 'Completed'},
            headers={
                'X-User-Id': 'user-1',
                'X-User-Role': '4',
                'X-User-Name': 'Alex Staff',
            }
        )
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertNotIn('next_instance', body)
        self.assertEqual(len(self.fake_firestore._data['Tasks']), 3)

    def test_completed_task_with_recurrence_disabled_creates_no_instance(self):
        base_task = self.fake_firestore._data['Tasks']['task-review']
        base_task['recurrence'] = {'enabled': False}
        base_task['recurrence_occurrence'] = None
        base_task['recurrence_series_id'] = None

        response = self.client.put(
            '/api/tasks/task-review',
            json={'task_status': 'Completed'},
            headers={
                'X-User-Id': 'user-1',
                'X-User-Role': '4',
                'X-User-Name': 'Alex Staff',
            }
        )
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertNotIn('next_instance', body)
        self.assertEqual(len(self.fake_firestore._data['Tasks']), 3)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
