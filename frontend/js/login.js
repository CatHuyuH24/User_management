// Login page functionality

document.addEventListener('DOMContentLoaded', function () {
  console.log('DOM loaded, initializing login page');

  // Check if all required elements exist
  const form = document.getElementById('loginForm');
  const username = document.getElementById('username');
  const password = document.getElementById('password');

  console.log('Form element:', form);
  console.log('Username element:', username);
  console.log('Password element:', password);

  if (!form) {
    console.error('Critical: Login form not found!');
    return;
  }

  if (!username) {
    console.error('Critical: Username field not found!');
    return;
  }

  if (!password) {
    console.error('Critical: Password field not found!');
    return;
  }

  // Redirect if already authenticated
  redirectIfAuthenticated();

  // Initialize form handlers
  initializeLoginForm();
  initializePasswordToggle();
});

function initializeLoginForm() {
  const form = document.getElementById('loginForm');

  if (!form) {
    console.error('Login form not found during initialization');
    return;
  }

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    console.log('Form submitted');

    if (validateForm()) {
      await submitLogin();
    }
  });

  // Real-time validation
  const inputs = form.querySelectorAll('input');
  console.log(`Found ${inputs.length} input fields`);
  inputs.forEach((input) => {
    input.addEventListener('blur', () => validateField(input.id));
    input.addEventListener('input', () => clearFieldError(input.id));
  });
}

function validateForm() {
  const form = document.getElementById('loginForm');
  if (!form) {
    console.error('Login form not found');
    return false;
  }

  clearAllErrors(form);

  let isValid = true;

  // Validate username
  const usernameElement = document.getElementById('username');
  if (!usernameElement) {
    console.error('Username field not found');
    return false;
  }
  const username = usernameElement.value.trim();
  if (!username) {
    setFieldError('username', 'Please enter your username');
    isValid = false;
  }

  // Validate password
  const passwordElement = document.getElementById('password');
  if (!passwordElement) {
    console.error('Password field not found');
    return false;
  }
  const password = passwordElement.value;
  if (!password) {
    setFieldError('password', 'Please enter your password');
    isValid = false;
  }

  return isValid;
}

function validateField(fieldId) {
  const field = document.getElementById(fieldId);
  if (!field) {
    console.warn(`Field with ID '${fieldId}' not found`);
    return;
  }

  const value = field.value.trim();

  switch (fieldId) {
    case 'username':
      if (!value) {
        setFieldError(fieldId, 'Please enter your username');
      } else {
        clearFieldError(fieldId);
      }
      break;

    case 'password':
      if (!value) {
        setFieldError(fieldId, 'Please enter your password');
      } else {
        clearFieldError(fieldId);
      }
      break;
  }
}

async function submitLogin() {
  showLoading(true);

  try {
    const usernameElement = document.getElementById('username');
    const passwordElement = document.getElementById('password');

    if (!usernameElement || !passwordElement) {
      throw new Error('Form fields not found');
    }

    const formData = {
      username: usernameElement.value.trim(),
      password: passwordElement.value,
    };

    console.log('Submitting login with username:', formData.username);

    const response = await apiCall('/login', {
      method: 'POST',
      body: JSON.stringify(formData),
    });

    // Check if MFA is required
    if (response.mfa_required) {
      showLoading(false);
      showAlert('MFA verification required', 'info');

      // Show MFA verification modal with the MFA token
      showMfaVerificationModal(response.mfa_token);
      return;
    }

    // Save the authentication token (for non-MFA login or when MFA is completed)
    saveAuthToken(response.access_token);

    // Get user profile to determine redirect destination
    const profile = await apiCall('/me', {
      method: 'GET',
    });

    showAlert('Login successful! Redirecting...', 'success');

    // Redirect based on user role
    setTimeout(() => {
      if (profile.role === 'admin' || profile.role === 'super_admin') {
        window.location.href = 'admin-dashboard.html';
      } else {
        window.location.href = 'client-dashboard.html';
      }
    }, 1000);
  } catch (error) {
    let errorMessage =
      'Login failed. Please check your credentials and try again.';

    if (error.message.includes('Incorrect username/email or password')) {
      errorMessage = 'Incorrect username or password. Please try again.';
    } else if (error.message.includes('Inactive user')) {
      errorMessage =
        'Your account has been deactivated. Please contact support.';
    } else if (error.message) {
      errorMessage = error.message;
    }

    showAlert(errorMessage, 'danger');
  } finally {
    showLoading(false);
  }
}

function initializePasswordToggle() {
  const toggleButton = document.getElementById('togglePassword');
  const passwordField = document.getElementById('password');

  if (!toggleButton || !passwordField) {
    console.warn('Password toggle elements not found');
    return;
  }

  toggleButton.addEventListener('click', function () {
    const type =
      passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordField.setAttribute('type', type);

    const icon = this.querySelector('i');
    if (icon) {
      icon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
    }
  });
}
