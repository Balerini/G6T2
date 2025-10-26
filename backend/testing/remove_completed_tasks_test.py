import collections
import copy
import os
import sys
import unittest
from datetime import datetime
from unittest.mock import patch


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402


class FakeServerTimestamp:
    """Sentinel used to mimic Firestore's SERVER_TIMESTAMP."""


class FakeArrayUnion:
    """Simple representation of Firestore ArrayUnion operations."""

    def __init__(self, values):
        self.values = list(values or [])


class FakeDocumentReference:
    """Mimics basic Firestore document reference behaviour needed for tests."""

    def __init__(self, coll_data, doc_id):
        self._coll_data = coll_data
        self.id = doc_id

    def get(self):
        data = self._coll_data.get(self.id)
        return FakeDocumentSnapshot(self.id, data, self._coll_data)

    def update(self, update_dict):
        if self.id not in self._coll_data or not isinstance(self._coll_data[self.id], dict):
            raise KeyError(f"Document {self.id} does not exist")

        current = copy.deepcopy(self._coll_data[self.id])

        for key, value in update_dict.items():
            if isinstance(value, FakeArrayUnion):
                existing = current.get(key)
                if existing is None:
                    existing = []
                elif not isinstance(existing, list):
                    existing = [existing]
                current[key] = existing + copy.deepcopy(value.values)
            elif isinstance(value, FakeServerTimestamp):
                current[key] = datetime.utcnow()
            else:
                current[key] = copy.deepcopy(value)

        self._coll_data[self.id] = current


class FakeDocumentSnapshot:
    """Simple stand-in for Firestore document snapshots."""

    def __init__(self, doc_id, data, coll_data):
        self.id = doc_id
        self._data = copy.deepcopy(data) if isinstance(data, dict) else None
        self.reference = FakeDocumentReference(coll_data, doc_id)

    @property
    def exists(self):
        return self._data is not None

    def to_dict(self):
        return copy.deepcopy(self._data) if self._data is not None else None


class FakeQuery:
    """Supports chaining where() calls with == and array_contains filters."""

    def __init__(self, coll_data, filters=None, limit=None):
        self._coll_data = coll_data
        self._filters = filters or []
        self._limit = limit

    def where(self, field, op, value):
        return FakeQuery(self._coll_data, self._filters + [(field, op, value)], self._limit)

    def limit(self, value):
        return FakeQuery(self._coll_data, list(self._filters), value)

    def stream(self):
        results = []
        for doc_id, doc in self._coll_data.items():
            if not isinstance(doc, dict):
                continue
            if self._matches(doc):
                results.append(FakeDocumentSnapshot(doc_id, doc, self._coll_data))

        if self._limit is not None:
            return results[: self._limit]

        return results

    def _matches(self, doc):
        for field, op, value in self._filters:
            field_value = doc.get(field)
            if op == '==':
                if field_value != value:
                    return False
            elif op == 'array_contains':
                if not isinstance(field_value, list) or value not in field_value:
                    return False
            else:
                raise NotImplementedError(f"Operator {op} not supported in fake query")
        return True


class FakeCollection:
    """Minimal Firestore collection wrapper built on a shared dict."""

    def __init__(self, client, name, coll_data):
        self._client = client
        self._name = name
        self._coll_data = coll_data

    def where(self, field, op, value):
        return FakeQuery(self._coll_data, [(field, op, value)])

    def stream(self):
        results = []
        for doc_id, doc in self._coll_data.items():
            if not isinstance(doc, dict):
                continue
            results.append(FakeDocumentSnapshot(doc_id, doc, self._coll_data))
        return results

    def document(self, doc_id):
        return FakeDocumentReference(self._coll_data, doc_id)

    def add(self, data):
        self._client._counters[self._name] += 1
        doc_id = f"{self._name.lower()}_{self._client._counters[self._name]}"
        self._coll_data[doc_id] = copy.deepcopy(data)
        return None, FakeDocumentReference(self._coll_data, doc_id)


class FakeFirestoreClient:
    """In-memory Firestore replacement covering the pieces the routes need."""

    def __init__(self, initial_data=None):
        self._data = copy.deepcopy(initial_data or {})
        self._counters = collections.defaultdict(int)

    def collection(self, name):
        coll_data = self._data.setdefault(name, {})
        return FakeCollection(self, name, coll_data)


