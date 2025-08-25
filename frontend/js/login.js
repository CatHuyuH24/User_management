// Login page functionality

document.addEventListener('DOMContentLoaded', function () {
  // Redirect if already authenticated
  redirectIfAuthenticated();

  // Initialize form handlers
  initializeLoginForm();
  initializePasswordToggle();
});

function initializeLoginForm() {
  const form = document.getElementById('loginForm');

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    if (validateForm()) {
      await submitLogin();
    }
  });

  // Real-time validation
  const inputs = form.querySelectorAll('input');
  inputs.forEach((input) => {
    input.addEventListener('blur', () => validateField(input.name));
    input.addEventListener('input', () => clearFieldError(input.id));
  });
}

function validateForm() {
  const form = document.getElementById('loginForm');
  clearAllErrors(form);

  let isValid = true;

  // Validate email
  const email = document.getElementById('email').value.trim();
  if (!validateEmail(email)) {
    setFieldError('email', 'Please enter a valid email address');
    isValid = false;
  }

  // Validate password
  const password = document.getElementById('password').value;
  if (!password) {
    setFieldError('password', 'Please enter your password');
    isValid = false;
  }

  return isValid;
}

function validateField(fieldName) {
  const field = document.getElementById(fieldName);
  if (!field) return;

  const value = field.value.trim();

  switch (fieldName) {
    case 'email':
      if (!validateEmail(value) && value) {
        setFieldError(fieldName, 'Please enter a valid email address');
      } else if (value) {
        clearFieldError(fieldName);
      }
      break;

    case 'password':
      if (!value) {
        setFieldError(fieldName, 'Please enter your password');
      } else {
        clearFieldError(fieldName);
      }
      break;
  }
}

async function submitLogin() {
  showLoading(true);

  try {
    const formData = {
      email: document.getElementById('email').value.trim(),
      password: document.getElementById('password').value,
    };

    const response = await apiCall('/auth/login', {
      method: 'POST',
      body: JSON.stringify(formData),
    });

    // Save the authentication token
    saveAuthToken(response.access_token);

    showAlert('Login successful! Redirecting to your profile...', 'success');

    // Redirect to profile page after 1 second
    setTimeout(() => {
      window.location.href = 'profile.html';
    }, 1000);
  } catch (error) {
    let errorMessage =
      'Login failed. Please check your credentials and try again.';

    if (error.message.includes('Incorrect email or password')) {
      errorMessage = 'Incorrect email or password. Please try again.';
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

  toggleButton.addEventListener('click', function () {
    const type =
      passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordField.setAttribute('type', type);

    const icon = this.querySelector('i');
    icon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
  });
}
