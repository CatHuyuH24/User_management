// Signup page functionality

document.addEventListener('DOMContentLoaded', function () {
  // Redirect if already authenticated
  redirectIfAuthenticated();

  // Initialize form handlers
  initializeSignupForm();
  initializePasswordStrengthChecker();
  initializePasswordToggle();
});

function initializeSignupForm() {
  const form = document.getElementById('signupForm');

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    if (validateForm()) {
      await submitSignup();
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
  const form = document.getElementById('signupForm');
  clearAllErrors(form);

  let isValid = true;

  // Validate username
  const username = document.getElementById('username').value.trim();
  const usernameValidation = validateUsername(username);
  if (!usernameValidation.isValid) {
    setFieldError('username', usernameValidation.errors[0]);
    isValid = false;
  }

  // Validate email
  const email = document.getElementById('email').value.trim();
  if (!validateEmail(email)) {
    setFieldError('email', 'Please enter a valid email address');
    isValid = false;
  }

  // Validate password
  const password = document.getElementById('password').value;
  const passwordValidation = validatePassword(password);
  if (!passwordValidation.isValid) {
    setFieldError('password', passwordValidation.errors[0]);
    isValid = false;
  }

  // Validate terms agreement
  const agreeTerms = document.getElementById('agreeTerms').checked;
  if (!agreeTerms) {
    setFieldError('agreeTerms', 'You must agree to the terms and conditions');
    isValid = false;
  }

  return isValid;
}

function validateField(fieldName) {
  const field = document.getElementById(fieldName);
  if (!field) return;

  const value = field.value.trim();

  switch (fieldName) {
    case 'username':
      const usernameValidation = validateUsername(value);
      if (!usernameValidation.isValid && value) {
        setFieldError(fieldName, usernameValidation.errors[0]);
      } else if (value) {
        clearFieldError(fieldName);
      }
      break;

    case 'email':
      if (!validateEmail(value) && value) {
        setFieldError(fieldName, 'Please enter a valid email address');
      } else if (value) {
        clearFieldError(fieldName);
      }
      break;

    case 'password':
      // Password validation is handled by the strength checker
      break;
  }
}

async function submitSignup() {
  showLoading(true);

  try {
    const formData = {
      username: document.getElementById('username').value.trim(),
      email: document.getElementById('email').value.trim(),
      password: document.getElementById('password').value,
      first_name: document.getElementById('firstName').value.trim() || null,
      last_name: document.getElementById('lastName').value.trim() || null,
    };

    const response = await apiCall('/signup', {
      method: 'POST',
      body: JSON.stringify(formData),
    });

    showAlert(
      `
            <strong>Account Created Successfully!</strong><br>
            Welcome ${response.user.first_name || response.user.username}! 
            You can now <a href="login.html" class="alert-link">sign in to your account</a>.
        `,
      'success'
    );

    // Clear form
    document.getElementById('signupForm').reset();
    updatePasswordStrength('');

    // Redirect to login after 3 seconds
    setTimeout(() => {
      window.location.href = 'login.html';
    }, 3000);
  } catch (error) {
    let errorMessage = 'An error occurred while creating your account.';

    if (error.message.includes('Email already registered')) {
      errorMessage =
        'This email address is already registered. Please use a different email or <a href="login.html" class="alert-link">sign in</a>.';
    } else if (error.message.includes('Username already taken')) {
      errorMessage =
        'This username is already taken. Please choose a different username.';
    } else if (error.message) {
      errorMessage = error.message;
    }

    showAlert(errorMessage, 'danger');
  } finally {
    showLoading(false);
  }
}

function initializePasswordStrengthChecker() {
  const passwordField = document.getElementById('password');

  passwordField.addEventListener('input', function () {
    updatePasswordStrength(this.value);
  });
}

function updatePasswordStrength(password) {
  const requirements = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /\d/.test(password),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
  };

  // Update requirement indicators
  updateRequirement('lengthReq', requirements.length);
  updateRequirement('uppercaseReq', requirements.uppercase);
  updateRequirement('lowercaseReq', requirements.lowercase);
  updateRequirement('numberReq', requirements.number);
  updateRequirement('specialReq', requirements.special);

  // Calculate strength
  const metRequirements = Object.values(requirements).filter(Boolean).length;
  const strengthMeter = document.getElementById('strengthMeter');

  if (password.length === 0) {
    strengthMeter.className = 'strength-meter';
    strengthMeter.style.width = '0%';
  } else if (metRequirements < 3) {
    strengthMeter.className = 'strength-meter strength-weak';
    strengthMeter.style.width = '33%';
  } else if (metRequirements < 5) {
    strengthMeter.className = 'strength-meter strength-medium';
    strengthMeter.style.width = '66%';
  } else {
    strengthMeter.className = 'strength-meter strength-strong';
    strengthMeter.style.width = '100%';
  }
}

function updateRequirement(reqId, met) {
  const element = document.getElementById(reqId);
  if (met) {
    element.className = 'requirement met';
    element.querySelector('i').className = 'fas fa-check me-2';
  } else {
    element.className = 'requirement unmet';
    element.querySelector('i').className = 'fas fa-circle me-2';
    element.querySelector('i').style.fontSize = '0.5rem';
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
