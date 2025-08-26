// Client Dashboard functionality

let currentTab = 'dashboard';
let currentBooks = [];
let currentLoans = [];
let currentNotifications = [];
let currentPage = 1;
let booksPerPage = 12;
let selectedBookId = null;

let currentFilters = {
  search: '',
  category: '',
  availability: '',
  sort: 'title',
};

document.addEventListener('DOMContentLoaded', function () {
  // Check authentication
  redirectIfNotAuthenticated();

  // Load user data
  loadUserProfile();

  // Load dashboard data
  loadDashboardData();

  // Initialize search
  initializeSearch();
});

async function loadUserProfile() {
  try {
    const profile = await apiCall('/me', {
      method: 'GET',
    });

    // Check if user is admin - redirect to admin portal
    if (profile.role === 'admin' || profile.role === 'super_admin') {
      showAlert('Redirecting to admin portal...', 'info');
      setTimeout(() => {
        window.location.href = 'admin-dashboard.html';
      }, 1500);
      return;
    }

    const fullName = [profile.first_name, profile.last_name]
      .filter(Boolean)
      .join(' ');
    document.getElementById('userName').textContent =
      fullName || profile.username;
  } catch (error) {
    if (error.message.includes('401')) {
      removeAuthToken();
      window.location.href = 'login.html';
    } else {
      showAlert('Failed to load profile', 'danger');
    }
  }
}

async function loadDashboardData() {
  showLoading(true);

  try {
    // Load stats, books, loans, and notifications
    await Promise.all([
      loadDashboardStats(),
      loadRecentActivity(),
      loadRecommendedBooks(),
      loadNotifications(),
    ]);
  } catch (error) {
    console.error('Failed to load dashboard data:', error);
    showAlert('Failed to load dashboard data', 'danger');
  } finally {
    showLoading(false);
  }
}

async function loadDashboardStats() {
  try {
    // Mock data for now - these would be actual API calls
    const stats = {
      totalBooksAvailable: 1234,
      currentLoans: 3,
      dueSoon: 1,
      overdue: 0,
    };

    document.getElementById('totalBooksAvailable').textContent =
      stats.totalBooksAvailable;
    document.getElementById('currentLoans').textContent = stats.currentLoans;
    document.getElementById('dueSoon').textContent = stats.dueSoon;
    document.getElementById('overdue').textContent = stats.overdue;

    // These would be actual API calls:
    // const stats = await apiCall('/users/me/stats', { method: 'GET' });
    // document.getElementById('totalBooksAvailable').textContent = stats.available_books;
    // document.getElementById('currentLoans').textContent = stats.current_loans;
    // document.getElementById('dueSoon').textContent = stats.due_soon;
    // document.getElementById('overdue').textContent = stats.overdue;
  } catch (error) {
    console.error('Failed to load stats:', error);
  }
}

async function loadRecentActivity() {
  try {
    const container = document.getElementById('recentActivity');

    // Mock recent activity data
    const activities = [
      {
        type: 'borrowed',
        book: 'The Great Gatsby',
        date: '2025-08-24',
        icon: 'fas fa-bookmark text-success',
      },
      {
        type: 'returned',
        book: 'To Kill a Mockingbird',
        date: '2025-08-22',
        icon: 'fas fa-undo text-info',
      },
      {
        type: 'due_reminder',
        book: '1984',
        date: '2025-08-21',
        icon: 'fas fa-clock text-warning',
      },
    ];

    if (activities.length === 0) {
      container.innerHTML = '<p class="text-muted">No recent activity</p>';
      return;
    }

    container.innerHTML = activities
      .map(
        (activity) => `
      <div class="d-flex align-items-center mb-3">
        <div class="me-3">
          <i class="${activity.icon} fa-lg"></i>
        </div>
        <div class="flex-grow-1">
          <div class="fw-bold">${activity.book}</div>
          <small class="text-muted">${getActivityText(
            activity.type
          )} • ${new Date(activity.date).toLocaleDateString()}</small>
        </div>
      </div>
    `
      )
      .join('');
  } catch (error) {
    console.error('Failed to load recent activity:', error);
    document.getElementById('recentActivity').innerHTML =
      '<p class="text-danger">Failed to load activity</p>';
  }
}

