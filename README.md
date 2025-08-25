# User Management Microservice Project

This project is a user management web application built with a microservices architecture using FastAPI.

## Features

- User registration and authentication
- User profile management (name, year of birth, description, avatar)
- RESTful API with FastAPI
- PostgreSQL database integration
- Docker containerization
- Automatic API documentation

## Project Structure

```
user_management/
├── docs/                    # Project documentation
│   ├── API_Specification.md
│   ├── System_Architecture.md
│   ├── UI_UX.md
│   └── User_Stories.md
├── services/               # Microservices
│   └── user-service/      # User management service
│       ├── app/           # FastAPI application
│       ├── tests/         # Test files
│       ├── Dockerfile     # Container configuration
│       └── requirements.txt
├── docker-compose.yml     # Service orchestration
├── init.bat              # Windows initialization script
└── init.sh               # Unix initialization script
```

## Quick Start

### Option 1: Use Initialization Scripts

**Windows:**

```cmd
init.bat
```

**Unix/Linux/macOS:**

```bash
chmod +x init.sh
./init.sh
```

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
