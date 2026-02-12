"""Main FastAPI application."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.logging import LoggingMiddleware
from app.core.config import check_environment_on_startup
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Validate environment variables on startup
check_environment_on_startup()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI application
app = FastAPI(
    title="Todo App API",
    description="Task management API with JWT authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Todo App API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Include API routes
from app.api.v1 import tasks, auth
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
