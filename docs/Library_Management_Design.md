# Library Management System Design

## Overview

The Library Management System extends the User Management application to include book lending functionality for both Client and Admin portals.

## Core Features

### Client Portal Features

- Browse available books
- Borrow books with specified return dates
- View borrowed books and return dates
- Receive notifications for overdue books
- Return books digitally
- Book recommendations

### Admin Portal Features

- Complete book CRUD operations
- Manage book inventory and availability
- Monitor all lending activities
- Handle overdue book notifications
- Generate reports on lending statistics
- Manage book categories and authors

## Database Schema

### Books Table

```sql
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR(13) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    publisher VARCHAR(255),
    publication_year INTEGER,
    category_id INTEGER REFERENCES book_categories(id),
    description TEXT,
    cover_image_url VARCHAR(500),
    total_copies INTEGER NOT NULL DEFAULT 1,
    available_copies INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT books_copies_valid CHECK (available_copies >= 0 AND available_copies <= total_copies)
);
```

### Book Categories Table

```sql
CREATE TABLE book_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Book Loans Table

```sql
CREATE TABLE book_loans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    loan_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP WITH TIME ZONE NOT NULL,
    return_date TIMESTAMP WITH TIME ZONE NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'returned', 'overdue')),
    renewal_count INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Notifications Table

```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'due_reminder', 'overdue', 'book_available'
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    is_email_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP WITH TIME ZONE NULL
);
```

## API Endpoints

### Books Management (Client)

- `GET /api/v1/books` - Browse available books (paginated, filtered)
- `GET /api/v1/books/{id}` - Get book details
- `POST /api/v1/books/{id}/borrow` - Borrow a book
- `GET /api/v1/users/me/loans` - Get user's borrowed books
- `POST /api/v1/loans/{id}/return` - Return a book
- `POST /api/v1/loans/{id}/renew` - Renew a loan

### Books Management (Admin)

- `POST /api/v1/admin/books` - Add new book
- `PUT /api/v1/admin/books/{id}` - Update book information
- `DELETE /api/v1/admin/books/{id}` - Remove book
- `GET /api/v1/admin/loans` - View all loans
- `GET /api/v1/admin/reports/overdue` - Get overdue books report

### Notifications

- `GET /api/v1/notifications` - Get user notifications
- `PUT /api/v1/notifications/{id}/read` - Mark notification as read
- `POST /api/v1/notifications/mark-all-read` - Mark all as read

### Book Categories

- `GET /api/v1/categories` - List all categories
- `POST /api/v1/admin/categories` - Create category (admin)
- `PUT /api/v1/admin/categories/{id}` - Update category (admin)

## Business Logic

### Lending Rules

- **Loan Duration**: 14 days default (configurable by admin)
- **Maximum Books**: 5 books per user simultaneously
- **Renewal**: Up to 2 renewals per book (if not reserved by others)
- **Overdue Grace**: 3-day grace period before penalties

### Notification System

- **Due Reminder**: 2 days before due date
- **Overdue Notice**: Day after due date, then weekly
- **Book Available**: When reserved book becomes available
- **Delivery Methods**: Web notification + email

### Email Templates

- Due date reminder
- Overdue notice with penalty information
- Book reservation confirmation
- New book arrival notifications

## User Interface Components

### Client Portal

- **Book Search**: Advanced search with filters
- **Book Details**: Cover, description, availability
- **My Books**: Current loans, history, renewals
- **Notifications**: In-app notification center
- **Wishlist**: Save books for later

### Admin Portal

- **Book Management**: CRUD operations with bulk actions
- **Loan Monitoring**: Real-time loan status dashboard
- **User Management**: View user lending history
- **Reports**: Overdue books, popular books, lending statistics
- **System Settings**: Configure lending rules and notifications

## Integration Points

### Email Service

- SMTP configuration for notifications
- Email templates and scheduling
- Bounce handling and delivery tracking

### File Storage

- Book cover image upload and storage
- Export capabilities for reports
- Backup and restore functionality

## Performance Considerations

### Caching Strategy

- Book catalog caching for faster searches
- User loan status caching
- Popular books and recommendations caching

### Database Optimization

- Indexes on frequently searched fields
- Partitioning for large notification tables
- Archiving strategy for old loan records

### Scalability

- Microservice architecture for different components
- Queue system for notification processing
- CDN for book cover images
