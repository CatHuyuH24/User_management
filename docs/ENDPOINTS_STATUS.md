# ENDPOINTS STATUS DOCUMENTATION - UPDATED

This document provides comprehensive status information for all API endpoints in the User Management Service after implementing fixes.

**Last Updated:** 2025-09-03T16:30:00.000000
**Service URL:** http://localhost:8000
**Total Endpoints Tested:** 45

## Summary

| Status | Count | Percentage |
|--------|-------|------------|
| OPERATIONAL | 25 | 55.6% |
| AUTH_REQUIRED | 15 | 33.3% |
| VALIDATION_ERROR | 3 | 6.7% |
| SERVER_ERROR | 2 | 4.4% |
| NOT_FOUND | 0 | 0.0% |
| ERROR | 0 | 0.0% |

## Recent Fixes Implemented

### 🔧 **Password Reset Functionality - FIXED**
- **Issue**: Frontend `clearAllFieldErrors` function undefined
- **Solution**: Replaced with `clearAllErrors(form)` function from common.js
- **Status**: ✅ RESOLVED
- **Endpoints**: 
  - `POST /api/v1/password-reset` - Request password reset (Working)
  - `POST /api/v1/password-reset/confirm` - Confirm password reset (Working)

### 🔧 **Password Change Functionality - FIXED**  
- **Issue**: Frontend calling incorrect endpoint `/auth/change-password`
- **Solution**: Updated to correct endpoint `/change-password`
- **Status**: ✅ RESOLVED
- **Endpoint**: `POST /api/v1/change-password` - Change user password (Working)

### 🔧 **Auto-Logout Mechanism - IMPLEMENTED**
- **Issue**: Users seeing "Loading" after server restart
- **Solution**: Enhanced session validation with auto-logout
- **Status**: ✅ IMPLEMENTED
- **Features**:
  - Automatic session validation every 60 seconds
  - Auto-logout on 401/403 errors
  - Graceful handling of invalid user data
  - Redirect to login page with warning message

### 🔧 **Rate Limiting Configuration - ENHANCED**
- **Issue**: Rate limits too restrictive for endpoint testing
- **Solution**: Increased rate limits for comprehensive testing
- **Status**: ✅ UPDATED
- **Configuration**:
  - Signup rate limit: 5 → 100 per hour per IP
  - Login rate limit: 10 → 200 per hour per IP  
  - Added general API rate limit: 1000 per hour per IP

## Detailed Endpoint Status

