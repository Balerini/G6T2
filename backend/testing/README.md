# Testing Directory - Single File Approach

## 🎯 How to Run Tests

All tests use the **single file approach** - each test file can be run directly without separate runners.

### 🔔 Bell Notification Tests (In-App Notifications)
```bash
# Run bell notification API tests
python3 -m unittest testing.test_notification_api

# Run with verbose output
python3 -m unittest testing.test_notification_api -v
```

### 📧 Task Reminder Tests (Email Notifications)
```bash
# Run task reminder tests
python3 -m unittest testing.test_task_reminder_unit

# Run with verbose output
python3 -m unittest testing.test_task_reminder_unit -v
```

### 🔐 Authentication Tests
```bash
# Run password tests
python3 -m unittest testing.auth.test_password_unit

# Run reset password tests
python3 -m unittest testing.auth.test_reset_password_unit

# Run registration API tests
python3 -m unittest testing.test_registration_api
```

### 🧪 Integration Tests
```bash
# Run integration tests
python3 -m unittest testing.test_integration

# Run all tests
python3 -m unittest testing
```

## 📋 Test Files Overview

### 🔔 Bell Notifications (In-App)
- `test_notification_api.py` - API endpoints with real data (14 tests)
- `test_notification_unit.py` - Unit tests (32 tests) - **REDUNDANT**

### 📧 Task Reminders (Email)
- `test_task_reminder_unit.py` - Email notifications and scheduling (19 tests)
- `test_task_reminder_edge_cases.py` - Edge cases (8 tests)

### 🔐 Authentication
- `testing/auth/test_password_unit.py` - Password validation/hashing (41 tests)
- `testing/auth/test_reset_password_unit.py` - Reset password (15 tests)
- `test_registration_api.py` - Registration API (14 tests)

### 🧪 Integration
- `test_integration.py` - Basic integration tests (4 tests)
- `test_unit.py` - General unit tests (4 tests)

## 🎯 Benefits of Single File Approach

✅ **Simple** - One command to run each test
✅ **Clean** - No separate runner files needed
✅ **Direct** - Run exactly what you want
✅ **Standard** - Uses Python's built-in unittest

## 🚀 Quick Start

```bash
# Run all notification tests
python3 -m unittest testing.test_notification_api testing.test_task_reminder_unit

# Run all authentication tests
python3 -m unittest testing.test_registration_api testing.auth.test_password_unit

# Run everything
python3 -m unittest testing
```