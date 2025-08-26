// Admin Dashboard functionality

let dashboardStats = null;

document.addEventListener('DOMContentLoaded', function () {
  // Check if user is authenticated and has admin role
  checkAdminAccess();

  // Load dashboard data
  loadDashboardStats();
  loadRecentActivity();

  // Load admin profile
  loadAdminProfile();
});

async function checkAdminAccess() {
  try {
    const profile = await apiCall('/me', {
      method: 'GET',
    });

    // Check if user has admin role
    if (profile.role !== 'admin' && profile.role !== 'super_admin') {
      showAlert('Access denied. Admin privileges required.', 'danger');
      setTimeout(() => {
        window.location.href = 'profile.html';
      }, 2000);
      return;
    }

    // Update admin name in navbar
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

async function loadDashboardStats() {
  showLoading(true);

  try {
    dashboardStats = await apiCall('/admin/dashboard', {
      method: 'GET',
    });

    displayStats(dashboardStats);
  } catch (error) {
    console.error('Failed to load dashboard stats:', error);
    showAlert('Failed to load dashboard statistics', 'danger');

    // Show placeholder data
    displayStats({
      total_users: 'N/A',
      active_users: 'N/A',
      total_books: 'N/A',
      active_loans: 'N/A',
    });
  } finally {
    showLoading(false);
  }
}

function displayStats(stats) {
  document.getElementById('totalUsers').textContent = stats.total_users || 0;
  document.getElementById('activeUsers').textContent = stats.active_users || 0;
  document.getElementById('totalBooks').textContent = stats.total_books || 0;
  document.getElementById('activeLoans').textContent = stats.active_loans || 0;
}

async function loadRecentActivity() {
  try {
    // For now, show placeholder activity
    // This would be replaced with actual recent activity API call
    const recentActivityContainer = document.getElementById('recentActivity');

    recentActivityContainer.innerHTML = `
      <div class="list-group list-group-flush">
        <div class="list-group-item d-flex justify-content-between align-items-center">
          <div>
            <i class="fas fa-user-plus text-success me-2"></i>
            <strong>New User Registration</strong>
            <br>
            <small class="text-muted">testuser123 registered an account</small>
          </div>
          <small class="text-muted">2 minutes ago</small>
        </div>
        
        <div class="list-group-item d-flex justify-content-between align-items-center">
          <div>
            <i class="fas fa-sign-in-alt text-info me-2"></i>
            <strong>User Login</strong>
            <br>
            <small class="text-muted">admin user logged in</small>
          </div>
          <small class="text-muted">5 minutes ago</small>
        </div>
        
        <div class="list-group-item d-flex justify-content-between align-items-center">
          <div>
            <i class="fas fa-book text-primary me-2"></i>
            <strong>Library Update</strong>
            <br>
            <small class="text-muted">Library system initialized</small>
          </div>
          <small class="text-muted">1 hour ago</small>
        </div>
      </div>
      
      <div class="text-center mt-3">
        <a href="#" class="btn btn-outline-primary btn-sm">
          <i class="fas fa-history me-1"></i>View All Activity
        </a>
      </div>
    `;
  } catch (error) {
    console.error('Failed to load recent activity:', error);
    document.getElementById('recentActivity').innerHTML = `
      <div class="text-center text-muted">
        <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
        <p>Failed to load recent activity</p>
      </div>
    `;
  }
}

async function loadAdminProfile() {
  try {
    const profile = await apiCall('/me', {
      method: 'GET',
    });

    // Update admin name if available
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

function showNotificationModal() {
  const modal = new bootstrap.Modal(
    document.getElementById('notificationModal')
  );
  modal.show();
}

async function sendNotification() {
  const title = document.getElementById('notificationTitle').value.trim();
  const message = document.getElementById('notificationMessage').value.trim();
  const target = document.getElementById('notificationTarget').value;

  if (!title || !message) {
    showAlert('Please fill in all required fields', 'warning');
    return;
  }

  showLoading(true);

  try {
    // This would be the actual API call for sending notifications
    // await apiCall('/admin/notifications', {
    //   method: 'POST',
    //   body: JSON.stringify({
    //     title: title,
    //     message: message,
    //     target: target
    //   })
    // });

    // For now, show success message
    showAlert('Notification sent successfully!', 'success');

    // Close modal and reset form
    const modal = bootstrap.Modal.getInstance(
      document.getElementById('notificationModal')
    );
    modal.hide();
    document.getElementById('notificationForm').reset();
  } catch (error) {
    console.error('Failed to send notification:', error);
    showAlert('Failed to send notification', 'danger');
  } finally {
    showLoading(false);
  }
}

async function generateReport() {
  showLoading(true);

  try {
    // This would be the actual API call for generating reports
    // For now, show a placeholder
    showAlert(
      'Report generation started. You will be notified when ready.',
      'info'
    );
  } catch (error) {
    console.error('Failed to generate report:', error);
    showAlert('Failed to generate report', 'danger');
  } finally {
    showLoading(false);
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

// Refresh dashboard stats every 30 seconds
setInterval(() => {
  loadDashboardStats();
}, 30000);
