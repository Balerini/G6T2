import unittest
from flask import Flask
from app import create_app

class TestHealthEndpoint(unittest.TestCase):
    """Unit tests for the health check endpoint"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_health_endpoint_returns_ok(self):
        """Test that /health returns status ok"""
        response = self.client.get('/health')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.json)
        self.assertEqual(response.json['status'], 'ok')
    
    def test_health_endpoint_method(self):
        """Test that /health only accepts GET requests"""
        # GET should work
        response_get = self.client.get('/health')
        self.assertEqual(response_get.status_code, 200)
        
        # POST should fail (method not allowed)
        response_post = self.client.post('/health')
        self.assertEqual(response_post.status_code, 405)  # Method Not Allowed
    
    def test_health_response_format(self):
        """Test that health response has correct format"""
        response = self.client.get('/health')
        
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'ok')
    
    def test_health_endpoint_performance(self):
        """Test that health endpoint responds quickly"""
        import time
        
        start_time = time.time()
        response = self.client.get('/health')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Health check should be fast (< 100ms)
        self.assertLess(response_time, 0.1, "Health check took too long")
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
