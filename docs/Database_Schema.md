# Database Schema Documentation

## Overview

This document defines the complete database schema for the User Management web application, based on the system requirements and API specifications.

## Database: PostgreSQL

### Database Configuration

- **Database Name**: `user_management_db`
- **Character Set**: UTF-8
- **Collation**: utf8_general_ci

## Tables

### 1. users

**Purpose**: Store core user information for authentication and profile management.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    role VARCHAR(20) DEFAULT 'client' CHECK (role IN ('client', 'admin', 'super_admin')),
    mfa_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE NULL,

    -- Profile fields
    first_name VARCHAR(100) NULL,
    last_name VARCHAR(100) NULL,
    year_of_birth INTEGER NULL CHECK (year_of_birth >= 1900 AND year_of_birth <= EXTRACT(YEAR FROM CURRENT_DATE)),
    description TEXT NULL,
    avatar_url VARCHAR(500) NULL,

    -- Constraints
    CONSTRAINT users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
    CONSTRAINT users_username_length CHECK (LENGTH(username) >= 3),
    CONSTRAINT users_description_length CHECK (LENGTH(description) <= 1000)
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_role ON users(role);
```

### 2. mfa_secrets

**Purpose**: Store MFA secrets and backup codes for two-factor authentication.

```sql
CREATE TABLE mfa_secrets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    secret_key VARCHAR(32) NOT NULL, -- Base32 encoded secret
    is_enabled BOOLEAN DEFAULT FALSE,
    backup_codes TEXT[], -- Array of hashed backup codes
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP WITH TIME ZONE NULL
);

-- Indexes
CREATE INDEX idx_mfa_secrets_user_id ON mfa_secrets(user_id);
```

### 3. email_verifications

**Purpose**: Handle email verification during user registration.

```sql
CREATE TABLE email_verifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    verification_token VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    verified_at TIMESTAMP WITH TIME ZONE NULL,
    is_used BOOLEAN DEFAULT FALSE
);

-- Indexes
CREATE INDEX idx_email_verifications_user_id ON email_verifications(user_id);
CREATE INDEX idx_email_verifications_token ON email_verifications(verification_token);
CREATE INDEX idx_email_verifications_expires_at ON email_verifications(expires_at);
```

### 4. book_categories

**Purpose**: Categorize books in the library system.

```sql
CREATE TABLE book_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_book_categories_name ON book_categories(name);
```

### 5. books

**Purpose**: Store book information for the library management system.

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

    -- Constraints
    CONSTRAINT books_copies_valid CHECK (available_copies >= 0 AND available_copies <= total_copies),
    CONSTRAINT books_isbn_valid CHECK (LENGTH(isbn) IN (10, 13))
);

-- Indexes
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_author ON books(author);
CREATE INDEX idx_books_category_id ON books(category_id);
CREATE INDEX idx_books_isbn ON books(isbn);
```

### 6. book_loans

**Purpose**: Track book borrowing and lending activities.

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

-- Indexes
CREATE INDEX idx_book_loans_user_id ON book_loans(user_id);
CREATE INDEX idx_book_loans_book_id ON book_loans(book_id);
CREATE INDEX idx_book_loans_due_date ON book_loans(due_date);
CREATE INDEX idx_book_loans_status ON book_loans(status);
```

### 7. notifications

**Purpose**: Store user notifications for web and email delivery.

```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'due_reminder', 'overdue', 'book_available', 'system'
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    is_email_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP WITH TIME ZONE NULL
);

-- Indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
```

### 8. user_sessions

**Purpose**: Track user login sessions and JWT tokens for security and session management.

```sql
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_jti VARCHAR(255) UNIQUE NOT NULL, -- JWT ID for token blacklisting
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP WITH TIME ZONE NULL,
    user_agent TEXT NULL,
    ip_address INET NULL,

    -- Constraints
    CONSTRAINT sessions_expires_after_issued CHECK (expires_at > issued_at)
);

-- Indexes
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_token_jti ON user_sessions(token_jti);
CREATE INDEX idx_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX idx_sessions_revoked ON user_sessions(revoked);
```

### 3. password_reset_tokens

**Purpose**: Handle secure password reset functionality.

```sql
CREATE TABLE password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP WITH TIME ZONE NULL,

    -- Constraints
    CONSTRAINT reset_tokens_expires_after_created CHECK (expires_at > created_at)
);

-- Indexes
CREATE INDEX idx_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX idx_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX idx_reset_tokens_expires_at ON password_reset_tokens(expires_at);
```

### 4. audit_logs

**Purpose**: Track important user actions for security and compliance.

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100) NULL,
    details JSONB NULL,
    ip_address INET NULL,
    user_agent TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
```

## Schema Features

### Security Features

1. **Password Hashing**: Passwords stored as bcrypt hashes
2. **Email Validation**: Regex constraint for email format
3. **Session Management**: JWT token tracking with revocation capability
4. **Audit Logging**: Complete audit trail for security monitoring
5. **Data Constraints**: Input validation at database level

### Performance Features

1. **Strategic Indexing**: Indexes on frequently queried columns
2. **Efficient Data Types**: Appropriate data types for optimal storage
3. **Foreign Key Constraints**: Maintain referential integrity

### Scalability Features

1. **Timestamps**: All tables include created_at/updated_at for tracking
2. **Soft Deletes**: Users can be deactivated rather than deleted
3. **Extensible Design**: Schema can be extended for additional features

## Migration Strategy

1. **Initial Migration**: Create all tables with base structure
2. **Data Seeding**: Insert default/system users if needed
3. **Index Creation**: Create performance indexes
4. **Constraint Addition**: Add business logic constraints

## Data Retention Policy

- **User Sessions**: Automatically clean up expired sessions (> 30 days)
- **Password Reset Tokens**: Clean up expired tokens (> 24 hours)
- **Audit Logs**: Retain for 1 year for compliance
- **Inactive Users**: Archive users inactive for > 2 years

## Backup Strategy

- **Full Backup**: Daily full database backup
- **Incremental Backup**: Hourly transaction log backup
- **Point-in-Time Recovery**: 30-day recovery window
- **Cross-Region Replication**: For disaster recovery
