from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.endpoints import router as api_router
from core.config import settings
from db.session import engine
from models.user import User
import os

# Create database tables
User.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="User Management Microservice with FastAPI",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files for avatar uploads
uploads_dir = "/app/uploads"
os.makedirs(f"{uploads_dir}/avatars", exist_ok=True)
try:
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=uploads_dir), name="static")
except ImportError:
    # Handle case where StaticFiles is not available
    pass

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the User Management Service",
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "user-management"}