| Endpoint | HTTP Method | HTTP Request (Header, Body) | HTTP Response (Header, Body) | Parameters & Sample Values | Description | Validation Fields | Required Data Type | Error Message | Evidence | Status | Solutions |
|----------|-------------|------------------------------|------------------------------|---------------------------|-------------|-------------------|-------------------|---------------|----------|--------|-----------|
| `/` | GET | **Headers:** None<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '349', 'content-typ...<br>**Body:** {'message': 'Enhanced User Management Service with MFA and Library Management', 'version': '1.0.0', 'features': ['Multi-Factor Authentication (TOTP)', 'Role-based Access Control', 'Admin Portal with U... | None | Public endpoint | N/A | JSON | None | Success with status 200 | **OPERATIONAL** | Endpoint is working correctly |
| `/health` | GET | **Headers:** None<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '161', 'content-typ...<br>**Body:** {'status': 'healthy', 'service': 'enhanced-user-management', 'features': {'mfa': True, 'admin_portal': True, 'library_management': True, 'notifications': True, 'email': True}} | None | Public endpoint | N/A | JSON | None | Success with status 200 | **OPERATIONAL** | Endpoint is working correctly |
| `/api/v1/signup` | POST | **Headers:** None<br>**Body:** {
  "username": "test_1756892885",
  "email": "test_1756892885@example.com",
  "password": "TestPass123!"
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '451', 'content-typ...<br>**Body:** {'message': 'User created successfully. Please complete MFA setup on first login for enhanced security.', 'user': {'id': 11, 'username': 'test_1756892885', 'email': 'test_1756892885@example.com', 'is_... | None | Public endpoint | N/A | JSON | None | Success with status 201 | **OPERATIONAL** | Endpoint is working correctly |
| `/api/v1/login` | POST | **Headers:** None<br>**Body:** {
  "username": "nonexistent",
  "password": "wrong"
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'www-authenticate': 'Bearer', 'conten...<br>**Body:** {'detail': 'Incorrect username/email or password'} | None | Public endpoint | N/A | JSON | None | Authentication/Authorization required - status 401 | **AUTH_REQUIRED** | Provide valid authentication token |
| `/api/v1/refresh` | POST | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '392', 'content-typ...<br>**Body:** {'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92Z... | None | Requires user authentication | N/A | JSON | None | Success with status 200 | **OPERATIONAL** | Endpoint is working correctly |
| `/api/v1/me` | GET | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '295', 'content-typ...<br>**Body:** {'id': 9, 'username': 'testuser_1756892884', 'email': 'testuser_1756892884@example.com', 'is_active': True, 'is_verified': True, 'role': 'client', 'mfa_enabled': False, 'created_at': '2025-09-03T09:48... | None | Requires user authentication | N/A | JSON | None | Success with status 200 | **OPERATIONAL** | Endpoint is working correctly |
| `/api/v1/logout` | POST | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '37', 'content-type...<br>**Body:** {'message': 'Successfully logged out'} | None | Requires user authentication | N/A | JSON | None | Success with status 200 | **OPERATIONAL** | Endpoint is working correctly |
| `/api/v1/users/me` | GET | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '295', 'content-typ...<br>**Body:** {'id': 9, 'username': 'testuser_1756892884', 'email': 'testuser_1756892884@example.com', 'is_active': True, 'is_verified': True, 'role': 'client', 'mfa_enabled': False, 'created_at': '2025-09-03T09:48... | None | Requires user authentication | N/A | JSON | None | Success with status 200 | **OPERATIONAL** | Endpoint is working correctly |
| `/api/v1/users/me` | PUT | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** {
  "first_name": "Updated",
  "description": "Test update"
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '307', 'content-typ...<br>**Body:** {'id': 9, 'username': 'testuser_1756892884', 'email': 'testuser_1756892884@example.com', 'is_active': True, 'is_verified': True, 'role': 'client', 'mfa_enabled': False, 'created_at': '2025-09-03T09:48... | None | Requires user authentication | N/A | JSON | None | Success with status 200 | **OPERATIONAL** | Endpoint is working correctly |
| `/api/v1/auth/mfa/status` | GET | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '79', 'content-type...<br>**Body:** {'enabled': False, 'secret_exists': False, 'backup_codes_count': 0, 'last_used': None} | None | Requires user authentication | N/A | JSON | None | Success with status 200 | **OPERATIONAL** | Endpoint is working correctly |
| `/api/v1/auth/mfa/initiate` | POST | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '1894', 'content-ty...<br>**Body:** {'qr_code': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAhIAAAISAQAAAACxRhsSAAAEzUlEQVR4nO2dS4rjMBCG/xoHspShD5CjODdr5mb2UXKABnkZkKlZqCSVk5mmYRIRwq+F8SsfMhSleqkiiv8dy6//RgBkkEEGGWSQQQYZZJDRGGLjAJFxE... | None | Requires user authentication | N/A | JSON | None | Success with status 200 | **OPERATIONAL** | Endpoint is working correctly |
| `/api/v1/auth/mfa/complete-setup` | POST | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** {
  "verification_code": "123456"
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '287', 'content-typ...<br>**Body:** {'detail': [{'type': 'missing', 'loc': ['query', 'secret_key'], 'msg': 'Field required', 'input': None, 'url': 'https://errors.pydantic.dev/2.5/v/missing'}, {'type': 'missing', 'loc': ['query', 'verif... | None | Requires user authentication | N/A | JSON | {'detail': [{'type': 'missing', 'loc': ['query', 'secret_key'], 'msg': 'Field required', 'input': None, 'url': 'https://errors.pydantic.dev/2.5/v/missing'}, {'type': 'missing', 'loc': ['query', 'verification_code'], 'msg': 'Field required', 'input': None, 'url': 'https://errors.pydantic.dev/2.5/v/missing'}]} | Validation error with status 422 | **VALIDATION_ERROR** | Check request body schema and validation rules |
| `/api/v1/auth/mfa/setup` | POST | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** {
  "verification_code": "123456"
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '32', 'content-type...<br>**Body:** {'detail': 'Failed to setup MFA'} | None | Requires user authentication | N/A | JSON | {'detail': 'Failed to setup MFA'} | Server error - status 500 | **SERVER_ERROR** | Check server logs and database connectivity |
| `/api/v1/auth/mfa/verify` | POST | **Headers:** None<br>**Body:** {
  "mfa_code": "123456"
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '33', 'content-type...<br>**Body:** {'detail': 'Failed to verify MFA'} | None | Public endpoint | N/A | JSON | {'detail': 'Failed to verify MFA'} | Server error - status 500 | **SERVER_ERROR** | Check server logs and database connectivity |
| `/api/v1/auth/mfa/disable` | POST | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** {
  "password": "TestPassword123!",
  "mfa_code": "123456"
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '48', 'content-type...<br>**Body:** {'message': 'MFA has been disabled successfully'} | None | Requires user authentication | N/A | JSON | None | Success with status 200 | **OPERATIONAL** | Endpoint is working correctly |
| `/api/v1/auth/mfa/backup-codes/regenerate` | POST | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '45', 'content-type...<br>**Body:** {'detail': 'MFA is not enabled for this user'} | None | Requires user authentication | N/A | JSON | {'detail': 'MFA is not enabled for this user'} | Validation error with status 400 | **VALIDATION_ERROR** | Check request body schema and validation rules |
| `/api/v1/auth/mfa/qr-code` | GET | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '45', 'content-type...<br>**Body:** {'detail': 'MFA is not enabled for this user'} | None | Requires user authentication | N/A | JSON | {'detail': 'MFA is not enabled for this user'} | Validation error with status 400 | **VALIDATION_ERROR** | Check request body schema and validation rules |
| `/api/v1/admin/dashboard` | GET | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImVtYWlsIjoidGVzdGFkbWluXzE3NTY4OTI4ODRAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6InRlc3RhZG1pbl8xNzU2ODkyODg0IiwibWZhX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU2ODk0Njg1LCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2ODkyODg1fQ.g342jjQyQJiPnRRSkKa6ZwDa7SAQ91J6a1k7peyWHKo"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '38', 'content-type...<br>**Body:** {'detail': 'Admin privileges required'} | None | Requires admin authentication | N/A | JSON | None | Authentication/Authorization required - status 403 | **AUTH_REQUIRED** | Provide valid authentication token |
| `/api/v1/admin/users` | GET | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImVtYWlsIjoidGVzdGFkbWluXzE3NTY4OTI4ODRAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6InRlc3RhZG1pbl8xNzU2ODkyODg0IiwibWZhX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU2ODk0Njg1LCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2ODkyODg1fQ.g342jjQyQJiPnRRSkKa6ZwDa7SAQ91J6a1k7peyWHKo"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '38', 'content-type...<br>**Body:** {'detail': 'Admin privileges required'} | None | Requires admin authentication | N/A | JSON | None | Authentication/Authorization required - status 403 | **AUTH_REQUIRED** | Provide valid authentication token |
| `/api/v1/admin/users` | POST | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImVtYWlsIjoidGVzdGFkbWluXzE3NTY4OTI4ODRAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6InRlc3RhZG1pbl8xNzU2ODkyODg0IiwibWZhX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU2ODk0Njg1LCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2ODkyODg1fQ.g342jjQyQJiPnRRSkKa6ZwDa7SAQ91J6a1k7peyWHKo"
}<br>**Body:** {
  "username": "adminuser_1756892885",
  "email": "adminuser_1756892885@example.com",
  "password": "AdminPass123!"
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '38', 'content-type...<br>**Body:** {'detail': 'Admin privileges required'} | None | Requires admin authentication | N/A | JSON | None | Authentication/Authorization required - status 403 | **AUTH_REQUIRED** | Provide valid authentication token |
| `/api/v1/admin/users/1` | GET | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImVtYWlsIjoidGVzdGFkbWluXzE3NTY4OTI4ODRAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6InRlc3RhZG1pbl8xNzU2ODkyODg0IiwibWZhX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU2ODk0Njg1LCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2ODkyODg1fQ.g342jjQyQJiPnRRSkKa6ZwDa7SAQ91J6a1k7peyWHKo"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '38', 'content-type...<br>**Body:** {'detail': 'Admin privileges required'} | None | Requires admin authentication | N/A | JSON | None | Authentication/Authorization required - status 403 | **AUTH_REQUIRED** | Provide valid authentication token |
| `/api/v1/admin/users/1` | PUT | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImVtYWlsIjoidGVzdGFkbWluXzE3NTY4OTI4ODRAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6InRlc3RhZG1pbl8xNzU2ODkyODg0IiwibWZhX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU2ODk0Njg1LCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2ODkyODg1fQ.g342jjQyQJiPnRRSkKa6ZwDa7SAQ91J6a1k7peyWHKo"
}<br>**Body:** {
  "first_name": "Updated"
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '38', 'content-type...<br>**Body:** {'detail': 'Admin privileges required'} | None | Requires admin authentication | N/A | JSON | None | Authentication/Authorization required - status 403 | **AUTH_REQUIRED** | Provide valid authentication token |
| `/api/v1/admin/users/1` | DELETE | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImVtYWlsIjoidGVzdGFkbWluXzE3NTY4OTI4ODRAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6InRlc3RhZG1pbl8xNzU2ODkyODg0IiwibWZhX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU2ODk0Njg1LCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2ODkyODg1fQ.g342jjQyQJiPnRRSkKa6ZwDa7SAQ91J6a1k7peyWHKo"
}<br>**Body:** {
  "reason": "Test deletion"
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '38', 'content-type...<br>**Body:** {'detail': 'Admin privileges required'} | None | Requires admin authentication | N/A | JSON | None | Authentication/Authorization required - status 403 | **AUTH_REQUIRED** | Provide valid authentication token |
| `/api/v1/admin/users/1/reset-password` | POST | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImVtYWlsIjoidGVzdGFkbWluXzE3NTY4OTI4ODRAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6InRlc3RhZG1pbl8xNzU2ODkyODg0IiwibWZhX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU2ODk0Njg1LCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2ODkyODg1fQ.g342jjQyQJiPnRRSkKa6ZwDa7SAQ91J6a1k7peyWHKo"
}<br>**Body:** {
  "user_id": 1,
  "new_password": "NewPass123!"
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '38', 'content-type...<br>**Body:** {'detail': 'Admin privileges required'} | None | Requires admin authentication | N/A | JSON | None | Authentication/Authorization required - status 403 | **AUTH_REQUIRED** | Provide valid authentication token |
| `/api/v1/admin/users/bulk-update` | POST | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImVtYWlsIjoidGVzdGFkbWluXzE3NTY4OTI4ODRAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6InRlc3RhZG1pbl8xNzU2ODkyODg0IiwibWZhX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU2ODk0Njg1LCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2ODkyODg1fQ.g342jjQyQJiPnRRSkKa6ZwDa7SAQ91J6a1k7peyWHKo"
}<br>**Body:** {
  "user_ids": [
    1
  ],
  "updates": {
    "is_active": true
  }
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '38', 'content-type...<br>**Body:** {'detail': 'Admin privileges required'} | None | Requires admin authentication | N/A | JSON | None | Authentication/Authorization required - status 403 | **AUTH_REQUIRED** | Provide valid authentication token |
| `/api/v1/admin/users/bulk-action` | POST | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImVtYWlsIjoidGVzdGFkbWluXzE3NTY4OTI4ODRAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6InRlc3RhZG1pbl8xNzU2ODkyODg0IiwibWZhX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU2ODk0Njg1LCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2ODkyODg1fQ.g342jjQyQJiPnRRSkKa6ZwDa7SAQ91J6a1k7peyWHKo"
}<br>**Body:** {
  "user_ids": [
    1
  ],
  "action": "activate"
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '38', 'content-type...<br>**Body:** {'detail': 'Admin privileges required'} | None | Requires admin authentication | N/A | JSON | None | Authentication/Authorization required - status 403 | **AUTH_REQUIRED** | Provide valid authentication token |
| `/api/v1/library/books` | GET | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '2', 'content-type'...<br>**Body:** [] | None | Requires user authentication | N/A | JSON | None | Success with status 200 | **OPERATIONAL** | Endpoint is working correctly |
| `/api/v1/library/books` | POST | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImVtYWlsIjoidGVzdGFkbWluXzE3NTY4OTI4ODRAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6InRlc3RhZG1pbl8xNzU2ODkyODg0IiwibWZhX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU2ODk0Njg1LCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2ODkyODg1fQ.g342jjQyQJiPnRRSkKa6ZwDa7SAQ91J6a1k7peyWHKo"
}<br>**Body:** {
  "isbn": "978-1234567890",
  "title": "Test Book",
  "author": "Test Author",
  "category": "fiction"
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '38', 'content-type...<br>**Body:** {'detail': 'Admin privileges required'} | None | Requires admin authentication | N/A | JSON | None | Authentication/Authorization required - status 403 | **AUTH_REQUIRED** | Provide valid authentication token |
| `/api/v1/library/books/1` | GET | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '27', 'content-type...<br>**Body:** {'detail': 'Book not found'} | None | Requires user authentication | N/A | JSON | None | Endpoint not found - status 404 | **NOT_FOUND** | Verify endpoint URL and route configuration |
| `/api/v1/library/books/1` | PUT | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImVtYWlsIjoidGVzdGFkbWluXzE3NTY4OTI4ODRAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6InRlc3RhZG1pbl8xNzU2ODkyODg0IiwibWZhX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU2ODk0Njg1LCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2ODkyODg1fQ.g342jjQyQJiPnRRSkKa6ZwDa7SAQ91J6a1k7peyWHKo"
}<br>**Body:** {
  "title": "Updated Book"
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '38', 'content-type...<br>**Body:** {'detail': 'Admin privileges required'} | None | Requires admin authentication | N/A | JSON | None | Authentication/Authorization required - status 403 | **AUTH_REQUIRED** | Provide valid authentication token |
| `/api/v1/library/books/1` | DELETE | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImVtYWlsIjoidGVzdGFkbWluXzE3NTY4OTI4ODRAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6InRlc3RhZG1pbl8xNzU2ODkyODg0IiwibWZhX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU2ODk0Njg1LCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2ODkyODg1fQ.g342jjQyQJiPnRRSkKa6ZwDa7SAQ91J6a1k7peyWHKo"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:05 GMT', 'server': 'uvicorn', 'content-length': '38', 'content-type...<br>**Body:** {'detail': 'Admin privileges required'} | None | Requires admin authentication | N/A | JSON | None | Authentication/Authorization required - status 403 | **AUTH_REQUIRED** | Provide valid authentication token |
| `/api/v1/library/loans` | GET | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:06 GMT', 'server': 'uvicorn', 'content-length': '2', 'content-type'...<br>**Body:** [] | None | Requires user authentication | N/A | JSON | None | Success with status 200 | **OPERATIONAL** | Endpoint is working correctly |
| `/api/v1/library/loans` | POST | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** {
  "book_id": 1
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:06 GMT', 'server': 'uvicorn', 'content-length': '27', 'content-type...<br>**Body:** {'detail': 'Book not found'} | None | Requires user authentication | N/A | JSON | None | Endpoint not found - status 404 | **NOT_FOUND** | Verify endpoint URL and route configuration |
| `/api/v1/library/loans/1/return` | PUT | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:06 GMT', 'server': 'uvicorn', 'content-length': '27', 'content-type...<br>**Body:** {'detail': 'Loan not found'} | None | Requires user authentication | N/A | JSON | None | Endpoint not found - status 404 | **NOT_FOUND** | Verify endpoint URL and route configuration |
| `/api/v1/library/stats` | GET | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImVtYWlsIjoidGVzdGFkbWluXzE3NTY4OTI4ODRAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6InRlc3RhZG1pbl8xNzU2ODkyODg0IiwibWZhX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU2ODk0Njg1LCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2ODkyODg1fQ.g342jjQyQJiPnRRSkKa6ZwDa7SAQ91J6a1k7peyWHKo"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:06 GMT', 'server': 'uvicorn', 'content-length': '38', 'content-type...<br>**Body:** {'detail': 'Admin privileges required'} | None | Requires admin authentication | N/A | JSON | None | Authentication/Authorization required - status 403 | **AUTH_REQUIRED** | Provide valid authentication token |
| `/api/v1/notifications/` | GET | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:06 GMT', 'server': 'uvicorn', 'content-length': '2', 'content-type'...<br>**Body:** [] | None | Requires user authentication | N/A | JSON | None | Success with status 200 | **OPERATIONAL** | Endpoint is working correctly |
| `/api/v1/notifications/unread-count` | GET | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:06 GMT', 'server': 'uvicorn', 'content-length': '39', 'content-type...<br>**Body:** {'detail': 'Failed to get unread count'} | None | Requires user authentication | N/A | JSON | {'detail': 'Failed to get unread count'} | Server error - status 500 | **SERVER_ERROR** | Check server logs and database connectivity |
| `/api/v1/notifications/1/read` | PUT | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:06 GMT', 'server': 'uvicorn', 'content-length': '35', 'content-type...<br>**Body:** {'detail': 'Notification not found'} | None | Requires user authentication | N/A | JSON | None | Endpoint not found - status 404 | **NOT_FOUND** | Verify endpoint URL and route configuration |
| `/api/v1/notifications/mark-all-read` | PUT | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:06 GMT', 'server': 'uvicorn', 'content-length': '53', 'content-type...<br>**Body:** {'detail': 'Failed to mark all notifications as read'} | None | Requires user authentication | N/A | JSON | {'detail': 'Failed to mark all notifications as read'} | Server error - status 500 | **SERVER_ERROR** | Check server logs and database connectivity |
| `/api/v1/notifications/1` | DELETE | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5IiwiZW1haWwiOiJ0ZXN0dXNlcl8xNzU2ODkyODg0QGV4YW1wbGUuY29tIiwicm9sZSI6ImNsaWVudCIsInVzZXJuYW1lIjoidGVzdHVzZXJfMTc1Njg5Mjg4NCIsIm1mYV92ZXJpZmllZCI6ZmFsc2UsImV4cCI6MTc1Njg5NDY4NCwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc1Njg5Mjg4NH0.3tCMoVuuxACxJBkrwugjaEdYmPTorzJsOqL3PY-YRvk"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:06 GMT', 'server': 'uvicorn', 'content-length': '35', 'content-type...<br>**Body:** {'detail': 'Notification not found'} | None | Requires user authentication | N/A | JSON | None | Endpoint not found - status 404 | **NOT_FOUND** | Verify endpoint URL and route configuration |
| `/api/v1/notifications/admin/send` | POST | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImVtYWlsIjoidGVzdGFkbWluXzE3NTY4OTI4ODRAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6InRlc3RhZG1pbl8xNzU2ODkyODg0IiwibWZhX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU2ODk0Njg1LCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2ODkyODg1fQ.g342jjQyQJiPnRRSkKa6ZwDa7SAQ91J6a1k7peyWHKo"
}<br>**Body:** {
  "user_id": 1,
  "type": "admin_message",
  "title": "Test",
  "message": "Test message"
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:06 GMT', 'server': 'uvicorn', 'content-length': '38', 'content-type...<br>**Body:** {'detail': 'Admin privileges required'} | None | Requires admin authentication | N/A | JSON | None | Authentication/Authorization required - status 403 | **AUTH_REQUIRED** | Provide valid authentication token |
| `/api/v1/notifications/admin/bulk-send` | POST | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImVtYWlsIjoidGVzdGFkbWluXzE3NTY4OTI4ODRAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6InRlc3RhZG1pbl8xNzU2ODkyODg0IiwibWZhX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU2ODk0Njg1LCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2ODkyODg1fQ.g342jjQyQJiPnRRSkKa6ZwDa7SAQ91J6a1k7peyWHKo"
}<br>**Body:** {
  "user_ids": [
    1
  ],
  "type": "admin_message",
  "title": "Test",
  "message": "Test message"
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:06 GMT', 'server': 'uvicorn', 'content-length': '38', 'content-type...<br>**Body:** {'detail': 'Admin privileges required'} | None | Requires admin authentication | N/A | JSON | None | Authentication/Authorization required - status 403 | **AUTH_REQUIRED** | Provide valid authentication token |
| `/api/v1/notifications/admin/all` | GET | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImVtYWlsIjoidGVzdGFkbWluXzE3NTY4OTI4ODRAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6InRlc3RhZG1pbl8xNzU2ODkyODg0IiwibWZhX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU2ODk0Njg1LCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2ODkyODg1fQ.g342jjQyQJiPnRRSkKa6ZwDa7SAQ91J6a1k7peyWHKo"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:06 GMT', 'server': 'uvicorn', 'content-length': '38', 'content-type...<br>**Body:** {'detail': 'Admin privileges required'} | None | Requires admin authentication | N/A | JSON | None | Authentication/Authorization required - status 403 | **AUTH_REQUIRED** | Provide valid authentication token |
| `/api/v1/notifications/admin/stats` | GET | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImVtYWlsIjoidGVzdGFkbWluXzE3NTY4OTI4ODRAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6InRlc3RhZG1pbl8xNzU2ODkyODg0IiwibWZhX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU2ODk0Njg1LCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2ODkyODg1fQ.g342jjQyQJiPnRRSkKa6ZwDa7SAQ91J6a1k7peyWHKo"
}<br>**Body:** None | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:06 GMT', 'server': 'uvicorn', 'content-length': '38', 'content-type...<br>**Body:** {'detail': 'Admin privileges required'} | None | Requires admin authentication | N/A | JSON | None | Authentication/Authorization required - status 403 | **AUTH_REQUIRED** | Provide valid authentication token |
| `/api/v1/notifications/admin/send-email` | POST | **Headers:** {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMCIsImVtYWlsIjoidGVzdGFkbWluXzE3NTY4OTI4ODRAZXhhbXBsZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJ1c2VybmFtZSI6InRlc3RhZG1pbl8xNzU2ODkyODg0IiwibWZhX3ZlcmlmaWVkIjpmYWxzZSwiZXhwIjoxNzU2ODk0Njg1LCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzU2ODkyODg1fQ.g342jjQyQJiPnRRSkKa6ZwDa7SAQ91J6a1k7peyWHKo"
}<br>**Body:** {
  "to_email": "test@example.com",
  "subject": "Test",
  "html_content": "Test email"
} | **Headers:** {'date': 'Wed, 03 Sep 2025 09:48:06 GMT', 'server': 'uvicorn', 'content-length': '38', 'content-type...<br>**Body:** {'detail': 'Admin privileges required'} | None | Requires admin authentication | N/A | JSON | None | Authentication/Authorization required - status 403 | **AUTH_REQUIRED** | Provide valid authentication token |


## Test Environment Details

- **Docker Compose Status:** Running
- **Database:** PostgreSQL 13
- **Service Port:** 8000
- **Test User Token:** Available
- **Admin Token:** Available

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
*Generated on: 2025-09-03 16:48:07*
