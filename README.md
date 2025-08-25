# User Management Web Application

A complete full-stack web application for user management with sign-up, login, and profile management features.

## 🏗️ Architecture

### Backend

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL 13
- **Authentication**: JWT tokens with bcrypt password hashing
- **Containerization**: Docker & Docker Compose
- **API Documentation**: Automatic OpenAPI/Swagger docs

### Frontend

- **Framework**: Vanilla JavaScript with Bootstrap 5
- **Styling**: Responsive design with custom CSS
- **Icons**: Font Awesome 6
- **Server**: Python HTTP server with CORS support

## 📁 Project Structure

```
user_management/
├── services/
│   └── user-service/
│       ├── app/
│       │   ├── api/v1/                  # API endpoints
│       │   │   ├── auth.py              # Authentication endpoints
│       │   │   ├── users.py             # User management endpoints
│       │   │   └── endpoints.py         # Router configuration
│       │   ├── core/                    # Core configuration
│       │   ├── db/                      # Database configuration
│       │   ├── models/                  # SQLAlchemy models
│       │   │   └── user.py              # User model
│       │   ├── schemas/                 # Pydantic schemas
│       │   │   └── user.py              # User schemas
│       │   ├── services/                # Business logic
│       │   └── main.py                  # FastAPI application
│       ├── requirements.txt             # Python dependencies
│       └── Dockerfile                   # Container configuration
├── frontend/
│   ├── index.html                       # Landing page
│   ├── signup.html                      # User registration
│   ├── login.html                       # User authentication
│   ├── profile.html                     # User profile management
│   ├── server.html                      # Server information
│   ├── images/
│   │   └── user-management-icon.jpg     # Favicon
│   ├── js/
│   │   ├── common.js                    # Shared utilities
│   │   ├── signup.js                    # Registration logic
│   │   ├── login.js                     # Authentication logic
│   │   └── profile.js                   # Profile management
│   └── frontend_server.py              # Development server
├── docker-compose.yml                  # Multi-service orchestration
├── docs/                               # Project documentation
├── init.sh                             # Initialization script (Unix/Linux)
├── init.bat                            # Initialization script (Windows)
└── README.md                           # This file
```

│ │ ├── login.js # Authentication logic
│ │ └── profile.js # Profile management
│ └── frontend_server.py # Development server
├── Database_Schema.md # Database design documentation
└── README.md # This file

````

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for frontend server)

### Option 1: Automated Setup (Recommended)

Use the initialization script for easy setup:

**Windows:**
```cmd
init.bat
````

**Unix/Linux/macOS:**

```bash
chmod +x init.sh
./init.sh
```

### Option 2: Manual Setup

### 1. Start Backend Services

Navigate to the root directory and start the services:

```powershell
docker-compose up --build
```

This will start:

- PostgreSQL database on port 5432
- FastAPI application on port 8000

### 2. Start Frontend Server

In a new terminal, navigate to the frontend directory:

```powershell
cd frontend
python frontend_server.py
```

The frontend will be available at `http://localhost:3000`

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432 (user: admin, password: password123, db: user_management)

### Option 2: Manual Setup

1. **Prerequisites:**

   - Docker
   - Docker Compose

2. **Start the application:**

   ```bash
   docker-compose up --build -d
   ```

3. **Access the services:**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Interactive API: http://localhost:8000/redoc

## Development

### Local Development Setup

1. **Clone and navigate to project:**

   ```bash
   cd user_management
   ```

2. **Start services:**

   ```bash
   docker-compose up --build
   ```

3. **Check logs:**

   ```bash
   docker-compose logs -f user-service
   ```

4. **Stop services:**
   ```bash
   docker-compose down
   ```

## 📚 API Endpoints

### Authentication

- `POST /api/v1/auth/signup` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/verify-token` - Token verification

### User Management

- `GET /api/v1/users/me` - Get user profile (authenticated)
- `PUT /api/v1/users/me` - Update user profile (authenticated)
- `POST /api/v1/users/me/avatar` - Upload user avatar (authenticated)
- `DELETE /api/v1/users/me` - Delete user account (authenticated)

### System

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /docs` - API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## 🔐 Security Features

- **Password Hashing**: bcrypt with salt rounds
- **JWT Authentication**: Secure token-based authentication
- **Token Expiration**: 30-minute token lifetime
- **Input Validation**: Comprehensive request validation
- **CORS Support**: Configurable cross-origin requests
- **File Upload Security**: Avatar upload with type and size validation

## 💻 Frontend Features

### Landing Page (`index.html`)

- Service status checking
- Navigation to all application features
- Responsive design with modern UI
- Custom favicon

### Sign-up Page (`signup.html`)

- Real-time form validation
- Password strength indicator
- Duplicate email checking
- Automatic redirect after successful registration

### Login Page (`login.html`)

- User authentication
- JWT token management
- Remember login state
- Redirect to profile after login

### Profile Page (`profile.html`)

- View/edit user information
- **Avatar upload and management**
- Account management
- Secure logout functionality
- Delete account option

### Database

The project uses PostgreSQL running in a Docker container. Connection details:

- Host: localhost (from host machine) / db (from containers)
- Port: 5432
- Database: db
- Username: user
- Password: password

## Documentation

Detailed documentation is available in the `docs/` directory:

- **User Stories**: Requirements and user scenarios
- **System Architecture**: Technical architecture overview
- **API Specification**: Detailed API endpoint documentation
- **UI/UX Design**: Frontend design specifications

## Status

✅ **Currently Initialized and Running**

The project has been successfully initialized with:

- ✅ FastAPI service running on port 8000
- ✅ PostgreSQL database running
- ✅ Docker containers operational
- ✅ API documentation accessible

## Next Steps

1. Implement user authentication endpoints
2. Add user profile management features
3. Set up database models and migrations
4. Add comprehensive testing
5. Implement frontend application
