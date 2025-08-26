// Admin Users Management functionality

let currentUsers = [];
let currentPage = 1;
let usersPerPage = 10;
let totalUsers = 0;
let currentFilters = {
  search: '',
  role: '',
  status: '',
  verification: '',
};

document.addEventListener('DOMContentLoaded', function () {
  // Check admin access
  checkAdminAccess();

  // Load users
  loadUsers();

  // Initialize search
  initializeSearch();

  // Load admin profile
  loadAdminProfile();
});

async function checkAdminAccess() {
  try {
    const profile = await apiCall('/me', {
      method: 'GET',
    });

    if (profile.role !== 'admin' && profile.role !== 'super_admin') {
      showAlert('Access denied. Admin privileges required.', 'danger');
      setTimeout(() => {
        window.location.href = 'profile.html';
      }, 2000);
      return;
    }

    const fullName = [profile.first_name, profile.last_name]
      .filter(Boolean)
      .join(' ');
    document.getElementById('adminName').textContent =
      fullName || profile.username;
  } catch (error) {
    if (error.message.includes('401')) {
      removeAuthToken();
      window.location.href = 'login.html';
    } else {
      showAlert('Failed to verify admin access', 'danger');
      setTimeout(() => {
        window.location.href = 'login.html';
      }, 2000);
    }
  }
}

async function loadUsers(page = 1) {
  showLoading(true);
  currentPage = page;

  try {
    // Build query parameters
    const params = new URLSearchParams({
      skip: (page - 1) * usersPerPage,
      limit: usersPerPage,
    });

    if (currentFilters.search) {
      params.append('search', currentFilters.search);
    }
    if (currentFilters.role) {
      params.append('role', currentFilters.role);
    }
    if (currentFilters.status !== '') {
      params.append('is_active', currentFilters.status);
    }
    if (currentFilters.verification !== '') {
      params.append('is_verified', currentFilters.verification);
    }

    const users = await apiCall(`/admin/users?${params.toString()}`, {
      method: 'GET',
    });

    currentUsers = users;
    displayUsers(users);
    updatePagination();
  } catch (error) {
    console.error('Failed to load users:', error);
    showAlert('Failed to load users', 'danger');
    displayUsersError();
  } finally {
    showLoading(false);
  }
}

function displayUsers(users) {
  const tbody = document.getElementById('usersTableBody');

  if (!users || users.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center py-4">
          <i class="fas fa-users fa-3x text-muted mb-3"></i>
          <p class="text-muted">No users found</p>
        </td>
      </tr>
    `;
    document.getElementById('userCount').textContent = '0';
    return;
  }

  document.getElementById('userCount').textContent = users.length;

  tbody.innerHTML = users
    .map((user) => {
      const avatar = user.avatar_url
        ? `<img src="${user.avatar_url}" class="user-avatar" alt="Avatar">`
        : `<div class="user-avatar-placeholder">${user.username
            .charAt(0)
            .toUpperCase()}</div>`;

      const statusBadge = user.is_active
        ? '<span class="badge bg-success status-badge">Active</span>'
        : '<span class="badge bg-danger status-badge">Inactive</span>';

      const verifiedBadge = user.is_verified
        ? '<span class="badge bg-success status-badge">Verified</span>'
        : '<span class="badge bg-warning status-badge">Unverified</span>';

      const roleBadge = getRoleBadge(user.role);

      const lastLogin = user.last_login
        ? new Date(user.last_login).toLocaleDateString()
        : 'Never';

      const fullName =
        [user.first_name, user.last_name].filter(Boolean).join(' ') ||
        user.username;

      return `
      <tr>
        <td>
          <div class="d-flex align-items-center">
            ${avatar}
            <div class="ms-3">
              <div class="fw-bold">${fullName}</div>
              <div class="text-muted small">@${user.username}</div>
            </div>
          </div>
        </td>
        <td>${user.email}</td>
        <td>${roleBadge}</td>
        <td>${statusBadge}</td>
        <td>${verifiedBadge}</td>
        <td><small>${lastLogin}</small></td>
        <td>
          <div class="btn-group" role="group">
            <button class="btn btn-sm btn-outline-primary action-btn" 
                    onclick="viewUser(${user.id})" title="View Details">
              <i class="fas fa-eye"></i>
            </button>
            <button class="btn btn-sm btn-outline-warning action-btn" 
                    onclick="editUser(${user.id})" title="Edit User">
              <i class="fas fa-edit"></i>
            </button>
            <button class="btn btn-sm btn-outline-info action-btn" 
                    onclick="resetPassword(${user.id})" title="Reset Password">
              <i class="fas fa-key"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger action-btn" 
                    onclick="deleteUser(${user.id})" title="Delete User">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
    })
    .join('');
}

