# User Management Project Charter

## 1. Overview & Objectives

This project is a user management web application built with a microservices architecture using FastAPI.

- **Primary Tech Stack:** Python/FastAPI (Backend), React/TypeScript (Frontend), PostgreSQL (Database), Docker/Kubernetes (Infrastructure).

- **Project Structure**
  - `docs/`: Contains all project documentation.
  - `services/`: Contains the individual microservices.
  - `user-service/`: The service for handling user authentication and profile management.
  - `docker-compose.yml`: Orchestrates the services for local development.

## 2. Common Commands

1.  **Prerequisites:**

    - Docker
    - Docker Compose

2.  **Run the application:**
    ```bash
    docker-compose up --build
    ```

The user service will be available at `http://localhost:8000`.

## 3. Programming Standards

- **REQUIRED:** All APIs must strictly follow the structure defined in [API Specification](docs/API_Specification.md).
- **REQUIRED:** All endpoints must implement centralized exception handling and return errors according to the defined structure.
- Always use FastAPI's dependency injection.
- Avoid placing complex business logic directly in route files. Extract logic into `service` or `use_case` modules.
- All functions and classes must include Google-style docstrings.
- Adhere to best practices and industry standards for microservices implementation.
- Ensure centralized log storage for both backend and frontend functionalities.
- The UI/UX must be user-centric and user-friendly.

## 4. Immutable Architectural Decisions

- Implement centralized log management.
- Use microservices for the backend.
- Ensure frontend fallback mechanisms, resiliency, and simplicity to enhance user experience.

## 5. Key Reference Documents

- [API Specification](docs/API_Specification.md)
- [Software Requirements](docs/SRS.md)
- [System Architecture](docs/System_Architecture.md)
- [UI/UX Design](docs/UI_UX.md)
- [User Stories](docs/User_Stories.md)
