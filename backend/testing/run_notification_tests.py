#!/usr/bin/env python3
"""
Simple test runner for notification unit tests
Runs notification tests without requiring coverage.py
"""
import sys
import os
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_notification_tests():
    """Run notification unit tests"""
    print("🔔 Running Notification Unit Tests...")
    print("=" * 50)
    
    try:
        # Import and run the notification tests
        from test_notification_unit import (
            TestNotificationService,
            TestNotificationAPI, 
            TestNotificationWorkflow,
            TestNotificationEdgeCases
        )
        
        # Create test suite
        test_suite = unittest.TestSuite()
        
        # Add test classes
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestNotificationService))
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestNotificationAPI))
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestNotificationWorkflow))
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestNotificationEdgeCases))
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(test_suite)
        
        # Print summary
        print(f"\n{'='*50}")
        print(f"NOTIFICATION UNIT TESTS SUMMARY")
        print(f"{'='*50}")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
        print(f"Success rate: {success_rate:.1f}%")
        
        if result.failures:
            print(f"\nFAILURES:")
            for test, traceback in result.failures:
                print(f"- {test}")
                print(f"  {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print(f"\nERRORS:")
            for test, traceback in result.errors:
                print(f"- {test}")
                print(f"  {traceback.split('Exception:')[-1].strip()}")
        
        return result.wasSuccessful()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        return False

if __name__ == '__main__':
    success = run_notification_tests()
    sys.exit(0 if success else 1)
