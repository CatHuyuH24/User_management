#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Analyzes all endpoints for the User Management Service
"""

import requests
import json
import time
import os
from typing import Dict, Any, List, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

class EndpointTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None
        self.test_results = []
        self.test_user_id = None
        self.test_admin_id = None
        
    def log_test_result(self, endpoint: str, method: str, status_code: int, 
                       response_data: Any = None, error: str = None, 
                       test_status: str = "PASS"):
        """Log test results for documentation"""
        result = {
            "endpoint": endpoint,
            "method": method,
            "expected_status": status_code,
            "actual_status": getattr(response_data, 'status_code', 'N/A') if hasattr(response_data, 'status_code') else 'N/A',
            "test_status": test_status,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "response_sample": str(response_data)[:200] if response_data else None
        }
        self.test_results.append(result)
        
    def test_health_endpoints(self):
        """Test basic health endpoints"""
        logger.info("Testing health endpoints...")
        
        # Test root endpoint
        try:
            response = self.session.get(f"{BASE_URL}/")
            self.log_test_result("/", "GET", 200, response.json())
            logger.info(f"Root endpoint: {response.status_code}")
        except Exception as e:
            self.log_test_result("/", "GET", 200, None, str(e), "FAIL")
            
        # Test health endpoint
        try:
            response = self.session.get(f"{BASE_URL}/health")
            self.log_test_result("/health", "GET", 200, response.json())
            logger.info(f"Health endpoint: {response.status_code}")
        except Exception as e:
            self.log_test_result("/health", "GET", 200, None, str(e), "FAIL")

    def test_signup_login(self):
        """Test user signup and login"""
        logger.info("Testing authentication endpoints...")
        
        # Test user signup
        signup_data = {
            "username": "testuser123",
            "email": "testuser@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            response = self.session.post(f"{API_V1}/signup", json=signup_data)
            self.log_test_result("/api/v1/signup", "POST", 201, response.json())
            logger.info(f"Signup: {response.status_code}")
            if response.status_code == 201:
                response_data = response.json()
                if 'user' in response_data:
                    self.test_user_id = response_data['user'].get('id')
        except Exception as e:
            self.log_test_result("/api/v1/signup", "POST", 201, None, str(e), "FAIL")
            
        # Test admin signup
        admin_signup_data = {
            "username": "testadmin123",
            "email": "testadmin@example.com", 
            "password": "AdminPassword123!",
            "first_name": "Test",
            "last_name": "Admin",
            "role": "admin"
        }
        
        try:
            response = self.session.post(f"{API_V1}/signup", json=admin_signup_data)
            self.log_test_result("/api/v1/signup", "POST", 201, response.json())
            if response.status_code == 201:
                response_data = response.json()
                if 'user' in response_data:
                    self.test_admin_id = response_data['user'].get('id')
        except Exception as e:
            self.log_test_result("/api/v1/signup", "POST", 201, None, str(e), "FAIL")
            
        # Test user login
        login_data = {
            "username": "testuser123",
            "password": "TestPassword123!"
        }
        
        try:
            response = self.session.post(f"{API_V1}/login", json=login_data)
            self.log_test_result("/api/v1/login", "POST", 200, response.json())
            logger.info(f"User login: {response.status_code}")
            if response.status_code == 200:
                self.user_token = response.json().get('access_token')
        except Exception as e:
            self.log_test_result("/api/v1/login", "POST", 200, None, str(e), "FAIL")
            
        # Test admin login  
        admin_login_data = {
            "username": "testadmin123",
            "password": "AdminPassword123!"
        }
        
        try:
            response = self.session.post(f"{API_V1}/login", json=admin_login_data)
            self.log_test_result("/api/v1/login", "POST", 200, response.json())
            logger.info(f"Admin login: {response.status_code}")
            if response.status_code == 200:
                self.admin_token = response.json().get('access_token')
        except Exception as e:
            self.log_test_result("/api/v1/login", "POST", 200, None, str(e), "FAIL")

    def test_auth_endpoints(self):
        """Test authenticated endpoints"""
        if not self.user_token:
            logger.warning("No user token available, skipping auth tests")
            return
            
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test get current user (auth endpoint)
        try:
            response = self.session.get(f"{API_V1}/me", headers=headers)
            self.log_test_result("/api/v1/me", "GET", 200, response.json())
            logger.info(f"Get current user (auth): {response.status_code}")
        except Exception as e:
            self.log_test_result("/api/v1/me", "GET", 200, None, str(e), "FAIL")
            
        # Test refresh token
        try:
            response = self.session.post(f"{API_V1}/refresh", headers=headers)
            self.log_test_result("/api/v1/refresh", "POST", 200, response.json())
            logger.info(f"Refresh token: {response.status_code}")
        except Exception as e:
            self.log_test_result("/api/v1/refresh", "POST", 200, None, str(e), "FAIL")
            
        # Test logout
        try:
            response = self.session.post(f"{API_V1}/logout", headers=headers)
            self.log_test_result("/api/v1/logout", "POST", 200, response.json())
            logger.info(f"Logout: {response.status_code}")
        except Exception as e:
            self.log_test_result("/api/v1/logout", "POST", 200, None, str(e), "FAIL")

    def test_user_endpoints(self):
        """Test user profile endpoints"""
        if not self.user_token:
            logger.warning("No user token available, skipping user tests")
            return
            
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test get current user profile
        try:
            response = self.session.get(f"{API_V1}/users/me", headers=headers)
            self.log_test_result("/api/v1/users/me", "GET", 200, response.json())
            logger.info(f"Get user profile: {response.status_code}")
        except Exception as e:
            self.log_test_result("/api/v1/users/me", "GET", 200, None, str(e), "FAIL")
            
        # Test update user profile
        update_data = {
            "first_name": "Updated Test",
            "last_name": "Updated User",
            "year_of_birth": 1990,
            "description": "Test user description"
        }
        
        try:
            response = self.session.put(f"{API_V1}/users/me", json=update_data, headers=headers)
            self.log_test_result("/api/v1/users/me", "PUT", 200, response.json())
            logger.info(f"Update user profile: {response.status_code}")
        except Exception as e:
            self.log_test_result("/api/v1/users/me", "PUT", 200, None, str(e), "FAIL")

    def test_mfa_endpoints(self):
        """Test MFA endpoints"""
        if not self.user_token:
            logger.warning("No user token available, skipping MFA tests")
            return
            
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test MFA status
        try:
            response = self.session.get(f"{API_V1}/auth/mfa/status", headers=headers)
            self.log_test_result("/api/v1/auth/mfa/status", "GET", 200, response.json())
            logger.info(f"MFA status: {response.status_code}")
        except Exception as e:
            self.log_test_result("/api/v1/auth/mfa/status", "GET", 200, None, str(e), "FAIL")
            
        # Test MFA initiate setup
        try:
            response = self.session.post(f"{API_V1}/auth/mfa/initiate", headers=headers)
            self.log_test_result("/api/v1/auth/mfa/initiate", "POST", 200, response.json())
            logger.info(f"MFA initiate: {response.status_code}")
        except Exception as e:
            self.log_test_result("/api/v1/auth/mfa/initiate", "POST", 200, None, str(e), "FAIL")
            
        # Test MFA QR code
        try:
            response = self.session.get(f"{API_V1}/auth/mfa/qr-code", headers=headers)
            self.log_test_result("/api/v1/auth/mfa/qr-code", "GET", 200, "QR Code data")
            logger.info(f"MFA QR code: {response.status_code}")
        except Exception as e:
            self.log_test_result("/api/v1/auth/mfa/qr-code", "GET", 200, None, str(e), "FAIL")

    def test_admin_endpoints(self):
        """Test admin endpoints"""
        if not self.admin_token:
            logger.warning("No admin token available, skipping admin tests")
            return
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test admin dashboard
        try:
            response = self.session.get(f"{API_V1}/admin/dashboard", headers=headers)
            self.log_test_result("/api/v1/admin/dashboard", "GET", 200, response.json())
            logger.info(f"Admin dashboard: {response.status_code}")
        except Exception as e:
            self.log_test_result("/api/v1/admin/dashboard", "GET", 200, None, str(e), "FAIL")
            
        # Test get all users
        try:
            response = self.session.get(f"{API_V1}/admin/users", headers=headers)
            self.log_test_result("/api/v1/admin/users", "GET", 200, response.json())
            logger.info(f"Get all users: {response.status_code}")
        except Exception as e:
            self.log_test_result("/api/v1/admin/users", "GET", 200, None, str(e), "FAIL")
            
        # Test create user as admin
        admin_user_data = {
            "username": "adminuser123",
            "email": "adminuser@example.com",
            "password": "AdminUser123!",
            "first_name": "Admin",
            "last_name": "Created"
        }
        
        try:
            response = self.session.post(f"{API_V1}/admin/users", json=admin_user_data, headers=headers)
            self.log_test_result("/api/v1/admin/users", "POST", 201, response.json())
            logger.info(f"Create user as admin: {response.status_code}")
        except Exception as e:
            self.log_test_result("/api/v1/admin/users", "POST", 201, None, str(e), "FAIL")

    def test_library_endpoints(self):
        """Test library endpoints"""
        if not self.admin_token:
            logger.warning("No admin token available, skipping library tests")
            return
            
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test get library stats
        try:
            response = self.session.get(f"{API_V1}/library/stats", headers=headers)
            self.log_test_result("/api/v1/library/stats", "GET", 200, response.json())
            logger.info(f"Library stats: {response.status_code}")
        except Exception as e:
            self.log_test_result("/api/v1/library/stats", "GET", 200, None, str(e), "FAIL")
            
        # Test get books
        try:
            response = self.session.get(f"{API_V1}/library/books", headers=headers)
            self.log_test_result("/api/v1/library/books", "GET", 200, response.json())
            logger.info(f"Get books: {response.status_code}")
        except Exception as e:
            self.log_test_result("/api/v1/library/books", "GET", 200, None, str(e), "FAIL")
            
        # Test create book
        book_data = {
            "isbn": "978-0123456789",
            "title": "Test Book",
            "author": "Test Author", 
            "category": "fiction",
            "description": "A test book",
            "total_copies": 5
        }
        
        try:
            response = self.session.post(f"{API_V1}/library/books", json=book_data, headers=headers)
            self.log_test_result("/api/v1/library/books", "POST", 201, response.json())
            logger.info(f"Create book: {response.status_code}")
            if response.status_code == 201:
                book_id = response.json().get('id')
                
                # Test get specific book
                try:
                    response = self.session.get(f"{API_V1}/library/books/{book_id}", headers=headers)
                    self.log_test_result(f"/api/v1/library/books/{book_id}", "GET", 200, response.json())
                    logger.info(f"Get book by ID: {response.status_code}")
                except Exception as e:
                    self.log_test_result(f"/api/v1/library/books/{book_id}", "GET", 200, None, str(e), "FAIL")
                    
        except Exception as e:
            self.log_test_result("/api/v1/library/books", "POST", 201, None, str(e), "FAIL")

    def test_notification_endpoints(self):
        """Test notification endpoints"""
        if not self.user_token:
            logger.warning("No user token available, skipping notification tests")
            return
            
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test get notifications
        try:
            response = self.session.get(f"{API_V1}/notifications/", headers=headers)
            self.log_test_result("/api/v1/notifications/", "GET", 200, response.json())
            logger.info(f"Get notifications: {response.status_code}")
        except Exception as e:
            self.log_test_result("/api/v1/notifications/", "GET", 200, None, str(e), "FAIL")
            
        # Test get unread count
        try:
            response = self.session.get(f"{API_V1}/notifications/unread-count", headers=headers)
            self.log_test_result("/api/v1/notifications/unread-count", "GET", 200, response.json())
            logger.info(f"Get unread count: {response.status_code}")
        except Exception as e:
            self.log_test_result("/api/v1/notifications/unread-count", "GET", 200, None, str(e), "FAIL")
            
        # Test mark all read
        try:
            response = self.session.put(f"{API_V1}/notifications/mark-all-read", headers=headers)
            self.log_test_result("/api/v1/notifications/mark-all-read", "PUT", 200, response.json())
            logger.info(f"Mark all read: {response.status_code}")
        except Exception as e:
            self.log_test_result("/api/v1/notifications/mark-all-read", "PUT", 200, None, str(e), "FAIL")

    def run_all_tests(self):
        """Run all endpoint tests"""
        logger.info("Starting comprehensive endpoint testing...")
        
        # Give services time to fully start
        time.sleep(5)
        
        self.test_health_endpoints()
        self.test_signup_login()
        self.test_auth_endpoints()
        self.test_user_endpoints()
        self.test_mfa_endpoints()
        self.test_admin_endpoints()
        self.test_library_endpoints()
        self.test_notification_endpoints()
        
        return self.test_results

def main():
    tester = EndpointTester()
    results = tester.run_all_tests()
    
    # Save results
    with open('endpoint_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
        
    logger.info(f"Testing completed. {len(results)} tests performed.")
    logger.info("Results saved to endpoint_test_results.json")
    
    # Print summary
    passed = len([r for r in results if r['test_status'] == 'PASS'])
    failed = len([r for r in results if r['test_status'] == 'FAIL'])
    
    print(f"\nTest Summary:")
    print(f"Total tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print("\nFailed tests:")
        for result in results:
            if result['test_status'] == 'FAIL':
                print(f"- {result['method']} {result['endpoint']}: {result['error']}")

if __name__ == "__main__":
    main()
