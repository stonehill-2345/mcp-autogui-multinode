import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Import logger early to initialize logging configuration
from core.logger import logger
from core.config import settings
from tool_server.api.endpoint import router
from middleware.request_id import RequestIDMiddleware
from middleware.auth import APIKeyMiddleware


def create_http_server() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title=settings.title,
        version=settings.version,
        description="Local tool service API",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Should restrict specific domains in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add request ID middleware
    app.add_middleware(RequestIDMiddleware)
    
    # Add API key authentication middleware (if enabled)
    if settings.api_key_enabled:
        app.add_middleware(APIKeyMiddleware)
        logger.info("API key authentication is enabled")
    else:
        logger.info("API key authentication is disabled")
    
    # Register routes
    app.include_router(router)
    return app


# Create global app instance
tool_server_app = create_http_server()

def start_http_server():
    """Start HTTP server"""
    logger.info("Starting HTTP server on {}:{}", settings.host, settings.port)
    logger.info("Environment: {}", settings.environment)
    logger.info("Reload mode: {}", settings.reload)
    logger.info("API Documentation: http://{}:{}/docs", settings.host, settings.port)

    uvicorn.run(
        "tool:tool_server_app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )

def main():
    """Main entry point for the tool service"""
    logger.info("Starting HTTP tool service...")
    start_http_server()


if __name__ == "__main__":
    main()