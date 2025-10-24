# Backend Testing Suite

This directory contains all testing files organized by category for better project structure and maintainability.



## Test Categories

### 1. **Unit Tests** (`test_unit.py`)
- **Purpose**: Test individual functions and methods in isolation
- **Scope**: Single functions, classes, or small components
- **Dependencies**: Minimal external dependencies
- **Speed**: Fast execution

### 2. **Integration Tests** (`test_integration.py`)
- **Purpose**: Test interaction between different components
- **Scope**: Multiple modules working together
- **Dependencies**: Database, external services
- **Speed**: Slower than unit tests

### 3. **Email Tests** (`test_email.py`)
- **Purpose**: Test email service functionality
- **Scope**: SMTP configuration, email templates, delivery
- **Dependencies**: Email service configuration
- **Speed**: Medium execution time

### 4. **Authentication Tests** (`testing/auth/`)
- **Purpose**: Test password validation, hashing, and verification
- **Scope**: User authentication, security features
- **Dependencies**: Password functions, hashing algorithms
- **Speed**: Fast execution with comprehensive coverage

## Running Tests

### Run All Tests
```bash
# From backend directory
python3 -m pytest testing/ -v
```

### Run Specific Test Categories
```bash
# Unit tests
python3 testing/test_unit.py

# Integration tests
python3 testing/test_integration.py

# Email tests
python3 testing/test_email.py

# Authentication tests
cd testing/auth
python3 simple_password_test.py
```

### Run with Coverage
```bash
# Install coverage if not already installed
pip3 install coverage pytest-cov

# Run with coverage
python3 -m pytest testing/ --cov=. --cov-report=html --cov-report=term
```

## Coverage Analysis

Each test category provides coverage analysis:

- **Unit Tests**: Function-level coverage
- **Integration Tests**: Component interaction coverage
- **Email Tests**: Email service coverage
- **Authentication Tests**: Password security coverage (100% function coverage)

## Test Configuration

### Dependencies
- `pytest` - Test framework
- `coverage` - Coverage analysis
- `pytest-cov` - Coverage integration
- `unittest` - Built-in testing framework

### Environment Setup
```bash
# Install testing dependencies
pip3 install -r testing/auth/requirements-test.txt

# Or install individually
pip3 install pytest coverage pytest-cov
```

## Best Practices

1. **Test Organization**: Keep tests organized by functionality
2. **Naming Convention**: Use descriptive test names
3. **Coverage Goals**: Aim for >80% coverage on critical functions
4. **Test Isolation**: Each test should be independent
5. **Documentation**: Document test purpose and expected behavior

## Debugging Tests

### Common Issues
1. **Import Errors**: Check Python path and module structure
2. **Database Issues**: Ensure test database is properly configured
3. **Environment Variables**: Verify all required env vars are set
4. **Dependencies**: Ensure all required packages are installed

### Debug Commands
```bash
# Run with verbose output
python3 -m pytest testing/ -v -s

# Run specific test with debugging
python3 -m pytest testing/unit/test_unit.py::test_specific_function -v -s

# Check test discovery
python3 -m pytest --collect-only testing/
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    cd backend
    python3 -m pytest testing/ --cov=. --cov-report=xml
    
- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: backend/coverage.xml
```

