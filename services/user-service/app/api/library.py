from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional
from datetime import datetime, date, timedelta
from core.database import get_db
from services.auth_service import auth_service, get_current_active_user_dependency, require_admin_dependency
from models.user import User
from models.library import Book, BookLoan, BookCategory as BookCategoryModel
from schemas.library import (
    BookCreate,
    BookUpdate,
    BookResponse,
    BookSearchFilters,
    BookLoanCreate,
    BookLoanResponse,
    BookLoanUpdate,
    BookLoanFilters,
    LibraryStats,
    UserLoanHistory,
    PopularBook,
    BookStatus,
    LoanStatus
)
from schemas.user import UserRole
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/library", tags=["Library Management"])

# Book management endpoints
@router.get("/books", response_model=List[BookResponse])
async def get_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    available_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Get books with filtering and pagination"""
    try:
        query = db.query(Book)
        
        # Apply filters
        if search:
            search_filter = or_(
                Book.title.ilike(f"%{search}%"),
                Book.author.ilike(f"%{search}%"),
                Book.isbn.ilike(f"%{search}%"),
                Book.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if category:
            query = query.filter(Book.category == category)
        
        if available_only:
            query = query.filter(Book.available_copies > 0)
        
        # Get books with pagination
        books = query.order_by(Book.title).offset(skip).limit(limit).all()
        
        return [BookResponse.model_validate(book) for book in books]
        
    except Exception as e:
        logger.error(f"Error getting books: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get books"
        )

@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Get book by ID"""
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        return BookResponse.model_validate(book)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting book: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get book"
        )

@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_create: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_dependency)
):
    """Create a new book (Admin only)"""
    try:
        # Check if book with ISBN already exists
        existing_book = db.query(Book).filter(Book.isbn == book_create.isbn).first()
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book with this ISBN already exists"
            )
        
        # Create book
        book_data = book_create.model_dump()
        book_data['available_copies'] = book_data['total_copies']
        book_data['status'] = BookStatus.AVAILABLE
        
        book = Book(**book_data)
        db.add(book)
        db.commit()
        db.refresh(book)
        
        logger.info(f"Book created: {book.id} by admin {current_user.id}")
        
        return BookResponse.model_validate(book)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating book: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create book"
        )

@router.put("/books/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book_update: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_dependency)
):
    """Update book (Admin only)"""
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        # Update fields
        update_data = book_update.model_dump(exclude_unset=True)
        
        # Handle total_copies change
        if 'total_copies' in update_data:
            new_total = update_data['total_copies']
            old_total = book.total_copies
            borrowed_copies = old_total - book.available_copies
            
            if new_total < borrowed_copies:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot reduce total copies below borrowed copies ({borrowed_copies})"
                )
            
            book.available_copies = new_total - borrowed_copies
        
        # Update other fields
        for field, value in update_data.items():
            if hasattr(book, field):
                setattr(book, field, value)
        
        book.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Book updated: {book_id} by admin {current_user.id}")
        
        return BookResponse.model_validate(book)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating book: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update book"
        )

@router.delete("/books/{book_id}")
async def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_dependency)
):
    """Delete book (Admin only)"""
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        # Check if book has active loans
        active_loans = db.query(BookLoan).filter(
            and_(
                BookLoan.book_id == book_id,
                BookLoan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE])
            )
        ).count()
        
        if active_loans > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete book with {active_loans} active loans"
            )
        
        db.delete(book)
        db.commit()
        
        logger.info(f"Book deleted: {book_id} by admin {current_user.id}")
        
        return {"message": "Book deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting book: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete book"
        )

