# User Stories

This document outlines the user stories for the user management web application.

## Epic: User Authentication

### As a new user, I want to be able to sign up for an account so that I can access the application.

- **Acceptance Criteria:**
  - I can navigate to a sign-up page.
  - I need to provide a unique username, a valid email address, and a strong password.
  - The system validates my input and provides clear error messages for invalid data.
  - Upon successful registration, I am redirected to the login page.

### As a registered user, I want to be able to log in to my account so that I can access my user profile.

- **Acceptance Criteria:**
  - I can navigate to a login page.
  - I can log in using my email/username and password.
  - The system validates my credentials.
  - If the credentials are correct, I am redirected to my user main page.
  - If the credentials are incorrect, I see a clear error message.

### As a logged-in user, I want to be able to log out of my account to secure my session.

- **Acceptance Criteria:**
  - I can find and click a "Logout" button.
  - Upon clicking, my session is terminated, and I am redirected to the login or home page.

## Epic: User Profile Management

### As a logged-in user, I want to view my user profile page to see my information.

- **Acceptance Criteria:**
  - After logging in, I am taken to my user profile page.
  - The page displays my name, year of birth, a short description, and my avatar.

### As a logged-in user, I want to be able to edit my profile information so that I can keep it up to date.

- **Acceptance Criteria:**
  - I can find an "Edit Profile" button on my profile page.
  - Clicking it allows me to update my name, year of birth, and description.
  - I can save the changes, and the updated information is reflected on my profile page.

### As a logged-in user, I want to be able to upload or change my avatar so I can personalize my profile.

- **Acceptance Criteria:**
  - In the "Edit Profile" section, I can upload an image file for my avatar.
  - The system validates the file type and size.
  - Once uploaded, the new avatar is displayed on my profile page.