function getActivityText(type) {
  switch (type) {
    case 'borrowed':
      return 'Borrowed';
    case 'returned':
      return 'Returned';
    case 'renewed':
      return 'Renewed';
    case 'due_reminder':
      return 'Due reminder sent';
    case 'overdue':
      return 'Book overdue';
    default:
      return 'Activity';
  }
}

async function loadRecommendedBooks() {
  try {
    const container = document.getElementById('recommendedBooks');

    // Mock recommended books
    const books = [
      {
        id: 1,
        title: 'Clean Code',
        author: 'Robert C. Martin',
        cover_url: null,
      },
      {
        id: 2,
        title: 'The Art of War',
        author: 'Sun Tzu',
        cover_url: null,
      },
    ];

    if (books.length === 0) {
      container.innerHTML =
        '<p class="text-muted">No recommendations available</p>';
      return;
    }

    container.innerHTML = books
      .map((book) => {
        const cover = book.cover_url
          ? `<img src="${book.cover_url}" class="card-img-top" style="height: 120px; object-fit: cover;" alt="Cover">`
          : `<div class="card-img-top d-flex align-items-center justify-content-center bg-primary text-white" style="height: 120px; font-size: 1.5rem;">${book.title.charAt(
              0
            )}</div>`;

        return `
        <div class="card mb-2" style="cursor: pointer;" onclick="showBookDetails(${book.id})">
          ${cover}
          <div class="card-body p-2">
            <h6 class="card-title mb-1" style="font-size: 0.9rem;">${book.title}</h6>
            <p class="card-text mb-0" style="font-size: 0.8rem; color: #666;">${book.author}</p>
          </div>
        </div>
      `;
      })
      .join('');
  } catch (error) {
    console.error('Failed to load recommended books:', error);
    document.getElementById('recommendedBooks').innerHTML =
      '<p class="text-danger">Failed to load recommendations</p>';
  }
}

async function loadBooks(page = 1) {
  showLoading(true);
  currentPage = page;

  try {
    // Build query parameters
    const params = new URLSearchParams({
      skip: (page - 1) * booksPerPage,
      limit: booksPerPage,
    });

    if (currentFilters.search) {
      params.append('search', currentFilters.search);
    }
    if (currentFilters.category) {
      params.append('category', currentFilters.category);
    }
    if (currentFilters.availability === 'available') {
      params.append('available_only', 'true');
    }
    if (currentFilters.sort) {
      params.append('sort_by', currentFilters.sort);
    }

    // Mock books data for now
    const mockBooks = generateMockBooksForClient();
    currentBooks = mockBooks;
    displayBooks(mockBooks);
    updateBooksPagination();

    // This would be the actual API call:
    // const books = await apiCall(`/books?${params.toString()}`, {
    //   method: 'GET',
    // });
    // currentBooks = books;
    // displayBooks(books);
    // updateBooksPagination();
  } catch (error) {
    console.error('Failed to load books:', error);
    showAlert('Failed to load books', 'danger');
    displayBooksError();
  } finally {
    showLoading(false);
  }
}

function generateMockBooksForClient() {
  return [
    {
      id: 1,
      title: 'The Great Gatsby',
      author: 'F. Scott Fitzgerald',
      category: 'Fiction',
      cover_url: null,
      available_copies: 3,
      total_copies: 5,
      description: 'A classic American novel set in the Jazz Age.',
    },
    {
      id: 2,
      title: 'To Kill a Mockingbird',
      author: 'Harper Lee',
      category: 'Fiction',
      cover_url: null,
      available_copies: 2,
      total_copies: 4,
      description:
        'A gripping tale of racial injustice and childhood innocence.',
    },
    {
      id: 3,
      title: '1984',
      author: 'George Orwell',
      category: 'Fiction',
      cover_url: null,
      available_copies: 0,
      total_copies: 6,
      description: 'A dystopian social science fiction novel.',
    },
    {
      id: 4,
      title: 'Clean Code',
      author: 'Robert C. Martin',
      category: 'Technology',
      cover_url: null,
      available_copies: 1,
      total_copies: 3,
      description: 'A handbook of agile software craftsmanship.',
    },
    {
      id: 5,
      title: 'The Art of War',
      author: 'Sun Tzu',
      category: 'History',
      cover_url: null,
      available_copies: 2,
      total_copies: 2,
      description: 'Ancient Chinese military treatise.',
    },
    {
      id: 6,
      title: 'Sapiens',
      author: 'Yuval Noah Harari',
      category: 'Non-Fiction',
      cover_url: null,
      available_copies: 4,
      total_copies: 5,
      description: 'A brief history of humankind.',
    },
  ];
}

