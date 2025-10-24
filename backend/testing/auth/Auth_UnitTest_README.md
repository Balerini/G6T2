# Password Unit Testing with Coverage

This directory contains comprehensive unit tests for the password validation, hashing, and verification functionality in the sign-up feature.

## Files Overview

- `test_password_unit.py` - Main unit test file with comprehensive test cases
- `simple_password_test.py` - Simple test runner (no external dependencies)
- `run_password_tests.py` - Advanced test runner with coverage analysis
- `requirements-test.txt` - Testing dependencies
- `.coveragerc` - Coverage configuration

## 🚀 Quick Start (Simple Testing)

For basic testing without external dependencies:

```bash
cd backend/testing/auth
python3 simple_password_test.py
```

This will run all password tests and provide basic coverage analysis.

## Advanced Testing with Coverage

For detailed coverage analysis:

### 1. Install Dependencies
```bash
cd backend/testing/auth
pip install -r requirements-test.txt
```

### 2. Run Tests with Coverage
```bash
python3 run_password_tests.py
```

### 3. View Coverage Reports
- **HTML Report**: Open `htmlcov/index.html` in your browser
- **JSON Report**: Check `coverage.json` for detailed data
- **Text Report**: Displayed in terminal

## 📊 Test Coverage

The tests cover:

### Password Validation (`validate_password`)
- Length requirements (8-12 characters)
- Character requirements (uppercase, lowercase, digit, special)
- Edge cases and boundary conditions
- Error message validation

### Password Hashing (`hash_password`)
- Salt generation and storage
- Hash consistency
- Security properties (different salts for same password)

### Password Verification (`verify_password`)
- Correct password verification
- Incorrect password rejection
- Error handling for invalid inputs
- Case sensitivity

### Integration Tests
- Complete password flow (validate → hash → verify)
- Real-world scenarios
- Error propagation

##  Test Categories

### 1. **TestPasswordValidation** (18 tests)
- Length validation (too short, too long, exact boundaries)
- Character requirements (uppercase, lowercase, digit, special)
- Edge cases (empty, None, whitespace)
- Multiple requirement failures

### 2. **TestPasswordHashing** (5 tests)
- Return type validation
- Salt inclusion verification
- Uniqueness of hashes
- Hex conversion testing

### 3. **TestPasswordVerification** (9 tests)
- Correct password verification
- Incorrect password rejection
- Error handling (invalid hex, short hex, None)
- Case sensitivity
- Unicode support

### 4. **TestPasswordIntegration** (3 tests)
- Complete password flow
- Invalid validation handling
- Storage simulation

### 5. **TestPasswordEdgeCases** (6 tests)
- Boundary conditions (8 and 12 characters)
- All valid special characters
- Unicode special characters
- Whitespace handling

## Coverage Analysis

The tests provide comprehensive coverage of:

- **Function Coverage**: 100% of password-related functions
- **Line Coverage**: All code paths in password functions
- **Branch Coverage**: All conditional logic
- **Edge Case Coverage**: Boundary conditions and error cases

## Running Individual Test Categories

```bash
# Run only validation tests
python3 -m unittest test_password_unit.TestPasswordValidation -v

# Run only hashing tests  
python3 -m unittest test_password_unit.TestPasswordHashing -v

# Run only verification tests
python3 -m unittest test_password_unit.TestPasswordVerification -v
```

## Debugging Failed Tests

If tests fail:

1. **Check the error message** - Most failures show the expected vs actual result
2. **Run individual test methods**:
   ```bash
   python3 -m unittest test_password_unit.TestPasswordValidation.test_password_too_short -v
   ```
3. **Check app.py functions** - Ensure password functions are properly implemented
4. **Verify imports** - Make sure all required modules are available

## Test Requirements

### Password Validation Rules (from app.py):
- Length: 8-12 characters
- Uppercase: At least one A-Z
- Lowercase: At least one a-z  
- Digit: At least one 0-9
- Special: At least one of `!@#$%^&*()_+-=[]{}|;:,.<>?`

### Valid Test Passwords:
- `Abc123!@#` (8 chars, all requirements)
- `Abc123!@#$%^` (12 chars, all requirements)

### Invalid Test Passwords:
- `Abc123!` (7 chars - too short)
- `Abcdefgh1!@#` (13 chars - too long)
- `abc123!@#` (no uppercase)
- `ABC123!@#` (no lowercase)
- `Abcdefg!@#` (no digit)
- `Abc123456` (no special char)

##  Expected Results

When all tests pass, you should see:
- ✅ All 41 test cases passing
- ✅ 100% function coverage for password features
- ✅ Comprehensive error message validation
- ✅ Security property verification (salt uniqueness, hash verification)

## Manual Testing

You can also test the password functions manually:

```python
from app import validate_password, hash_password, verify_password

# Test validation
result = validate_password("Abc123!@#")
print(result)  # Should be None (valid)

# Test hashing
hashed = hash_password("Abc123!@#")
print(hashed.hex())  # Should show hex string

# Test verification
is_valid = verify_password(hashed.hex(), "Abc123!@#")
print(is_valid)  # Should be True
```

