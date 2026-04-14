"""
Fake Job Detection API - FastAPI Application

This module provides the main FastAPI application with:
- Automatic Swagger UI documentation at /docs
- ReDoc documentation at /redoc
- CORS middleware for frontend access
- Health check endpoints
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load .env from backend directory so it works when running from any cwd (e.g. project root)
_backend_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_backend_dir, ".env"))
load_dotenv()  # also allow cwd .env

# Import routers
from app.routes.predict import router as predict_router

# Create FastAPI app
app = FastAPI(
    title="Fake Job Detection API",
    description="AI-powered API to detect fraudulent job postings using BERT model",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predict_router, prefix="/api", tags=["Prediction"])


@app.get("/")
def root():
    return {"message": "Fake Job Detection API", "status": "running", "docs": "/docs"}


@app.on_event("startup")
def log_model_path():
    """Log resolved model path at startup so you can verify it when using API docs."""
    from app.utils.config import Config
    path = Config.get_model_path()
    print(f"[STARTUP] Model path: {path}")
    print(f"[STARTUP] Path exists: {os.path.exists(path)}")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API status check"""
    return {
        "message": "Fake Job Detection API",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
