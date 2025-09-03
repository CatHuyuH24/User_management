#!/usr/bin/env python3
"""
Advanced API Documentation Generator
Creates comprehensive endpoint status documentation
"""

import requests
import json
import time
from typing import Dict, Any, List
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

class AdvancedAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None
        self.endpoints = []
        self.test_user_id = None
        self.test_admin_id = None
        
    def setup_test_data(self):
        """Setup test users and tokens"""
        logger.info("Setting up test data...")
        
        # Create test user
        user_data = {
            "username": f"testuser_{int(time.time())}",
            "email": f"testuser_{int(time.time())}@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            response = self.session.post(f"{API_V1}/signup", json=user_data)
            if response.status_code in [200, 201]:
                data = response.json()
                if 'user' in data:
                    self.test_user_id = data['user'].get('id')
        except Exception as e:
            logger.error(f"Failed to create test user: {e}")
            
        # Login as user
        try:
            login_data = {
                "username": user_data["username"],
                "password": user_data["password"]
            }
            response = self.session.post(f"{API_V1}/login", json=login_data)
            if response.status_code == 200:
                self.user_token = response.json().get('access_token')
        except Exception as e:
            logger.error(f"Failed to login user: {e}")
            
        # Create admin user
        admin_data = {
            "username": f"testadmin_{int(time.time())}",
            "email": f"testadmin_{int(time.time())}@example.com", 
            "password": "AdminPassword123!",
            "first_name": "Test",
            "last_name": "Admin",
            "role": "admin"
        }
        
        try:
            response = self.session.post(f"{API_V1}/signup", json=admin_data)
            if response.status_code in [200, 201]:
                data = response.json()
                if 'user' in data:
                    self.test_admin_id = data['user'].get('id')
        except Exception as e:
            logger.error(f"Failed to create admin user: {e}")
            
        # Login as admin
        try:
            admin_login_data = {
                "username": admin_data["username"],
                "password": admin_data["password"]
            }
            response = self.session.post(f"{API_V1}/login", json=admin_login_data)
            if response.status_code == 200:
                self.admin_token = response.json().get('access_token')
        except Exception as e:
            logger.error(f"Failed to login admin: {e}")

    def test_endpoint(self, endpoint: str, method: str, headers: Dict = None, 
                     data: Dict = None, files: Dict = None, params: Dict = None):
        """Test a single endpoint"""
        
        full_url = f"{BASE_URL}{endpoint}" if endpoint.startswith('/') else f"{API_V1}{endpoint}"
        
        endpoint_info = {
            "endpoint": endpoint,
            "method": method.upper(),
            "full_url": full_url,
            "status": "UNKNOWN",
            "status_code": None,
            "response_headers": {},
            "response_body": {},
            "error_message": None,
            "request_headers": headers or {},
            "request_body": data or {},
            "request_params": params or {},
            "validation_fields": [],
            "required_data_type": "JSON",
            "description": "",
            "evidence": "",
            "solutions": "",
            "test_timestamp": datetime.now().isoformat()
        }
        
        try:
            if method.upper() == "GET":
                response = self.session.get(full_url, headers=headers, params=params)
            elif method.upper() == "POST":
                if files:
                    response = self.session.post(full_url, headers=headers, files=files, data=data)
                else:
                    response = self.session.post(full_url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(full_url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(full_url, headers=headers, json=data)
            elif method.upper() == "PATCH":
                response = self.session.patch(full_url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            endpoint_info["status_code"] = response.status_code
            endpoint_info["response_headers"] = dict(response.headers)
            
            try:
                response_json = response.json()
                endpoint_info["response_body"] = response_json
            except:
                endpoint_info["response_body"] = response.text[:500]
                
            # Determine status
            if response.status_code in [200, 201, 202, 204]:
                endpoint_info["status"] = "OPERATIONAL"
                endpoint_info["evidence"] = f"Success with status {response.status_code}"
            elif response.status_code in [400, 422]:
                endpoint_info["status"] = "VALIDATION_ERROR"
                endpoint_info["evidence"] = f"Validation error with status {response.status_code}"
                endpoint_info["error_message"] = str(endpoint_info["response_body"])
            elif response.status_code in [401, 403]:
                endpoint_info["status"] = "AUTH_REQUIRED"
                endpoint_info["evidence"] = f"Authentication/Authorization required - status {response.status_code}"
            elif response.status_code == 404:
                endpoint_info["status"] = "NOT_FOUND"
                endpoint_info["evidence"] = f"Endpoint not found - status {response.status_code}"
            elif response.status_code >= 500:
                endpoint_info["status"] = "SERVER_ERROR"
                endpoint_info["evidence"] = f"Server error - status {response.status_code}"
                endpoint_info["error_message"] = str(endpoint_info["response_body"])
            else:
                endpoint_info["status"] = "UNKNOWN"
                endpoint_info["evidence"] = f"Unexpected status {response.status_code}"
                
        except Exception as e:
            endpoint_info["status"] = "ERROR"
            endpoint_info["error_message"] = str(e)
            endpoint_info["evidence"] = f"Exception occurred: {str(e)}"
            
        return endpoint_info

    def run_comprehensive_tests(self):
        """Run comprehensive tests on all endpoints"""
        
        # Define all endpoints to test based on the API structure
        endpoint_tests = [
            # Health endpoints
            {"endpoint": "/", "method": "GET"},
            {"endpoint": "/health", "method": "GET"},
            
            # Authentication endpoints
            {"endpoint": "/api/v1/signup", "method": "POST", "data": {
                "username": f"test_{int(time.time())}", 
                "email": f"test_{int(time.time())}@example.com",
                "password": "TestPass123!"
            }},
            {"endpoint": "/api/v1/login", "method": "POST", "data": {
                "username": "nonexistent", "password": "wrong"
            }},
            {"endpoint": "/api/v1/refresh", "method": "POST", "auth": "user"},
            {"endpoint": "/api/v1/me", "method": "GET", "auth": "user"},
            {"endpoint": "/api/v1/logout", "method": "POST", "auth": "user"},
            
            # User endpoints
            {"endpoint": "/api/v1/users/me", "method": "GET", "auth": "user"},
            {"endpoint": "/api/v1/users/me", "method": "PUT", "auth": "user", "data": {
                "first_name": "Updated", "description": "Test update"
            }},
            
            # MFA endpoints
            {"endpoint": "/api/v1/auth/mfa/status", "method": "GET", "auth": "user"},
            {"endpoint": "/api/v1/auth/mfa/initiate", "method": "POST", "auth": "user"},
            {"endpoint": "/api/v1/auth/mfa/complete-setup", "method": "POST", "auth": "user", "data": {
                "verification_code": "123456"
            }},
            {"endpoint": "/api/v1/auth/mfa/setup", "method": "POST", "auth": "user", "data": {
                "verification_code": "123456"
            }},
            {"endpoint": "/api/v1/auth/mfa/verify", "method": "POST", "data": {
                "mfa_code": "123456"
            }},
            {"endpoint": "/api/v1/auth/mfa/disable", "method": "POST", "auth": "user", "data": {
                "password": "TestPassword123!", "mfa_code": "123456"
            }},
            {"endpoint": "/api/v1/auth/mfa/backup-codes/regenerate", "method": "POST", "auth": "user"},
            {"endpoint": "/api/v1/auth/mfa/qr-code", "method": "GET", "auth": "user"},
            
            # Admin endpoints
            {"endpoint": "/api/v1/admin/dashboard", "method": "GET", "auth": "admin"},
            {"endpoint": "/api/v1/admin/users", "method": "GET", "auth": "admin"},
            {"endpoint": "/api/v1/admin/users", "method": "POST", "auth": "admin", "data": {
                "username": f"adminuser_{int(time.time())}", 
                "email": f"adminuser_{int(time.time())}@example.com",
                "password": "AdminPass123!"
            }},
            {"endpoint": "/api/v1/admin/users/1", "method": "GET", "auth": "admin"},
            {"endpoint": "/api/v1/admin/users/1", "method": "PUT", "auth": "admin", "data": {
                "first_name": "Updated"
            }},
            {"endpoint": "/api/v1/admin/users/1", "method": "DELETE", "auth": "admin", "data": {
                "reason": "Test deletion"
            }},
            {"endpoint": "/api/v1/admin/users/1/reset-password", "method": "POST", "auth": "admin", "data": {
                "user_id": 1, "new_password": "NewPass123!"
            }},
            {"endpoint": "/api/v1/admin/users/bulk-update", "method": "POST", "auth": "admin", "data": {
                "user_ids": [1], "updates": {"is_active": True}
            }},
            {"endpoint": "/api/v1/admin/users/bulk-action", "method": "POST", "auth": "admin", "data": {
                "user_ids": [1], "action": "activate"
            }},
            
            # Library endpoints
            {"endpoint": "/api/v1/library/books", "method": "GET", "auth": "user"},
            {"endpoint": "/api/v1/library/books", "method": "POST", "auth": "admin", "data": {
                "isbn": "978-1234567890", "title": "Test Book", "author": "Test Author", "category": "fiction"
            }},
            {"endpoint": "/api/v1/library/books/1", "method": "GET", "auth": "user"},
            {"endpoint": "/api/v1/library/books/1", "method": "PUT", "auth": "admin", "data": {
                "title": "Updated Book"
            }},
            {"endpoint": "/api/v1/library/books/1", "method": "DELETE", "auth": "admin"},
            {"endpoint": "/api/v1/library/loans", "method": "GET", "auth": "user"},
            {"endpoint": "/api/v1/library/loans", "method": "POST", "auth": "user", "data": {
                "book_id": 1
            }},
            {"endpoint": "/api/v1/library/loans/1/return", "method": "PUT", "auth": "user"},
            {"endpoint": "/api/v1/library/stats", "method": "GET", "auth": "admin"},
            
            # Notification endpoints
            {"endpoint": "/api/v1/notifications/", "method": "GET", "auth": "user"},
            {"endpoint": "/api/v1/notifications/unread-count", "method": "GET", "auth": "user"},
            {"endpoint": "/api/v1/notifications/1/read", "method": "PUT", "auth": "user"},
            {"endpoint": "/api/v1/notifications/mark-all-read", "method": "PUT", "auth": "user"},
            {"endpoint": "/api/v1/notifications/1", "method": "DELETE", "auth": "user"},
            {"endpoint": "/api/v1/notifications/admin/send", "method": "POST", "auth": "admin", "data": {
                "user_id": 1, "type": "admin_message", "title": "Test", "message": "Test message"
            }},
            {"endpoint": "/api/v1/notifications/admin/bulk-send", "method": "POST", "auth": "admin", "data": {
                "user_ids": [1], "type": "admin_message", "title": "Test", "message": "Test message"
            }},
            {"endpoint": "/api/v1/notifications/admin/all", "method": "GET", "auth": "admin"},
            {"endpoint": "/api/v1/notifications/admin/stats", "method": "GET", "auth": "admin"},
            {"endpoint": "/api/v1/notifications/admin/send-email", "method": "POST", "auth": "admin", "data": {
                "to_email": "test@example.com", "subject": "Test", "html_content": "Test email"
            }}
        ]
        
        results = []
        
        for test_config in endpoint_tests:
            headers = {}
            if test_config.get("auth") == "user" and self.user_token:
                headers["Authorization"] = f"Bearer {self.user_token}"
            elif test_config.get("auth") == "admin" and self.admin_token:
                headers["Authorization"] = f"Bearer {self.admin_token}"
                
            result = self.test_endpoint(
                endpoint=test_config["endpoint"],
                method=test_config["method"],
                headers=headers,
                data=test_config.get("data"),
                params=test_config.get("params")
            )
            
            # Add additional context
            if test_config.get("auth"):
                result["description"] = f"Requires {test_config['auth']} authentication"
            else:
                result["description"] = "Public endpoint"
                
            # Add solutions based on status
            if result["status"] == "AUTH_REQUIRED":
                result["solutions"] = "Provide valid authentication token"
            elif result["status"] == "VALIDATION_ERROR":
                result["solutions"] = "Check request body schema and validation rules"
            elif result["status"] == "SERVER_ERROR":
                result["solutions"] = "Check server logs and database connectivity"
            elif result["status"] == "NOT_FOUND":
                result["solutions"] = "Verify endpoint URL and route configuration"
            elif result["status"] == "OPERATIONAL":
                result["solutions"] = "Endpoint is working correctly"
                
            results.append(result)
            
        return results

    def generate_markdown_report(self, results: List[Dict]):
        """Generate markdown documentation"""
        
        markdown = """# ENDPOINTS STATUS DOCUMENTATION

This document provides comprehensive status information for all API endpoints in the User Management Service.

**Last Updated:** {timestamp}
**Service URL:** {base_url}
**Total Endpoints Tested:** {total_endpoints}

## Summary

| Status | Count | Percentage |
|--------|-------|------------|
| OPERATIONAL | {operational} | {operational_pct:.1f}% |
| AUTH_REQUIRED | {auth_required} | {auth_required_pct:.1f}% |
| VALIDATION_ERROR | {validation_error} | {validation_error_pct:.1f}% |
| SERVER_ERROR | {server_error} | {server_error_pct:.1f}% |
| NOT_FOUND | {not_found} | {not_found_pct:.1f}% |
| ERROR | {error} | {error_pct:.1f}% |

## Detailed Endpoint Status

| Endpoint | HTTP Method | HTTP Request (Header, Body) | HTTP Response (Header, Body) | Parameters & Sample Values | Description | Validation Fields | Required Data Type | Error Message | Evidence | Status | Solutions |
|----------|-------------|------------------------------|------------------------------|---------------------------|-------------|-------------------|-------------------|---------------|----------|--------|-----------|
""".format(
            timestamp=datetime.now().isoformat(),
            base_url=BASE_URL,
            total_endpoints=len(results),
            operational=len([r for r in results if r['status'] == 'OPERATIONAL']),
            operational_pct=len([r for r in results if r['status'] == 'OPERATIONAL']) / len(results) * 100,
            auth_required=len([r for r in results if r['status'] == 'AUTH_REQUIRED']),
            auth_required_pct=len([r for r in results if r['status'] == 'AUTH_REQUIRED']) / len(results) * 100,
            validation_error=len([r for r in results if r['status'] == 'VALIDATION_ERROR']),
            validation_error_pct=len([r for r in results if r['status'] == 'VALIDATION_ERROR']) / len(results) * 100,
            server_error=len([r for r in results if r['status'] == 'SERVER_ERROR']),
            server_error_pct=len([r for r in results if r['status'] == 'SERVER_ERROR']) / len(results) * 100,
            not_found=len([r for r in results if r['status'] == 'NOT_FOUND']),
            not_found_pct=len([r for r in results if r['status'] == 'NOT_FOUND']) / len(results) * 100,
            error=len([r for r in results if r['status'] == 'ERROR']),
            error_pct=len([r for r in results if r['status'] == 'ERROR']) / len(results) * 100
        )
        
        for result in results:
            # Format request headers
            req_headers = json.dumps(result['request_headers'], indent=2) if result['request_headers'] else "None"
            req_body = json.dumps(result['request_body'], indent=2) if result['request_body'] else "None"
            
            # Format response headers (truncated)
            resp_headers = str(dict(result['response_headers']))[:100] + "..." if len(str(result['response_headers'])) > 100 else str(result['response_headers'])
            resp_body = str(result['response_body'])[:200] + "..." if len(str(result['response_body'])) > 200 else str(result['response_body'])
            
            # Format parameters
            params = json.dumps(result['request_params']) if result['request_params'] else "None"
            
            markdown += f"""| `{result['endpoint']}` | {result['method']} | **Headers:** {req_headers}<br>**Body:** {req_body} | **Headers:** {resp_headers}<br>**Body:** {resp_body} | {params} | {result['description']} | {', '.join(result['validation_fields']) if result['validation_fields'] else 'N/A'} | {result['required_data_type']} | {result['error_message'] or 'None'} | {result['evidence']} | **{result['status']}** | {result['solutions']} |
"""
        
        markdown += f"""

## Test Environment Details

- **Docker Compose Status:** Running
- **Database:** PostgreSQL 13
- **Service Port:** 8000
- **Test User Token:** {'Available' if self.user_token else 'Not Available'}
- **Admin Token:** {'Available' if self.admin_token else 'Not Available'}

## Recommendations

1. **Authentication Issues:** Ensure all protected endpoints properly validate JWT tokens
2. **Validation Errors:** Review Pydantic schemas and validation rules
3. **Server Errors:** Check database connectivity and error handling
4. **Missing Endpoints:** Verify route registration in main.py

## Next Steps

1. Fix any VALIDATION_ERROR or SERVER_ERROR endpoints
2. Implement proper error handling for all endpoints
3. Add comprehensive input validation
4. Ensure proper CORS configuration
5. Set up monitoring and logging for production

---

*Report generated by Advanced API Testing Tool*
*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return markdown

def main():
    tester = AdvancedAPITester()
    
    # Setup test data
    tester.setup_test_data()
    
    # Run comprehensive tests
    results = tester.run_comprehensive_tests()
    
    # Generate and save markdown report
    markdown_report = tester.generate_markdown_report(results)
    
    with open('docs/ENDPOINTS_STATUS.md', 'w', encoding='utf-8') as f:
        f.write(markdown_report)
        
    # Save JSON results
    with open('endpoint_detailed_results.json', 'w') as f:
        json.dump(results, f, indent=2)
        
    logger.info(f"Testing completed. {len(results)} endpoints tested.")
    logger.info("Markdown report saved to docs/ENDPOINTS_STATUS.md")
    logger.info("JSON results saved to endpoint_detailed_results.json")
    
    # Print summary
    status_counts = {}
    for result in results:
        status = result['status']
        status_counts[status] = status_counts.get(status, 0) + 1
        
    print(f"\nEndpoint Status Summary:")
    for status, count in status_counts.items():
        print(f"{status}: {count}")

if __name__ == "__main__":
    main()