function displayBooks(books) {
  const grid = document.getElementById('booksGrid');

  if (!books || books.length === 0) {
    grid.innerHTML = `
      <div class="col-12 text-center py-5">
        <i class="fas fa-book-open fa-5x text-muted mb-3"></i>
        <h4 class="text-muted">No books found</h4>
        <p class="text-muted">Try adjusting your search criteria</p>
      </div>
    `;
    return;
  }

  grid.innerHTML = books
    .map((book) => {
      const cover = book.cover_url
        ? `<img src="${book.cover_url}" class="book-cover" alt="Book Cover">`
        : `<div class="book-cover-placeholder">${book.title
            .charAt(0)
            .toUpperCase()}</div>`;

      const availabilityBadge =
        book.available_copies > 0
          ? `<span class="badge bg-success availability-badge">${book.available_copies} available</span>`
          : `<span class="badge bg-danger availability-badge">Not available</span>`;

      return `
      <div class="col-lg-3 col-md-4 col-sm-6">
        <div class="card book-card" onclick="showBookDetails(${book.id})">
          ${cover}
          <div class="card-body">
            <h5 class="book-title">${book.title}</h5>
            <p class="book-author">by ${book.author}</p>
            <div class="d-flex justify-content-between align-items-center">
              <span class="badge bg-secondary">${book.category}</span>
              ${availabilityBadge}
            </div>
          </div>
        </div>
      </div>
    `;
    })
    .join('');
}

function displayBooksError() {
  const grid = document.getElementById('booksGrid');
  grid.innerHTML = `
    <div class="col-12 text-center py-5">
      <i class="fas fa-exclamation-triangle fa-5x text-danger mb-3"></i>
      <h4 class="text-danger">Failed to load books</h4>
      <button class="btn btn-outline-primary" onclick="loadBooks()">
        <i class="fas fa-retry me-1"></i>Try Again
      </button>
    </div>
  `;
}

async function loadUserLoans() {
  showLoading(true);

  try {
    // Mock loans data
    const mockLoans = [
      {
        id: 1,
        book: {
          id: 1,
          title: 'The Great Gatsby',
          author: 'F. Scott Fitzgerald',
          cover_url: null,
        },
        loan_date: '2025-08-20',
        due_date: '2025-08-27',
        status: 'active',
        renewal_count: 0,
      },
      {
        id: 2,
        book: {
          id: 4,
          title: 'Clean Code',
          author: 'Robert C. Martin',
          cover_url: null,
        },
        loan_date: '2025-08-18',
        due_date: '2025-08-25',
        status: 'active',
        renewal_count: 1,
      },
    ];

    currentLoans = mockLoans;
    displayUserLoans(mockLoans);

    // This would be the actual API call:
    // const loans = await apiCall('/users/me/loans', { method: 'GET' });
    // currentLoans = loans;
    // displayUserLoans(loans);
  } catch (error) {
    console.error('Failed to load loans:', error);
    showAlert('Failed to load your books', 'danger');
    displayLoansError();
  } finally {
    showLoading(false);
  }
}

