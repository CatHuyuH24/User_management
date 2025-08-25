// Profile page functionality

let userProfile = null;

document.addEventListener('DOMContentLoaded', function () {
  // Redirect if not authenticated
  redirectIfNotAuthenticated();

  // Load user profile
  loadUserProfile();

  // Initialize form handlers
  initializeEditForm();
});

async function loadUserProfile() {
  showLoading(true);

  try {
    userProfile = await apiCall('/users/me', {
      method: 'GET',
    });

    displayProfile(userProfile);
  } catch (error) {
    if (error.message.includes('401')) {
      // Token expired or invalid
      removeAuthToken();
      window.location.href = 'login.html';
    } else {
      showAlert(
        'Failed to load profile. Please try refreshing the page.',
        'danger'
      );
    }
  } finally {
    showLoading(false);
  }
}

function displayProfile(profile) {
  // Update header
  const fullName = [profile.first_name, profile.last_name]
    .filter(Boolean)
    .join(' ');
  document.getElementById('profileName').textContent =
    fullName || profile.username;
  document.getElementById('profileEmail').textContent = profile.email;

  // Update display fields
  document.getElementById('displayUsername').textContent = profile.username;
  document.getElementById('displayFirstName').textContent =
    profile.first_name || 'Not specified';
  document.getElementById('displayLastName').textContent =
    profile.last_name || 'Not specified';
  document.getElementById('displayYearOfBirth').textContent =
    profile.year_of_birth || 'Not specified';
  document.getElementById('displayDescription').textContent =
    profile.description || 'No description provided';

  // Format and display creation date
  const createdDate = new Date(profile.created_at);
  document.getElementById('displayCreatedAt').textContent =
    createdDate.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });

  // Display account status
  const statusBadge = profile.is_active
    ? '<span class="badge bg-success">Active</span>'
    : '<span class="badge bg-danger">Inactive</span>';
  document.getElementById('displayStatus').innerHTML = statusBadge;
}

function toggleEditMode(edit) {
  const viewMode = document.getElementById('viewMode');
  const editMode = document.getElementById('editMode');

  if (edit) {
    // Populate edit form with current values
    document.getElementById('editFirstName').value =
      userProfile.first_name || '';
    document.getElementById('editLastName').value = userProfile.last_name || '';
    document.getElementById('editYearOfBirth').value =
      userProfile.year_of_birth || '';
    document.getElementById('editDescription').value =
      userProfile.description || '';

    // Update character count
    updateDescriptionCount();

    viewMode.style.display = 'none';
    editMode.style.display = 'block';
  } else {
    viewMode.style.display = 'block';
    editMode.style.display = 'none';

    // Clear any errors
    clearAllErrors(document.getElementById('editProfileForm'));
  }
}

function initializeEditForm() {
  const form = document.getElementById('editProfileForm');
  const descriptionField = document.getElementById('editDescription');

  // Handle form submission
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    await updateProfile();
  });

  // Handle description character count
  descriptionField.addEventListener('input', updateDescriptionCount);
}

function updateDescriptionCount() {
  const description = document.getElementById('editDescription').value;
  const count = description.length;
  const countElement = document.getElementById('descriptionCount');

  countElement.textContent = count;

  if (count > 1000) {
    countElement.style.color = 'var(--accent-color)';
  } else if (count > 900) {
    countElement.style.color = 'var(--warning-color)';
  } else {
    countElement.style.color = '';
  }
}

async function updateProfile() {
  showLoading(true);

  try {
    // Prepare update data
    const updateData = {
      first_name: document.getElementById('editFirstName').value.trim() || null,
      last_name: document.getElementById('editLastName').value.trim() || null,
      year_of_birth:
        parseInt(document.getElementById('editYearOfBirth').value) || null,
      description:
        document.getElementById('editDescription').value.trim() || null,
    };

    // Validate data
    if (
      updateData.year_of_birth &&
      (updateData.year_of_birth < 1900 || updateData.year_of_birth > 2024)
    ) {
      setFieldError(
        'editYearOfBirth',
        'Please enter a valid year between 1900 and 2024'
      );
      return;
    }

    if (updateData.description && updateData.description.length > 1000) {
      setFieldError(
        'editDescription',
        'Description must be no more than 1000 characters'
      );
      return;
    }

    // Submit update
    const updatedProfile = await apiCall('/users/me', {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });

    // Update local profile data
    userProfile = updatedProfile;

    // Update display
    displayProfile(updatedProfile);

    // Switch back to view mode
    toggleEditMode(false);

    showAlert('Profile updated successfully!', 'success');
  } catch (error) {
    if (error.message.includes('401')) {
      // Token expired or invalid
      removeAuthToken();
      window.location.href = 'login.html';
    } else {
      showAlert(
        error.message || 'Failed to update profile. Please try again.',
        'danger'
      );
    }
  } finally {
    showLoading(false);
  }
}

function logout() {
  // Show confirmation dialog
  if (confirm('Are you sure you want to logout?')) {
    // Remove authentication token
    removeAuthToken();

    // Show message and redirect
    showAlert('You have been logged out successfully.', 'info');

    setTimeout(() => {
      window.location.href = 'index.html';
    }, 1000);
  }
}
