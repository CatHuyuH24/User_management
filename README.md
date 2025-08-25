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
├── backend/
│   ├── services/
│   │   └── user-service/
│   │       ├── app/
│   │       │   ├── __init__.py
│   │       │   ├── main.py              # FastAPI application
│   │       │   ├── database.py          # Database connection
│   │       │   ├── models.py            # SQLAlchemy models
│   │       │   ├── schemas.py           # Pydantic schemas
│   │       │   ├── crud.py              # Database operations
│   │       │   ├── auth.py              # Authentication utilities
│   │       │   └── utils.py             # Helper functions
│   │       ├── requirements.txt         # Python dependencies
│   │       └── Dockerfile               # Container configuration
│   ├── docker-compose.yml              # Multi-service orchestration
│   └── init.sql                         # Database initialization
├── frontend/
│   ├── index.html                       # Landing page
│   ├── signup.html                      # User registration
│   ├── login.html                       # User authentication
│   ├── profile.html                     # User profile management
│   ├── server.html                      # Server information
│   ├── js/
│   │   ├── common.js                    # Shared utilities
│   │   ├── signup.js                    # Registration logic
│   │   ├── login.js                     # Authentication logic
│   │   └── profile.js                   # Profile management
│   └── frontend_server.py              # Development server
├── Database_Schema.md                   # Database design documentation
└── README.md                           # This file
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for frontend server)

### 1. Start Backend Services

Navigate to the backend directory and start the services:

```powershell
cd backend
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

### API Endpoints

- `GET /` - Welcome message
- `GET /docs` - API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

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
