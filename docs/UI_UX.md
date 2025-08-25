# UI/UX Design

This document outlines the user interface (UI) and user experience (UX) design for the user management web application.

## 1. Overall Design Philosophy

- **Clean and Modern:** The UI features an uncluttered, modern aesthetic using Bootstrap 5 framework.
- **Intuitive:** Navigation and user flows are straightforward and easy to understand.
- **Responsive:** The application is fully responsive and works seamlessly on desktops, tablets, and mobile devices.
- **Professional Branding:** Custom favicon and consistent visual identity across all pages.
- **User-Centered:** Focus on ease of use and clear user feedback.

## 2. Technology Stack

- **Frontend Framework:** Vanilla JavaScript with Bootstrap 5
- **Styling:** Custom CSS with Bootstrap 5 components
- **Icons:** Font Awesome 6 for consistent iconography
- **Branding:** Custom favicon (user-management-icon.jpg) on all pages

## 3. Page Designs

### 3.1. Landing Page (index.html)

- **Layout:** Hero section with modern gradient background
- **Elements:**
  - Application Logo and Favicon
  - Welcome message and service description
  - Service status indicators
  - Navigation buttons to Sign Up and Login
  - Professional gradient design with hover effects

### 3.2. Sign-Up Page (signup.html)

- **Layout:** Centered form with modern card design
- **Elements:**
  - Application Logo and Favicon
  - "Create Account" Heading
  - Username Input Field with validation
  - Email Input Field with format validation
  - Password Input Field with strength indicator
  - First Name and Last Name (optional)
  - Real-time validation feedback
  - "Create Account" Button with loading states
  - Link to Login Page

### 3.3. Login Page (login.html)

- **Layout:** Similar to sign-up page, centered form with card design
- **Elements:**
  - Application Logo and Favicon
  - "Sign In" Heading
  - Email Input Field
  - Password Input Field
  - "Sign In" Button with loading states
  - Link to Sign-Up Page
  - Error handling with user-friendly messages

### 3.4. Profile Page (profile.html)

- **Layout:** Single-column responsive layout with header and content sections
- **Elements:**
  - **Header Section:**
    - Application Logo and Favicon
    - User avatar (with upload functionality)
    - Username and email display
    - Navigation and logout options
  - **Profile Section:**
    - View/Edit mode toggle
    - User information display (readonly/editable)
    - Avatar upload with drag-and-drop support
    - Form validation and error handling
    - Save/Cancel buttons with confirmation dialogs
    - Account deletion option with safety confirmations

### 2.4. Edit Profile Modal/Page

- **Trigger:** Clicking the "Edit Profile" button on the main page.
- **Layout:** A form, which can be a modal overlay or a separate page.
- **Elements:**
  - "Edit Profile" Heading
  - Avatar Upload Section
    - Current Avatar Preview
    - "Upload New Avatar" Button
  - Year of Birth Input Field
  - Description Text Area
  - "Save Changes" Button
  - "Cancel" Button

## 3. User Flow

1.  **New User:**

    - Lands on the Login page.
    - Clicks "Sign up".
    - Fills out the sign-up form and submits.
    - Is redirected to the Login page.

2.  **Existing User:**

    - Lands on the Login page.
    - Fills out the login form and submits.
    - Is redirected to their User Main Page.

3.  **Profile Update:**

    - On the User Main Page, clicks "Edit Profile".
    - The edit form appears.
    - User modifies their information and/or uploads a new avatar.
    - Clicks "Save Changes".
    - The User Main Page updates to show the new information.

4.  **Logout:**
    - Clicks the "Logout" button in the header.
    - Is redirected to the Login page.