function displayUserLoans(loans) {
  const container = document.getElementById('loansList');

  if (!loans || loans.length === 0) {
    container.innerHTML = `
      <div class="text-center py-5">
        <i class="fas fa-bookmark fa-5x text-muted mb-3"></i>
        <h4 class="text-muted">No borrowed books</h4>
        <p class="text-muted">Browse our collection to find your next great read!</p>
        <button class="btn btn-primary" onclick="showBooksTab()">
          <i class="fas fa-book me-1"></i>Browse Books
        </button>
      </div>
    `;
    return;
  }

  container.innerHTML = loans
    .map((loan) => {
      const dueDate = new Date(loan.due_date);
      const today = new Date();
      const daysUntilDue = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));

      let statusClass = '';
      let statusText = '';
      let dueDateClass = 'due-date';

      if (daysUntilDue < 0) {
        statusClass = 'overdue';
        statusText = 'Overdue';
        dueDateClass += ' overdue';
      } else if (daysUntilDue <= 2) {
        statusClass = 'due-soon';
        statusText = 'Due Soon';
        dueDateClass += ' due-soon';
      } else {
        statusText = 'Active';
      }

      const cover = loan.book.cover_url
        ? `<img src="${loan.book.cover_url}" style="width: 60px; height: 80px; object-fit: cover; border-radius: 4px;" alt="Cover">`
        : `<div style="width: 60px; height: 80px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 4px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 18px;">${loan.book.title.charAt(
            0
          )}</div>`;

      return `
      <div class="card loan-card ${statusClass}">
        <div class="card-body">
          <div class="row align-items-center">
            <div class="col-auto">
              ${cover}
            </div>
            <div class="col">
              <h5 class="mb-1">${loan.book.title}</h5>
              <p class="text-muted mb-1">by ${loan.book.author}</p>
              <small class="text-muted">Borrowed: ${new Date(
                loan.loan_date
              ).toLocaleDateString()}</small>
            </div>
            <div class="col-auto text-end">
              <div class="${dueDateClass}">Due: ${dueDate.toLocaleDateString()}</div>
              <div class="mt-1">
                <span class="badge bg-${
                  statusClass === 'overdue'
                    ? 'danger'
                    : statusClass === 'due-soon'
                    ? 'warning'
                    : 'success'
                }">${statusText}</span>
              </div>
              <div class="mt-2">
                <button class="btn btn-sm btn-outline-primary me-2" onclick="renewBook(${
                  loan.id
                })" 
                        ${loan.renewal_count >= 2 ? 'disabled' : ''}>
                  <i class="fas fa-sync me-1"></i>Renew${
                    loan.renewal_count >= 2 ? ' (Max)' : ''
                  }
                </button>
                <button class="btn btn-sm btn-outline-success" onclick="returnBook(${
                  loan.id
                })">
                  <i class="fas fa-undo me-1"></i>Return
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
    })
    .join('');
}

function displayLoansError() {
  const container = document.getElementById('loansList');
  container.innerHTML = `
    <div class="text-center py-5">
      <i class="fas fa-exclamation-triangle fa-5x text-danger mb-3"></i>
      <h4 class="text-danger">Failed to load your books</h4>
      <button class="btn btn-outline-primary" onclick="loadUserLoans()">
        <i class="fas fa-retry me-1"></i>Try Again
      </button>
    </div>
  `;
}

async function loadNotifications() {
  try {
    // Mock notifications data
    const mockNotifications = [
      {
        id: 1,
        type: 'due_reminder',
        title: 'Book Due Tomorrow',
        message:
          'Your book "Clean Code" is due tomorrow. Please return it to avoid late fees.',
        is_read: false,
        created_at: '2025-08-25T10:00:00Z',
      },
      {
        id: 2,
        type: 'book_available',
        title: 'Reserved Book Available',
        message:
          'Your reserved book "Atomic Habits" is now available for pickup.',
        is_read: true,
        created_at: '2025-08-24T15:30:00Z',
      },
    ];

    currentNotifications = mockNotifications;
    updateNotificationBadge();
    displayNotifications(mockNotifications);

    // This would be the actual API call:
    // const notifications = await apiCall('/notifications', { method: 'GET' });
    // currentNotifications = notifications;
    // updateNotificationBadge();
    // displayNotifications(notifications);
  } catch (error) {
    console.error('Failed to load notifications:', error);
  }
}

function updateNotificationBadge() {
  const unreadCount = currentNotifications.filter((n) => !n.is_read).length;
  const badge = document.getElementById('notificationBadge');

  if (unreadCount > 0) {
    badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
    badge.style.display = 'flex';
  } else {
    badge.style.display = 'none';
  }
}

function displayNotifications(notifications) {
  const container = document.getElementById('notificationsList');

  if (!notifications || notifications.length === 0) {
    container.innerHTML = `
      <div class="text-center py-5">
        <i class="fas fa-bell fa-5x text-muted mb-3"></i>
        <h4 class="text-muted">No notifications</h4>
        <p class="text-muted">You're all caught up!</p>
      </div>
    `;
    return;
  }

  container.innerHTML = notifications
    .map((notification) => {
      const iconClass = getNotificationIcon(notification.type);
      const date = new Date(notification.created_at).toLocaleDateString();

      return `
      <div class="card mb-3 ${
        notification.is_read ? '' : 'border-primary'
      }" onclick="markNotificationRead(${notification.id})">
        <div class="card-body">
          <div class="d-flex align-items-start">
            <div class="me-3">
              <i class="${iconClass} fa-lg text-primary"></i>
            </div>
            <div class="flex-grow-1">
              <h6 class="mb-1 ${notification.is_read ? '' : 'fw-bold'}">${
        notification.title
      }</h6>
              <p class="mb-1">${notification.message}</p>
              <small class="text-muted">${date}</small>
            </div>
            ${
              !notification.is_read
                ? '<div class="badge bg-primary">New</div>'
                : ''
            }
          </div>
        </div>
      </div>
    `;
    })
    .join('');
}

function getNotificationIcon(type) {
  switch (type) {
    case 'due_reminder':
      return 'fas fa-clock';
    case 'overdue':
      return 'fas fa-exclamation-triangle';
    case 'book_available':
      return 'fas fa-book';
    case 'renewal_success':
      return 'fas fa-sync';
    default:
      return 'fas fa-info-circle';
  }
}

// Tab Management
function showDashboardTab() {
  hideAllTabs();
  document.getElementById('dashboardTab').style.display = 'block';
  currentTab = 'dashboard';
  loadDashboardData();
}

function showBooksTab() {
  hideAllTabs();
  document.getElementById('booksTab').style.display = 'block';
  currentTab = 'books';
  loadBooks();
}

function showLoansTab() {
  hideAllTabs();
  document.getElementById('loansTab').style.display = 'block';
  currentTab = 'loans';
  loadUserLoans();
}

function showNotificationsTab() {
  hideAllTabs();
  document.getElementById('notificationsTab').style.display = 'block';
  currentTab = 'notifications';
  loadNotifications();
}

function hideAllTabs() {
  document.getElementById('dashboardTab').style.display = 'none';
  document.getElementById('booksTab').style.display = 'none';
  document.getElementById('loansTab').style.display = 'none';
  document.getElementById('notificationsTab').style.display = 'none';
}

// Book Actions
async function showBookDetails(bookId) {
  const book = currentBooks.find((b) => b.id === bookId);
  if (!book) return;

  selectedBookId = bookId;

  const cover = book.cover_url
    ? `<img src="${book.cover_url}" class="img-fluid mb-3" style="max-width: 200px;" alt="Book Cover">`
    : `<div class="bg-primary text-white d-flex align-items-center justify-content-center mb-3" style="width: 200px; height: 250px; font-size: 3rem; border-radius: 8px;">${book.title.charAt(
        0
      )}</div>`;

  const content = `
    <div class="row">
      <div class="col-md-4 text-center">
        ${cover}
      </div>
      <div class="col-md-8">
        <h4>${book.title}</h4>
        <p class="text-muted">by ${book.author}</p>
        <p><strong>Category:</strong> ${book.category}</p>
        <p><strong>Availability:</strong> ${book.available_copies}/${
    book.total_copies
  } copies available</p>
        ${
          book.description
            ? `<p><strong>Description:</strong></p><p>${book.description}</p>`
            : ''
        }
      </div>
    </div>
  `;

  document.getElementById('bookDetailsContent').innerHTML = content;

  const borrowBtn = document.getElementById('borrowBookBtn');
  if (book.available_copies > 0) {
    borrowBtn.style.display = 'block';
    borrowBtn.disabled = false;
  } else {
    borrowBtn.style.display = 'none';
  }

  const modal = new bootstrap.Modal(
    document.getElementById('bookDetailsModal')
  );
  modal.show();
}

async function borrowBook() {
  if (!selectedBookId) return;

  showLoading(true);

  try {
    // This would be the actual API call:
    // await apiCall(`/books/${selectedBookId}/borrow`, {
    //   method: 'POST'
    // });

    showAlert(
      'Book borrowed successfully! Check "My Books" to see your loan details.',
      'success'
    );

    // Close modal
    const modal = bootstrap.Modal.getInstance(
      document.getElementById('bookDetailsModal')
    );
    modal.hide();

    // Refresh data
    loadDashboardData();
    if (currentTab === 'books') {
      loadBooks(currentPage);
    }
  } catch (error) {
    console.error('Failed to borrow book:', error);
    showAlert(`Failed to borrow book: ${error.message}`, 'danger');
  } finally {
    showLoading(false);
  }
}

async function renewBook(loanId) {
  showLoading(true);

  try {
    // This would be the actual API call:
    // await apiCall(`/loans/${loanId}/renew`, {
    //   method: 'POST'
    // });

    showAlert('Book renewed successfully!', 'success');
    loadUserLoans();
  } catch (error) {
    console.error('Failed to renew book:', error);
    showAlert(`Failed to renew book: ${error.message}`, 'danger');
  } finally {
    showLoading(false);
  }
}

async function returnBook(loanId) {
  if (!confirm('Are you sure you want to return this book?')) {
    return;
  }

  showLoading(true);

  try {
    // This would be the actual API call:
    // await apiCall(`/loans/${loanId}/return`, {
    //   method: 'POST'
    // });

    showAlert('Book returned successfully!', 'success');
    loadUserLoans();
    loadDashboardData();
  } catch (error) {
    console.error('Failed to return book:', error);
    showAlert(`Failed to return book: ${error.message}`, 'danger');
  } finally {
    showLoading(false);
  }
}

// Search and Filters
function initializeSearch() {
  const searchInput = document.getElementById('searchBooks');
  let searchTimeout;

  if (searchInput) {
    searchInput.addEventListener('input', function () {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        currentFilters.search = this.value.trim();
        loadBooks(1);
      }, 500);
    });
  }
}

function applyBookFilters() {
  currentFilters.category = document.getElementById('categoryFilter').value;
  currentFilters.availability =
    document.getElementById('availabilityFilter').value;
  currentFilters.sort = document.getElementById('sortBooks').value;

  loadBooks(1);
}

function refreshBooks() {
  loadBooks(currentPage);
}

function updateBooksPagination() {
  document.getElementById('currentBooksPage').textContent = currentPage;
}

function previousBooksPage() {
  if (currentPage > 1) {
    loadBooks(currentPage - 1);
  }
}

function nextBooksPage() {
  loadBooks(currentPage + 1);
}

// Notification Actions
async function markNotificationRead(notificationId) {
  try {
    // This would be the actual API call:
    // await apiCall(`/notifications/${notificationId}/read`, {
    //   method: 'PUT'
    // });

    // Update local data
    const notification = currentNotifications.find(
      (n) => n.id === notificationId
    );
    if (notification) {
      notification.is_read = true;
      updateNotificationBadge();
      displayNotifications(currentNotifications);
    }
  } catch (error) {
    console.error('Failed to mark notification as read:', error);
  }
}

async function markAllNotificationsRead() {
  try {
    // This would be the actual API call:
    // await apiCall('/notifications/mark-all-read', {
    //   method: 'POST'
    // });

    // Update local data
    currentNotifications.forEach((n) => (n.is_read = true));
    updateNotificationBadge();
    displayNotifications(currentNotifications);

    showAlert('All notifications marked as read', 'success');
  } catch (error) {
    console.error('Failed to mark all notifications as read:', error);
    showAlert('Failed to mark notifications as read', 'danger');
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
