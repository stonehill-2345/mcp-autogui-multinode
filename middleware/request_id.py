from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar
from uuid import uuid4

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")

def get_request_id() -> str:
    """Get request ID from context variable"""
    return request_id_ctx.get()

def set_request_id(rid: str):
    """Set request ID in context variable"""
    request_id_ctx.set(rid)

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to each request"""
    async def dispatch(self, request: Request, call_next) -> Response:
        # Get request ID from header, or generate a new one if not provided
        header_rid = request.headers.get("X-Request-ID")
        request_id = header_rid if header_rid else str(uuid4())
        set_request_id(request_id)
        
        # Add request ID to response header
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response