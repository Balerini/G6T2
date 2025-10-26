#!/usr/bin/env python3
"""
Unit Test Runner with Coverage
Runs all unit tests with comprehensive coverage reporting.
"""

import sys
import os
import subprocess
import unittest
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_unit_tests_with_coverage():
    """Run all unit tests with coverage reporting"""
    
    print("=" * 80)
    print("UNIT TESTING WITH COVERAGE")
    print("=" * 80)
    print(f"Test Run Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("✓ Testing individual functions with coverage analysis")
    print("✓ No external dependencies (no Flask, no database)")
    print("✓ Coverage report generation")
    print("=" * 80)
    
    try:
        # Run coverage on application feature unit tests only
        test_modules = [
            'testing.unit.test_password_validation',      # Authentication features
            'testing.unit.test_register_validation',      # Registration features  
            'testing.unit.test_reset_password_validation', # Password reset features
            'testing.unit.test_project_completion',       # Project completion logic
            'testing.unit.test_email_service',            # Email notification features
            'testing.unit.test_notification_unit',        # Notification features
            'testing.unit.test_recurrence_features',      # Recurrence features
            'testing.unit.test_dashboard_analytics',       # Dashboard utility functions
            'testing.unit.test_compute_effective_due_date' # Effective due date computation
        ]
        
        # Run coverage
        cmd = [
            sys.executable, '-m', 'coverage', 'run', '--source=.',
            '-m', 'unittest'
        ] + test_modules
        
        print("Running unit tests with coverage...")
        print(f"Command: {' '.join(cmd)}")
        print("-" * 80)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Unit tests passed!")
        else:
            print("❌ Unit tests failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
        
        # Generate coverage report
        print("\n" + "=" * 80)
        print("GENERATING COVERAGE REPORT")
        print("=" * 80)
        
        # Terminal report
        print("\n--- TERMINAL COVERAGE REPORT ---")
        subprocess.run([sys.executable, '-m', 'coverage', 'report'], check=True)
        
        # HTML report
        print("\n--- GENERATING HTML COVERAGE REPORT ---")
        subprocess.run([sys.executable, '-m', 'coverage', 'html'], check=True)
        print("✅ HTML coverage report generated in htmlcov/")
        
        
        print("\n" + "=" * 80)
        print("COVERAGE TESTING COMPLETED")
        print("=" * 80)
        print("📊 Coverage reports generated:")
        print("  - Terminal: Displayed above")
        print("  - HTML: htmlcov/index.html")
        print("=" * 80)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running coverage: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_individual_feature_coverage(feature):
    """Run coverage for individual feature"""
    
    feature_tests = {
        'password': 'testing.unit.test_password_unit',
        'dashboard': 'testing.unit.test_dashboard_unit',
        'project': 'testing.unit.test_project_unit',
        'task': 'testing.unit.test_task_unit',
        'health': 'testing.unit.test_health_unit',
        'notification': 'testing.unit.test_notification_unit',
        'email': 'testing.unit.test_email_service_unit',
        'subtask': 'testing.unit.test_subtask_unit',
        'collaborators': 'testing.unit.test_collaborators_project',
        'reminder': 'testing.unit.test_task_reminder_unit', 
        
    }
    
    if feature not in feature_tests:
        print(f"❌ Unknown feature: {feature}")
        print(f"Available features: {list(feature_tests.keys())}")
        return False
    
    test_module = feature_tests[feature]
    
    print(f"Running coverage for {feature} feature...")
    print("=" * 60)
    
    try:
        # Run coverage for specific feature
        cmd = [
            sys.executable, '-m', 'coverage', 'run', '--source=.',
            '-m', 'unittest', test_module
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {feature} tests passed!")
        else:
            print(f"❌ {feature} tests failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
        
        # Generate coverage report for this feature
        subprocess.run([sys.executable, '-m', 'coverage', 'report'], check=True)
        
        return True
        
    except Exception as e:
        print(f"❌ Error running {feature} coverage: {e}")
        return False

def run_coverage_with_threshold(threshold=80):
    """Run coverage with minimum threshold"""
    
    print(f"Running unit tests with {threshold}% coverage threshold...")
    print("=" * 80)
    
    try:
        # Run tests with coverage
        success = run_unit_tests_with_coverage()
        if not success:
            return False
        
        # Check coverage threshold
        result = subprocess.run([sys.executable, '-m', 'coverage', 'report'], 
                              capture_output=True, text=True)
        
        # Parse coverage percentage from output
        lines = result.stdout.split('\n')
        for line in lines:
            if 'TOTAL' in line:
                # Extract percentage from line like "TOTAL                   1234    123    90%"
                parts = line.split()
                if len(parts) >= 4:
                    percentage_str = parts[-1].replace('%', '')
                    try:
                        coverage_percentage = float(percentage_str)
                        print(f"\n📊 Coverage: {coverage_percentage}% (Threshold: {threshold}%)")
                        
                        if coverage_percentage >= threshold:
                            print(f"✅ Coverage threshold met!")
                            return True
                        else:
                            print(f"❌ Coverage threshold not met!")
                            return False
                    except ValueError:
                        print("❌ Could not parse coverage percentage")
                        return False
        
        print("❌ Could not find coverage information")
        return False
        
    except Exception as e:
        print(f"❌ Error checking coverage threshold: {e}")
        return False

def main():
    """Main test runner with command line arguments"""
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python run_unit_tests_with_coverage.py all                    # Run all unit tests with coverage")
        print("  python run_unit_tests_with_coverage.py <feature>              # Run specific feature with coverage")
        print("  python run_unit_tests_with_coverage.py threshold <percentage>  # Run with coverage threshold")
        print("  Available features: password, dashboard, project, task, health, notification, email, subtask, collaborators, reminder")
        return False
    
    command = sys.argv[1].lower()
    
    if command == 'all':
        return run_unit_tests_with_coverage()
    elif command == 'threshold':
        if len(sys.argv) < 3:
            print("❌ Please specify threshold percentage")
            return False
        try:
            threshold = float(sys.argv[2])
            return run_coverage_with_threshold(threshold)
        except ValueError:
            print("❌ Invalid threshold percentage")
            return False
    elif command in ['password', 'dashboard', 'project', 'task', 'health', 'notification', 'email', 'subtask', 'collaborators', 'reminder']:
        return run_individual_feature_coverage(command)
    else:
        print(f"❌ Unknown command: {command}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
