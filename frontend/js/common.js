// Common utility functions and API configuration

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Utility functions
function showAlert(message, type = 'info') {
  const alertContainer = document.getElementById('alertContainer');
  if (!alertContainer) return;

  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

  alertContainer.appendChild(alertDiv);

  // Auto-remove after 5 seconds
  setTimeout(() => {
    if (alertDiv.parentNode) {
      alertDiv.parentNode.removeChild(alertDiv);
    }
  }, 5000);
}

function showLoading(show = true) {
  const loadingOverlay = document.getElementById('loadingOverlay');
  if (loadingOverlay) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
  }
}

function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function validatePassword(password) {
  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

  return {
    isValid:
      password.length >= minLength &&
      hasUpperCase &&
      hasLowerCase &&
      hasNumbers &&
      hasSpecialChar,
    errors: [
      ...(password.length < minLength
        ? ['Password must be at least 8 characters long']
        : []),
      ...(!hasUpperCase
        ? ['Password must contain at least one uppercase letter']
        : []),
      ...(!hasLowerCase
        ? ['Password must contain at least one lowercase letter']
        : []),
      ...(!hasNumbers ? ['Password must contain at least one number'] : []),
      ...(!hasSpecialChar
        ? ['Password must contain at least one special character']
        : []),
    ],
  };
}

function validateUsername(username) {
  const usernameRegex = /^[a-zA-Z0-9_]+$/;
  return {
    isValid:
      username.length >= 3 &&
      username.length <= 50 &&
      usernameRegex.test(username),
    errors: [
      ...(username.length < 3
        ? ['Username must be at least 3 characters long']
        : []),
      ...(username.length > 50
        ? ['Username must be no more than 50 characters long']
        : []),
      ...(!usernameRegex.test(username)
        ? ['Username can only contain letters, numbers, and underscores']
        : []),
    ],
  };
}

// API call functions
async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  // Add authorization header if token exists
  const token = localStorage.getItem('authToken');
  if (token) {
    defaultOptions.headers['Authorization'] = `Bearer ${token}`;
  }

  const finalOptions = { ...defaultOptions, ...options };

  try {
    const response = await fetch(url, finalOptions);
    const data = await response.json();

    if (!response.ok) {
      // Handle authentication errors (401) and forbidden errors (403)
      if (response.status === 401 || response.status === 403) {
        console.warn('Authentication failed - redirecting to login');
        handleAuthenticationFailure();
        throw new Error('Authentication required');
      }
      throw new Error(data.detail || 'An error occurred');
    }

    return data;
  } catch (error) {
    console.error('API call failed:', error);
    
    // If it's a network error or the server is unreachable, also check auth
    if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
      console.warn('Network error - checking authentication status');
      // Don't auto-logout on network errors, but log the issue
    }
    
    throw error;
  }
}

// Authentication functions
function saveAuthToken(token) {
  localStorage.setItem('authToken', token);
}

function getAuthToken() {
  return localStorage.getItem('authToken');
}

function removeAuthToken() {
  localStorage.removeItem('authToken');
}

function isAuthenticated() {
  return !!getAuthToken();
}

// Handle authentication failures and auto-logout
function handleAuthenticationFailure() {
  console.log('Handling authentication failure - logging out user');
  
  // Clear the auth token
  removeAuthToken();
  
  // Show a brief message
  showAlert('Your session has expired. Please log in again.', 'warning');
  
  // Redirect to login page after a short delay
  setTimeout(() => {
    window.location.href = 'login.html';
  }, 1500);
}

// Check if user data is in "Loading" state and handle appropriately
async function validateUserSession() {
  if (!isAuthenticated()) {
    return false;
  }
  
  try {
    // Try to fetch user profile to validate session
    const response = await fetch(`${API_BASE_URL}/me`, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        handleAuthenticationFailure();
        return false;
      }
    }
    
    const userData = await response.json();
    
    // Check if user data indicates invalid state
    if (!userData || !userData.username || userData.username === 'Loading' || !userData.email) {
      console.warn('Invalid user data detected - logging out');
      handleAuthenticationFailure();
      return false;
    }
    
    return true;
  } catch (error) {
    console.error('Session validation failed:', error);
    handleAuthenticationFailure();
    return false;
  }
}

// Form validation styling
function setFieldError(fieldId, error) {
  const field = document.getElementById(fieldId);
  const errorElement = document.getElementById(`${fieldId}Error`);

  if (field) {
    field.classList.add('is-invalid');
  }

  if (errorElement) {
    errorElement.textContent = error;
    errorElement.style.display = 'block';
  }
}

function clearFieldError(fieldId) {
  const field = document.getElementById(fieldId);
  const errorElement = document.getElementById(`${fieldId}Error`);

  if (field) {
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
  }

  if (errorElement) {
    errorElement.style.display = 'none';
  }
}

function clearAllErrors(form) {
  const invalidFields = form.querySelectorAll('.is-invalid');
  const errorMessages = form.querySelectorAll('.invalid-feedback');

  invalidFields.forEach((field) => {
    field.classList.remove('is-invalid');
  });

  errorMessages.forEach((error) => {
    error.style.display = 'none';
  });
}

// Redirect if already authenticated
function redirectIfAuthenticated() {
  if (isAuthenticated()) {
    window.location.href = 'profile.html';
  }
}

// Redirect if not authenticated
function redirectIfNotAuthenticated() {
  if (!isAuthenticated()) {
    window.location.href = 'login.html';
  }
}
