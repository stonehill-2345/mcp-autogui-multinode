"""Global logger configuration using loguru"""
import sys
from pathlib import Path
from loguru import logger
from core.config import settings
from middleware.request_id import get_request_id


# Configure patcher to add request_id to all log records
def add_request_id(record):
    """Add request_id to log record from context variable"""
    request_id = get_request_id()
    record["extra"]["request_id"] = request_id if request_id else "-"
    return record


# Apply patcher to logger
logger = logger.patch(add_request_id)

# Remove default logger handler
logger.remove()

# Add console handler with custom format (includes request_id)
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <yellow>[{extra[request_id]}]</yellow> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.reload else "INFO",
    colorize=True,
)

# Add file handlers only in production mode (when reload=False)
# In development mode (reload=True), logs only go to console
if not settings.environment == "development":
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | [{extra[request_id]}] | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="00:00",  # Rotate at midnight
        retention="30 days",  # Keep logs for 30 days
        compression="zip",  # Compress old logs
        encoding="utf-8",
    )

    # Add error file handler for errors only
    logger.add(
        log_dir / "error_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | [{extra[request_id]}] | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="00:00",
        retention="90 days",  # Keep error logs longer
        compression="zip",
        encoding="utf-8",
    )


# Export logger instance for use throughout the application
__all__ = ["logger"]

