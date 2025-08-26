from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

class BookCategory(str, Enum):
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    SCIENCE = "science"
    HISTORY = "history"
    BIOGRAPHY = "biography"
    TECHNOLOGY = "technology"
    ARTS = "arts"
    CHILDREN = "children"
    REFERENCE = "reference"
    OTHER = "other"

class BookStatus(str, Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"
    LOST = "lost"

class LoanStatus(str, Enum):
    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"
    LOST = "lost"

# Book schemas
class BookCreate(BaseModel):
    isbn: str = Field(..., min_length=10, max_length=17, description="ISBN-10 or ISBN-13")
    title: str = Field(..., min_length=1, max_length=500)
    author: str = Field(..., min_length=1, max_length=200)
    publisher: Optional[str] = Field(None, max_length=200)
    publication_year: Optional[int] = Field(None, ge=1000, le=2030)
    category: BookCategory
    description: Optional[str] = Field(None, max_length=2000)
    total_copies: int = Field(1, ge=1, le=1000, description="Total number of copies")
    cover_image_url: Optional[str] = Field(None, max_length=500)
    
    @validator('isbn')
    def validate_isbn(cls, v):
        # Remove hyphens and spaces
        isbn = v.replace('-', '').replace(' ', '')
        if len(isbn) not in [10, 13]:
            raise ValueError('ISBN must be 10 or 13 digits')
        if not isbn.isdigit():
            raise ValueError('ISBN must contain only digits')
        return isbn

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    author: Optional[str] = Field(None, min_length=1, max_length=200)
    publisher: Optional[str] = Field(None, max_length=200)
    publication_year: Optional[int] = Field(None, ge=1000, le=2030)
    category: Optional[BookCategory] = None
    description: Optional[str] = Field(None, max_length=2000)
    total_copies: Optional[int] = Field(None, ge=1, le=1000)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    status: Optional[BookStatus] = None

class BookResponse(BaseModel):
    id: int
    isbn: str
    title: str
    author: str
    publisher: Optional[str]
    publication_year: Optional[int]
    category: BookCategory
    description: Optional[str]
    total_copies: int
    available_copies: int
    status: BookStatus
    cover_image_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class BookSearchFilters(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    category: Optional[BookCategory] = None
    status: Optional[BookStatus] = None
    available_only: bool = False

# Book loan schemas
class BookLoanCreate(BaseModel):
    book_id: int = Field(..., description="ID of the book to borrow")
    
class BookLoanResponse(BaseModel):
    id: int
    book_id: int
    user_id: int
    loan_date: date
    due_date: date
    return_date: Optional[date]
    status: LoanStatus
    fine_amount: Optional[float]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Related objects
    book: BookResponse
    user_email: str
    user_name: str

    class Config:
        from_attributes = True

class BookLoanUpdate(BaseModel):
    status: Optional[LoanStatus] = None
    return_date: Optional[date] = None
    fine_amount: Optional[float] = Field(None, ge=0, description="Fine amount in dollars")
    notes: Optional[str] = Field(None, max_length=500)

class BookLoanFilters(BaseModel):
    user_id: Optional[int] = None
    book_id: Optional[int] = None
    status: Optional[LoanStatus] = None
    overdue_only: bool = False
    due_before: Optional[date] = None
    due_after: Optional[date] = None

# Library statistics schemas
class LibraryStats(BaseModel):
    total_books: int
    total_copies: int
    available_copies: int
    borrowed_copies: int
    total_loans: int
    active_loans: int
    overdue_loans: int
    total_users: int
    active_borrowers: int

class UserLoanHistory(BaseModel):
    user_id: int
    user_email: str
    user_name: str
    total_loans: int
    active_loans: int
    overdue_loans: int
    total_fines: float
    last_loan_date: Optional[date]
    loans: List[BookLoanResponse]

class PopularBook(BaseModel):
    book: BookResponse
    loan_count: int
    current_loans: int
