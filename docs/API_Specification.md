# API Specification

This document defines the API endpoints for the user management service.

## Base URL

`/api/v1`

## Authentication

Authentication will be handled using JSON Web Tokens (JWT). The token must be included in the `Authorization` header of protected requests as a Bearer token.

`Authorization: Bearer <your_jwt_token>`

---

## 1. Auth Endpoints

### `POST /auth/signup`

- **Description:** Registers a new user.
- **Request Body:**
  ```json
  {
    "username": "newuser",
    "email": "user@example.com",
    "password": "a_strong_password"
  }
  ```
- **Responses:**
  - `201 Created`: User successfully created.
    ```json
    {
      "message": "User created successfully"
    }
    ```
  - `400 Bad Request`: Invalid input data (e.g., email already exists, weak password).

### `POST /auth/login`

- **Description:** Authenticates a user and returns a JWT.
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "a_strong_password"
  }
  ```
- **Responses:**
  - `200 OK`: Login successful.
    ```json
    {
      "access_token": "your_jwt_token",
      "token_type": "bearer"
    }
    ```
  - `401 Unauthorized`: Invalid credentials.

---

## 2. User Profile Endpoints

These endpoints require authentication.

### `GET /users/me`

- **Description:** Retrieves the profile of the currently authenticated user.
- **Responses:**
  - `200 OK`:
    ```json
    {
      "username": "newuser",
      "email": "user@example.com",
      "year_of_birth": 1990,
      "description": "A short bio.",
      "avatar_url": "/path/to/avatar.jpg"
    }
    ```
  - `401 Unauthorized`: Token is missing or invalid.

### `PUT /users/me`

- **Description:** Updates the profile of the currently authenticated user.
- **Request Body:**
  ```json
  {
    "year_of_birth": 1991,
    "description": "An updated bio."
  }
  ```
- **Responses:**
  - `200 OK`: Profile updated successfully.
    ```json
    {
      "message": "Profile updated successfully"
    }
    ```
  - `400 Bad Request`: Invalid input data.
  - `401 Unauthorized`: Token is missing or invalid.

### `POST /users/me/avatar`

- **Description:** Uploads or updates the avatar for the currently authenticated user.
- **Request Body:** `multipart/form-data` with the image file.
- **Responses:**
  - `200 OK`: Avatar uploaded successfully.
    ```json
    {
      "avatar_url": "/new/path/to/avatar.jpg"
    }
    ```
  - `400 Bad Request`: Invalid file type or size.
  - `401 Unauthorized`: Token is missing or invalid.
