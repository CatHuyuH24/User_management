# Admin Portal Design

## Overview

The Admin Portal provides comprehensive management capabilities for the User Management and Library Management systems, with enhanced security through mandatory MFA.

## Core Features

### User Management

- View all registered users with detailed profiles
- Search and filter users by various criteria
- Delete user accounts with proper audit trail
- Reset user passwords and MFA settings
- Monitor user activity and login history
- Bulk operations for user management

### Library Management

- Complete book inventory management
- Loan monitoring and management
- Overdue book tracking and notifications
- Generate comprehensive reports
- System configuration and settings
- Category and author management

### Security & Compliance

- Mandatory MFA for all admin accounts
- Comprehensive audit logging
- Role-based access control
- Session monitoring and management
- Security alert system

## User Interface Design

### Dashboard

- **Key Metrics**: Active users, total books, active loans, overdue items
- **Recent Activity**: Latest user registrations, book additions, loan activities
- **System Status**: Server health, notification queue status
- **Quick Actions**: Add book, create user, send announcement

### User Management Interface

- **User List**: Paginated table with search and filter capabilities
- **User Details**: Full profile view with activity history
- **Bulk Actions**: Delete multiple users, send notifications
- **User Analytics**: Registration trends, activity patterns

### Library Management Interface

- **Book Catalog**: Grid and list views with advanced filtering
- **Loan Management**: Active loans, overdue tracking, renewal requests
- **Reports**: Lending statistics, popular books, user behavior
- **System Settings**: Loan duration, notification settings, penalties

## Access Control

### Admin Roles

- **Super Admin**: Full system access and configuration
- **User Admin**: User management and basic reporting
- **Library Admin**: Book and loan management
- **Read-Only Admin**: View-only access for reporting

### Permission Matrix

```
Feature                 | Super | User  | Library | Read-Only
------------------------|-------|-------|---------|----------
User CRUD              |   ✓   |   ✓   |    ✗    |    ✗
User Deletion          |   ✓   |   ✓   |    ✗    |    ✗
Book CRUD              |   ✓   |   ✗   |    ✓    |    ✗
Loan Management        |   ✓   |   ✗   |    ✓    |    ✗
System Settings        |   ✓   |   ✗   |    ✗    |    ✗
Reports Access         |   ✓   |   ✓   |    ✓    |    ✓
Audit Logs             |   ✓   |   ✗   |    ✗    |    ✗
```

## Security Requirements

### Authentication

- Mandatory MFA setup for all admin accounts
- Strong password requirements (minimum 12 characters)
- Session timeout after 30 minutes of inactivity
- Account lockout after 3 failed attempts

### Authorization

- Role-based access control (RBAC)
- Permission validation on every action
- API endpoint protection
- Resource-level access control

### Audit & Compliance

- All admin actions logged with full context
- User data access tracking
- Export capabilities for compliance reporting
- Data retention policies

## API Endpoints

### Admin Authentication

- `POST /api/v1/admin/auth/login` - Admin login with MFA
- `POST /api/v1/admin/auth/mfa/verify` - Verify admin MFA
- `POST /api/v1/admin/auth/logout` - Admin logout

### User Management

- `GET /api/v1/admin/users` - List all users (paginated)
- `GET /api/v1/admin/users/{id}` - Get user details
- `DELETE /api/v1/admin/users/{id}` - Delete user account
- `POST /api/v1/admin/users/{id}/reset-password` - Reset user password
- `POST /api/v1/admin/users/{id}/disable-mfa` - Disable user MFA
- `GET /api/v1/admin/users/{id}/activity` - Get user activity log

### Library Management

- `GET /api/v1/admin/books` - List all books with full details
- `POST /api/v1/admin/books` - Add new book
- `PUT /api/v1/admin/books/{id}` - Update book
- `DELETE /api/v1/admin/books/{id}` - Remove book
- `GET /api/v1/admin/loans` - List all loans
- `POST /api/v1/admin/loans/{id}/force-return` - Force book return

### Reports & Analytics

- `GET /api/v1/admin/reports/users` - User statistics
- `GET /api/v1/admin/reports/books` - Book statistics
- `GET /api/v1/admin/reports/loans` - Loan statistics
- `GET /api/v1/admin/reports/overdue` - Overdue books report
- `GET /api/v1/admin/audit-logs` - System audit logs

### System Management

- `GET /api/v1/admin/system/status` - System health status
- `PUT /api/v1/admin/system/settings` - Update system settings
- `POST /api/v1/admin/system/maintenance` - Trigger maintenance tasks
- `GET /api/v1/admin/system/notifications` - System notifications

## Default Admin Account

### Initial Setup

- **Email**: uynhhuc810@gmail.com
- **Password**: aAdDmMiInna33%$
- **Role**: Super Admin
- **MFA**: Required on first login
- **Status**: Active, verified

### Security Configuration

- Account cannot be deleted through UI
- Requires current password for any changes
- All actions logged with enhanced detail
- Automatic session monitoring

## Implementation Considerations

### Frontend Architecture

- Separate admin portal with distinct routing
- Component-based architecture for reusability
- Real-time updates for critical information
- Responsive design for mobile administration

### Backend Services

- Dedicated admin service for enhanced security
- Rate limiting for admin endpoints
- Input validation and sanitization
- Comprehensive error handling

### Database Design

- Admin-specific tables for enhanced audit
- Proper indexing for admin queries
- Data archiving strategies
- Backup and recovery procedures

### Monitoring & Alerting

- Admin action monitoring
- Failed login attempt alerts
- System performance monitoring
- Security incident detection
