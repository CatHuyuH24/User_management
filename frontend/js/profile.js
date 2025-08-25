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

  // Update avatar
  displayAvatar(profile.avatar_url);

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
  const avatarUpload = document.getElementById('avatarUpload');

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

    // Show avatar upload controls
    if (avatarUpload) {
      avatarUpload.style.display = 'block';
    }

    viewMode.style.display = 'none';
    editMode.style.display = 'block';
  } else {
    viewMode.style.display = 'block';
    editMode.style.display = 'none';

    // Hide avatar upload controls
    if (avatarUpload) {
      avatarUpload.style.display = 'none';
    }

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

// Avatar related functions
function displayAvatar(avatarUrl) {
  const avatarImage = document.getElementById('avatarImage');
  const avatarIcon = document.getElementById('avatarIcon');

  if (avatarUrl) {
    const fullAvatarUrl = avatarUrl.startsWith('http')
      ? avatarUrl
      : `http://localhost:8000${avatarUrl}`;

    avatarImage.src = fullAvatarUrl;
    avatarImage.style.display = 'block';
    avatarIcon.style.display = 'none';
  } else {
    avatarImage.style.display = 'none';
    avatarIcon.style.display = 'flex';
  }
}

function initializeAvatarUpload() {
  const avatarFile = document.getElementById('avatarFile');
  const avatarUpload = document.getElementById('avatarUpload');

  if (avatarFile) {
    avatarFile.addEventListener('change', handleAvatarUpload);
  }

  // Show avatar upload controls in edit mode
  const editModeToggle = document.querySelector(
    '[onclick="toggleEditMode(true)"]'
  );
  if (editModeToggle) {
    editModeToggle.addEventListener('click', () => {
      if (avatarUpload) {
        avatarUpload.style.display = 'block';
      }
    });
  }

  // Hide avatar upload controls in view mode
  const cancelEditButton = document.querySelector(
    '[onclick="toggleEditMode(false)"]'
  );
  if (cancelEditButton) {
    cancelEditButton.addEventListener('click', () => {
      if (avatarUpload) {
        avatarUpload.style.display = 'none';
      }
    });
  }
}

async function handleAvatarUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  // Validate file type
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
  if (!allowedTypes.includes(file.type)) {
    showAlert('Please select a valid image file (JPG, PNG, or GIF)', 'danger');
    return;
  }

  // Validate file size (5MB)
  const maxSize = 5 * 1024 * 1024;
  if (file.size > maxSize) {
    showAlert('File size must be less than 5MB', 'danger');
    return;
  }

  showLoading(true);

  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/users/me/avatar`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${getAuthToken()}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Avatar upload failed');
    }

    const updatedProfile = await response.json();

    // Update global profile data
    userProfile = updatedProfile;

    // Update avatar display
    displayAvatar(updatedProfile.avatar_url);

    showAlert('Avatar updated successfully!', 'success');
  } catch (error) {
    console.error('Avatar upload error:', error);
    showAlert(error.message || 'Failed to upload avatar', 'danger');
  } finally {
    showLoading(false);
    // Clear the file input
    event.target.value = '';
  }
}

// Initialize avatar upload when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
  initializeAvatarUpload();
});