function getRoleBadge(role) {
  switch (role) {
    case 'super_admin':
      return '<span class="badge bg-danger role-badge">Super Admin</span>';
    case 'admin':
      return '<span class="badge bg-warning role-badge">Admin</span>';
    case 'client':
      return '<span class="badge bg-primary role-badge">Client</span>';
    default:
      return '<span class="badge bg-secondary role-badge">Unknown</span>';
  }
}

function displayUsersError() {
  const tbody = document.getElementById('usersTableBody');
  tbody.innerHTML = `
    <tr>
      <td colspan="7" class="text-center py-4">
        <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
        <p class="text-danger">Failed to load users</p>
        <button class="btn btn-outline-primary btn-sm" onclick="loadUsers()">
          <i class="fas fa-retry me-1"></i>Try Again
        </button>
      </td>
    </tr>
  `;
}

function initializeSearch() {
  const searchInput = document.getElementById('searchInput');
  let searchTimeout;

  searchInput.addEventListener('input', function () {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      currentFilters.search = this.value.trim();
      loadUsers(1);
    }, 500);
  });
}

function applyFilters() {
  currentFilters.role = document.getElementById('roleFilter').value;
  currentFilters.status = document.getElementById('statusFilter').value;
  currentFilters.verification =
    document.getElementById('verificationFilter').value;

  loadUsers(1);
}

function refreshUsers() {
  loadUsers(currentPage);
}

function updatePagination() {
  // For now, simple pagination
  // This would be enhanced with actual pagination data from the API
  const showingStart = (currentPage - 1) * usersPerPage + 1;
  const showingEnd = Math.min(currentPage * usersPerPage, currentUsers.length);

  document.getElementById('showingStart').textContent = showingStart;
  document.getElementById('showingEnd').textContent = showingEnd;
  document.getElementById('totalUsers').textContent = currentUsers.length;
}

function showCreateUserModal() {
  const modal = new bootstrap.Modal(document.getElementById('createUserModal'));
  modal.show();
}