# Loan management endpoints
@router.post("/loans", response_model=BookLoanResponse, status_code=status.HTTP_201_CREATED)
async def borrow_book(
    loan_create: BookLoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Borrow a book"""
    try:
        # Check if book exists and is available
        book = db.query(Book).filter(Book.id == loan_create.book_id).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        if book.available_copies <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book is not available for borrowing"
            )
        
        # Check user's current active loans (implement loan limit)
        active_loans = db.query(BookLoan).filter(
            and_(
                BookLoan.user_id == current_user.id,
                BookLoan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE])
            )
        ).count()
        
        max_loans = 5  # Could be configurable
        if active_loans >= max_loans:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum loan limit ({max_loans}) reached"
            )
        
        # Check if user already has this book
        existing_loan = db.query(BookLoan).filter(
            and_(
                BookLoan.user_id == current_user.id,
                BookLoan.book_id == loan_create.book_id,
                BookLoan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE])
            )
        ).first()
        
        if existing_loan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have this book borrowed"
            )
        
        # Create loan
        loan_date = date.today()
        due_date = loan_date + timedelta(days=14)  # 2 weeks loan period
        
        loan = BookLoan(
            book_id=loan_create.book_id,
            user_id=current_user.id,
            loan_date=loan_date,
            due_date=due_date,
            status=LoanStatus.ACTIVE
        )
        
        # Update book availability
        book.available_copies -= 1
        
        db.add(loan)
        db.commit()
        db.refresh(loan)
        
        logger.info(f"Book borrowed: {loan_create.book_id} by user {current_user.id}")
        
        # Create response with related data
        response = BookLoanResponse(
            **loan.__dict__,
            book=BookResponse.model_validate(book),
            user_email=current_user.email,
            user_name=f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.username
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error borrowing book: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to borrow book"
        )

@router.get("/loans", response_model=List[BookLoanResponse])
async def get_loans(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[LoanStatus] = Query(None),
    user_id: Optional[int] = Query(None),
    book_id: Optional[int] = Query(None),
    overdue_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Get loans (users see their own, admins see all)"""
    try:
        query = db.query(BookLoan)
        
        # Regular users can only see their own loans
        if current_user.role == UserRole.CLIENT:
            query = query.filter(BookLoan.user_id == current_user.id)
        else:
            # Admins can filter by user_id
            if user_id is not None:
                query = query.filter(BookLoan.user_id == user_id)
        
        # Apply filters
        if book_id is not None:
            query = query.filter(BookLoan.book_id == book_id)
        
        if status_filter is not None:
            query = query.filter(BookLoan.status == status_filter)
        
        if overdue_only:
            query = query.filter(
                and_(
                    BookLoan.due_date < date.today(),
                    BookLoan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE])
                )
            )
        
        # Get loans with pagination
        loans = query.order_by(desc(BookLoan.loan_date)).offset(skip).limit(limit).all()
        
        # Build response with related data
        response_loans = []
        for loan in loans:
            book = db.query(Book).filter(Book.id == loan.book_id).first()
            user = db.query(User).filter(User.id == loan.user_id).first()
            
            response = BookLoanResponse(
                **loan.__dict__,
                book=BookResponse.model_validate(book),
                user_email=user.email,
                user_name=f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username
            )
            response_loans.append(response)
        
        return response_loans
        
    except Exception as e:
        logger.error(f"Error getting loans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get loans"
        )

@router.put("/loans/{loan_id}/return", response_model=BookLoanResponse)
async def return_book(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Return a borrowed book"""
    try:
        loan = db.query(BookLoan).filter(BookLoan.id == loan_id).first()
        if not loan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Loan not found"
            )
        
        # Check if user owns this loan (unless admin)
        if current_user.role == UserRole.CLIENT and loan.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only return your own books"
            )
        
        # Check if book is already returned
        if loan.status == LoanStatus.RETURNED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book is already returned"
            )
        
        # Update loan
        loan.return_date = date.today()
        loan.status = LoanStatus.RETURNED
        
        # Calculate fine for overdue books
        if loan.return_date > loan.due_date:
            days_overdue = (loan.return_date - loan.due_date).days
            fine_per_day = 0.50  # Could be configurable
            loan.fine_amount = days_overdue * fine_per_day
        
        # Update book availability
        book = db.query(Book).filter(Book.id == loan.book_id).first()
        book.available_copies += 1
        
        loan.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Book returned: loan {loan_id} by user {current_user.id}")
        
        # Build response
        user = db.query(User).filter(User.id == loan.user_id).first()
        response = BookLoanResponse(
            **loan.__dict__,
            book=BookResponse.model_validate(book),
            user_email=user.email,
            user_name=f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error returning book: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to return book"
        )

@router.get("/stats", response_model=LibraryStats)
async def get_library_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_dependency)
):
    """Get library statistics (Admin only)"""
    try:
        # Book statistics
        total_books = db.query(Book).count()
        total_copies = db.query(func.sum(Book.total_copies)).scalar() or 0
        available_copies = db.query(func.sum(Book.available_copies)).scalar() or 0
        borrowed_copies = total_copies - available_copies
        
        # Loan statistics
        total_loans = db.query(BookLoan).count()
        active_loans = db.query(BookLoan).filter(
            BookLoan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE])
        ).count()
        overdue_loans = db.query(BookLoan).filter(
            and_(
                BookLoan.due_date < date.today(),
                BookLoan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE])
            )
        ).count()
        
        # User statistics
        total_users = db.query(User).count()
        active_borrowers = db.query(BookLoan.user_id).filter(
            BookLoan.status.in_([LoanStatus.ACTIVE, LoanStatus.OVERDUE])
        ).distinct().count()
        
        return LibraryStats(
            total_books=total_books,
            total_copies=total_copies,
            available_copies=available_copies,
            borrowed_copies=borrowed_copies,
            total_loans=total_loans,
            active_loans=active_loans,
            overdue_loans=overdue_loans,
            total_users=total_users,
            active_borrowers=active_borrowers
        )
        
    except Exception as e:
        logger.error(f"Error getting library stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get library statistics"
        )
