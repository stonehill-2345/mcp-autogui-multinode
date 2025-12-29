from fastapi import APIRouter
from core.config import settings
from .v1.computer import router as computer_router

# Create main router
router = APIRouter()

# Include routers
router.include_router(computer_router, prefix=settings.api_prefix)

@router.get("/")
async def root():
    """Root path, returns API information"""
    return {
        "message": "Computer Use MCP Service",
        "version": settings.version,
        "docs": "/docs",
        "api": settings.api_prefix,
    }

@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

