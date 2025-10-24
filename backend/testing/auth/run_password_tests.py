#!/usr/bin/env python3
"""
Script to run password unit tests with coverage analysis.
This script focuses specifically on password validation, hashing, and verification functions.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command, description):
    """Run a command and return the result"""
    print(f"\nINFO {description}")
    print(f"Running: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        print(f"Error running command: {e}")
        return False, "", str(e)

def check_coverage_installed():
    """Check if coverage.py is installed"""
    try:
        import coverage
        print("PASS Coverage.py is installed")
        return True
    except ImportError:
        print("ERROR Coverage.py is not installed")
        return False

def install_coverage():
    """Install coverage.py if not available"""
    print("\nINFO Installing coverage.py...")
    success, stdout, stderr = run_command("pip install coverage", "Installing coverage")
    if success:
        print("PASS Coverage.py installed successfully")
        return True
    else:
        print("ERROR Failed to install coverage.py")
        print(f"Error: {stderr}")
        return False

def run_tests_with_coverage():
    """Run password tests with coverage analysis"""
    print("\nINFO Running password unit tests with coverage...")
    
    # Run tests with coverage
    success, stdout, stderr = run_command(
        "coverage run --source=app test_password_unit.py", 
        "Running password tests with coverage"
    )
    
    if not success:
        print("ERROR Tests failed to run")
        return False
    
    return True

def generate_coverage_report():
    """Generate coverage report"""
    print("\nINFO Generating coverage report...")
    
    # Generate text report
    success, stdout, stderr = run_command("coverage report", "Generating text coverage report")
    if success:
        print("PASS Text coverage report generated")
        print(stdout)
    else:
        print("ERROR Failed to generate text coverage report")
        print(stderr)
    
    # Generate HTML report
    success, stdout, stderr = run_command("coverage html", "Generating HTML coverage report")
    if success:
        print("PASS HTML coverage report generated")
        print("INFO HTML report available in: htmlcov/index.html")
    else:
        print("ERROR Failed to generate HTML coverage report")
        print(stderr)
    
    # Generate JSON report for detailed analysis
    success, stdout, stderr = run_command("coverage json", "Generating JSON coverage report")
    if success:
        print("PASS JSON coverage report generated")
        return True
    else:
        print("ERROR Failed to generate JSON coverage report")
        print(stderr)
        return False

def analyze_coverage():
    """Analyze coverage results"""
    try:
        with open('coverage.json', 'r') as f:
            coverage_data = json.load(f)
        
        total_lines = coverage_data['totals']['num_statements']
        covered_lines = coverage_data['totals']['covered_lines']
        missing_lines = coverage_data['totals']['missing_lines']
        coverage_percent = coverage_data['totals']['percent_covered']
        
        print(f"\nINFO COVERAGE ANALYSIS")
        print("=" * 50)
        print(f"Total lines: {total_lines}")
        print(f"Covered lines: {covered_lines}")
        print(f"Missing lines: {missing_lines}")
        print(f"Coverage percentage: {coverage_percent:.2f}%")
        
        # Analyze specific files
        files = coverage_data['files']
        print(f"\nINFO FILE-SPECIFIC COVERAGE:")
        print("-" * 30)
        
        for filename, file_data in files.items():
            if 'app.py' in filename:  # Focus on app.py
                file_percent = file_data['summary']['percent_covered']
                file_lines = file_data['summary']['num_statements']
                file_covered = file_data['summary']['covered_lines']
                file_missing = file_data['summary']['missing_lines']
                
                print(f"INFO {filename}:")
                print(f"   Lines: {file_lines}, Covered: {file_covered}, Missing: {file_missing}")
                print(f"   Coverage: {file_percent:.2f}%")
                
                # Show missing lines for password-related functions
                if 'missing_lines' in file_data:
                    missing = file_data['missing_lines']
                    if missing:
                        print(f"   Missing lines: {missing[:10]}{'...' if len(missing) > 10 else ''}")
        
        return True
        
    except Exception as e:
        print(f"ERROR Error analyzing coverage: {e}")
        return False

def main():
    """Main function to run all tests and coverage analysis"""
    print("PASSWORD UNIT TESTS WITH COVERAGE")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("ERROR app.py not found. Please run this script from the backend directory.")
        return False
    
    if not os.path.exists('test_password_unit.py'):
        print("ERROR test_password_unit.py not found. Please ensure the test file exists.")
        return False
    
    # Step 1: Check/install coverage
    if not check_coverage_installed():
        if not install_coverage():
            print("ERROR Cannot proceed without coverage.py")
            return False
    
    # Step 2: Run tests with coverage
    if not run_tests_with_coverage():
        print("ERROR Tests failed to run")
        return False
    
    # Step 3: Generate coverage reports
    if not generate_coverage_report():
        print("ERROR Failed to generate coverage reports")
        return False
    
    # Step 4: Analyze coverage
    if not analyze_coverage():
        print("ERROR Failed to analyze coverage")
        return False
    
    print("\nPASS PASSWORD TESTING COMPLETE!")
    print("INFO Check htmlcov/index.html for detailed HTML coverage report")
    print("INFO Check coverage.json for detailed JSON coverage data")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
