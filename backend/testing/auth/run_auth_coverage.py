#!/usr/bin/env python3
"""
Generate coverage report specifically for authentication features
"""

import os
import sys
import subprocess

def main():
    """Generate authentication-specific coverage report"""
    print("AUTHENTICATION COVERAGE REPORT")
    print("=" * 50)
    
    # Get the backend directory
    current_file = os.path.abspath(__file__)
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    
    if not os.path.exists(os.path.join(backend_dir, 'app.py')):
        print("ERROR: app.py not found. Please run from backend directory.")
        return False
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Run coverage for auth tests only
    print("Running authentication tests with coverage...")
    result = subprocess.run([
        'coverage', 'run', '--source=app', 
        '-m', 'unittest', 'testing.auth.test_password_unit'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: Tests failed: {result.stderr}")
        return False
    
    # Generate HTML report in auth-specific directory
    print("Generating HTML coverage report...")
    html_result = subprocess.run([
        'coverage', 'html', '-d', 'testing/auth/htmlcov'
    ], capture_output=True, text=True)
    
    if html_result.returncode != 0:
        print(f"ERROR: HTML generation failed: {html_result.stderr}")
        return False
    
    # Show coverage report
    print("\nAUTHENTICATION COVERAGE SUMMARY:")
    print("-" * 40)
    report_result = subprocess.run([
        'coverage', 'report', '--include=app.py', '--show-missing'
    ], capture_output=True, text=True)
    
    print(report_result.stdout)
    
    print(f"\nHTML report generated at: testing/auth/htmlcov/index.html")
    print("Open with: open testing/auth/htmlcov/index.html")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