async function createUser() {
  const form = document.getElementById('createUserForm');
  if (!validateCreateUserForm()) {
    return;
  }

  showLoading(true);

  try {
    const userData = {
      username: document.getElementById('newUsername').value.trim(),
      email: document.getElementById('newEmail').value.trim(),
      password: document.getElementById('newPassword').value,
      first_name: document.getElementById('newFirstName').value.trim() || null,
      last_name: document.getElementById('newLastName').value.trim() || null,
      role: document.getElementById('newRole').value,
      is_active: document.getElementById('newIsActive').checked,
      is_verified: document.getElementById('newIsVerified').checked,
    };

    await apiCall('/admin/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });

    showAlert('User created successfully!', 'success');

    // Close modal and reset form
    const modal = bootstrap.Modal.getInstance(
      document.getElementById('createUserModal')
    );
    modal.hide();
    form.reset();

    // Reload users
    loadUsers(currentPage);
  } catch (error) {
    console.error('Failed to create user:', error);
    showAlert(`Failed to create user: ${error.message}`, 'danger');
  } finally {
    showLoading(false);
  }
}

function validateCreateUserForm() {
  const username = document.getElementById('newUsername').value.trim();
  const email = document.getElementById('newEmail').value.trim();
  const password = document.getElementById('newPassword').value;

  let isValid = true;

  // Clear previous errors
  clearFieldError('newUsername');
  clearFieldError('newEmail');
  clearFieldError('newPassword');

  // Validate username
  const usernameValidation = validateUsername(username);
  if (!usernameValidation.isValid) {
    setFieldError('newUsername', usernameValidation.errors[0]);
    isValid = false;
  }

  // Validate email
  if (!validateEmail(email)) {
    setFieldError('newEmail', 'Please enter a valid email address');
    isValid = false;
  }

  // Validate password
  const passwordValidation = validatePassword(password);
  if (!passwordValidation.isValid) {
    setFieldError('newPassword', passwordValidation.errors[0]);
    isValid = false;
  }

  return isValid;
}

async function viewUser(userId) {
  const user = currentUsers.find((u) => u.id === userId);
  if (!user) return;

  showAlert(`Viewing user: ${user.username} (${user.email})`, 'info');
}

async function editUser(userId) {
  const user = currentUsers.find((u) => u.id === userId);
  if (!user) return;

  showAlert(
    `Edit functionality for ${user.username} would be implemented here`,
    'info'
  );
}

async function resetPassword(userId) {
  const user = currentUsers.find((u) => u.id === userId);
  if (!user) return;

  if (!confirm(`Reset password for ${user.username}?`)) {
    return;
  }

  showLoading(true);

  try {
    // This would be the actual API call
    // await apiCall(`/admin/users/${userId}/reset-password`, {
    //   method: 'POST'
    // });

    showAlert(
      `Password reset for ${user.username} - functionality to be implemented`,
      'info'
    );
  } catch (error) {
    console.error('Failed to reset password:', error);
    showAlert('Failed to reset password', 'danger');
  } finally {
    showLoading(false);
  }
}

async function deleteUser(userId) {
  const user = currentUsers.find((u) => u.id === userId);
  if (!user) return;

  if (
    !confirm(
      `Are you sure you want to delete user "${user.username}"?\n\nThis action cannot be undone.`
    )
  ) {
    return;
  }

  showLoading(true);

  try {
    await apiCall(`/admin/users/${userId}`, {
      method: 'DELETE',
    });

    showAlert(`User ${user.username} deleted successfully`, 'success');
    loadUsers(currentPage);
  } catch (error) {
    console.error('Failed to delete user:', error);
    showAlert(`Failed to delete user: ${error.message}`, 'danger');
  } finally {
    showLoading(false);
  }
}

function exportUsers() {
  if (currentUsers.length === 0) {
    showAlert('No users to export', 'warning');
    return;
  }

  // Create CSV content
  const headers = [
    'Username',
    'Email',
    'Role',
    'Status',
    'Verified',
    'Created At',
  ];
  const csvContent = [
    headers.join(','),
    ...currentUsers.map((user) =>
      [
        user.username,
        user.email,
        user.role,
        user.is_active ? 'Active' : 'Inactive',
        user.is_verified ? 'Verified' : 'Unverified',
        new Date(user.created_at).toLocaleDateString(),
      ].join(',')
    ),
  ].join('\n');

  // Download CSV
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `users_export_${new Date().toISOString().split('T')[0]}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);

  showAlert('Users exported successfully', 'success');
}

async function loadAdminProfile() {
  try {
    const profile = await apiCall('/me', {
      method: 'GET',
    });

    const fullName = [profile.first_name, profile.last_name]
      .filter(Boolean)
      .join(' ');

    if (fullName) {
      document.getElementById('adminName').textContent = fullName;
    }
  } catch (error) {
    console.error('Failed to load admin profile:', error);
  }
}

function logout() {
  if (confirm('Are you sure you want to logout?')) {
    removeAuthToken();
    showAlert('Logged out successfully', 'success');
    setTimeout(() => {
      window.location.href = 'login.html';
    }, 1000);
  }
}
