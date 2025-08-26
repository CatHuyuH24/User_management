# User Stories

This document outlines the user stories for the User Management and Library Management web application, covering both Client and Admin portals.

## Epic: User Authentication & MFA

### As a new user, I want to be able to sign up for an account so that I can access the application.

- **Acceptance Criteria:**
  - I can navigate to a sign-up page.
  - I need to provide a unique username, a valid email address, and a strong password.
  - The system validates my input and provides clear error messages for invalid data.
  - I receive an email verification link to activate my account.
  - Upon successful registration and email verification, I am prompted to set up MFA.

### As a registered user, I want to be able to log in to my account with multi-factor authentication so that my account is secure.

- **Acceptance Criteria:**
  - I can navigate to a login page.
  - I enter my email/username and password for primary authentication.
  - If MFA is enabled, I am prompted to enter a 6-digit code from my authenticator app.
  - If I lose my authenticator, I can use backup codes to regain access.
  - Upon successful authentication, I am redirected to the appropriate portal (client/admin).

### As a logged-in user, I want to manage my MFA settings so that I can maintain account security.

- **Acceptance Criteria:**
  - I can view my current MFA status in my profile settings.
  - I can enable MFA by scanning a QR code with an authenticator app.
  - I can generate and download backup codes for emergency access.
  - I can disable MFA by providing my current password and MFA code.

## Epic: User Profile Management

### As a logged-in user, I want to view my user profile page to see my information.

- **Acceptance Criteria:**
  - After logging in, I am taken to my user profile page.
  - The page displays my name, year of birth, a short description, and my avatar.
  - I can see my MFA status and borrowed books count.

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

## Epic: Library Management (Client Portal)

### As a client user, I want to browse available books so that I can find something to read.

- **Acceptance Criteria:**
  - I can view a catalog of available books with covers, titles, and authors.
  - I can search books by title, author, or category.
  - I can filter books by availability, category, and publication year.
  - I can view detailed information about each book including description and availability.

### As a client user, I want to borrow books so that I can read them.

- **Acceptance Criteria:**
  - I can click a "Borrow" button on available books.
  - The system checks if I'm within my borrowing limit (5 books max).
  - I receive confirmation of the loan with due date information.
  - The book's availability count is updated in real-time.

### As a client user, I want to manage my borrowed books so that I can track due dates and returns.

- **Acceptance Criteria:**
  - I can view all my currently borrowed books with due dates.
  - I can see my borrowing history.
  - I can renew books if eligible (up to 2 renewals).
  - I can return books digitally and receive confirmation.

### As a client user, I want to receive notifications about my borrowed books so that I don't incur penalties.

- **Acceptance Criteria:**
  - I receive web notifications 2 days before books are due.
  - I receive email reminders for upcoming due dates.
  - I get notified when books become overdue.
  - I can mark notifications as read and manage my notification preferences.

## Epic: Admin Portal - User Management

### As an admin, I want to view all users in the system so that I can manage them effectively.

- **Acceptance Criteria:**
  - I can access an admin portal with enhanced security (mandatory MFA).
  - I can view a paginated list of all registered users.
  - I can search and filter users by various criteria (name, email, status).
  - I can view detailed user profiles including activity history.

### As an admin, I want to delete user accounts so that I can manage inactive or problematic users.

- **Acceptance Criteria:**
  - I can select users and delete their accounts.
  - The system requires confirmation before deletion.
  - All user data is properly removed with audit trail.
  - Any borrowed books are automatically returned.
  - Deletion actions are logged for compliance.

### As an admin, I want to reset user MFA settings so that I can help users who lost access.

- **Acceptance Criteria:**
  - I can disable MFA for users who lost their authenticator.
  - I can force users to set up MFA again on next login.
  - All MFA-related actions are logged with admin details.
  - Users receive notification when their MFA is reset.

## Epic: Admin Portal - Library Management

### As an admin, I want to manage the book catalog so that I can maintain an up-to-date library.

- **Acceptance Criteria:**
  - I can add new books with all details (title, author, ISBN, copies).
  - I can edit existing book information and availability.
  - I can remove books from the catalog.
  - I can bulk import books from CSV files.
  - I can manage book categories and authors.

### As an admin, I want to monitor all book loans so that I can ensure proper library operations.

- **Acceptance Criteria:**
  - I can view all active loans with user and book details.
  - I can see overdue books and send targeted reminders.
  - I can force return books if necessary.
  - I can generate reports on lending statistics and popular books.

### As an admin, I want to manage system settings so that I can configure library operations.

- **Acceptance Criteria:**
  - I can set loan duration and renewal policies.
  - I can configure notification settings and templates.
  - I can manage user borrowing limits.
  - I can set up automated overdue handling.

## Epic: Notification System

### As a user, I want to receive timely notifications so that I can manage my borrowed books effectively.

- **Acceptance Criteria:**
  - I receive web notifications for due dates, overdue books, and system updates.
  - I receive email notifications for important events.
  - I can customize my notification preferences.
  - Notifications are marked as read when I interact with them.

### As an admin, I want to send system-wide announcements so that I can communicate with all users.

- **Acceptance Criteria:**
  - I can compose and send announcements to all users or specific groups.
  - I can schedule announcements for future delivery.
  - I can track announcement delivery and read status.
  - Users receive announcements through their preferred channels.
