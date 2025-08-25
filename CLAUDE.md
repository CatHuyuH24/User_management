# User Management Microservice Project

This project is a user management web application built with a microservices architecture using FastAPI.

## Project Structure

- `docs/`: Contains all project documentation.
- `services/`: Contains the individual microservices.
  - `user-service/`: The service for handling user authentication and profile management.
- `docker-compose.yml`: Orchestrates the services for local development.

## Getting Started

1.  **Prerequisites:**

    - Docker
    - Docker Compose

2.  **Run the application:**
    ```bash
    docker-compose up --build
    ```

The user service will be available at `http://localhost:8000`.