class FakeFirestoreModule:
    """Replaces firebase_admin.firestore for tests."""

    def __init__(self):
        self.SERVER_TIMESTAMP = FakeServerTimestamp()

    def ArrayUnion(self, values):
        return FakeArrayUnion(values)


class DummyNotificationService:
    """No-op notification service used to satisfy route dependencies."""

    def notify_task_assigned(self, *args, **kwargs):
        return None

    def notify_task_updated(self, *args, **kwargs):
        return None

    def get_user_notifications(self, *args, **kwargs):
        return []

    def mark_as_read(self, *args, **kwargs):
        return True

    def mark_all_as_read(self, *args, **kwargs):
        return 0

    def delete_notification(self, *args, **kwargs):
        return True

    def notify_upcoming_deadlines(self, *args, **kwargs):
        return 0


class TaskApiTestCaseBase(unittest.TestCase):
    """Shared harness that runs the real Flask app against an in-memory Firestore."""

    def setUp(self):
        self.notification_stub = DummyNotificationService()
        self.firestore_module = FakeFirestoreModule()
        self.fake_firestore = FakeFirestoreClient(self.build_initial_data())

        self._original_stdout_encoding = None
        if hasattr(sys.stdout, "reconfigure"):
            try:
                self._original_stdout_encoding = sys.stdout.encoding
                sys.stdout.reconfigure(encoding="utf-8")
            except Exception:
                self._original_stdout_encoding = None

        self._patchers = [
            patch('routes.task.get_firestore_client', return_value=self.fake_firestore),
            patch('app.get_firestore_client', return_value=self.fake_firestore),
            patch('app.get_firebase_app', return_value=None),
            patch('routes.task.firestore', new=self.firestore_module),
            patch('routes.task.notification_service', new=self.notification_stub),
            patch('app.notification_service', new=self.notification_stub),
        ]

        for patcher in self._patchers:
            patcher.start()

        self.app = create_app()
        self.app.testing = True
        self._disable_log_request()
        self.client = self.app.test_client()

    def reset_firestore_state(self):
        """Restore the fake Firestore to its initial dataset."""
        self.fake_firestore._data = self.build_initial_data()
        self.fake_firestore._counters = collections.defaultdict(int)

    def tearDown(self):
        for patcher in reversed(getattr(self, "_patchers", [])):
            patcher.stop()

        if self._original_stdout_encoding:
            try:
                sys.stdout.reconfigure(encoding=self._original_stdout_encoding)
            except Exception:
                pass

    def build_initial_data(self):
        base_start = datetime(2024, 1, 1, 9, 0, 0)
        base_end = datetime(2024, 1, 10, 18, 0, 0)

        return {
            'Tasks': {
                'task-active': {
                    'task_ID': 'task-active',
                    'task_name': 'Prepare report',
                    'task_status': 'Ongoing',
                    'assigned_to': ['user-1'],
                    'owner': 'user-1',
                    'proj_ID': 'project-1',
                    'proj_name': 'Ops Excellence',
                    'start_date': base_start,
                    'end_date': base_end,
                    'is_deleted': False,
                    'status_history': [],
                    'status_log': [],
                    'recurrence': {'enabled': False},
                    'recurrence_occurrence': None,
                    'recurrence_series_id': None,
                },
                'task-complete': {
                    'task_ID': 'task-complete',
                    'task_name': 'Archive files',
                    'task_status': 'Completed',
                    'assigned_to': ['user-1'],
                    'owner': 'user-1',
                    'proj_ID': 'project-1',
                    'proj_name': 'Ops Excellence',
                    'start_date': base_start,
                    'end_date': base_end,
                    'is_deleted': False,
                    'status_history': [],
                    'status_log': [],
                    'recurrence': {'enabled': False},
                    'recurrence_occurrence': None,
                    'recurrence_series_id': None,
                },
                'task-review': {
                    'task_ID': 'task-review',
                    'task_name': 'Draft SOP',
                    'task_status': 'Under Review',
                    'assigned_to': ['user-1'],
                    'owner': 'user-1',
                    'proj_ID': 'project-1',
                    'proj_name': 'Ops Excellence',
                    'start_date': base_start,
                    'end_date': base_end,
                    'is_deleted': False,
                    'status_history': [],
                    'status_log': [],
                    'recurrence': {'enabled': False},
                    'recurrence_occurrence': None,
                    'recurrence_series_id': None,
                },
            },
            'Projects': {
                'project-1': {
                    'proj_name': 'Ops Excellence',
                    'end_date': None,
                }
            }
        }

    def _disable_log_request(self):
        """Remove the noisy before_request logger that prints emojis (breaks cp1252)."""
        funcs = self.app.before_request_funcs.get(None, [])
        for func in list(funcs):
            if getattr(func, "__name__", "") == "log_request":
                funcs.remove(func)


