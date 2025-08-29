# Enhanced User Management & Library System

A comprehensive user management system with Multi-Factor Authentication (MFA), Admin Portal, and Library Management capabilities built with FastAPI, PostgreSQL, and modern web technologies.

## 🚀 Features

### Core Features

- **User Registration & Authentication** - Secure user signup/login with JWT tokens
- **Multi-Factor Authentication (MFA)** - TOTP-based 2FA with QR codes and backup codes
- **Role-Based Access Control** - Client, Admin, and Super Admin roles
- **Email Verification** - Account verification via email
- **Password Security** - Strong password requirements and secure hashing

### Client Portal

- **Digital Library Access** - Browse and search extensive book collection
- **Book Borrowing & Returns** - Seamless borrowing process with due date tracking
- **Personal Dashboard** - View borrowed books, due dates, and reading history
- **Notifications Center** - Due date reminders and library announcements
- **Profile Management** - Update personal information and preferences
- **Mobile Responsive** - Full functionality on all devices

### Admin Portal

- **User Management** - Create, update, delete, and manage all users
- **Library Administration** - Complete book catalog management
- **Loan Monitoring** - Track all borrowing activities and overdue books
- **Analytics Dashboard** - Comprehensive statistics and reports
- **Bulk Operations** - Perform actions on multiple users/books simultaneously
- **Audit Trail** - Track all admin actions and changes

### Library Management

- **Book Catalog** - Complete book management with ISBN, categories, and metadata
- **Inventory Tracking** - Real-time availability and copy management
- **Loan System** - Book borrowing with due dates and renewal options
- **Search & Filtering** - Advanced book search by title, author, genre, and availability
- **Overdue Management** - Automated notifications and tracking
- **Categories & Collections** - Organize books by genre, topic, and collections

### Security Features

- **JWT Authentication** - Secure token-based authentication
- **Role-Based Authorization** - Granular permission system
- **Password Encryption** - Bcrypt hashing with salt
- **Session Management** - Secure session handling
- **Input Validation** - Comprehensive data validation and sanitization

## 🏗️ Architecture

```
user_management/
├── services/
│   └── user-service/
│       ├── app/
│       │   ├── api/           # API endpoints
│       │   │   ├── v1/        # Version 1 API
│       │   │   ├── admin.py   # Admin management
│       │   │   ├── library.py # Library management
│       │   │   ├── mfa.py     # Multi-factor auth
│       │   │   └── notifications.py
│       │   ├── core/          # Core configuration
│       │   ├── models/        # Database models
│       │   ├── schemas/       # Pydantic schemas
│       │   ├── services/      # Business logic
│       │   └── templates/     # Email templates
│       ├── scripts/           # Utility scripts
│       └── requirements.txt
├── frontend/                  # Frontend application
├── docs/                      # Documentation
└── docker-compose.yml
```

## 🛠️ Technology Stack

- **Backend**: FastAPI 0.104.1, Python 3.9+
- **Database**: PostgreSQL 13+
- **Authentication**: JWT with MFA (TOTP)
- **Email**: SMTP with HTML templates
- **Security**: bcrypt, pyotp, rate limiting
- **Documentation**: OpenAPI/Swagger
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

- Python 3.9 or higher
- PostgreSQL 13 or higher
- Docker and Docker Compose (optional)
- SMTP server for email functionality

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd user_management
```

### 2. Environment Setup

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/user_management_db
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=user_management_db

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MFA_TOKEN_EXPIRE_MINUTES=10

# Application
APP_NAME=User Management System
VERSION=1.0.0
API_V1_STR=/api/v1
DEBUG=True

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=True
FROM_EMAIL=noreply@yourapp.com
FROM_NAME=User Management System

# Redis (for background tasks)
REDIS_URL=redis://localhost:6379/0
```

### 3. Using Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f user-service

