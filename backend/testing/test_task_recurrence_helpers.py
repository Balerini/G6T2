import unittest
from datetime import datetime
from routes.task import _add_months, _compute_next_occurrence_dates, _should_stop_recurrence, _parse_date_value


class TestTaskRecurrenceHelpers(unittest.TestCase):
    def test_parse_date_value(self):
        self.assertEqual(_parse_date_value('2025-01-02'), datetime(2025, 1, 2).date())
        self.assertEqual(_parse_date_value(datetime(2025, 1, 3)), datetime(2025, 1, 3).date())
        self.assertIsNone(_parse_date_value('invalid-date'))

    def test_add_months_preserves_day_when_possible(self):
        start = datetime(2024, 1, 15)
        self.assertEqual(_add_months(start, 1), datetime(2024, 2, 15))
        # February short month
        self.assertEqual(_add_months(datetime(2024, 1, 31), 1), datetime(2024, 2, 29))

    def test_compute_next_occurrence_daily(self):
        start = datetime(2024, 4, 5)
        end = datetime(2024, 4, 5, 17)
        nxt_start, nxt_end = _compute_next_occurrence_dates(start, end, {'frequency': 'daily', 'interval': 2})
        self.assertEqual(nxt_start, datetime(2024, 4, 7))
        self.assertEqual(nxt_end, datetime(2024, 4, 7, 17))

    def test_compute_next_occurrence_weekly_wrap(self):
        start = datetime(2024, 4, 5)  # Friday (weekday 4)
        nxt_start, _ = _compute_next_occurrence_dates(start, None, {'frequency': 'weekly', 'interval': 1, 'weeklyDays': [1, 4]})
        # Should wrap to Tuesday next week
        self.assertEqual(nxt_start, datetime(2024, 4, 9))

    def test_compute_next_occurrence_monthly_specific_day(self):
        start = datetime(2024, 1, 30)
        nxt_start, _ = _compute_next_occurrence_dates(start, None, {'frequency': 'monthly', 'interval': 1, 'monthlyDay': 31})
        self.assertEqual(nxt_start, datetime(2024, 2, 29))

    def test_compute_next_occurrence_custom_months(self):
        start = datetime(2024, 1, 10)
        nxt_start, _ = _compute_next_occurrence_dates(start, None, {'frequency': 'custom', 'interval': 2, 'customUnit': 'months'})
        self.assertEqual(nxt_start, datetime(2024, 3, 10))

    def test_compute_next_occurrence_default_fallback(self):
        start = datetime(2024, 1, 1)
        nxt_start, _ = _compute_next_occurrence_dates(start, None, {'frequency': 'unknown', 'interval': 3})
        self.assertEqual(nxt_start, datetime(2024, 1, 4))

    def test_should_stop_recurrence_after(self):
        info = {'endCondition': 'after', 'endAfterOccurrences': 3}
        self.assertTrue(_should_stop_recurrence(info, 4, datetime(2024, 1, 10)))
        self.assertFalse(_should_stop_recurrence(info, 3, datetime(2024, 1, 9)))

    def test_should_stop_recurrence_on_date(self):
        info = {'endCondition': 'onDate', 'endDate': '2024-04-30'}
        self.assertFalse(_should_stop_recurrence(info, 2, datetime(2024, 4, 25)))
        self.assertTrue(_should_stop_recurrence(info, 2, datetime(2024, 5, 1)))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