class TestTaskFiltersAndRecurrence(TaskApiTestCaseBase):
    """Covers task filtering, editing, and recurrence behaviour."""

    OWNER_HEADERS = {
        'X-User-Id': 'user-1',
        'X-User-Role': '4',
        'X-User-Name': 'Alex Staff',
    }

    def test_active_filter_hides_completed_tasks(self):
        """Filtering for Active tasks should exclude Completed items."""
        response = self.client.get(
            '/api/tasks',
            query_string={'userId': 'user-1', 'status': 'Active'}
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        returned_ids = {task['id'] for task in payload}

        self.assertIn('task-active', returned_ids)
        self.assertIn('task-review', returned_ids)
        self.assertNotIn('task-complete', returned_ids)

        returned_statuses = {task['task_status'] for task in payload}
        self.assertNotIn('Completed', returned_statuses)

    def test_completed_filter_returns_only_completed_tasks(self):
        """Filtering for Completed should surface only completed work."""
        response = self.client.get(
            '/api/tasks',
            query_string={'userId': 'user-1', 'status': 'Completed'}
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()

        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]['id'], 'task-complete')
        self.assertEqual(payload[0]['task_status'], 'Completed')

    def test_task_status_update_reflected_in_filters(self):
        """Marking a task as completed should hide it from Active without refresh."""
        update_response = self.client.put(
            '/api/tasks/task-active',
            json={'task_status': 'Completed'},
            headers=self.OWNER_HEADERS,
        )
        self.assertEqual(update_response.status_code, 200)

        stored = (
            self.fake_firestore
            .collection('Tasks')
            .document('task-active')
            .get()
            .to_dict()
        )
        self.assertEqual(stored['task_status'], 'Completed')

        active_response = self.client.get(
            '/api/tasks',
            query_string={'userId': 'user-1', 'status': 'Active'}
        )
        active_ids = {task['id'] for task in active_response.get_json()}
        self.assertNotIn('task-active', active_ids)

        completed_response = self.client.get(
            '/api/tasks',
            query_string={'userId': 'user-1', 'status': 'Completed'}
        )
        completed_ids = {task['id'] for task in completed_response.get_json()}
        self.assertIn('task-active', completed_ids)
        self.assertIn('task-complete', completed_ids)

    def test_recurrence_update_normalizes_payload(self):
        """Recurrence updates should be stored in normalized camelCase form."""
        recurrence_payload = {
            'recurrence': {
                'enabled': True,
                'frequency': 'WEEKLY',
                'interval': '2',
                'weekly_days': [1, 3],
                'end_condition': 'after',
                'end_after_occurrences': '5',
            }
        }

        response = self.client.put(
            '/api/tasks/task-review',
            json=recurrence_payload,
            headers={
                'X-User-Id': 'user-1',
                'X-User-Role': '4',
                'X-User-Name': 'Alex Staff',
            }
        )
        self.assertEqual(response.status_code, 200)

        stored = (
            self.fake_firestore
            .collection('Tasks')
            .document('task-review')
            .get()
            .to_dict()
        )

        expected_recurrence = {
            'enabled': True,
            'frequency': 'weekly',
            'interval': 2,
            'weeklyDays': ['1', '3'],
            'endCondition': 'after',
            'endAfterOccurrences': 5,
        }

        self.assertEqual(stored['recurrence'], expected_recurrence)

    def test_get_tasks_with_unknown_user_returns_empty(self):
        response = self.client.get(
            '/api/tasks',
            query_string={'userId': 'no-such-user', 'status': 'Active'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_get_tasks_without_user_id_returns_all_non_deleted(self):
        response = self.client.get('/api/tasks')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(len(payload), 3)
        ids = {task['id'] for task in payload}
        self.assertTrue({'task-active', 'task-review', 'task-complete'}.issubset(ids))

    def test_update_nonexistent_task_returns_404(self):
        response = self.client.put(
            '/api/tasks/does-not-exist',
            json={'task_status': 'Completed'},
            headers=self.OWNER_HEADERS,
        )
        self.assertEqual(response.status_code, 404)

    def test_update_missing_auth_returns_400(self):
        response = self.client.put(
            '/api/tasks/task-active',
            json={'task_status': 'Completed'},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing user context', response.get_json()['error'])

    def test_update_invalid_status_value_normalizes(self):
        response = self.client.put(
            '/api/tasks/task-active',
            json={'task_status': ''},
            headers=self.OWNER_HEADERS,
        )
        self.assertEqual(response.status_code, 200)
        stored = (
            self.fake_firestore
            .collection('Tasks')
            .document('task-active')
            .get()
            .to_dict()
        )
        self.assertEqual(stored['task_status'], '')
        history_entry = stored['status_history'][-1]
        self.assertEqual(history_entry['new_status'], 'Unassigned')

    def test_recurrence_invalid_end_occurrences_returns_400(self):
        payload = {
            'recurrence': {
                'enabled': True,
                'frequency': 'weekly',
                'end_condition': 'after',
                'end_after_occurrences': 'zero',
            }
        }
        response = self.client.put(
            '/api/tasks/task-review',
            json=payload,
            headers=self.OWNER_HEADERS,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('endafteroccurrences', response.get_json()['error'].lower())

    def test_update_with_malformed_json_returns_400(self):
        response = self.client.put(
            '/api/tasks/task-active',
            data='not json',
            headers=self.OWNER_HEADERS,
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn('Unsupported Media Type', response.get_json()['error'])

    def test_soft_deleted_tasks_are_excluded(self):
        self.fake_firestore._data['Tasks']['task-active']['is_deleted'] = True
        response = self.client.get(
            '/api/tasks',
            query_string={'userId': 'user-1', 'status': 'Active'}
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        ids = {task['id'] for task in payload}
        self.assertNotIn('task-active', ids)

    def test_permission_denied_for_unrelated_user(self):
        outsider_headers = {
            'X-User-Id': 'outsider',
            'X-User-Role': '4',
            'X-User-Name': 'Hacker',
        }
        response = self.client.put(
            '/api/tasks/task-review',
            json={'task_desc': 'Should fail'},
            headers=outsider_headers,
        )
        self.assertEqual(response.status_code, 403)

    def test_get_task_with_special_character_id(self):
        self.fake_firestore._data['Tasks']['task-çø∂€'] = {
            'task_ID': 'task-çø∂€',
            'task_name': 'Special ID Task',
            'task_status': 'Ongoing',
            'assigned_to': ['user-1'],
            'owner': 'user-1',
            'proj_ID': 'project-1',
            'proj_name': 'Ops Excellence',
            'start_date': datetime(2024, 2, 1, 9, 0),
            'end_date': datetime(2024, 2, 10, 18, 0),
            'is_deleted': False,
            'status_history': [],
            'status_log': [],
            'recurrence': {'enabled': False},
        }
        response = self.client.get('/api/tasks/task-çø∂€')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['task_name'], 'Special ID Task')

    def test_update_with_extremely_long_description(self):
        long_desc = 'A' * 5000
        response = self.client.put(
            '/api/tasks/task-review',
            json={'task_desc': long_desc},
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
        self.assertEqual(stored['task_desc'], long_desc)

    def test_database_failure_returns_500(self):
        with patch('routes.task.get_firestore_client', side_effect=Exception('DB down')):
            response = self.client.get(
                '/api/tasks',
                query_string={'userId': 'user-1', 'status': 'Active'}
            )
        self.assertEqual(response.status_code, 500)
        self.assertIn('DB down', response.get_json()['error'])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