# Stop services
docker-compose down
```

### 4. Manual Setup

#### Install Dependencies

```bash
cd services/user-service
pip install -r requirements.txt
pip install -r requirements-test.txt  # For testing
```

#### Setup Database

```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Create database
createdb user_management_db
```

#### Initialize Database and Create Admin

```bash
# Run the admin creation script
python scripts/create_admin.py
```

#### Start the Service

```bash
cd services/user-service
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Testing

The project includes comprehensive testing capabilities:

#### API Integration Tests

Run the comprehensive API test suite:

```bash
cd services/user-service
python test_runner.py
```

This will test:

- ✅ Authentication (signup, login, security)
- ✅ User profile management (get, update, avatar upload)
- ✅ Admin functionality (dashboard, user management)
- ✅ Security measures (token validation, access control)
- ✅ Error handling and validation

#### Unit Tests

```bash
cd services/user-service
pytest tests/ -v
```

#### Test Coverage

The test suite covers:

- User registration and authentication
- JWT token management
- Profile updates and avatar uploads
- Admin user management and deletion
- Role-based access control
- Input validation and error handling
- Security measures and edge cases

## 🔧 Configuration

### Default Admin Account

After running the setup script, you'll have access to:

**Super Admin user**

- Username: `super`
- Email: `super@admin.com`
- Password: `SuperAdminPassword123!`
- Role: Super Admin

**Client user**

- Username: `client`
- Email: `client@example.com`
- Password: `ClientPassword123?`
- Role: Client

**Login**: Use either username or email with the password above.
**Important**: Change this password immediately after first login!

### Email Configuration

For Gmail SMTP:

1. Enable 2-factor authentication
2. Generate an app password
3. Use the app password in `SMTP_PASSWORD`

### MFA Setup

Users can enable MFA by:

1. Going to their profile settings
2. Scanning the QR code with an authenticator app
3. Entering the verification code
4. Saving the backup codes

## 📚 API Documentation

Once the service is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication

- `POST /api/v1/signup` - User registration (no email verification required)
- `POST /api/v1/login` - User login with username or email (returns MFA token if enabled)
- `POST /api/v1/auth/mfa/verify` - Complete MFA verification

**Login Methods**: Users can log in using either their username or email address with their password.

#### MFA Management

- `POST /api/v1/auth/mfa/setup` - Setup MFA for user
- `GET /api/v1/auth/mfa/status` - Get MFA status
- `POST /api/v1/auth/mfa/disable` - Disable MFA

#### Admin Portal

- `GET /api/v1/admin/dashboard` - Admin dashboard stats
- `GET /api/v1/admin/users` - List all users
- `POST /api/v1/admin/users` - Create user as admin
- `DELETE /api/v1/admin/users/{id}` - Delete user

#### Library Management

- `GET /api/v1/library/books` - List books
- `POST /api/v1/library/books` - Add book (Admin)
- `POST /api/v1/library/loans` - Borrow book
- `PUT /api/v1/library/loans/{id}/return` - Return book

#### Notifications

- `GET /api/v1/notifications/` - Get user notifications
- `PUT /api/v1/notifications/{id}/read` - Mark as read
- `POST /api/v1/notifications/admin/send` - Send notification (Admin)

## 🖥️ Frontend Application

### Features

The frontend application provides comprehensive web interfaces for both clients and administrators.

#### Client Portal (`client-dashboard.html`)

- **Dashboard Overview** - Personal library statistics and activity
- **Book Browser** - Search and filter books with advanced options
- **My Books** - Manage borrowed books, renewals, and returns
- **Notifications** - Due date reminders and library announcements
- **Profile Management** - Update personal information

#### Admin Portal (`admin-dashboard.html`)

- **Admin Dashboard** - System statistics and monitoring
- **User Management** (`admin-users.html`) - CRUD operations for all users
- **Library Management** (`admin-library.html`) - Complete book catalog administration
- **Analytics** - Borrowing patterns and system usage reports

