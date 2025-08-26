// Admin Library Management functionality

let currentBooks = [];
let currentPage = 1;
let booksPerPage = 10;
let totalBooks = 0;
let currentFilters = {
  search: '',
  genre: '',
  availability: '',
  language: '',
  sortBy: 'title',
};

document.addEventListener('DOMContentLoaded', function () {
  // Check admin access
  checkAdminAccess();

  // Load books and stats
  loadBooks();
  loadLibraryStats();

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

async function loadLibraryStats() {
  try {
    // Since we don't have specific library stats endpoints, we'll use placeholder data
    // In a real implementation, these would come from actual API endpoints

    // For now, show placeholder data
    document.getElementById('totalBooks').textContent = '1,234';
    document.getElementById('availableBooks').textContent = '987';
    document.getElementById('borrowedBooks').textContent = '247';
    document.getElementById('overdueBooks').textContent = '23';

    // These would be actual API calls:
    // const stats = await apiCall('/admin/library/stats', { method: 'GET' });
    // document.getElementById('totalBooks').textContent = stats.total_books;
    // document.getElementById('availableBooks').textContent = stats.available_books;
    // document.getElementById('borrowedBooks').textContent = stats.borrowed_books;
    // document.getElementById('overdueBooks').textContent = stats.overdue_books;
  } catch (error) {
    console.error('Failed to load library stats:', error);
    // Show placeholder data on error
    document.getElementById('totalBooks').textContent = '-';
    document.getElementById('availableBooks').textContent = '-';
    document.getElementById('borrowedBooks').textContent = '-';
    document.getElementById('overdueBooks').textContent = '-';
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
    if (currentFilters.genre) {
      params.append('genre', currentFilters.genre);
    }
    if (currentFilters.availability) {
      params.append('availability', currentFilters.availability);
    }
    if (currentFilters.language) {
      params.append('language', currentFilters.language);
    }
    if (currentFilters.sortBy) {
      params.append('sort_by', currentFilters.sortBy);
    }

    // For now, using mock data since the books endpoints might not be implemented
    const mockBooks = generateMockBooks();
    currentBooks = mockBooks;
    displayBooks(mockBooks);
    updatePagination();

    // This would be the actual API call:
    // const books = await apiCall(`/admin/books?${params.toString()}`, {
    //   method: 'GET',
    // });
    // currentBooks = books;
    // displayBooks(books);
    // updatePagination();
  } catch (error) {
    console.error('Failed to load books:', error);
    showAlert('Failed to load books', 'danger');
    displayBooksError();
  } finally {
    showLoading(false);
  }
}

function generateMockBooks() {
  // Mock data for demonstration
  return [
    {
      id: 1,
      title: 'The Great Gatsby',
      author: 'F. Scott Fitzgerald',
      isbn: '978-0-7432-7356-5',
      publisher: 'Scribner',
      genre: 'Fiction',
      language: 'English',
      published_year: 1925,
      description: 'A classic American novel set in the Jazz Age.',
      cover_url: null,
      total_copies: 5,
      available_copies: 3,
      created_at: '2023-01-15T10:30:00Z',
    },
    {
      id: 2,
      title: 'To Kill a Mockingbird',
      author: 'Harper Lee',
      isbn: '978-0-06-112008-4',
      publisher: 'J.B. Lippincott & Co.',
      genre: 'Fiction',
      language: 'English',
      published_year: 1960,
      description:
        'A gripping tale of racial injustice and childhood innocence.',
      cover_url: null,
      total_copies: 4,
      available_copies: 2,
      created_at: '2023-01-20T14:15:00Z',
    },
    {
      id: 3,
      title: '1984',
      author: 'George Orwell',
      isbn: '978-0-452-28423-4',
      publisher: 'Secker & Warburg',
      genre: 'Fiction',
      language: 'English',
      published_year: 1949,
      description: 'A dystopian social science fiction novel.',
      cover_url: null,
      total_copies: 6,
      available_copies: 0,
      created_at: '2023-02-01T09:45:00Z',
    },
    {
      id: 4,
      title: 'Clean Code',
      author: 'Robert C. Martin',
      isbn: '978-0-13-235088-4',
      publisher: 'Prentice Hall',
      genre: 'Technology',
      language: 'English',
      published_year: 2008,
      description: 'A handbook of agile software craftsmanship.',
      cover_url: null,
      total_copies: 3,
      available_copies: 1,
      created_at: '2023-02-10T16:20:00Z',
    },
    {
      id: 5,
      title: 'The Art of War',
      author: 'Sun Tzu',
      isbn: '978-1-59030-963-7',
      publisher: 'Various',
      genre: 'History',
      language: 'English',
      published_year: -500,
      description: 'Ancient Chinese military treatise.',
      cover_url: null,
      total_copies: 2,
      available_copies: 2,
      created_at: '2023-02-15T11:30:00Z',
    },
  ];
}

function displayBooks(books) {
  const tbody = document.getElementById('booksTableBody');

  if (!books || books.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center py-4">
          <i class="fas fa-books fa-3x text-muted mb-3"></i>
          <p class="text-muted">No books found</p>
        </td>
      </tr>
    `;
    document.getElementById('totalBooksCount').textContent = '0';
    return;
  }

  document.getElementById('totalBooksCount').textContent = books.length;

  tbody.innerHTML = books
    .map((book) => {
      const cover = book.cover_url
        ? `<img src="${book.cover_url}" class="book-cover" alt="Book Cover">`
        : `<div class="book-cover-placeholder">${book.title
            .charAt(0)
            .toUpperCase()}</div>`;

      const availabilityBadge = getAvailabilityBadge(
        book.available_copies,
        book.total_copies
      );

      const genreBadge = `<span class="badge bg-secondary genre-badge">${book.genre}</span>`;

      const publishedYear =
        book.published_year > 0 ? book.published_year : 'Ancient';

      return `
      <tr>
        <td class="text-center">
          ${cover}
        </td>
        <td>
          <div class="book-info">
            <div class="book-title">${book.title}</div>
            <div class="book-author">by ${book.author}</div>
            ${
              book.isbn ? `<div class="book-isbn">ISBN: ${book.isbn}</div>` : ''
            }
            ${
              book.publisher
                ? `<div class="text-muted small">Publisher: ${book.publisher}</div>`
                : ''
            }
          </div>
        </td>
        <td>${genreBadge}</td>
        <td>
          <span class="badge bg-info genre-badge">${book.language}</span>
        </td>
        <td>${availabilityBadge}</td>
        <td>
          <span class="text-muted">${publishedYear}</span>
        </td>
        <td>
          <div class="btn-group" role="group">
            <button class="btn btn-sm btn-outline-primary action-btn" 
                    onclick="viewBook(${book.id})" title="View Details">
              <i class="fas fa-eye"></i>
            </button>
            <button class="btn btn-sm btn-outline-warning action-btn" 
                    onclick="editBook(${book.id})" title="Edit Book">
              <i class="fas fa-edit"></i>
            </button>
            <button class="btn btn-sm btn-outline-info action-btn" 
                    onclick="manageLoans(${book.id})" title="Manage Loans">
              <i class="fas fa-exchange-alt"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger action-btn" 
                    onclick="deleteBook(${book.id})" title="Delete Book">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
    })
    .join('');
}

function getAvailabilityBadge(available, total) {
  if (available === 0) {
    return `
      <span class="badge bg-danger availability-badge">
        All Borrowed (0/${total})
      </span>
    `;
  } else if (available === total) {
    return `
      <span class="badge bg-success availability-badge">
        All Available (${available}/${total})
      </span>
    `;
  } else {
    return `
      <span class="badge bg-warning availability-badge">
        ${available}/${total} Available
      </span>
    `;
  }
}

function displayBooksError() {
  const tbody = document.getElementById('booksTableBody');
  tbody.innerHTML = `
    <tr>
      <td colspan="7" class="text-center py-4">
        <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
        <p class="text-danger">Failed to load books</p>
        <button class="btn btn-outline-primary btn-sm" onclick="loadBooks()">
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
      loadBooks(1);
    }, 500);
  });
}

function applyFilters() {
  currentFilters.genre = document.getElementById('genreFilter').value;
  currentFilters.availability =
    document.getElementById('availabilityFilter').value;
  currentFilters.language = document.getElementById('languageFilter').value;
  currentFilters.sortBy = document.getElementById('sortBy').value;

  loadBooks(1);
}

function refreshBooks() {
  loadBooks(currentPage);
  loadLibraryStats();
}

function updatePagination() {
  const showingStart = (currentPage - 1) * booksPerPage + 1;
  const showingEnd = Math.min(currentPage * booksPerPage, currentBooks.length);

  document.getElementById('showingStart').textContent = showingStart;
  document.getElementById('showingEnd').textContent = showingEnd;
  document.getElementById('totalBooksCount').textContent = currentBooks.length;
  document.getElementById('currentPageNum').textContent = currentPage;
}

function previousPage() {
  if (currentPage > 1) {
    loadBooks(currentPage - 1);
  }
}

function nextPage() {
  // In a real implementation, this would check against total pages from the API
  loadBooks(currentPage + 1);
}

function showAddBookModal() {
  const modal = new bootstrap.Modal(document.getElementById('addBookModal'));
  modal.show();
}

async function addBook() {
  const form = document.getElementById('addBookForm');
  if (!validateAddBookForm()) {
    return;
  }

  showLoading(true);

  try {
    const bookData = {
      title: document.getElementById('newTitle').value.trim(),
      author: document.getElementById('newAuthor').value.trim(),
      isbn: document.getElementById('newISBN').value.trim() || null,
      publisher: document.getElementById('newPublisher').value.trim() || null,
      genre: document.getElementById('newGenre').value,
      language: document.getElementById('newLanguage').value,
      published_year:
        parseInt(document.getElementById('newPublishedYear').value) || null,
      description:
        document.getElementById('newDescription').value.trim() || null,
      cover_url: document.getElementById('newCoverUrl').value.trim() || null,
      total_copies: parseInt(document.getElementById('newTotalCopies').value),
    };

    // This would be the actual API call:
    // await apiCall('/admin/books', {
    //   method: 'POST',
    //   body: JSON.stringify(bookData)
    // });

    showAlert('Book added successfully!', 'success');

    // Close modal and reset form
    const modal = bootstrap.Modal.getInstance(
      document.getElementById('addBookModal')
    );
    modal.hide();
    form.reset();

    // Reload books and stats
    loadBooks(currentPage);
    loadLibraryStats();
  } catch (error) {
    console.error('Failed to add book:', error);
    showAlert(`Failed to add book: ${error.message}`, 'danger');
  } finally {
    showLoading(false);
  }
}

function validateAddBookForm() {
  const title = document.getElementById('newTitle').value.trim();
  const author = document.getElementById('newAuthor').value.trim();
  const genre = document.getElementById('newGenre').value;
  const language = document.getElementById('newLanguage').value;
  const totalCopies = parseInt(document.getElementById('newTotalCopies').value);
  const isbn = document.getElementById('newISBN').value.trim();

  let isValid = true;

  // Clear previous errors
  clearFieldError('newTitle');
  clearFieldError('newAuthor');
  clearFieldError('newGenre');
  clearFieldError('newLanguage');
  clearFieldError('newTotalCopies');
  clearFieldError('newISBN');

  // Validate required fields
  if (!title) {
    setFieldError('newTitle', 'Title is required');
    isValid = false;
  }

  if (!author) {
    setFieldError('newAuthor', 'Author is required');
    isValid = false;
  }

  if (!genre) {
    setFieldError('newGenre', 'Genre is required');
    isValid = false;
  }

  if (!language) {
    setFieldError('newLanguage', 'Language is required');
    isValid = false;
  }

  if (!totalCopies || totalCopies < 1) {
    setFieldError('newTotalCopies', 'Total copies must be at least 1');
    isValid = false;
  }

  // Validate ISBN format if provided
  if (isbn) {
    const isbnRegex = /^(?:97[89][-\s]?)?[\d\-\s]{10,17}[\dX]$/i;
    if (!isbnRegex.test(isbn.replace(/[-\s]/g, ''))) {
      setFieldError('newISBN', 'Please enter a valid ISBN');
      isValid = false;
    }
  }

  return isValid;
}

async function viewBook(bookId) {
  const book = currentBooks.find((b) => b.id === bookId);
  if (!book) return;

  let details = `
    <strong>Title:</strong> ${book.title}<br>
    <strong>Author:</strong> ${book.author}<br>
    <strong>Genre:</strong> ${book.genre}<br>
    <strong>Language:</strong> ${book.language}<br>
    <strong>Availability:</strong> ${book.available_copies}/${book.total_copies} copies available
  `;

  if (book.isbn) details += `<br><strong>ISBN:</strong> ${book.isbn}`;
  if (book.publisher)
    details += `<br><strong>Publisher:</strong> ${book.publisher}`;
  if (book.published_year)
    details += `<br><strong>Published:</strong> ${book.published_year}`;
  if (book.description)
    details += `<br><br><strong>Description:</strong><br>${book.description}`;

  showAlert(details, 'info');
}

async function editBook(bookId) {
  const book = currentBooks.find((b) => b.id === bookId);
  if (!book) return;

  showAlert(
    `Edit functionality for "${book.title}" would be implemented here`,
    'info'
  );
}

async function manageLoans(bookId) {
  const book = currentBooks.find((b) => b.id === bookId);
  if (!book) return;

  showAlert(
    `Loan management for "${book.title}" would be implemented here`,
    'info'
  );
}

async function deleteBook(bookId) {
  const book = currentBooks.find((b) => b.id === bookId);
  if (!book) return;

  if (
    !confirm(
      `Are you sure you want to delete "${book.title}"?\n\nThis action cannot be undone.`
    )
  ) {
    return;
  }

  showLoading(true);

  try {
    // This would be the actual API call:
    // await apiCall(`/admin/books/${bookId}`, {
    //   method: 'DELETE'
    // });

    showAlert(`Book "${book.title}" deleted successfully`, 'success');
    loadBooks(currentPage);
    loadLibraryStats();
  } catch (error) {
    console.error('Failed to delete book:', error);
    showAlert(`Failed to delete book: ${error.message}`, 'danger');
  } finally {
    showLoading(false);
  }
}

function exportBooks() {
  if (currentBooks.length === 0) {
    showAlert('No books to export', 'warning');
    return;
  }

  // Create CSV content
  const headers = [
    'Title',
    'Author',
    'ISBN',
    'Genre',
    'Language',
    'Year',
    'Total Copies',
    'Available',
  ];
  const csvContent = [
    headers.join(','),
    ...currentBooks.map((book) =>
      [
        `"${book.title}"`,
        `"${book.author}"`,
        book.isbn || '',
        book.genre,
        book.language,
        book.published_year || '',
        book.total_copies,
        book.available_copies,
      ].join(',')
    ),
  ].join('\n');

  // Download CSV
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `library_books_${new Date().toISOString().split('T')[0]}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);

  showAlert('Books exported successfully', 'success');
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
