# User Management Project Charter

## 1. Overview & Objectives

This project is a user management web application built with a microservices architecture using FastAPI and modern frontend technologies.

- **Primary Tech Stack:** Python/FastAPI (Backend), Vanilla JavaScript/Bootstrap 5 (Frontend), PostgreSQL (Database), Docker (Infrastructure).

- **Project Structure**
  - `docs/`: Contains all project documentation.
  - `services/`: Contains the individual microservices.
  - `services/user-service/`: The service for handling user authentication and profile management.
  - `frontend/`: Contains the web application frontend.
  - `docker-compose.yml`: Orchestrates the services for local development.

## 2. Common Commands

1. **Prerequisites:**

   - Docker and Docker Compose
   - Python 3.9+ (for frontend server)

2. **Quick Start (Automated):**

   ```bash
   # Unix/Linux/macOS
   chmod +x init.sh
   ./init.sh

   # Windows
   init.bat
   ```

3. **Manual Setup:**

   ```bash
   # Start backend services
   docker-compose up --build -d

   # Start frontend server (in new terminal)
   cd frontend
   python frontend_server.py
   ```

4. **Access Points:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 3. Programming Standards

- **REQUIRED:** All APIs must strictly follow the structure defined in [API Specification](docs/API_Specification.md).
- **REQUIRED:** All endpoints must implement centralized exception handling and return errors according to the defined structure.
- Always use FastAPI's dependency injection for backend services.
- Avoid placing complex business logic directly in route files. Extract logic into `service` or `use_case` modules.
- All functions and classes must include Google-style docstrings.
- Adhere to best practices and industry standards for microservices implementation.
- Ensure centralized log storage for both backend and frontend functionalities.
- The UI/UX must be user-centric and user-friendly with responsive design.
- All frontend pages must include proper favicon implementation.
- Security best practices for file uploads (avatar images).

## 4. Immutable Architectural Decisions

- Implement centralized log management.
- Use microservices for the backend.
- Ensure frontend fallback mechanisms, resiliency, and simplicity to enhance user experience.
- JWT-based authentication with secure token management.
- File upload capabilities with proper security validation.
- Bootstrap 5 for responsive frontend design.

## 5. Key Reference Documents

- [API Specification](docs/API_Specification.md)
- [Database Schema](docs/Database_Schema.md)
- [System Architecture](docs/System_Architecture.md)
- [UI/UX Design](docs/UI_UX.md)
- [User Stories](docs/User_Stories.md)
- [UI/UX Design](docs/UI_UX.md)
- [User Stories](docs/User_Stories.md)