### Access Points

- **Home Page**: `http://localhost:3001/` - Welcome page with registration/login
- **Login**: `http://localhost:3001/login.html` - Authentication page
- **Registration**: `http://localhost:3001/signup.html` - New user registration
- **Client Portal**: `http://localhost:3001/client-dashboard.html` - Main client interface
- **Admin Portal**: `http://localhost:3001/admin-dashboard.html` - Administrative interface

### Role-Based Navigation

The application automatically redirects users based on their role:

- **Clients**: Redirected to client dashboard after login
- **Admin/Super Admin**: Redirected to admin dashboard after login
- **Unauthenticated**: Redirected to login page

### Technical Features

- **Responsive Design** - Mobile-friendly Bootstrap 5 interface
- **Real-time Updates** - Dynamic content loading and updates
- **Form Validation** - Client-side and server-side validation
- **Error Handling** - Comprehensive error messages and recovery
- **Security** - JWT token-based authentication with automatic refresh

### Development Server

To run the frontend development server:

```bash
cd frontend
python -m http.server 3001
```

Access the application at `http://localhost:3001`

## 🧪 Testing

### Sample Users

The setup script can create sample users for testing:

- **john_client** / john@example.com / ClientPass123!
- **jane_librarian** / jane@example.com / AdminPass123!
- **bob_reader** / bob@example.com / ReaderPass123!

### Testing MFA

1. Login with a user account
2. Setup MFA in profile settings
3. Use Google Authenticator or similar app
4. Test login with MFA verification

### Testing Library System

1. Login as admin
2. Add books to the library
3. Login as regular user
4. Borrow and return books
5. Check notifications for due dates

## 🔒 Security Features

- **Password Security**: Bcrypt hashing with salt
- **JWT Tokens**: Secure token-based authentication
- **MFA Protection**: TOTP-based two-factor authentication
- **Rate Limiting**: Protection against brute force attacks
- **Role-Based Access**: Granular permission control
- **Input Validation**: Comprehensive request validation
- **SQL Injection Protection**: ORM-based queries

## 📧 Email Templates

The system includes pre-built email templates for:

- Welcome emails
- Email verification
- Password reset
- Book due reminders
- Overdue notices
- Admin notifications

Templates are customizable and support variables.

## 🔄 Database Schema

The system uses multiple interconnected tables:

- **users** - User accounts and authentication
- **mfa_secrets** - MFA secrets and backup codes
- **email_verifications** - Email verification tokens
- **books** - Book catalog and metadata
- **book_categories** - Book categorization
- **book_loans** - Borrowing and return tracking
- **notifications** - User notifications and emails

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Use secure, production values
2. **Database**: Use managed PostgreSQL service
3. **Email**: Configure proper SMTP service
4. **Redis**: Set up Redis for background tasks
5. **HTTPS**: Enable SSL/TLS certificates
6. **Rate Limiting**: Configure appropriate limits
7. **Monitoring**: Set up logging and monitoring

### Docker Production

```bash
# Build for production
docker-compose -f docker-compose.prod.yml up -d
```

## 📝 API Examples

### User Registration

```bash
curl -X POST "http://localhost:8000/api/v1/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### Setup MFA

```bash
curl -X POST "http://localhost:8000/api/v1/auth/mfa/setup" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"verification_code": "123456"}'
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection**: Check PostgreSQL is running and credentials are correct
2. **Email Not Sending**: Verify SMTP configuration and credentials
3. **MFA Setup Failed**: Ensure QR code is scanned correctly
4. **Permission Denied**: Check user roles and authentication

### Logs

```bash
# Docker logs
docker-compose logs user-service

# Application logs
tail -f logs/app.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For support and questions:

- Create an issue on GitHub
- Check the documentation in `/docs`
- Review the API documentation at `/docs`

---

**Built with ❤️ using FastAPI and modern Python technologies**
